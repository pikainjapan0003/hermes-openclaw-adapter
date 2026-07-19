"""Branch closeout for local stores and the mock-only result/intake helpers.

Every filesystem write in this module is constrained to pytest ``tmp_path``.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app import health_store
from app import queue_intake_bridge_v0_7 as bridge
from app import result_sink
from app.mock_adapter_v0_7 import prepare_queue_candidate_from_mock_request
from app.queue_store import (
    ALL_STATUSES,
    ARCHIVED,
    CANCELLED,
    COMPLETED,
    FAILED,
    QUEUED,
    REJECTED,
    RUNNING,
    WAITING_REVIEW,
    QueueStore,
)


def _request(**overrides: object) -> dict:
    value = {
        "request_id": "request-storage",
        "requested_by": "owner",
        "intent": "inspect",
        "goal": "inspect synthetic state",
        "task_type": "query",
        "risk_level": 0,
        "approval_required": False,
        "input_summary": "synthetic input",
        "target_runtime": "mock",
        "target_workspace": "local",
        "metadata": {"mock": True},
    }
    value.update(overrides)
    return value


def _envelope(**overrides: object) -> dict:
    return prepare_queue_candidate_from_mock_request(_request(**overrides))


def _enqueue(store: QueueStore, task_id: str, status: str = QUEUED) -> dict:
    row = store.enqueue(
        task_id=task_id,
        title="synthetic",
        task_text="read-only rehearsal",
        safety_level=1,
        payload={"metadata": {"synthetic_local_only": True}},
        initial_status=status,
    )
    assert row is not None
    return row


def test_health_status_parsing_and_store_roundtrip(tmp_path: Path) -> None:
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)
    assert health_store.derive_status(None, now=now) == health_store.UNKNOWN
    assert health_store.derive_status("bad", now=now) == health_store.UNKNOWN
    assert health_store.derive_status((now - timedelta(seconds=5)).isoformat(), now=now) == health_store.ONLINE
    assert health_store.derive_status((now - timedelta(seconds=60)).replace(tzinfo=None).isoformat(), now=now) == health_store.STALE

    store = health_store.HealthStore(tmp_path / "health.sqlite3")
    assert store.get("missing") is None
    assert store.snapshot("missing")["status"] == health_store.UNKNOWN

    row = store.record("worker-a", pid=7, metadata={"mode": "mock"}, last_seen_at=now.isoformat())
    assert row["status"] == "idle"
    assert row["metadata"] == {"mode": "mock"}
    updated = store.record("worker-a", status="running", current_task_id="task-a")
    assert updated["pid"] == 7
    assert updated["status"] == "running"
    snapshot = store.snapshot("worker-a", stale_seconds=10**9)
    assert snapshot["raw_status"] == "running"
    assert snapshot["current_task_id"] == "task-a"


def test_health_metadata_decode_failures_are_empty(tmp_path: Path) -> None:
    store = health_store.HealthStore(tmp_path / "health-bad.sqlite3")
    store.record("bad-json", metadata_json="{broken")
    store.record("not-map", metadata_json="[]")
    assert store.get("bad-json")["metadata"] == {}
    assert store.get("not-map")["metadata"] == {}


def test_queue_store_lifecycle_queries_and_transitions(tmp_path: Path) -> None:
    store = QueueStore(tmp_path / "queue.sqlite3")
    assert store.claim_next() is None
    with pytest.raises(ValueError):
        _enqueue(store, "invalid", COMPLETED)

    queued = _enqueue(store, "queued")
    duplicate = _enqueue(store, "queued")
    assert duplicate["created_at"] == queued["created_at"]
    review = _enqueue(store, "review", WAITING_REVIEW)
    assert review["status"] == WAITING_REVIEW

    claimed = store.claim_next()
    assert claimed is not None and claimed["status"] == RUNNING and claimed["attempts"] == 1
    assert store.cancel_if_queued("queued") is False
    assert store.reset_stale_running() == 1
    assert store.get("queued")["status"] == QUEUED
    assert store.cancel_if_queued("queued") is True
    assert store.get("queued")["status"] == CANCELLED

    approved = store.approve("review")
    assert approved is not None and approved["status"] == QUEUED
    assert store.approve("review") is None
    assert store.reject("review", "late") is None

    second_review = _enqueue(store, "review-2", WAITING_REVIEW)
    assert second_review["status"] == WAITING_REVIEW
    rejected = store.reject("review-2", "no")
    assert rejected is not None and rejected["status"] == REJECTED

    assert store.cancel_control("review", "owner") ["status"] == CANCELLED
    assert store.cancel_control("review", "again") is None
    assert store.archive("review", "done")["status"] == ARCHIVED
    assert store.archive("review", "again") is None

    failed = store.mark_failed("review-2", "synthetic failure")
    assert failed is not None and failed["status"] == FAILED
    assert store.retry_failed("review-2", "retry")["status"] == QUEUED
    assert store.retry_failed("review-2") is None
    assert store.mark_completed("review-2", "result-1")["status"] == COMPLETED
    assert store.requeue("review-2", "again")["status"] == QUEUED
    assert store.mark_cancelled("review-2")["status"] == CANCELLED

    events = store.append_approval_decision_event(
        "review-2", {"decision_type": "reject", "dispatch_allowed_at_decision": False}
    )
    assert events is not None
    assert store.append_approval_decision_event("missing", {}) is None

    assert store.get("missing") is None
    assert store.total() == 3
    assert len(store.list()) == 3
    assert store.list(status=ARCHIVED)[0]["task_id"] == "review"
    counts = store.counts_by_status()
    assert set(counts) == set(ALL_STATUSES)
    all_page, all_total = store.list_page(limit=2)
    assert len(all_page) == 2 and all_total == 3
    archived_page, archived_total = store.list_page(status=ARCHIVED)
    assert len(archived_page) == archived_total == 1


def test_queue_recent_failed_and_archive_without_error_change(tmp_path: Path) -> None:
    store = QueueStore(tmp_path / "queue-failed.sqlite3")
    _enqueue(store, "failed")
    store.mark_failed("failed", "reason")
    assert store.recent_failed()[0]["task_id"] == "failed"
    archived = store.archive("failed", "ignored")
    assert archived is not None and archived["status"] == ARCHIVED
    assert archived["error"] == "reason"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, True), (False, False), (1, True), (0, False), (" yes ", True), (None, False)],
)
def test_result_sink_boolean_coercion(value, expected) -> None:
    assert result_sink._coerce_bool(value) is expected


def test_result_sink_builds_ledger_and_mock_writes_only_to_tmp_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    task = {
        "task_id": "task-sink",
        "title": "synthetic",
        "status": "completed",
        "safety_level": 1,
        "payload": json.dumps(
            {"metadata": {"requires_confirmation": "yes", "source": "mock"}}
        ),
    }
    row = result_sink.build_task_ledger_row(
        task, {"result_text": " x " * 300, "finished_at": "now"}
    )
    assert row["requires_confirmation"] is True
    assert len(row["result_summary"]) <= result_sink.MAX_SUMMARY_LEN
    assert row["metadata_json"] != "{}"
    assert result_sink._payload_metadata({"payload": "{bad"}) == {}
    assert result_sink._payload_metadata({"payload": []}) == {}
    assert result_sink._payload_metadata({"payload": {"metadata": []}}) == {}
    assert result_sink._truncate(None) == ""

    monkeypatch.setattr(result_sink, "RESULT_SINK_ENABLED", False)
    assert result_sink.emit_result(task)["status"] == "disabled"
    monkeypatch.setattr(result_sink, "RESULT_SINK_ENABLED", True)
    monkeypatch.setattr(result_sink, "RESULT_SINK_TYPE", "other")
    assert result_sink.emit_result(task)["status"] == "skipped"

    output = tmp_path / "mock" / "rows.jsonl"
    monkeypatch.setattr(result_sink, "RESULT_SINK_TYPE", "google_sheets")
    monkeypatch.setattr(result_sink, "RESULT_SINK_MODE", "mock")
    monkeypatch.setattr(result_sink, "MOCK_GOOGLE_SHEETS_ROWS_PATH", str(output))
    written = result_sink.emit_result(task)
    assert written["status"] == "mock_written"
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["_mock"] is True

    monkeypatch.setattr(result_sink, "_append_mock_row", lambda _row: (_ for _ in ()).throw(OSError("synthetic")))
    assert result_sink.emit_result(task)["status"] == "error"


def test_result_sink_env_bool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SYNTHETIC_BOOL", raising=False)
    assert result_sink._env_bool("SYNTHETIC_BOOL", True) is True
    monkeypatch.setenv("SYNTHETIC_BOOL", "off")
    assert result_sink._env_bool("SYNTHETIC_BOOL", True) is False


def _enable_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUEUE_INTAKE_ENABLED", "true")
    monkeypatch.setenv("INTAKE_ALLOWED_TASK_TYPES", "query")
    monkeypatch.delenv("GLOBAL_KILL_SWITCH", raising=False)
    monkeypatch.delenv("INTAKE_KILL_SWITCH", raising=False)
    monkeypatch.delenv("INTAKE_SECURITY_GATES_ENABLED", raising=False)


def test_intake_bridge_gate_precedence_and_helpers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(bridge.QueueIntakeBridgeError):
        bridge.intake_task_envelope_local_only([])

    request = _envelope()
    monkeypatch.setenv("GLOBAL_KILL_SWITCH", "true")
    assert bridge.intake_task_envelope_local_only(request)["reason"] == "global_kill_switch_active"
    monkeypatch.delenv("GLOBAL_KILL_SWITCH")
    monkeypatch.setenv("INTAKE_KILL_SWITCH", "yes")
    assert bridge.intake_task_envelope_local_only(request)["reason"] == "kill_switch_active"
    monkeypatch.delenv("INTAKE_KILL_SWITCH")
    monkeypatch.delenv("QUEUE_INTAKE_ENABLED", raising=False)
    assert bridge.intake_task_envelope_local_only(request)["reason"] == "intake_disabled"

    _enable_bridge(monkeypatch)
    monkeypatch.setenv("INTAKE_ALLOWED_TASK_TYPES", "other")
    assert bridge.intake_task_envelope_local_only(request)["reason"] == "task_type_not_allowlisted"
    assert bridge._extract_requested_tools({"metadata": []}) is None
    assert bridge._resolve_intake_db_path("explicit") == "explicit"
    monkeypatch.setenv("INTAKE_QUEUE_DB_PATH", str(tmp_path / "from-env.sqlite3"))
    assert bridge._resolve_intake_db_path(None).endswith("from-env.sqlite3")


def test_intake_bridge_security_rejection_production_refusal_and_tmp_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _enable_bridge(monkeypatch)
    request = _envelope(
        allowed_tools=["read"],
        denied_tools=["shell"],
        metadata={"mock": True, "requested_tools": ["shell"]},
    )
    monkeypatch.setenv("INTAKE_SECURITY_GATES_ENABLED", "true")
    rejected = bridge.intake_task_envelope_local_only(request, db_path=str(tmp_path / "reject.sqlite3"))
    assert rejected["reason"] == "security_gate_rejected"
    assert rejected["audit_event"]["observation_only"] is True
    assert not (tmp_path / "reject.sqlite3").exists()

    monkeypatch.delenv("INTAKE_SECURITY_GATES_ENABLED")
    production = tmp_path / "production.sqlite3"
    monkeypatch.setenv("QUEUE_DB_PATH", str(production))
    refused = bridge.intake_task_envelope_local_only(_envelope(), db_path=str(production))
    assert refused["reason"] == "refuse_production_db"
    assert not production.exists()

    intake_db = tmp_path / "intake.sqlite3"
    accepted = bridge.intake_task_envelope_local_only(_envelope(), db_path=str(intake_db))
    assert accepted["accepted"] is True
    assert accepted["initial_status"] == WAITING_REVIEW
    assert intake_db.exists()
    row = QueueStore(intake_db).get(accepted["task_id"])
    payload = json.loads(row["payload"])
    assert payload["metadata"]["executable_by_worker"] is False
    assert payload["status"] == "pending_approval"
