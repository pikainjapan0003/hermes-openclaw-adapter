"""Counterexample-heavy tests for the Phase 9 braking-system gate."""

from __future__ import annotations

import ast
import hashlib
import json
import threading
import time
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

import pytest

from app.phase9_abort import AbortScenario
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
    _find_in_flight_denial,
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
        self._lock = threading.Lock()

    def __call__(self) -> datetime:
        with self._lock:
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


class BarrierPresence(SameEndpointPresence):
    def __init__(self, barrier: threading.Barrier) -> None:
        super().__init__()
        self._barrier = barrier

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        inputs = super().collect_after_second_challenge(challenge)
        self._barrier.wait(timeout=5)
        return inputs


class UnavailableCoordinationLock:
    def __init__(self) -> None:
        self.acquire_calls = 0
        self.release_calls = 0

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        del blocking, timeout
        self.acquire_calls += 1
        return False

    def release(self) -> None:
        self.release_calls += 1
        raise AssertionError("an unacquired lock must not be released")


class ReleaseFailingCoordinationLock:
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        del blocking, timeout
        return True

    def release(self) -> None:
        raise RuntimeError("synthetic coordination release failure")


class AcquiredThenRaisingCoordinationLock:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.release_calls = 0

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        acquired = self._lock.acquire(blocking, timeout)
        assert acquired is True
        raise RuntimeError("synthetic failure after acquisition")

    def release(self) -> None:
        self.release_calls += 1
        self._lock.release()


class TmpBurnLedger:
    def __init__(
        self,
        target: Path,
        *,
        fail: bool = False,
        lock_fail: bool = False,
        commit_delay_seconds: float = 0.0,
    ) -> None:
        self._target = target
        self.fail = fail
        self.lock_fail = lock_fail
        self.commit_delay_seconds = commit_delay_seconds
        self.commits = 0
        self.lock_entries = 0
        self._ledger_lock = threading.Lock()

    @property
    def target(self) -> Path:
        return self._target

    def _records(self) -> list[dict[str, Any]]:
        if not self._target.exists():
            return []
        return [json.loads(line) for line in self._target.read_text().splitlines()]

    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        if self.lock_fail:
            raise TimeoutError("synthetic ledger lock failure")
        acquired = self._ledger_lock.acquire(timeout=timeout_seconds)
        if not acquired:
            raise TimeoutError("synthetic ledger lock timeout")
        try:
            self.lock_entries += 1
            yield
        finally:
            self._ledger_lock.release()

    def contains(self, token_digest: str) -> bool:
        return any(item["token_digest"] == token_digest for item in self._records())

    def commit(self, record) -> BurnReceipt:
        if self.fail:
            raise OSError("synthetic burn failure")
        if self.commit_delay_seconds:
            time.sleep(self.commit_delay_seconds)
        self.commits += 1
        payload = record.safe_record()
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self._target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded + "\n")
            handle.flush()
        digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        return BurnReceipt(record.token_digest, digest, durable=True, verified=True)


class ExitFailingLedger(TmpBurnLedger):
    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        with super().exclusive_lock(timeout_seconds=timeout_seconds):
            yield
        raise OSError("synthetic ledger exit failure after commit")


class MaskedInternalDenialLedger(TmpBurnLedger):
    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        with super().exclusive_lock(timeout_seconds=timeout_seconds):
            yield
        try:
            raise GateDenied(
                "SYNTHETIC_MASKED_DENIAL",
                AbortScenario.PRECALL_AUDIT_FAILURE,
            )
        except GateDenied as denial:
            raise OSError("SENSITIVE-LEDGER-WRAPPER") from denial


class DurableThenFailingCommitLedger(TmpBurnLedger):
    """The record reaches the ledger, then the commit call fails.

    This is the dangerous case: the burn really happened, so any code that
    reads as "nothing was written, retry is safe" would be wrong.
    """

    def commit(self, record) -> BurnReceipt:
        super().commit(record)
        raise OSError("synthetic failure after the record became durable")


class UnreadableAfterCommitFailureLedger(TmpBurnLedger):
    """Commit fails and the durability probe cannot answer either."""

    def __init__(self, target: Path) -> None:
        super().__init__(target)
        self._commit_attempted = False

    def commit(self, record) -> BurnReceipt:
        self._commit_attempted = True
        raise OSError("synthetic commit failure")

    def contains(self, token_digest: str) -> bool:
        if self._commit_attempted:
            raise OSError("synthetic ledger read failure")
        return super().contains(token_digest)


def _physical_record_count(target: Path) -> int:
    if not target.exists():
        return 0
    return len([line for line in target.read_text().splitlines() if line])


class CountingExecutor:
    test_double = True

    def __init__(self, *, mutate: Path | None = None) -> None:
        self.calls = 0
        self.argv: tuple[str, ...] | None = None
        self.timeout: int | None = None
        self.mutate = mutate
        self._lock = threading.Lock()

    def execute(
        self,
        argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        with self._lock:
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
    ledger: TmpBurnLedger | None = None,
    gate_token_audit_coordination_lock: Any | None = None,
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
    selected_ledger = (
        ledger
        if ledger is not None
        else TmpBurnLedger(
            tmp_path / "burn.jsonl",
            fail=burn_fail,
        )
    )
    selected_executor = executor or CountingExecutor()
    selected_coordination_lock = (
        gate_token_audit_coordination_lock
        if gate_token_audit_coordination_lock is not None
        else threading.Lock()
    )
    presence = SameEndpointPresence(verbatim=verbatim)
    gate = Phase9Gate(
        rehearsal_id="rehearsal-001",
        contract_verifier=StaticVerifier(),
        preflight_verifier=StaticVerifier(),
        audit_authorization_verifier=StaticAuditVerifier(),
        burn_ledger=selected_ledger,
        version_probe=StaticVersionProbe(version),
        snapshotter=DirectorySnapshotter(state_root),
        presence_channel=presence,
        executor=selected_executor,
        clock=Clock(),
        challenge_bytes=lambda size: b"c" * size,
        gate_token_audit_coordination_lock=selected_coordination_lock,
    )
    return (
        gate,
        request,
        raw,
        owner_text,
        selected_ledger,
        selected_executor,
        presence,
        state_root,
    )


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
    assert result.trace == (
        "1:DENY_ALL_TO_CHECKING",
        "2:CONTRACTS_VERIFIED",
        "3:HASHES_RECOMPUTED",
        "4:PHASE9_CONTRACT_ACCEPTED",
        "5:OWNER_PROCEDURE_CHECKED",
        "6:TOKEN_VERIFIED",
        "7:PREFLIGHT_REVALIDATED",
        "8:SECOND_CHALLENGE_COMPLETED",
        "9:SIX_PREDICATES_RECOMPUTED",
        "10:BURN_DURABLE_AND_VERIFIED",
        "11:ONE_SHOT_CAPABILITY_CREATED",
        "12:ARGV_REVALIDATED",
        "13:ONE_SHOT_CONSUMED",
        "14:CLOSED_DENY",
        "15:POST_ATTEMPT_EVIDENCE_COMPUTED",
    )
    burn_text = ledger.target.read_text(encoding="utf-8")
    assert owner_text not in burn_text
    assert "owner_instruction_digest" in burn_text


def test_coordination_lock_is_a_required_constructor_argument(tmp_path: Path) -> None:
    state_root = tmp_path / "required-lock-state"
    state_root.mkdir()
    ledger = TmpBurnLedger(tmp_path / "required-lock-burn.jsonl")

    with pytest.raises(TypeError, match="gate_token_audit_coordination_lock"):
        Phase9Gate(  # type: ignore[call-arg]
            rehearsal_id="rehearsal-001",
            contract_verifier=StaticVerifier(),
            preflight_verifier=StaticVerifier(),
            audit_authorization_verifier=StaticAuditVerifier(),
            burn_ledger=ledger,
            version_probe=StaticVersionProbe(),
            snapshotter=DirectorySnapshotter(state_root),
            presence_channel=SameEndpointPresence(),
            executor=CountingExecutor(),
            clock=Clock(),
        )


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


def test_concurrent_same_token_is_burned_once_and_executes_once(
    tmp_path: Path,
) -> None:
    process_lock = threading.Lock()
    ledger = TmpBurnLedger(
        tmp_path / "burn.jsonl",
        commit_delay_seconds=0.05,
    )
    executor = CountingExecutor()
    barrier = threading.Barrier(2)
    gate_one, request, raw, owner_text, _ledger, _executor, _presence, root = _fixture(
        tmp_path,
        ledger=ledger,
        executor=executor,
        gate_token_audit_coordination_lock=process_lock,
    )
    gate_one.presence_channel = BarrierPresence(barrier)
    gate_two = Phase9Gate(
        rehearsal_id="rehearsal-001",
        contract_verifier=StaticVerifier(),
        preflight_verifier=StaticVerifier(),
        audit_authorization_verifier=StaticAuditVerifier(),
        burn_ledger=ledger,
        version_probe=StaticVersionProbe(),
        snapshotter=DirectorySnapshotter(root),
        presence_channel=BarrierPresence(barrier),
        executor=executor,
        clock=Clock(),
        challenge_bytes=lambda size: b"q" * size,
        gate_token_audit_coordination_lock=process_lock,
    )
    outcomes: list[str] = []
    outcome_lock = threading.Lock()

    def invoke(gate: Phase9Gate) -> None:
        try:
            gate.run(
                request,
                presented_raw_token=raw,
                owner_authorization_text=owner_text,
            )
        except GateDenied as exc:
            outcome = exc.code
        else:
            outcome = "EXECUTED"
        with outcome_lock:
            outcomes.append(outcome)

    threads = (
        threading.Thread(target=invoke, args=(gate_one,)),
        threading.Thread(target=invoke, args=(gate_two,)),
    )
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert all(not thread.is_alive() for thread in threads)
    assert sorted(outcomes) == ["EXECUTED", "TOKEN_ALREADY_BURNED"]
    assert executor.calls == 1
    assert ledger.commits == 1
    assert ledger.lock_entries == 2
    assert gate_one.state is GateState.CLOSED_DENY
    assert gate_two.state is GateState.CLOSED_DENY


def test_process_coordination_lock_unavailable_fails_closed(
    tmp_path: Path,
) -> None:
    coordination_lock = UnavailableCoordinationLock()
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path,
        gate_token_audit_coordination_lock=coordination_lock,
    )

    with pytest.raises(GateDenied, match="COORDINATION_LOCK_UNAVAILABLE"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert coordination_lock.acquire_calls == 1
    assert coordination_lock.release_calls == 0
    assert ledger.lock_entries == 0
    assert ledger.commits == 0
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.rejection_count == 1


def test_ledger_exclusive_lock_unavailable_fails_closed(tmp_path: Path) -> None:
    ledger = TmpBurnLedger(tmp_path / "burn.jsonl", lock_fail=True)
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    # The lock was never entered, so nothing was written.  Reporting a write
    # failure here would misdescribe the state on execution day.
    with pytest.raises(GateDenied, match="BURN_NOT_ATTEMPTED") as denial:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert denial.value.scenario is AbortScenario.PRECALL_AUDIT_FAILURE
    assert ledger.lock_entries == 0
    assert ledger.commits == 0
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.rejection_count == 1


def test_commit_failure_after_durability_reports_crash_after_burn(
    tmp_path: Path,
) -> None:
    target = tmp_path / "burn.jsonl"
    ledger = DurableThenFailingCommitLedger(target)
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    with pytest.raises(GateDenied, match="BURN_DURABLE_UNVERIFIED") as denial:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    # The record really landed, so the abort must not read as "safe to retry".
    assert denial.value.scenario is AbortScenario.CRASH_AFTER_BURN
    assert _physical_record_count(target) == 1
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.rejection_count == 1


def test_commit_failure_with_unreadable_probe_stays_conservative(
    tmp_path: Path,
) -> None:
    target = tmp_path / "burn.jsonl"
    ledger = UnreadableAfterCommitFailureLedger(target)
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    # Durability cannot be ruled out, so the conservative disposition applies.
    with pytest.raises(GateDenied, match="BURN_DURABLE_UNVERIFIED") as denial:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert denial.value.scenario is AbortScenario.CRASH_AFTER_BURN
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.rejection_count == 1


def test_commit_failure_proven_not_durable_reports_write_failure(
    tmp_path: Path,
) -> None:
    target = tmp_path / "burn.jsonl"
    ledger = TmpBurnLedger(target, fail=True)
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    with pytest.raises(GateDenied, match="BURN_WRITE_FAILED") as denial:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert denial.value.scenario is AbortScenario.PRECALL_AUDIT_FAILURE
    assert _physical_record_count(target) == 0
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY


def test_process_coordination_lock_release_failure_fails_closed(
    tmp_path: Path,
) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path,
        gate_token_audit_coordination_lock=ReleaseFailingCoordinationLock(),
    )

    with pytest.raises(GateDenied, match="COORDINATION_LOCK_RELEASE_FAILED") as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert ledger.commits == 1
    assert executor.calls == 0
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.frozen is True
    assert gate.freeze.rejection_count == 1
    assert gate.coordination_lock_poisoned is True
    assert caught.value.context == ("COORDINATION_LOCK_POISONED",)
    assert "COORDINATION_LOCK_POISONED" in gate.trace


def test_replay_denial_survives_simultaneous_release_failure(tmp_path: Path) -> None:
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path,
        gate_token_audit_coordination_lock=ReleaseFailingCoordinationLock(),
    )
    ledger.target.write_text(
        json.dumps({"token_digest": request.issued_token.binding.nonce_digest}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(GateDenied) as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert caught.value.code == "TOKEN_ALREADY_BURNED"
    assert caught.value.scenario is AbortScenario.TOKEN_INVALID_OR_REPLAYED
    assert caught.value.context == ("COORDINATION_LOCK_RELEASE_FAILED",)
    assert gate.freeze.rejection_count == 1
    assert gate.coordination_lock_poisoned is True
    assert executor.calls == 0


def test_ledger_exit_failure_after_commit_is_burn_verify_failure(
    tmp_path: Path,
) -> None:
    ledger = ExitFailingLedger(tmp_path / "burn.jsonl")
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    with pytest.raises(GateDenied) as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert caught.value.code == "BURN_VERIFY_FAILED"
    assert caught.value.scenario is AbortScenario.PRECALL_AUDIT_FAILURE
    assert ledger.commits == 1
    assert executor.calls == 0
    assert gate.freeze.rejection_count == 1


def test_masked_internal_denial_converges_to_closed_deny_once(
    tmp_path: Path,
) -> None:
    ledger = MaskedInternalDenialLedger(tmp_path / "burn.jsonl")
    gate, request, raw, owner_text, _ledger, executor, _presence, _root = _fixture(
        tmp_path,
        ledger=ledger,
    )

    with pytest.raises(GateDenied) as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert caught.value.code == "SYNTHETIC_MASKED_DENIAL"
    assert caught.value.scenario is AbortScenario.PRECALL_AUDIT_FAILURE
    assert caught.value.context == ("LEDGER_LOCK_EXIT_FAILED",)
    assert gate.state is GateState.CLOSED_DENY
    assert gate.freeze.frozen is True
    assert gate.freeze.rejection_count == 1
    assert executor.calls == 0


def test_find_in_flight_denial_stops_on_self_referential_context() -> None:
    wrapper = RuntimeError("SENSITIVE-SELF-LOOP")
    wrapper.__context__ = wrapper

    assert _find_in_flight_denial(wrapper) is None


def test_find_in_flight_denial_traverses_one_thousand_layers() -> None:
    denial = GateDenied(
        "ORIGINAL_DENIAL",
        AbortScenario.TOKEN_INVALID_OR_REPLAYED,
    )
    wrapper = RuntimeError("outer")
    current: BaseException = wrapper
    for layer in range(1000):
        next_error = RuntimeError(f"layer-{layer}")
        current.__context__ = next_error
        current = next_error
    current.__context__ = denial

    assert _find_in_flight_denial(wrapper) is denial


def test_masking_wrapper_payload_never_enters_recovered_denial() -> None:
    secret = "FAKE-SECRET-WRAPPER-PAYLOAD"
    denial = GateDenied(
        "ORIGINAL_DENIAL",
        AbortScenario.PRECALL_AUDIT_FAILURE,
    )
    wrapper = RuntimeError(secret)
    wrapper.__cause__ = denial

    recovered = _find_in_flight_denial(wrapper)

    assert recovered is denial
    assert secret not in str(recovered)
    assert secret not in repr(recovered)
    assert all(secret not in str(value) for value in recovered.args)
    assert all(secret not in value for value in recovered.context)


def test_acquire_that_raises_after_locking_is_released_and_denied(
    tmp_path: Path,
) -> None:
    coordination_lock = AcquiredThenRaisingCoordinationLock()
    gate, request, raw, owner_text, ledger, executor, _presence, _root = _fixture(
        tmp_path,
        gate_token_audit_coordination_lock=coordination_lock,
    )

    with pytest.raises(GateDenied, match="COORDINATION_LOCK_FAILED"):
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert coordination_lock.release_calls == 1
    assert gate.coordination_lock_poisoned is False
    assert gate.freeze.rejection_count == 1
    assert ledger.commits == 0
    assert executor.calls == 0


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
