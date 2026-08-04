"""Counterexample-heavy tests for the Phase 9 braking-system gate."""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from app.phase9_gate import (
    EXPECTED_OPENCLAW_VERSION,
    PHASE9_AUDIT_SCOPE,
    ActionRequest,
    BurnReceipt,
    DirectorySnapshotter,
    ExecutionResult,
    FreshChallenge,
    GateDenied,
    GateRequest,
    GateState,
    OwnerAuthorizedOpenClawExecutor,
    OwnerAuthorizedOpenClawVersionProbe,
    Phase9AuditAuthorizationRecord,
    Phase9Gate,
    build_openclaw_argv,
    validate_openclaw_argv,
)
from app.phase9_presence import EvidenceSource, PredicateEvidence, PresenceInputs
from app.phase9_token import TokenPresentation, issue_token


pytestmark = pytest.mark.contract

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
PACKET_HASH = "a" * 64
EVIDENCE_HASH = "b" * 64


class Clock:
    def __init__(self) -> None:
        self.current = NOW

    def __call__(self) -> datetime:
        self.current += timedelta(seconds=1)
        return self.current


class StaticVerifier:
    def __init__(self, result: bool = True) -> None:
        self.result = result
        self.calls = 0

    def verify(self, _request: GateRequest) -> bool:
        self.calls += 1
        return self.result


class StaticAuditVerifier:
    def __init__(self, result: bool = True) -> None:
        self.result = result

    def verify(
        self,
        record: Phase9AuditAuthorizationRecord,
        *,
        rehearsal_id: str,
        action_hash: str,
        now: datetime,
    ) -> bool:
        return (
            self.result
            and record.rehearsal_id == rehearsal_id
            and len(action_hash) == 64
            and record.authorized_at <= now < record.valid_until
        )


class StaticVersionProbe:
    def __init__(self, version: str = EXPECTED_OPENCLAW_VERSION) -> None:
        self.version = version
        self.calls = 0

    def probe_version(self) -> str:
        self.calls += 1
        return self.version


def _green(
    challenge: FreshChallenge,
    source: EvidenceSource,
) -> PredicateEvidence:
    return PredicateEvidence(
        verified=True,
        observed_at=challenge.issued_at + timedelta(milliseconds=1),
        valid_until=challenge.deadline,
        source=source,
        evidence_digest="d" * 64,
    )


class SameEndpointPresence:
    def __init__(self, *, verbatim: bool = True) -> None:
        self.verbatim = verbatim
        self.challenges: list[FreshChallenge] = []

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        self.challenges.append(challenge)
        return PresenceInputs(
            same_endpoint=True,
            owner_channel_contract_approved=_green(
                challenge, EvidenceSource.GATE_VERIFICATION
            ),
            best_effort_isolation_attested=_green(
                challenge, EvidenceSource.ISOLATION_PROBE
            ),
            fresh_challenge_bound=_green(challenge, EvidenceSource.OOB_CHANNEL),
            final_presence_reconfirmed=_green(
                challenge, EvidenceSource.OOB_CHANNEL
            ),
            channel_continuity_green=_green(
                challenge, EvidenceSource.ISOLATION_PROBE
            ),
            owner_presence_demonstrated=_green(
                challenge, EvidenceSource.OOB_CHANNEL
            ),
            owner_response_authenticated=_green(
                challenge, EvidenceSource.OWNER_AUTHENTICATOR
            ),
            owner_verbatim_authorization_verified=(
                _green(challenge, EvidenceSource.OWNER_PROCEDURE)
                if self.verbatim
                else None
            ),
        )


class TmpBurnLedger:
    def __init__(self, target: Path, *, fail: bool = False) -> None:
        self._target = target
        self.fail = fail
        self.commits = 0

    @property
    def target(self) -> Path:
        return self._target

    def _records(self) -> list[dict[str, Any]]:
        if not self._target.exists():
            return []
        return [json.loads(line) for line in self._target.read_text().splitlines()]

    def contains(self, token_digest: str) -> bool:
        return any(item["token_digest"] == token_digest for item in self._records())

    def commit(self, record) -> BurnReceipt:
        if self.fail:
            raise OSError("synthetic burn failure")
        self.commits += 1
        payload = record.safe_record()
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self._target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded + "\n")
            handle.flush()
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        return BurnReceipt(record.token_digest, digest, durable=True, verified=True)


class CountingExecutor:
    test_double = True

    def __init__(self, *, mutate: Path | None = None) -> None:
        self.calls = 0
        self.argv: tuple[str, ...] | None = None
        self.timeout: int | None = None
        self.mutate = mutate

    def execute(
        self,
        argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        self.calls += 1
        self.argv = argv
        self.timeout = timeout_seconds
        if self.mutate is not None:
            self.mutate.write_text("changed", encoding="utf-8")
        return ExecutionResult(0, False, "1" * 64, "2" * 64)


def _fixture(
    tmp_path: Path,
    *,
    burn_fail: bool = False,
    audit_record: bool = True,
    displayed_copy: bool = False,
    version: str = EXPECTED_OPENCLAW_VERSION,
    verbatim: bool = True,
    executor: CountingExecutor | None = None,
):
    state_root = tmp_path / "openclaw-state"
    state_root.mkdir()
    (state_root / "config.json").write_text("{}", encoding="utf-8")
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
        approval_packet_id="packet-001",
        approval_packet_hash=PACKET_HASH,
        evidence_bundle_hash=EVIDENCE_HASH,
        action_hash=action.digest(),
        rehearsal_id="rehearsal-001",
        session_ends_at=NOW + timedelta(minutes=5),
        session_hmac_key=b"h" * 32,
        key_id="session-001",
        now=NOW,
        random_bytes=lambda size: b"t" * size,
    )
    raw = issued.reveal_for_oob_once()
    owner_text = (
        "I authorize n1_harmless_query for target-local-demo in this rehearsal."
    )
    request = GateRequest(
        issued_token=issued,
        token_presentation=TokenPresentation.from_binding(issued.binding),
        action=action,
        system_display_strings=(owner_text,) if displayed_copy else ("safe digest view",),
        initial_challenge_id="initial-challenge",
        session_active=True,
        phase9_audit_authorization=(
            Phase9AuditAuthorizationRecord(
                record_id="owner-audit-auth-001",
                rehearsal_id="rehearsal-001",
                scope=PHASE9_AUDIT_SCOPE,
                owner_instruction_digest="f" * 64,
                authorized_at=NOW - timedelta(seconds=1),
                valid_until=NOW + timedelta(minutes=3),
            )
            if audit_record
            else None
        ),
    )
    ledger = TmpBurnLedger(tmp_path / "burn.jsonl", fail=burn_fail)
    selected_executor = executor or CountingExecutor()
    presence = SameEndpointPresence(verbatim=verbatim)
    gate = Phase9Gate(
        rehearsal_id="rehearsal-001",
        contract_verifier=StaticVerifier(),
        preflight_verifier=StaticVerifier(),
        audit_authorization_verifier=StaticAuditVerifier(),
        burn_ledger=ledger,
        version_probe=StaticVersionProbe(version),
        snapshotter=DirectorySnapshotter(state_root),
        presence_channel=presence,
        executor=selected_executor,
        clock=Clock(),
        challenge_bytes=lambda size: b"c" * size,
    )
    return gate, request, raw, owner_text, ledger, selected_executor, presence, state_root


def test_exact_fake_flow_burns_before_one_call_and_closes(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, presence, _root = _fixture(tmp_path)

    assert raw not in repr(request)
    assert owner_text not in repr(request)

    result = gate.run(
        request,
        presented_raw_token=raw,
        owner_authorization_text=owner_text,
    )

    assert ledger.commits == 1
    assert executor.calls == 1
    assert result.state is GateState.CLOSED_DENY
    assert result.retry_permitted is False
    assert result.effective_timeout_seconds == 12
    assert result.argv == build_openclaw_argv(request.action)
    assert "--local" in result.argv
    assert "--deliver" not in result.argv
    assert not any(item.startswith("--channel") for item in result.argv)
    assert result.trace.index("10:BURN_DURABLE_AND_VERIFIED") < result.trace.index(
        "13:ONE_SHOT_CONSUMED"
    )
    assert result.trace.index("8:SECOND_CHALLENGE_COMPLETED") < result.trace.index(
        "9:SIX_PREDICATES_RECOMPUTED"
    ) < result.trace.index("10:BURN_DURABLE_AND_VERIFIED")
    assert len(presence.challenges) == 1
    assert presence.challenges[0].challenge_id != request.initial_challenge_id
    assert result.presence.owner_presence_demonstrated is True
    assert result.presence.owner_response_authenticated is False
    assert result.presence.owner_verbatim_authorization_verified is True
    burn_text = ledger.target.read_text(encoding="utf-8")
    assert owner_text not in burn_text
    assert "owner_instruction_digest" in burn_text


def test_burn_failure_never_calls_executor(tmp_path: Path) -> None:
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path, burn_fail=True
    )

    with pytest.raises(GateDenied, match="BURN_WRITE_FAILED"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.frozen is True


def test_system_display_copy_is_rejected_before_burn(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path, displayed_copy=True
    )

    with pytest.raises(GateDenied, match="OWNER_AUTHORIZATION_DENIED"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert ledger.commits == 0
    assert executor.calls == 0


@pytest.mark.parametrize(
    "forbidden",
    [
        "--deliver",
        "--channel",
        "--reply-channel",
        "--reply-to",
        "--reply-account",
    ],
)
def test_delivery_and_channel_flags_fail_closed(forbidden: str) -> None:
    argv = (
        "openclaw",
        "agent",
        "--local",
        "--message",
        "safe",
        "--json",
        "--timeout",
        "10",
        forbidden,
        "forbidden-value",
    )

    with pytest.raises(GateDenied, match="ARGV_DENIED"):
        validate_openclaw_argv(argv)


def test_unknown_flag_and_gateway_mode_fail_closed() -> None:
    with pytest.raises(GateDenied, match="ARGV_DENIED"):
        validate_openclaw_argv(
            ("openclaw", "agent", "--local", "--message", "safe", "--json", "--timeout", "10", "--thinking")
        )
    with pytest.raises(GateDenied, match="ARGV_DENIED"):
        validate_openclaw_argv(
            ("openclaw", "agent", "--message", "safe", "--json", "--timeout", "10")
        )


def test_missing_phase9_audit_authorization_record_refuses_start(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path, audit_record=False
    )

    with pytest.raises(GateDenied, match="PHASE9_AUDIT_AUTHORIZATION_MISSING"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert ledger.commits == 0
    assert executor.calls == 0


def test_one_rejection_freezes_entire_rehearsal_and_never_retries(
    tmp_path: Path,
) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path, displayed_copy=True
    )
    with pytest.raises(GateDenied, match="OWNER_AUTHORIZATION_DENIED"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    repaired = replace(request, system_display_strings=("different",))
    with pytest.raises(GateDenied, match="REHEARSAL_FROZEN"):
        gate.run(
            repaired,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert gate.freeze.rejection_count == 2
    assert ledger.commits == 0
    assert executor.calls == 0


def test_same_endpoint_without_verbatim_evidence_denies(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path, verbatim=False
    )

    with pytest.raises(GateDenied, match="OWNER_PRESENCE_DENIED"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert ledger.commits == 0
    assert executor.calls == 0


def test_version_drift_is_preflight_failure_not_gateway_fallback(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path, version="OpenClaw future"
    )

    with pytest.raises(GateDenied, match="OPENCLAW_VERSION_DRIFT"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert ledger.commits == 0
    assert executor.calls == 0


def test_post_snapshot_difference_is_evidence_not_ignored(tmp_path: Path) -> None:
    state_file = tmp_path / "will-be-replaced"
    executor = CountingExecutor()
    gate, request, raw, owner_text, _ledger, executor, _presence, root = _fixture(
        tmp_path, executor=executor
    )
    executor.mutate = root / "new-session.json"
    del state_file

    result = gate.run(
        request,
        presented_raw_token=raw,
        owner_authorization_text=owner_text,
    )

    assert result.completion_class == "SIDE_EFFECT_DRIFT"
    assert result.filesystem_changes == ("new-session.json",)
    assert result.filesystem_before_digest != result.filesystem_after_digest
    assert result.retry_permitted is False


def test_real_runtime_placeholders_require_owner_execution_authorization() -> None:
    with pytest.raises(NotImplementedError, match="需 Owner 執行授權"):
        OwnerAuthorizedOpenClawExecutor().execute(
            ("openclaw", "agent"), timeout_seconds=1
        )
    with pytest.raises(NotImplementedError, match="需 Owner 執行授權"):
        OwnerAuthorizedOpenClawVersionProbe().probe_version()


def test_gate_source_has_no_subprocess_or_runtime_wiring() -> None:
    source_path = Path(__file__).parents[1] / "app" / "phase9_gate.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    call_names = {
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else node.func.id
        if isinstance(node.func, ast.Name)
        else ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }

    assert "subprocess" not in imports
    assert not {"Popen", "run", "check_call", "check_output"} & call_names
