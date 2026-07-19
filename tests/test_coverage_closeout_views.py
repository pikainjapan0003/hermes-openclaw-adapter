"""Branch closeout tests for legacy read-only display and annotation helpers."""

from __future__ import annotations

import copy
import json

import pytest

from app import approval_decision_event_recorder_v0_7 as recorder
from app import approval_decision_events_v0_7 as decisions
from app import audit_trail_display_v0_7 as audit_display
from app import dashboard_intake_view_v0_7 as intake_view
from app import queue_task_annotation_v0_7 as annotation


def _task(metadata: object = None, *, status: str = "waiting_review") -> dict:
    payload = {"metadata": metadata} if metadata is not None else {}
    return {
        "task_id": "task-view",
        "status": status,
        "safety_level": 1,
        "payload": payload,
    }


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"metadata": {}}, {"metadata": {}}),
        ('{"metadata": {}}', {"metadata": {}}),
        ("[]", {}),
        ("{broken", {}),
        (7, {}),
    ],
)
def test_payload_parsers_cover_dict_json_and_fail_closed_shapes(payload, expected) -> None:
    assert recorder._as_payload_dict(payload) == expected
    assert decisions._as_payload_dict(payload) == expected
    assert audit_display._as_payload_dict(payload) == expected
    assert annotation._as_payload_dict(payload) == expected


def test_metadata_fallbacks_and_normalizers() -> None:
    task = {"payload": {"metadata": "bad"}, "metadata": {"fallback": True}}
    assert recorder._metadata_of(task) == {"fallback": True}
    assert decisions.normalize_payload_metadata(task) == {"fallback": True}
    assert audit_display._normalize_metadata(task) == {"fallback": True}
    assert annotation.normalize_payload_metadata(task) == {"fallback": True}
    assert decisions.normalize_payload_metadata([]) == {}
    assert audit_display._normalize_metadata([]) == {}
    assert annotation.normalize_payload_metadata([]) == {}


def test_recorder_builds_safe_snapshots_and_appends_copy_on_write() -> None:
    task = _task(
        {
            "safety_level": 2,
            "requires_confirmation": True,
            "approval_readiness": "ready_for_owner_decision",
        }
    )
    task["safety_level"] = True
    original = copy.deepcopy(task)

    event = recorder.build_approval_decision_event(
        task,
        decision_type="approve",
        previous_status="waiting_review",
        next_status="queued",
        decided_by="",
        decision_reason=" ",
        via="",
    )

    assert event["decided_by"] == "owner"
    assert event["decision_reason"] == "not_provided"
    assert event["audit_record"]["via"] == "dashboard-approve"
    assert event["safety_snapshot"]["safety_level"] == 2
    assert event["execution_permission_at_decision"] is False
    assert event["dispatch_allowed_at_decision"] is False
    assert task == original

    payload = {"metadata": {"kept": 1, "approval_decision_events": [{"old": 1}]}}
    snapshot = copy.deepcopy(payload)
    appended = recorder.append_approval_decision_event_to_payload(payload, event)
    assert payload == snapshot
    assert appended["metadata"]["kept"] == 1
    assert len(appended["metadata"]["approval_decision_events"]) == 2

    assert len(recorder.append_approval_decision_event_to_payload("{}", event)["metadata"]["approval_decision_events"]) == 1
    assert len(recorder.append_approval_decision_event_to_payload({"metadata": []}, event)["metadata"]["approval_decision_events"]) == 1
    assert len(recorder.append_approval_decision_event_to_payload({"metadata": {"approval_decision_events": "bad"}}, event)["metadata"]["approval_decision_events"]) == 1


def test_decision_view_normalizes_hostile_legacy_events_without_authority() -> None:
    source_event = {
        "decision_id": "d-1",
        "task_id": "task-view",
        "decision_type": "approve",
        "decided_by": "owner",
        "decided_at": "2026-07-21T00:00:00Z",
        "decision_reason": "ok",
        "previous_status": "waiting_review",
        "next_status": "queued",
        "approval_readiness_at_decision": "ready_for_owner_decision",
        "execution_permission_at_decision": True,
        "dispatch_allowed_at_decision": True,
        "safety_snapshot": {"risk": 1},
        "annotation_snapshot": {"ready": True},
        "audit_record": {"append_only": True},
    }
    raw = {"metadata": {"approval_decision_events": [source_event, "bad"]}}
    snapshot = copy.deepcopy(raw)
    view = decisions.derive_approval_decision_event_view({"payload": json.dumps(raw)})

    assert view["event_count"] == 2
    assert view["events"][0]["decision_id"] == "d-1"
    assert view["events"][0]["execution_permission_at_decision"] is False
    assert view["events"][0]["dispatch_allowed_at_decision"] is False
    assert view["events"][1]["decision_id"] == "unknown"
    assert view["events"][1]["safety_snapshot"] == {}
    assert raw == snapshot

    empty = decisions.derive_approval_decision_event_view(_task({"approval_decision_events": "bad"}))
    assert empty["has_events"] is False


@pytest.mark.parametrize(
    ("status", "metadata", "expected"),
    [
        ("completed", {}, "archived_or_closed"),
        ("active", {"approval_decision_events": [{}]}, "owner_decided"),
        ("waiting_review", {}, "owner_review"),
        ("active", {"approval_readiness": "not_ready"}, "owner_review"),
        ("active", {"safety_level": 1}, "annotated"),
        ("draft", {}, "draft_or_created"),
    ],
)
def test_audit_display_lifecycle_precedence(status, metadata, expected) -> None:
    view = audit_display.derive_audit_trail_display_view(_task(metadata, status=status))
    assert view["lifecycle_state"] == expected
    assert view["read_only"] is True
    assert view["dispatch_allowed"] is False


def test_audit_display_helpers_and_timeline_edges() -> None:
    assert audit_display._status_looks_archived(1) is False
    assert audit_display._status_looks_archived(" ") is False
    assert audit_display._status_looks_review(1) is False
    assert audit_display._count_decision_events({"approval_decision_events": "bad"}) == 0
    assert audit_display._has_annotation_signal({}) is False
    timeline = audit_display._build_timeline_items(False, {}, 0)
    assert [item["kind"] for item in timeline] == ["result_message", "advice_message"]
    full = audit_display._build_timeline_items(True, {"annotation": {"x": 1}}, 2)
    assert [item["kind"] for item in full][:3] == ["task_message", "annotation", "decision_message"]


@pytest.mark.parametrize(
    ("metadata", "status", "source", "intake", "executable"),
    [
        ({"intake_source": "mock-adapter-local", "executable_by_worker": True}, "queued", "local-only", "unknown", "false"),
        ({"mock": True, "local_only": True}, "queued", "mock", "local-only", "false"),
        ({"mock": False, "local_only": False}, "queued", "real", "production", "true"),
        ({}, "completed", "unknown", "unknown", "false"),
        ({}, "custom", "unknown", "unknown", "unknown"),
    ],
)
def test_dashboard_intake_modes_and_worker_display(metadata, status, source, intake, executable) -> None:
    view = intake_view.derive_intake_status_view(_task(metadata, status=status))
    assert view["source_mode"] == source
    assert view["intake_mode"] == intake
    assert view["executable_by_worker"] == executable


def test_dashboard_intake_risk_approval_badges_and_input_edges() -> None:
    with pytest.raises(TypeError):
        intake_view.derive_intake_status_view([])
    assert intake_view._as_payload_dict("[]") == {}
    assert intake_view._as_payload_dict("{bad") == {}
    assert intake_view._extract_metadata({"metadata": {"x": 1}}, {}) == {"x": 1}
    assert intake_view._extract_metadata({"metadata": "bad"}, {}) == {}
    assert intake_view._is_int(True) is False

    task = {
        "task_id": "task-view",
        "status": "waiting_review",
        "safety_level": 9,
        "payload": {
            "risk_level": 2,
            "metadata": {"risk_level": 1, "approval_status": "explicit"},
        },
    }
    view = intake_view.derive_intake_status_view(task)
    assert view["risk_level"] == 1
    assert view["approval_status"] == "explicit"
    assert "risk:1" in view["display_badges"]
    assert intake_view._derive_approval_status({}, "waiting_review", None) == "pending"
    assert intake_view._derive_approval_status({}, "queued", 2) == "not_required"
    assert intake_view._derive_approval_status({}, "queued", 3) == "unknown"


@pytest.mark.parametrize(
    ("metadata", "status", "readiness", "blockers"),
    [
        ({"prohibited": True}, "queued", "prohibited", ["prohibited"]),
        ({"policy_decision": "PROHIBITED"}, "queued", "prohibited", ["prohibited"]),
        ({"blocked_by_policy": True}, "queued", "blocked_by_policy", ["blocked_by_policy"]),
        ({"approval_status": "BLOCKED_BY_POLICY"}, "queued", "blocked_by_policy", ["blocked_by_policy"]),
        ({"approval_readiness": "ready_for_owner_decision"}, "queued", "ready_for_owner_decision", []),
        ({}, "waiting_review", "owner_review_required", ["owner_review_required"]),
        ({}, "queued", "not_ready", ["missing_annotation"]),
    ],
)
def test_annotation_readiness_and_blocker_precedence(metadata, status, readiness, blockers) -> None:
    view = annotation.derive_queue_task_annotation(_task(metadata, status=status))
    assert view["approval_readiness"] == readiness
    assert view["approval_blockers"] == blockers
    assert view["execution_permission"] is False
    assert view["dispatch_allowed"] is False


def test_annotation_explicit_fields_and_fail_closed_types() -> None:
    metadata = {
        "approval_blockers": ["one"],
        "task_origin": "synthetic",
        "external_touchpoints": ["local"],
        "dry_run_available": True,
        "mock_available": "true",
    }
    view = annotation.derive_queue_task_annotation(_task(metadata))
    assert view["approval_blockers"] == ["one"]
    assert view["task_origin"] == "synthetic"
    assert view["external_touchpoints"] == ["local"]
    assert view["dry_run_available"] is True
    assert view["mock_available"] is False
    assert annotation.normalize_approval_readiness(" BAD ") == ""
    assert annotation._safe_str_list(["ok", 1]) == []
    assert annotation._equals_ci(1, "x") is False
