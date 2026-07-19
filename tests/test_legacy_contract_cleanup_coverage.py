"""Regression coverage for the frozen v0.7 contracts and cleanup preview."""

from __future__ import annotations

from copy import deepcopy

import pytest

from app import demo_task_cleanup_v0_7 as cleanup
from app.contracts_v0_7 import (
    ContractValidationError,
    load_json_schema,
    validate_callback_event,
    validate_task_envelope,
)


def _task() -> dict:
    return {
        "task_id": "task-1",
        "created_at": "2026-07-21T00:00:00Z",
        "created_by": "hermes",
        "source": "synthetic",
        "requested_by": "owner",
        "risk_level": 1,
        "approval_required": False,
        "approval_status": "not_required",
        "intent": "inspect",
        "goal": "validate a synthetic task",
        "task_type": "query",
        "priority": "normal",
        "input_summary": "synthetic input",
        "target_runtime": "mock",
        "target_workspace": "local",
        "idempotency_key": "idem-1",
        "max_retries": 2,
        "retry_count": 0,
        "status": "queued",
        "result_policy": {"mode": "ledger"},
        "callback_policy": {"mode": "ledger_only"},
        "metadata": {},
    }


def _callback() -> dict:
    return {
        "event_id": "event-1",
        "task_id": "task-1",
        "source": "mock-worker",
        "created_at": "2026-07-21T00:01:00Z",
        "event_type": "completed",
        "status": "completed",
        "summary": "done",
        "retryable": False,
        "metadata": {},
    }


@pytest.mark.parametrize(
    "name",
    ["task_envelope_v0_7", "task_envelope_v0_7.json", "task_envelope_v0_7.schema.json"],
)
def test_contract_schema_name_suffixes_are_supported(name: str) -> None:
    schema = load_json_schema(name)
    assert schema["title"] == "TaskEnvelope v0.7"


def test_missing_contract_schema_is_structurally_rejected() -> None:
    with pytest.raises(ContractValidationError, match="schema not found"):
        load_json_schema("absent_v0_7")


def test_valid_task_contract_is_returned_without_mutation() -> None:
    payload = _task()
    payload.update(
        input_payload_ref=None,
        allowed_tools=["read"],
        denied_tools=[],
    )
    snapshot = deepcopy(payload)
    assert validate_task_envelope(payload) is payload
    assert payload == snapshot


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("task_id", 1),
        ("approval_required", "no"),
        ("risk_level", True),
        ("risk_level", -1),
        ("risk_level", 5),
        ("max_retries", True),
        ("retry_count", -1),
        ("status", "unknown"),
        ("approval_status", "unknown"),
        ("result_policy", []),
        ("callback_policy", []),
        ("metadata", []),
        ("input_payload_ref", 4),
        ("allowed_tools", "read"),
        ("denied_tools", ["write", 1]),
    ],
)
def test_invalid_task_contract_values_fail_closed(field: str, value: object) -> None:
    payload = _task()
    payload[field] = value
    with pytest.raises(ContractValidationError):
        validate_task_envelope(payload)


@pytest.mark.parametrize("payload", [None, [], "task"])
def test_task_contract_requires_an_object(payload: object) -> None:
    with pytest.raises(ContractValidationError):
        validate_task_envelope(payload)


def test_task_contract_requires_all_fields() -> None:
    payload = _task()
    del payload["goal"]
    with pytest.raises(ContractValidationError):
        validate_task_envelope(payload)


def test_valid_callback_contract_supports_optional_fields() -> None:
    payload = _callback()
    payload.update(
        flow_id=None,
        result_ref="result-1",
        error_code=None,
        error_message=None,
        duration_ms=0,
        artifacts=[],
    )
    assert validate_callback_event(payload) is payload


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_id", 1),
        ("retryable", "false"),
        ("metadata", []),
        ("event_type", "unknown"),
        ("status", "unknown"),
        ("flow_id", 1),
        ("duration_ms", True),
        ("duration_ms", -1),
        ("artifacts", {}),
    ],
)
def test_invalid_callback_contract_values_fail_closed(field: str, value: object) -> None:
    payload = _callback()
    payload[field] = value
    with pytest.raises(ContractValidationError):
        validate_callback_event(payload)


def test_callback_contract_requires_object_and_required_fields() -> None:
    with pytest.raises(ContractValidationError):
        validate_callback_event([])
    payload = _callback()
    del payload["task_id"]
    with pytest.raises(ContractValidationError):
        validate_callback_event(payload)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"metadata": {}}, {"metadata": {}}),
        ('{"metadata": {"demo_task": true}}', {"metadata": {"demo_task": True}}),
        ("[]", {}),
        ("not-json", {}),
        (None, {}),
    ],
)
def test_cleanup_payload_normalization(value: object, expected: dict) -> None:
    assert cleanup._as_payload_dict(value) == expected


def test_cleanup_metadata_prefers_payload_then_falls_back_to_task() -> None:
    assert cleanup._normalize_metadata(None) == {}
    assert cleanup._normalize_metadata({"payload": {"metadata": {"demo_task": True}}}) == {
        "demo_task": True
    }
    assert cleanup._normalize_metadata({"payload": "{}", "metadata": {"sample_task": True}}) == {
        "sample_task": True
    }
    assert cleanup._normalize_metadata({"metadata": []}) == {}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (" YES ", True),
        ("false", False),
        (1, True),
        (1.0, True),
        (2, False),
        (None, False),
    ],
)
def test_cleanup_bool_coercion(value: object, expected: bool) -> None:
    assert cleanup._coerce_bool(value) is expected


@pytest.mark.parametrize(
    ("metadata", "expected_label"),
    [
        ({"demo_task": True}, "demo_task"),
        ({"sample_task": "yes"}, "sample_task"),
        ({"preview_task": 1}, "preview_task"),
        ({"test_task": True}, "test_task"),
        ({"cleanup_classification": " SAMPLE "}, "cleanup_classification=sample"),
        ({"task_classification": "test"}, "task_classification=test"),
    ],
)
def test_cleanup_demo_markers_are_explicit(metadata: dict, expected_label: str) -> None:
    assert cleanup._has_demo_marker(metadata) is True
    assert cleanup._demo_marker_label(metadata) == expected_label


def test_cleanup_helper_marker_branches() -> None:
    assert cleanup._classification_value({"classification": 1}, "classification") == ""
    assert cleanup._has_demo_marker({}) is False
    assert cleanup._demo_marker_label({}) == ""
    assert cleanup._has_production_marker({"production": True}) is True
    assert cleanup._has_production_marker({"production_task": "true"}) is True
    assert cleanup._has_production_marker({"cleanup_classification": "production"}) is True
    assert cleanup._has_production_marker({"task_classification": "production"}) is True
    assert cleanup._has_production_marker({}) is False
    assert cleanup._has_external_side_effect_marker({"external_execution": True}) is True
    assert cleanup._has_external_side_effect_marker({}) is False
    assert cleanup._has_secret_like_marker({"contains_secret": True}) is True
    assert cleanup._has_secret_like_marker({"secret_like": True}) is True
    assert cleanup._has_secret_like_marker({" API_KEY ": "redacted"}) is True
    assert cleanup._has_secret_like_marker({1: "not-a-string-key"}) is False
    assert cleanup._origin_is_unknown({"origin_unclear": True}) is True
    assert cleanup._origin_is_unknown({"origin": "unknown"}) is True
    assert cleanup._origin_is_unknown({}) is False
    assert cleanup._is_active_validation({"in_active_validation": True}) is True
    assert cleanup._is_active_validation({}) is False


def test_cleanup_safe_task_id_fallbacks() -> None:
    assert cleanup._safe_task_id({"task_id": "task-1"}, 0) == "task-1"
    assert cleanup._safe_task_id({"id": "legacy-1"}, 0) == "legacy-1"
    assert cleanup._safe_task_id({"task_id": "  "}, 3) == "index-3"
    assert cleanup._safe_task_id([], 4) == "index-4"


@pytest.mark.parametrize(
    ("metadata", "reason"),
    [
        ({}, "no explicit demo/sample/preview/test marker"),
        ({"demo_task": True, "production": True}, "production marker present"),
        ({"demo_task": True, "external_side_effect": True}, "external side effect marker present"),
        ({"demo_task": True, "password": "redacted"}, "secret-like marker present"),
        ({"demo_task": True, "origin": "unclear"}, "origin unknown"),
        (
            {"demo_task": True, "active_validation": True},
            "needed for active validation without owner_approved_replacement",
        ),
    ],
)
def test_cleanup_report_blocks_each_guard(metadata: dict, reason: str) -> None:
    report = cleanup.derive_demo_task_cleanup_dry_run_report([{"task_id": "task-1", "metadata": metadata}])
    assert report["candidate_count"] == 0
    assert report["blocked_items"] == [{"task_id": "task-1", "reason": reason}]


def test_cleanup_report_is_dry_run_only_and_does_not_mutate_input() -> None:
    tasks = [
        {"task_id": "candidate", "payload": {"metadata": {"demo_task": True}}},
        {
            "id": "active-approved",
            "metadata": {
                "sample_task": True,
                "active_validation": True,
                "owner_approved_replacement": True,
            },
        },
        "not-a-task",
    ]
    snapshot = deepcopy(tasks)
    report = cleanup.derive_demo_task_cleanup_dry_run_report(
        tuple(tasks), source_queue=7, target_environment="preview"
    )
    assert tasks == snapshot
    assert report["candidate_count"] == 2
    assert report["blocked_count"] == 1
    assert report["source_queue"] == "synthetic"
    assert report["target_environment"] == "preview"
    assert report["execution_mode"] == "dry_run_only"
    assert report["dry_run"] is True
    for key in (
        "apply_requested",
        "apply_allowed",
        "would_delete",
        "would_archive",
        "would_modify",
        "external_side_effects",
    ):
        assert report[key] is False
    assert report["owner_approval_required"] is True


def test_cleanup_report_rejects_nonlocal_environment_and_nonlist_tasks() -> None:
    blocked = cleanup.derive_demo_task_cleanup_dry_run_report(
        [{"task_id": "task-1", "metadata": {"demo_task": True}}],
        target_environment="production",
    )
    assert blocked["blocked_items"][0]["reason"] == "target_environment is not local or preview"
    empty = cleanup.derive_demo_task_cleanup_dry_run_report(
        {"task_id": "not-a-list"}, target_environment=None
    )
    assert empty["candidate_count"] == 0
    assert empty["blocked_count"] == 0
    assert empty["target_environment"] == ""
