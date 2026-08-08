"""Owner-readable Phase 9 N=1 entry point, locked to rehearsal mode.

This batch deliberately has no execution authorization.  The default path
constructs the real gate, verifier, locks, burn ledger, audit-chain adapter,
snapshotter, and presence parser around controlled in-memory boundaries.  A
request for real mode is rejected before any real executor can be built.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
import threading
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Protocol, Sequence, TextIO, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.phase9_audit_chain_writer import LocalAuditChainWriter
from app.phase9_burn_ledger import FileBurnLedger
from app.phase9_gate import (
    EXPECTED_OPENCLAW_VERSION,
    PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
    PHASE9_AUDIT_SCOPE,
    ActionRequest,
    AuditAuthorizationVerifier,
    DirectorySnapshotter,
    ExecutionResult,
    FreshChallenge,
    GateRequest,
    OwnerAuthorizedOpenClawVersionProbe,
    Phase9AuditAuthorizationRecord,
    Phase9Gate,
    PresenceChannel,
)
from app.phase9_openclaw_executor import ProcessOutcome
from app.phase9_preflight import (
    BoundedGateTokenAuditCoordinationLock,
    FrozenGateRequestVerifier,
)
from app.phase9_presence import PresenceInputs
from app.phase9_presence_channel import (
    JsonPresenceChannel,
    PresenceChannelError,
    PresenceEndpoint,
    PresenceRead,
    RegularFilePresenceReader,
)
from app.phase9_token import TokenPresentation
from app.phase9_token_issuer import (
    OwnerPresenceProof,
    Phase9TokenIssuer,
    TokenIssuanceRequest,
)


REHEARSAL_NOW = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)
REHEARSAL_ID = "phase9-n1-entrypoint-rehearsal"
OOB_RESPONSE_FILENAME = "owner-response.json"


class RealExecutorFactory(Protocol):
    """Execution-day construction boundary; this batch never invokes it."""

    def __call__(self) -> object:
        """Construct a real executor only under a future execution grant."""


class WorkspaceFactory(Protocol):
    def __call__(self) -> AbstractContextManager[str]:
        """Return an isolated rehearsal workspace context."""


class _AuditWriterModule(Protocol):
    REPO_ROOT: Path
    AUDIT_PATH: Path

    def read_audit_events(self) -> list[dict[str, Any]]: ...


def _audit_writer() -> _AuditWriterModule:
    return cast(_AuditWriterModule, importlib.import_module("app.audit_writer_local"))


@dataclass(frozen=True)
class RehearsalReport:
    """Non-secret evidence returned to the command-line presenter."""

    fake_executor_calls: int
    real_executor_calls: int
    trace: tuple[str, ...]
    burn_records: int
    audit_records: int


class _DeniedRealExecutorFactory:
    """Counter-bearing tripwire; no path in this batch may call it."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> object:
        self.calls += 1
        raise RuntimeError("real execution remains locked")


class _SteppingClock:
    def __init__(self) -> None:
        self._current = REHEARSAL_NOW

    def __call__(self) -> datetime:
        self._current += timedelta(seconds=1)
        return self._current


class _ControlledVersionRunner:
    """Synthetic version boundary; it never starts a process."""

    def __init__(self) -> None:
        self.calls = 0

    def invoke(
        self,
        argv: Sequence[str],
        *,
        timeout_seconds: int,
    ) -> ProcessOutcome:
        if tuple(argv) != ("openclaw", "--version") or timeout_seconds != 5:
            raise RuntimeError("rehearsal version request is invalid")
        self.calls += 1
        return ProcessOutcome(
            exit_code=0,
            timed_out=False,
            stdout=(EXPECTED_OPENCLAW_VERSION + "\n").encode("utf-8"),
            stderr=b"",
        )


class _ControlledDryRunExecutor:
    """Foreground fake with no subprocess, network, retry, or side effect."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(
        self,
        argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        del argv, timeout_seconds
        self.calls += 1
        return ExecutionResult(
            exit_code=0,
            timed_out=False,
            stdout_digest=hashlib.sha256(b"controlled rehearsal output").hexdigest(),
            stderr_digest=hashlib.sha256(b"").hexdigest(),
        )


class _ControlledTokenPresenceVerifier:
    """Accept only the fixed rehearsal proof bound to the issuance request."""

    def verify(
        self,
        proof: OwnerPresenceProof,
        *,
        request: TokenIssuanceRequest,
    ) -> bool:
        return (
            proof.rehearsal_id == request.rehearsal_id == REHEARSAL_ID
            and proof.approval_packet_hash == request.approval_packet_hash
            and proof.action_hash == request.action_hash
            and proof.observed_at <= request.now < proof.valid_until
        )


class _ControlledOwnerTokenEgress:
    """Hold the fixed rehearsal value in memory until its single presentation."""

    def __init__(self) -> None:
        self._raw_value: str | None = None

    def display_once(
        self,
        raw_value: str,
        *,
        mask_reference: str,
        expires_at: datetime,
    ) -> bool:
        del mask_reference, expires_at
        if self._raw_value is not None:
            return False
        self._raw_value = raw_value
        return True

    def take_for_rehearsal(self) -> str:
        if self._raw_value is None:
            raise RuntimeError("controlled token egress is empty")
        raw_value = self._raw_value
        self._raw_value = None
        return raw_value


class _FixedRehearsalRandom:
    """Return the fixed HMAC key and token vectors; never call a CSPRNG."""

    def __init__(self) -> None:
        self._values = (b"k" * 32, b"d" * 32)
        self.calls = 0

    def __call__(self, size: int) -> bytes:
        if size != 32 or self.calls >= len(self._values):
            raise RuntimeError("fixed rehearsal random request is invalid")
        value = self._values[self.calls]
        self.calls += 1
        return value


class _StaticPresenceReader:
    def __init__(self, observation: PresenceRead) -> None:
        self._observation = observation

    def read(
        self,
        endpoint: PresenceEndpoint,
        *,
        deadline: datetime,
    ) -> PresenceRead:
        del endpoint, deadline
        return self._observation


class _ControlledPresenceChannel:
    """Feed a synthetic response through the real JSON presence parser."""

    def __init__(
        self,
        *,
        response_path: Path,
        gate_principal: str,
        expected_owner_principal: str,
    ) -> None:
        self._response_path = response_path
        self._gate_principal = gate_principal
        self._expected_owner_principal = expected_owner_principal

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        observed_at = challenge.issued_at + timedelta(milliseconds=1)
        endpoint = PresenceEndpoint(
            path=self._response_path,
            medium="rehearsal-memory",
            gate_principal=self._gate_principal,
            expected_owner_principal=self._expected_owner_principal,
            contract_digest="c" * 64,
            continuity_id="rehearsal-continuity",
            max_validity_seconds=60,
        )
        payload = json.dumps(
            {
                "action_hash": challenge.action_hash,
                "approval_packet_hash": challenge.approval_packet_hash,
                "challenge_id": challenge.challenge_id,
                "continuity_id": "rehearsal-continuity",
                "owner_confirmed": True,
                "owner_verbatim_authorization_verified": True,
                "rehearsal_id": challenge.rehearsal_id,
            },
            sort_keys=True,
        ).encode("utf-8")
        reader = _StaticPresenceReader(
            PresenceRead(
                payload=payload,
                endpoint_path=self._response_path,
                medium="rehearsal-memory",
                owner_principal=self._expected_owner_principal,
                permissions_verified=True,
                observed_at=observed_at,
            )
        )
        return JsonPresenceChannel(
            endpoint=endpoint,
            reader=reader,
            clock=lambda: observed_at,
        ).collect_after_second_challenge(challenge)


def _runtime_gate_principal() -> str:
    return f"uid:{os.getuid()}"


def _validated_oob_directory(value: Path) -> Path:
    directory = Path(value)
    normalized = directory.as_posix().rstrip("/") or "/"
    # Execution-day OOB must live on WSL's native filesystem. DrvFS under
    # /mnt/c reports Windows files as the gate uid, defeating st_uid isolation.
    if normalized == "/mnt/c" or normalized.startswith("/mnt/c/"):
        raise ValueError("OOB directory must use WSL native storage, not /mnt/c")
    return directory


def _workspace_factory() -> AbstractContextManager[str]:
    return TemporaryDirectory(prefix="phase9-n1-rehearsal-")


def _print_owner_report(
    output: TextIO,
    report: RehearsalReport,
    *,
    synthetic_presence: bool,
) -> None:
    presence_message = (
        "第二道新挑戰已完成（合成 Owner 回應）。"
        if synthetic_presence
        else "第二道新挑戰已完成（真實 OOB 檔案讀取）。"
    )
    messages = (
        "契約格式已重新確認。",
        "這張單與這個動作的摘要已重新比對。",
        "Phase 9 的資料契約已接受。",
        "Owner 授權文字的動作與目標已核對（僅演練）。",
        "固定測試 token 已驗證；沒有產生真實 token。",
        "預檢、版本假件與檔案快照已通過。",
        presence_message,
        "六個在場條件已重新計算並全部通過。",
        "測試 token 已先寫入暫存作廢帳本。",
        "作廢證據已寫入暫存稽核鏈並驗證。",
        "一次性能力已建立，僅交給受控假 executor。",
        "命令參數已再次檢查，沒有投遞或 channel 旗標。",
        "受控演練完成後已回到全禁狀態，沒有自動重試。",
    )
    output.write("Phase 9 N=1 安全演練（不會呼叫真實 OpenClaw）\n")
    if synthetic_presence:
        output.write("⚠ 本次為合成回應，未經真實 OOB 管道。\n")
    for index, message in enumerate(messages, start=1):
        output.write(f"[{index}/13] {message}\n")
    output.write(f"受控假 executor 呼叫：{report.fake_executor_calls}\n")
    output.write(f"真實 executor 呼叫：{report.real_executor_calls}\n")
    output.write(f"暫存作廢記錄：{report.burn_records}\n")
    output.write(f"暫存稽核記錄：{report.audit_records}\n")
    output.write("結果：演練成功；系統保持禁止真實執行。\n")


def run_dry_rehearsal(
    *,
    output: TextIO,
    real_executor_factory: RealExecutorFactory,
    expected_owner_principal: str,
    oob_directory: Path | None = None,
    synthetic_presence: bool = False,
    workspace_factory: WorkspaceFactory = _workspace_factory,
) -> RehearsalReport:
    """Run exactly one controlled attempt; never construct the real executor."""

    if synthetic_presence and oob_directory is not None:
        raise ValueError("synthetic presence and real OOB directory are mutually exclusive")
    if not synthetic_presence and oob_directory is None:
        raise ValueError("real OOB directory is required")
    real_oob_directory = (
        None if oob_directory is None else _validated_oob_directory(oob_directory)
    )
    real_calls_before = int(getattr(real_executor_factory, "calls", 0))
    with workspace_factory() as workspace_text:
        workspace = Path(workspace_text)
        data_dir = workspace / "data"
        state_root = workspace / "openclaw-state"
        data_dir.mkdir(parents=True)
        state_root.mkdir()
        (state_root / "config.json").write_text(
            "{}\n", encoding="utf-8", newline="\n"
        )
        audit_target = data_dir / "audit_dev.jsonl"
        burn_target = workspace / "phase9_burn.jsonl"

        action = ActionRequest(
            action_name="n1_harmless_query",
            target="target-local-demo",
            message="Return one harmless local status summary.",
            requested_cli_timeout_seconds=30,
            gate_timeout_seconds=12,
            agent_id="main",
            model_id="safe-model",
        )
        token_request = TokenIssuanceRequest(
            approval_packet_id="packet-rehearsal-001",
            approval_packet_hash="a" * 64,
            evidence_bundle_hash="b" * 64,
            action_hash=action.digest(),
            rehearsal_id=REHEARSAL_ID,
            session_ends_at=REHEARSAL_NOW + timedelta(minutes=5),
            key_id="rehearsal-key",
            now=REHEARSAL_NOW,
            validity_seconds=600,
        )
        presence_proof = OwnerPresenceProof(
            rehearsal_id=REHEARSAL_ID,
            approval_packet_hash=token_request.approval_packet_hash,
            action_hash=token_request.action_hash,
            observed_at=REHEARSAL_NOW - timedelta(seconds=1),
            valid_until=REHEARSAL_NOW + timedelta(minutes=1),
            evidence_digest="c" * 64,
        )
        token_egress = _ControlledOwnerTokenEgress()
        fixed_random = _FixedRehearsalRandom()
        token_package = Phase9TokenIssuer(
            rehearsal_id=REHEARSAL_ID,
            presence_verifier=_ControlledTokenPresenceVerifier(),
            owner_egress=token_egress,
            random_bytes=fixed_random,
        ).issue(token_request, presence_proof=presence_proof)
        if fixed_random.calls != 2:
            raise RuntimeError("fixed rehearsal token vectors were not consumed exactly once")
        issued = token_package.issued_token
        presented_value = token_egress.take_for_rehearsal()
        request = GateRequest(
            issued_token=issued,
            token_presentation=TokenPresentation.from_binding(issued.binding),
            action=action,
            system_display_strings=("System displays non-secret digests only.",),
            initial_challenge_id="phase9-initial-rehearsal-challenge",
            session_active=True,
            phase9_audit_authorization=Phase9AuditAuthorizationRecord(
                record_id="phase9-audit-owner-grant-rehearsal",
                rehearsal_id=REHEARSAL_ID,
                scope=PHASE9_AUDIT_SCOPE,
                owner_instruction_digest=PHASE9_AUDIT_AUTHORIZATION_GRANT_SHA256,
                authorized_at=REHEARSAL_NOW - timedelta(seconds=1),
                valid_until=REHEARSAL_NOW + timedelta(minutes=3),
            ),
        )
        frozen_contract = FrozenGateRequestVerifier.freeze(request)
        frozen_preflight = FrozenGateRequestVerifier.freeze(request)
        fake_executor = _ControlledDryRunExecutor()
        version_runner = _ControlledVersionRunner()
        audit_writer = _audit_writer()
        original_root = audit_writer.REPO_ROOT
        original_path = audit_writer.AUDIT_PATH
        clock = _SteppingClock()
        gate_principal = _runtime_gate_principal()
        presence_channel: PresenceChannel
        if synthetic_presence:
            presence_channel = _ControlledPresenceChannel(
                response_path=workspace / "synthetic-owner-response",
                gate_principal=gate_principal,
                expected_owner_principal=expected_owner_principal,
            )
        elif real_oob_directory is not None:
            response_path = real_oob_directory / OOB_RESPONSE_FILENAME
            endpoint = PresenceEndpoint(
                path=response_path,
                medium="file",
                gate_principal=gate_principal,
                expected_owner_principal=expected_owner_principal,
                contract_digest="c" * 64,
                continuity_id="rehearsal-continuity",
                max_validity_seconds=60,
            )
            presence_channel = JsonPresenceChannel(
                endpoint=endpoint,
                reader=RegularFilePresenceReader(clock=clock),
                clock=clock,
            )
        else:
            raise RuntimeError("presence channel configuration is unavailable")
        try:
            audit_writer.REPO_ROOT = workspace
            audit_writer.AUDIT_PATH = audit_target
            gate = Phase9Gate(
                rehearsal_id=REHEARSAL_ID,
                contract_verifier=frozen_contract,
                preflight_verifier=frozen_preflight,
                audit_authorization_verifier=AuditAuthorizationVerifier(),
                burn_ledger=FileBurnLedger(burn_target),
                audit_chain_writer=LocalAuditChainWriter(),
                version_probe=OwnerAuthorizedOpenClawVersionProbe(
                    process_runner=version_runner
                ),
                snapshotter=DirectorySnapshotter(state_root),
                presence_channel=presence_channel,
                executor=fake_executor,
                clock=clock,
                gate_token_audit_coordination_lock=(
                    BoundedGateTokenAuditCoordinationLock(
                        mutex=threading.Lock(),
                        maximum_wait_seconds=5.0,
                    )
                ),
                challenge_bytes=lambda size: b"r" * size,
            )
            result = gate.run(
                request,
                presented_raw_token=presented_value,
                owner_authorization_text=(
                    "Controlled rehearsal authorizes n1_harmless_query for "
                    "target-local-demo only."
                ),
            )
            audit_records = audit_writer.read_audit_events()
        finally:
            audit_writer.REPO_ROOT = original_root
            audit_writer.AUDIT_PATH = original_path

        burn_records = len(
            [line for line in burn_target.read_text(encoding="utf-8").splitlines() if line]
        )
        report = RehearsalReport(
            fake_executor_calls=fake_executor.calls,
            real_executor_calls=(
                int(getattr(real_executor_factory, "calls", 0)) - real_calls_before
            ),
            trace=result.trace,
            burn_records=burn_records,
            audit_records=len(audit_records),
        )
        _print_owner_report(
            output,
            report,
            synthetic_presence=synthetic_presence,
        )
        return report


def main(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO,
    real_executor_factory: RealExecutorFactory | None = None,
    expected_owner_principal: str | None = None,
    oob_directory: Path | None = None,
    workspace_factory: WorkspaceFactory = _workspace_factory,
) -> int:
    """Select rehearsal mode; every real or malformed request stays denied."""

    arguments = tuple(argv or ())
    factory = real_executor_factory or _DeniedRealExecutorFactory()
    if arguments == ("--real",):
        output.write(
            "停止：本批沒有執行授權，真實 executor 不會被建立或呼叫。\n"
        )
        return 2
    allowed_arguments = {"--dry-run", "--synthetic-presence"}
    if (
        any(argument not in allowed_arguments for argument in arguments)
        or len(arguments) != len(set(arguments))
    ):
        output.write(
            "停止：參數不受支援。只允許 --dry-run 或 --synthetic-presence。\n"
        )
        return 2
    if expected_owner_principal is None or not expected_owner_principal.strip():
        output.write(
            "停止：未設定 Owner principal；請設定 PHASE9_OWNER_PRINCIPAL。\n"
        )
        return 2
    synthetic_presence = "--synthetic-presence" in arguments
    if synthetic_presence and oob_directory is not None:
        output.write("停止：合成回應與真實 OOB 目錄不可同時設定。\n")
        return 2
    if not synthetic_presence and oob_directory is None:
        output.write(
            "停止：未設定真實 OOB 目錄；請設定 PHASE9_OOB_DIRECTORY，或顯式使用 "
            "--synthetic-presence。\n"
        )
        return 2
    if oob_directory is not None:
        try:
            oob_directory = _validated_oob_directory(oob_directory)
        except ValueError:
            output.write(
                "停止：OOB 目錄不可位於 /mnt/c；請使用 WSL 原生路徑，例如 "
                "/var/hermes-phase9。\n"
            )
            return 2
    try:
        report = run_dry_rehearsal(
            output=output,
            real_executor_factory=factory,
            expected_owner_principal=expected_owner_principal,
            oob_directory=oob_directory,
            synthetic_presence=synthetic_presence,
            workspace_factory=workspace_factory,
        )
    except PresenceChannelError:
        output.write(
            "停止：Owner OOB 回應不可用（檔案不存在、逾時、principal 不符或內容無效）；"
            "未退回合成回應，也未啟動真實 executor。\n"
        )
        return 1
    except Exception:
        output.write(
            "停止：安全演練未完成；沒有重試，也沒有啟動真實 executor。\n"
        )
        return 1
    return 0 if report.real_executor_calls == 0 else 1


if __name__ == "__main__":
    oob_directory_text = os.environ.get("PHASE9_OOB_DIRECTORY")
    raise SystemExit(
        main(
            sys.argv[1:],
            output=sys.stdout,
            expected_owner_principal=os.environ.get("PHASE9_OWNER_PRINCIPAL"),
            oob_directory=(
                Path(oob_directory_text) if oob_directory_text else None
            ),
        )
    )


__all__ = ["RehearsalReport", "main", "run_dry_rehearsal"]
