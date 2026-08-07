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
)
from app.phase9_openclaw_executor import ProcessOutcome
from app.phase9_preflight import (
    BoundedGateTokenAuditCoordinationLock,
    FrozenGateRequestVerifier,
)
from app.phase9_presence import PresenceInputs
from app.phase9_presence_channel import (
    JsonPresenceChannel,
    PresenceEndpoint,
    PresenceRead,
)
from app.phase9_token import TokenPresentation, issue_token


REHEARSAL_NOW = datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc)
REHEARSAL_ID = "phase9-n1-entrypoint-rehearsal"


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

    test_double = True

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

    def __init__(self, *, response_path: Path) -> None:
        self._response_path = response_path

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        observed_at = challenge.issued_at + timedelta(milliseconds=1)
        endpoint = PresenceEndpoint(
            path=self._response_path,
            medium="rehearsal-memory",
            gate_principal="uid:1000",
            expected_owner_principal="uid:2000",
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
                owner_principal="uid:2000",
                permissions_verified=True,
                observed_at=observed_at,
            )
        )
        return JsonPresenceChannel(
            endpoint=endpoint,
            reader=reader,
            clock=lambda: observed_at,
        ).collect_after_second_challenge(challenge)


def _workspace_factory() -> AbstractContextManager[str]:
    return TemporaryDirectory(prefix="phase9-n1-rehearsal-")


def _print_owner_report(output: TextIO, report: RehearsalReport) -> None:
    messages = (
        "契約格式已重新確認。",
        "這張單與這個動作的摘要已重新比對。",
        "Phase 9 的資料契約已接受。",
        "Owner 授權文字的動作與目標已核對（僅演練）。",
        "固定測試 token 已驗證；沒有產生真實 token。",
        "預檢、版本假件與檔案快照已通過。",
        "第二道新挑戰已完成（合成 Owner 回應）。",
        "六個在場條件已重新計算並全部通過。",
        "測試 token 已先寫入暫存作廢帳本。",
        "作廢證據已寫入暫存稽核鏈並驗證。",
        "一次性能力已建立，僅交給受控假 executor。",
        "命令參數已再次檢查，沒有投遞或 channel 旗標。",
        "受控演練完成後已回到全禁狀態，沒有自動重試。",
    )
    output.write("Phase 9 N=1 安全演練（不會呼叫真實 OpenClaw）\n")
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
    workspace_factory: WorkspaceFactory = _workspace_factory,
) -> RehearsalReport:
    """Run exactly one controlled attempt; never construct the real executor."""

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
        issued = issue_token(
            approval_packet_id="packet-rehearsal-001",
            approval_packet_hash="a" * 64,
            evidence_bundle_hash="b" * 64,
            action_hash=action.digest(),
            rehearsal_id=REHEARSAL_ID,
            session_ends_at=REHEARSAL_NOW + timedelta(minutes=5),
            session_hmac_key=b"k" * 32,
            key_id="rehearsal-key",
            now=REHEARSAL_NOW,
            random_bytes=lambda size: b"d" * size,
        )
        presented_value = issued.reveal_for_oob_once()
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
                presence_channel=_ControlledPresenceChannel(
                    response_path=workspace / "synthetic-owner-response"
                ),
                executor=fake_executor,
                clock=_SteppingClock(),
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
                    "Synthetic rehearsal authorizes n1_harmless_query for "
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
        _print_owner_report(output, report)
        return report


def main(
    argv: Sequence[str] | None = None,
    *,
    output: TextIO,
    real_executor_factory: RealExecutorFactory | None = None,
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
    if arguments not in {(), ("--dry-run",)}:
        output.write(
            "停止：參數不受支援。只允許不帶參數或 --dry-run 安全演練。\n"
        )
        return 2
    try:
        report = run_dry_rehearsal(
            output=output,
            real_executor_factory=factory,
            workspace_factory=workspace_factory,
        )
    except Exception:
        output.write(
            "停止：安全演練未完成；沒有重試，也沒有啟動真實 executor。\n"
        )
        return 1
    return 0 if report.real_executor_calls == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], output=sys.stdout))


__all__ = ["RehearsalReport", "main", "run_dry_rehearsal"]
