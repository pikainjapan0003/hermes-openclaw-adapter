"""Branch edges for the two lowest covered legacy contract modules."""

from __future__ import annotations

import pytest

from app import contracts_v0_7 as contracts
from app import worker_mock_gateway_dry_run as worker_gateway


def _task() -> dict[str, object]:
    return {
        "task_id": "task-legacy-round3",
        "created_at": "2026-07-24T00:00:00Z",
        "created_by": "hermes",
        "source": "synthetic",
        "requested_by": "owner",
        "risk_level": 1,
        "approval_required": False,
        "approval_status": "not_required",
        "intent": "inspect",
        "goal": "cover legacy validation branches",
        "task_type": "query",
        "priority": "normal",
        "input_summary": "synthetic input",
        "target_runtime": "mock",
        "target_workspace": "local",
        "idempotency_key": "legacy-round3",
        "max_retries": 1,
        "retry_count": 0,
        "status": "queued",
        "result_policy": {},
        "callback_policy": {},
        "metadata": {},
    }


def _callback() -> dict[str, object]:
    return {
        "event_id": "event-legacy-round3",
        "task_id": "task-legacy-round3",
        "source": "mock-worker",
        "created_at": "2026-07-24T00:01:00Z",
        "event_type": "completed",
        "status": "completed",
        "summary": "synthetic callback",
        "retryable": False,
        "metadata": {},
    }


def test_contract_schema_loader_accepts_supported_name_suffixes() -> None:
    for name in (
        "task_envelope_v0_7",
        "task_envelope_v0_7.schema.json",
        "task_envelope_v0_7.json",
    ):
        schema = contracts.load_json_schema(name)
        assert isinstance(schema, dict)
        assert schema["title"]


@pytest.mark.parametrize(
    "field",
    (
        "approval_required",
        "risk_level",
        "max_retries",
        "retry_count",
        "status",
        "approval_status",
        "result_policy",
        "callback_policy",
        "metadata",
    ),
)
def test_task_required_field_absence_reaches_each_fail_closed_branch(
    field: str,
) -> None:
    payload = _task()
    del payload[field]
    with pytest.raises(contracts.ContractValidationError, match="缺少必要欄位"):
        contracts.validate_task_envelope(payload)


@pytest.mark.parametrize(
    "field",
    ("retryable", "metadata", "event_type", "status"),
)
def test_callback_required_field_absence_reaches_each_fail_closed_branch(
    field: str,
) -> None:
    payload = _callback()
    del payload[field]
    with pytest.raises(contracts.ContractValidationError, match="缺少必要欄位"):
        contracts.validate_callback_event(payload)


def test_worker_dry_run_rejects_each_required_true_flag() -> None:
    envelope = {
        "mock_only": True,
        "dry_run": False,
        "external_side_effects_allowed": False,
    }
    result = worker_gateway.run_worker_to_mock_gateway_dry_run(envelope)

    assert result["accepted"] is False
    assert result["mock_gateway_called"] is False
    assert result["rejection_details"] == ["dry_run must be true"]

