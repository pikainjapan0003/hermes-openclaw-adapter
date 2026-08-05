"""Cross-process and append-only evidence for the Phase 9 burn ledger."""

from __future__ import annotations

import ast
import hashlib
import json
import multiprocessing
import os
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from queue import Empty
from typing import Any, Iterator

import pytest

from app.hash_chain import canonical_json
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


class UnsafeNoOpLedger:
    """Deliberately broken contrast double; never production code."""

    def __init__(self, target: Path, first_contains_barrier: Any) -> None:
        self._target = target
        self._first_contains_barrier = first_contains_barrier
        self._first_contains = True

    @property
    def target(self) -> Path:
        return self._target

    @contextmanager
    def exclusive_lock(self, *, timeout_seconds: float) -> Iterator[None]:
        del timeout_seconds
        yield

    def _records(self) -> list[dict[str, Any]]:
        if not self._target.exists():
            return []
        return [
            json.loads(line)
            for line in self._target.read_text(encoding="utf-8").splitlines()
        ]

    def contains(self, token_digest: str) -> bool:
        result = any(
            record.get("token_digest") == token_digest for record in self._records()
        )
        if self._first_contains:
            self._first_contains = False
            self._first_contains_barrier.wait(timeout=10)
        return result

    def commit(self, record: BurnRecord) -> BurnReceipt:
        encoded = canonical_json(record.safe_record())
        with self._target.open("a+b") as handle:
            handle.write(encoded + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        return BurnReceipt(
            record.token_digest,
            hashlib.sha256(encoded).hexdigest(),
            durable=True,
            verified=True,
        )


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


def _process_worker(
    ledger_path: str,
    state_root: str,
    start_barrier: Any,
    first_contains_barrier: Any,
    outcomes: Any,
    executor_calls: Any,
    unsafe_noop_lock: bool,
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
        UnsafeNoOpLedger(target, first_contains_barrier)
        if unsafe_noop_lock
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
    unsafe_noop_lock: bool,
) -> tuple[list[str], list[tuple[str, int]], int]:
    context = multiprocessing.get_context("spawn")
    start_barrier = context.Barrier(2)
    first_contains_barrier = context.Barrier(2) if unsafe_noop_lock else None
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
                first_contains_barrier,
                outcomes,
                executor_calls,
                unsafe_noop_lock,
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


def test_commit_requires_exclusive_lock(tmp_path: Path) -> None:
    ledger = FileBurnLedger(tmp_path / "burn.jsonl")
    with pytest.raises(BurnLedgerError, match="requires the exclusive ledger lock"):
        ledger.commit(_burn_record())


@pytest.mark.slow
def test_cross_process_lock_allows_exactly_one_execution_for_twenty_rounds(
    tmp_path: Path,
) -> None:
    executor_counts: list[int] = []
    for round_number in range(20):
        outcomes, calls, line_count = _run_process_round(
            tmp_path,
            round_number,
            unsafe_noop_lock=False,
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
    outcomes, calls, line_count = _run_process_round(
        tmp_path,
        100,
        unsafe_noop_lock=True,
    )

    assert outcomes == ["EXECUTED", "EXECUTED"]
    assert len(calls) == 2
    assert line_count == 2


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
