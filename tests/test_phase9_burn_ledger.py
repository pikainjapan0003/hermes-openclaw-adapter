"""Cross-process and append-only evidence for the Phase 9 burn ledger.

Linux CI exercises only the POSIX ``fcntl`` branch.  The Windows ``msvcrt``
branch has native-host manual evidence but no continuing Linux-CI coverage;
reports must not describe that branch as CI-covered.
"""

from __future__ import annotations

import ast
import inspect
import multiprocessing
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from queue import Empty
from typing import Any, Iterator

import pytest

from app.phase9_burn_ledger import BurnLedgerError, FileBurnLedger
from app.phase9_gate import (
    EXPECTED_OPENCLAW_VERSION,
    PHASE9_AUDIT_SCOPE,
    ActionRequest,
    BurnReceipt,
    BurnRecord,
    DirectorySnapshotter,
    ExecutionResult,
    FreshChallenge,
    GateDenied,
    GateRequest,
    Phase9AuditAuthorizationRecord,
    Phase9Gate,
)
from app.phase9_presence import EvidenceSource, PredicateEvidence, PresenceInputs
from app.phase9_token import TokenPresentation, issue_token


pytestmark = pytest.mark.contract

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
PACKET_HASH = "a" * 64
EVIDENCE_HASH = "b" * 64


class ProcessClock:
    def __init__(self) -> None:
        self.current = NOW

    def __call__(self) -> datetime:
        self.current += timedelta(seconds=1)
        return self.current


class TrueVerifier:
    def verify(self, _request: GateRequest) -> bool:
        return True


class TrueAuditVerifier:
    def verify(
        self,
        record: Phase9AuditAuthorizationRecord,
        *,
        rehearsal_id: str,
        action_hash: str,
        now: datetime,
    ) -> bool:
        return (
            record.rehearsal_id == rehearsal_id
            and len(action_hash) == 64
            and record.authorized_at <= now < record.valid_until
        )


class StaticVersionProbe:
    def probe_version(self) -> str:
        return EXPECTED_OPENCLAW_VERSION


def _green(challenge: FreshChallenge, source: EvidenceSource) -> PredicateEvidence:
    return PredicateEvidence(
        verified=True,
        observed_at=challenge.issued_at + timedelta(milliseconds=1),
        valid_until=challenge.deadline,
        source=source,
        evidence_digest="d" * 64,
    )


class ProcessBarrierPresence:
    def __init__(self, barrier: Any) -> None:
        self._barrier = barrier

    def collect_after_second_challenge(
        self,
        challenge: FreshChallenge,
    ) -> PresenceInputs:
        self._barrier.wait(timeout=10)
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
            owner_verbatim_authorization_verified=_green(
                challenge, EvidenceSource.OWNER_PROCEDURE
            ),
        )


class ProcessExecutor:
    test_double = True

    def __init__(self, calls: Any) -> None:
        self._calls = calls

    def execute(
        self,
        _argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        self._calls.put(("EXECUTED", timeout_seconds))
        return ExecutionResult(0, False, "1" * 64, "2" * 64)


class LocalCountingExecutor:
    test_double = True

    def __init__(self) -> None:
        self.calls = 0
        self._lock = threading.Lock()

    def execute(
        self,
        _argv: tuple[str, ...],
        *,
        timeout_seconds: int,
    ) -> ExecutionResult:
        del timeout_seconds
        with self._lock:
            self.calls += 1
        return ExecutionResult(0, False, "1" * 64, "2" * 64)


class NoOpLockLedger(FileBurnLedger):
    """Production ledger with only its OS lock deliberately removed."""

    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        del timeout_seconds
        handle = self.target.open("a+b")
        with self._active_handle_lock:
            self._active_handle = handle
            self._active_owner_thread_id = threading.get_ident()
        try:
            yield
        finally:
            with self._active_handle_lock:
                self._active_handle = None
                self._active_owner_thread_id = None
            handle.close()


def _burn_record(token_digest: str = "c" * 64) -> BurnRecord:
    return BurnRecord(
        rehearsal_id="rehearsal-001",
        approval_packet_hash=PACKET_HASH,
        action_hash="e" * 64,
        token_digest=token_digest,
        binding_hash="f" * 64,
        burned_at=NOW,
        attempt_number=1,
        owner_presence_demonstrated=True,
        owner_verbatim_authorization_verified=True,
        owner_instruction_digest="1" * 64,
        authorization_record_id="owner-audit-auth-001",
    )


def _local_gate_fixture(
    tmp_path: Path,
    ledger: FileBurnLedger,
) -> tuple[Phase9Gate, GateRequest, str, str, LocalCountingExecutor]:
    state_root = tmp_path / "local-state"
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
        system_display_strings=("safe digest view",),
        initial_challenge_id="initial-challenge",
        session_active=True,
        phase9_audit_authorization=Phase9AuditAuthorizationRecord(
            record_id="owner-audit-auth-001",
            rehearsal_id="rehearsal-001",
            scope=PHASE9_AUDIT_SCOPE,
            owner_instruction_digest="f" * 64,
            authorized_at=NOW - timedelta(seconds=1),
            valid_until=NOW + timedelta(minutes=3),
        ),
    )
    executor = LocalCountingExecutor()
    gate = Phase9Gate(
        rehearsal_id="rehearsal-001",
        contract_verifier=TrueVerifier(),
        preflight_verifier=TrueVerifier(),
        audit_authorization_verifier=TrueAuditVerifier(),
        burn_ledger=ledger,
        version_probe=StaticVersionProbe(),
        snapshotter=DirectorySnapshotter(state_root),
        presence_channel=ProcessBarrierPresence(_ImmediateBarrier()),
        executor=executor,
        clock=ProcessClock(),
        gate_token_audit_coordination_lock=threading.Lock(),
        challenge_bytes=lambda size: b"c" * size,
    )
    return gate, request, raw, owner_text, executor


class _ImmediateBarrier:
    def wait(self, timeout: float) -> None:
        del timeout


def _process_worker(
    ledger_path: str,
    state_root: str,
    start_barrier: Any,
    outcomes: Any,
    executor_calls: Any,
    no_op_lock: bool,
) -> None:
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
        system_display_strings=("safe digest view",),
        initial_challenge_id="initial-challenge",
        session_active=True,
        phase9_audit_authorization=Phase9AuditAuthorizationRecord(
            record_id="owner-audit-auth-001",
            rehearsal_id="rehearsal-001",
            scope=PHASE9_AUDIT_SCOPE,
            owner_instruction_digest="f" * 64,
            authorized_at=NOW - timedelta(seconds=1),
            valid_until=NOW + timedelta(minutes=3),
        ),
    )
    target = Path(ledger_path)
    ledger = (
        NoOpLockLedger(target)
        if no_op_lock
        else FileBurnLedger(target)
    )
    gate = Phase9Gate(
        rehearsal_id="rehearsal-001",
        contract_verifier=TrueVerifier(),
        preflight_verifier=TrueVerifier(),
        audit_authorization_verifier=TrueAuditVerifier(),
        burn_ledger=ledger,
        version_probe=StaticVersionProbe(),
        snapshotter=DirectorySnapshotter(Path(state_root)),
        presence_channel=ProcessBarrierPresence(start_barrier),
        executor=ProcessExecutor(executor_calls),
        clock=ProcessClock(),
        challenge_bytes=lambda size: b"c" * size,
        gate_token_audit_coordination_lock=threading.Lock(),
    )
    start_barrier.wait(timeout=10)
    try:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )
    except GateDenied as exc:
        outcomes.put(exc.code)
    except Exception as exc:  # pragma: no cover - parent reports exact child failure
        outcomes.put(f"UNEXPECTED:{type(exc).__name__}")
    else:
        outcomes.put("EXECUTED")


def _queue_items(queue: Any, expected: int) -> list[Any]:
    values: list[Any] = []
    for _ in range(expected):
        try:
            values.append(queue.get(timeout=10))
        except Empty as exc:
            raise AssertionError("child process did not report an outcome") from exc
    return values


def _run_process_round(
    tmp_path: Path,
    round_number: int,
    *,
    no_op_lock: bool,
) -> tuple[list[str], list[tuple[str, int]], int]:
    context = multiprocessing.get_context("spawn")
    start_barrier = context.Barrier(2)
    outcomes = context.Queue()
    executor_calls = context.Queue()
    state_root = tmp_path / f"state-{round_number}"
    state_root.mkdir()
    (state_root / "config.json").write_text("{}", encoding="utf-8")
    ledger_path = tmp_path / f"burn-{round_number}.jsonl"
    processes = [
        context.Process(
            target=_process_worker,
            args=(
                str(ledger_path),
                str(state_root),
                start_barrier,
                outcomes,
                executor_calls,
                no_op_lock,
            ),
        )
        for _ in range(2)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=30)
    assert all(not process.is_alive() for process in processes)
    assert [process.exitcode for process in processes] == [0, 0]
    outcome_values = sorted(_queue_items(outcomes, 2))
    call_values: list[tuple[str, int]] = []
    while True:
        try:
            call_values.append(executor_calls.get_nowait())
        except Empty:
            break
    line_count = len(ledger_path.read_text(encoding="utf-8").splitlines())
    return outcome_values, call_values, line_count


def test_append_is_durable_verified_and_physically_re_read(tmp_path: Path) -> None:
    ledger = FileBurnLedger(tmp_path / "burn.jsonl")
    record = _burn_record()

    with ledger.exclusive_lock(timeout_seconds=1):
        assert ledger.contains(record.token_digest) is False
        receipt = ledger.commit(record)
        assert ledger.contains(record.token_digest) is True

    assert receipt.durable is True
    assert receipt.verified is True
    assert len(ledger.target.read_text(encoding="utf-8").splitlines()) == 1
    second_reader = FileBurnLedger(ledger.target)
    assert second_reader.contains(record.token_digest) is True


def test_fsync_failure_returns_non_durable_receipt(tmp_path: Path) -> None:
    def fail_fsync(_descriptor: int) -> None:
        raise OSError("synthetic fsync failure")

    ledger = FileBurnLedger(tmp_path / "burn.jsonl", fsync_fn=fail_fsync)
    with ledger.exclusive_lock(timeout_seconds=1):
        receipt = ledger.commit(_burn_record())

    assert receipt.durable is False
    assert receipt.verified is False


def test_fsync_failure_denies_gate_before_executor(tmp_path: Path) -> None:
    def fail_fsync(_descriptor: int) -> None:
        raise OSError("synthetic fsync failure")

    ledger = FileBurnLedger(tmp_path / "gate-burn.jsonl", fsync_fn=fail_fsync)
    gate, request, raw, owner_text, executor = _local_gate_fixture(tmp_path, ledger)

    with pytest.raises(GateDenied) as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert caught.value.code == "BURN_VERIFY_FAILED"
    assert executor.calls == 0


@pytest.mark.parametrize("failed_operation", ["flush", "seek", "read"])
def test_active_handle_read_oserror_is_payload_free_burn_ledger_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_operation: str,
) -> None:
    class FailingReadHandle:
        def flush(self) -> None:
            if failed_operation == "flush":
                raise OSError("SENSITIVE-FLUSH-PAYLOAD")

        def seek(self, _offset: int) -> None:
            if failed_operation == "seek":
                raise OSError("SENSITIVE-SEEK-PAYLOAD")

        def read(self) -> bytes:
            if failed_operation == "read":
                raise OSError("SENSITIVE-READ-PAYLOAD")
            return b""

    ledger = FileBurnLedger(tmp_path / "burn.jsonl")
    monkeypatch.setattr(
        ledger,
        "_active_handle_for_caller",
        lambda: FailingReadHandle(),
    )

    with pytest.raises(BurnLedgerError) as caught:
        ledger.contains("c" * 64)

    assert str(caught.value) == "burn ledger could not be read"
    assert "SENSITIVE" not in str(caught.value)


def test_corrupt_replay_barrier_is_verify_failure_and_never_executes(
    tmp_path: Path,
) -> None:
    ledger = FileBurnLedger(tmp_path / "corrupt-burn.jsonl")
    ledger.target.write_bytes(b"not-json\n")
    gate, request, raw, owner_text, executor = _local_gate_fixture(tmp_path, ledger)

    with pytest.raises(GateDenied) as caught:
        gate.run(
            request,
            presented_raw_token=raw,
            owner_authorization_text=owner_text,
        )

    assert caught.value.code == "BURN_VERIFY_FAILED"
    assert executor.calls == 0
    assert gate.state.value == "CLOSED_DENY"
    assert gate.freeze.frozen is True


def test_commit_requires_exclusive_lock(tmp_path: Path) -> None:
    ledger = FileBurnLedger(tmp_path / "burn.jsonl")
    with pytest.raises(BurnLedgerError, match="requires the exclusive ledger lock"):
        ledger.commit(_burn_record())


@pytest.mark.slow
def test_shared_file_ledger_instance_waits_and_reports_replay_for_150_rounds(
    tmp_path: Path,
) -> None:
    """The object lock is bounded process-local state protection, not OS locking."""

    executor_counts: list[int] = []
    burn_counts: list[int] = []
    for round_number in range(150):
        round_root = tmp_path / f"shared-instance-{round_number}"
        round_root.mkdir()
        ledger = FileBurnLedger(round_root / "burn.jsonl")
        gate_one, request, raw, owner_text, executor = _local_gate_fixture(
            round_root,
            ledger,
        )
        barrier = threading.Barrier(2)
        gate_one.presence_channel = ProcessBarrierPresence(barrier)
        gate_two = Phase9Gate(
            rehearsal_id="rehearsal-001",
            contract_verifier=TrueVerifier(),
            preflight_verifier=TrueVerifier(),
            audit_authorization_verifier=TrueAuditVerifier(),
            burn_ledger=ledger,
            version_probe=StaticVersionProbe(),
            snapshotter=gate_one.snapshotter,
            presence_channel=ProcessBarrierPresence(barrier),
            executor=executor,
            clock=ProcessClock(),
            gate_token_audit_coordination_lock=threading.Lock(),
            challenge_bytes=lambda size: b"c" * size,
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
        executor_counts.append(executor.calls)
        burn_count = len(ledger.target.read_text(encoding="utf-8").splitlines())
        burn_counts.append(burn_count)
        assert executor.calls == 1
        assert burn_count == 1

    print(
        "shared_instance_rounds=150 "
        f"max_executor_calls={max(executor_counts)} "
        f"max_burn_records={max(burn_counts)} "
        "replay_code=TOKEN_ALREADY_BURNED"
    )


@pytest.mark.slow
def test_independent_file_ledger_instances_share_os_lock_for_twenty_rounds(
    tmp_path: Path,
) -> None:
    """Distinct Python objects rely on the OS lock, not shared object identity."""

    executor_counts: list[int] = []
    burn_counts: list[int] = []
    for round_number in range(20):
        round_root = tmp_path / f"independent-instances-{round_number}"
        round_root.mkdir()
        target = round_root / "burn.jsonl"
        ledger_one = FileBurnLedger(target)
        ledger_two = FileBurnLedger(target)
        gate_one, request, raw, owner_text, executor = _local_gate_fixture(
            round_root,
            ledger_one,
        )
        barrier = threading.Barrier(2)
        gate_one.presence_channel = ProcessBarrierPresence(barrier)
        gate_two = Phase9Gate(
            rehearsal_id="rehearsal-001",
            contract_verifier=TrueVerifier(),
            preflight_verifier=TrueVerifier(),
            audit_authorization_verifier=TrueAuditVerifier(),
            burn_ledger=ledger_two,
            version_probe=StaticVersionProbe(),
            snapshotter=gate_one.snapshotter,
            presence_channel=ProcessBarrierPresence(barrier),
            executor=executor,
            clock=ProcessClock(),
            gate_token_audit_coordination_lock=threading.Lock(),
            challenge_bytes=lambda size: b"c" * size,
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
        executor_counts.append(executor.calls)
        burn_count = len(target.read_text(encoding="utf-8").splitlines())
        burn_counts.append(burn_count)
        assert executor.calls == 1
        assert burn_count == 1

    print(
        "independent_instance_rounds=20 "
        f"max_executor_calls={max(executor_counts)} "
        f"max_burn_records={max(burn_counts)}"
    )


@pytest.mark.slow
def test_cross_process_lock_allows_exactly_one_execution_for_twenty_rounds(
    tmp_path: Path,
) -> None:
    executor_counts: list[int] = []
    for round_number in range(20):
        outcomes, calls, line_count = _run_process_round(
            tmp_path,
            round_number,
            no_op_lock=False,
        )
        executor_counts.append(len(calls))
        assert outcomes == ["EXECUTED", "TOKEN_ALREADY_BURNED"]
        assert line_count == 1
    print(
        "cross_process_rounds=20 "
        f"max_executor_calls={max(executor_counts)} "
        f"max_burn_records=1"
    )
    assert max(executor_counts) == 1


def test_noop_lock_control_demonstrates_double_execution(tmp_path: Path) -> None:
    round_results: list[tuple[list[str], int, int]] = []
    for round_number in range(100, 105):
        outcomes, calls, line_count = _run_process_round(
            tmp_path,
            round_number,
            no_op_lock=True,
        )
        assert outcomes in (
            ["EXECUTED", "EXECUTED"],
            ["EXECUTED", "TOKEN_ALREADY_BURNED"],
        )
        assert len(calls) == outcomes.count("EXECUTED")
        # On NTFS, unlocked concurrent append can silently lose one record.
        # That is a worse no-lock failure mode, not a reason to weaken
        # protected tests.
        assert line_count in {1, 2}
        round_results.append((outcomes, len(calls), line_count))

    double_execution_rounds = sum(
        outcomes == ["EXECUTED", "EXECUTED"]
        for outcomes, _, _ in round_results
    )
    assert double_execution_rounds >= 1
    assert NoOpLockLedger.__bases__ == (FileBurnLedger,)
    assert {
        name
        for name, value in NoOpLockLedger.__dict__.items()
        if callable(value)
    } == {"exclusive_lock"}
    no_op_lock_source = inspect.getsource(NoOpLockLedger.exclusive_lock)
    assert not any(
        forbidden in no_op_lock_source
        for forbidden in ("Barrier", "barrier", "sleep", "Event", "wait(")
    )
    assert NoOpLockLedger.contains is FileBurnLedger.contains
    assert NoOpLockLedger.commit is FileBurnLedger.commit
    print(
        "noop_rounds=5 "
        f"double_execution_rounds={double_execution_rounds} "
        f"executor_calls={[calls for _, calls, _ in round_results]} "
        f"burn_records={[records for _, _, records in round_results]}"
    )


def test_burn_ledger_source_is_append_only_and_has_no_runtime_wiring() -> None:
    source_path = Path(__file__).parents[1] / "app" / "phase9_burn_ledger.py"
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
    open_modes = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "open"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    }

    assert open_modes == {"a+b", "rb"}
    assert not {"truncate", "unlink", "rename", "replace", "mkdir"} & call_names
    assert not {"subprocess", "socket"} & imports
    assert not {"Popen", "run", "system"} & call_names


def test_missing_parent_is_rejected_without_creating_directory(tmp_path: Path) -> None:
    parent = tmp_path / "absent"
    ledger = FileBurnLedger(parent / "burn.jsonl")

    with pytest.raises(BurnLedgerError, match="could not be opened"):
        with ledger.exclusive_lock(timeout_seconds=1):
            pass

    assert parent.exists() is False
