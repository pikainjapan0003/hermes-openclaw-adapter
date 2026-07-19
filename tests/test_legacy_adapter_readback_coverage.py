"""Regression coverage for two isolated legacy mock-only helpers."""

from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import pytest

from app import hermes_result_readback_mock as readback
from app import mock_adapter_v0_7 as adapter
from app.contracts_v0_7 import ContractValidationError, validate_task_envelope


def _result_message() -> dict:
    return {
        "result_id": "result-synthetic-1",
        "task_id": "task-synthetic-1",
        "status": "completed",
        "source": "synthetic_local_only",
        "mock_gateway": True,
        "worker_dry_run": True,
        "real_openclaw_called": False,
        "worker_dispatched": False,
        "external_side_effects_performed": False,
        "queue_written": False,
        "audit_trail_written": False,
    }


def _request(**overrides: object) -> dict:
    request = {
        "request_id": "request-1",
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
    request.update(overrides)
    return request


def test_valid_result_readback_is_safe_valid_and_does_not_mutate_input() -> None:
    source = _result_message()
    snapshot = deepcopy(source)

    advice = readback.build_hermes_result_readback_advice(source)

    assert source == snapshot
    assert advice["accepted"] is True
    assert advice["readback_id"] == "readback-result-synthetic-1"
    assert advice["source_result_id"] == source["result_id"]
    assert readback.validate_hermes_result_readback_advice(advice) == {
        "valid": True,
        "violations": [],
    }
    for field, safe_value in readback.FORCED_READBACK_SAFETY_FIELDS.items():
        assert advice[field] is safe_value


def test_result_readback_requires_mapping_and_all_required_fields() -> None:
    rejected = readback.build_hermes_result_readback_advice([])
    assert rejected["accepted"] is False
    assert rejected["rejection_reason"] == "result_message must be a mapping"

    source = _result_message()
    del source["result_id"]
    rejected = readback.build_hermes_result_readback_advice(source)
    assert rejected["accepted"] is False
    assert rejected["rejection_reason"] == "missing required result message fields"
    assert "missing field: result_id" in rejected["rejection_details"]


@pytest.mark.parametrize(
    ("field", "value", "violation"),
    [
        ("source", "external", "source must be"),
        ("mock_gateway", False, "mock_gateway must be true"),
        ("worker_dry_run", False, "worker_dry_run must be true"),
        ("real_openclaw_called", True, "real_openclaw_called must be false"),
        ("worker_dispatched", True, "worker_dispatched must be false"),
        ("external_side_effects_performed", True, "external_side_effects_performed must be false"),
        ("queue_written", True, "queue_written must be false"),
        ("audit_trail_written", True, "audit_trail_written must be false"),
    ],
)
def test_result_readback_rejects_each_unsafe_source_flag(
    field: str, value: object, violation: str
) -> None:
    source = _result_message()
    source[field] = value
    rejected = readback.build_hermes_result_readback_advice(source)
    assert rejected["accepted"] is False
    assert rejected["rejection_reason"] == "unsafe result message flags"
    assert any(violation in detail for detail in rejected["rejection_details"])


def test_result_readback_propagates_underlying_advice_rejection(monkeypatch) -> None:
    fake_module = SimpleNamespace(
        build_mock_hermes_advice=lambda _context: {
            "accepted": False,
            "rejection_reason": None,
            "rejection_details": ["synthetic rejection"],
        }
    )
    monkeypatch.setattr(readback, "_load_generator_module", lambda: fake_module)

    rejected = readback.build_hermes_result_readback_advice(_result_message())

    assert rejected["accepted"] is False
    assert rejected["rejection_reason"] == "underlying mock Hermes advice rejected"
    assert rejected["rejection_details"] == ["synthetic rejection"]


def test_result_readback_validator_fails_closed() -> None:
    assert readback.validate_hermes_result_readback_advice(None) == {
        "valid": False,
        "violations": ["readback_advice must be a mapping"],
    }
    accepted = readback.build_hermes_result_readback_advice(_result_message())
    del accepted["owner_question"]
    accepted["must_not_execute"] = False

    validation = readback.validate_hermes_result_readback_advice(accepted)

    assert validation["valid"] is False
    assert "missing field: owner_question" in validation["violations"]
    assert "must_not_execute must be True" in validation["violations"]


def test_mock_adapter_builds_valid_envelope_with_stable_idempotency_key() -> None:
    request = _request(
        created_by="mock-planner",
        source="mock-source",
        priority="high",
        max_retries=4,
        result_policy={"mode": "display"},
        callback_policy={"mode": "none"},
        input_payload_ref=None,
        allowed_tools=["read"],
        denied_tools=[],
    )
    first = adapter.build_task_envelope_from_mock_request(request)
    second = adapter.build_task_envelope_from_mock_request(request)

    assert first["task_id"] != second["task_id"]
    assert first["idempotency_key"] == second["idempotency_key"]
    assert first["status"] == "draft"
    assert first["created_by"] == "mock-planner"
    assert first["allowed_tools"] == ["read"]
    validate_task_envelope(first)


def test_mock_adapter_request_validation_fails_closed() -> None:
    with pytest.raises(adapter.MockAdapterError, match="dict"):
        adapter.build_task_envelope_from_mock_request([])

    missing = _request()
    del missing["request_id"]
    with pytest.raises(adapter.MockAdapterError, match="request_id"):
        adapter.build_task_envelope_from_mock_request(missing)

    with pytest.raises(adapter.MockAdapterError, match="metadata"):
        adapter.build_task_envelope_from_mock_request(_request(metadata=[]))

    with pytest.raises(ContractValidationError):
        adapter.build_task_envelope_from_mock_request(_request(risk_level=5))


@pytest.mark.parametrize(
    ("risk_level", "approval_required", "status", "approval_status"),
    [
        (0, False, "queued", "not_required"),
        (2, False, "queued", "not_required"),
        (3, False, "pending_approval", "pending"),
        (4, False, "pending_approval", "pending"),
        (1, True, "pending_approval", "pending"),
    ],
)
def test_mock_adapter_approval_gate_branches(
    risk_level: int,
    approval_required: bool,
    status: str,
    approval_status: str,
) -> None:
    envelope = adapter.build_task_envelope_from_mock_request(
        _request(risk_level=risk_level, approval_required=approval_required)
    )
    snapshot = deepcopy(envelope)

    gated = adapter.apply_approval_gate(envelope)

    assert envelope == snapshot
    assert gated["status"] == status
    assert gated["approval_status"] == approval_status
    assert gated["approval_required"] is (status == "pending_approval")


def test_mock_adapter_gate_requires_mapping_and_risk_level() -> None:
    with pytest.raises(adapter.MockAdapterError, match="dict"):
        adapter.apply_approval_gate([])
    with pytest.raises(adapter.MockAdapterError, match="risk_level"):
        adapter.apply_approval_gate({})


def test_mock_adapter_prepares_valid_queue_candidate() -> None:
    candidate = adapter.prepare_queue_candidate_from_mock_request(_request(risk_level=1))
    assert candidate["status"] == "queued"
    assert validate_task_envelope(candidate) is candidate
