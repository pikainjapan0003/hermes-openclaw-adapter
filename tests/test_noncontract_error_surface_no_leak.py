"""Non-contract pure helpers must not echo hostile markers on rejected input."""

from __future__ import annotations

import json

import pytest

from app.contracts_v0_7 import ContractValidationError, validate_task_envelope
from app.dashboard_intake_view_v0_7 import derive_intake_status_view
from app.hermes_result_readback_mock import build_hermes_result_readback_advice
from app.hermes_strategy_suggestion_model import build_hermes_strategy_suggestion
from app.mock_adapter_v0_7 import MockAdapterError, build_task_envelope_from_mock_request
from app.mock_openclaw_gateway import build_mock_openclaw_response


SECRET = "FAKE-SECRET-20260727"
ABSOLUTE_PATH = r"C:\Users\Owner\private\payload.txt"
MARKERS = (SECRET, ABSOLUTE_PATH)


def _assert_markers_absent(value: object) -> None:
    serialized = json.dumps(value, ensure_ascii=False, default=str)
    assert all(marker not in serialized for marker in MARKERS)


def _legacy_task() -> dict[str, object]:
    return {
        "task_id": "task-1",
        "created_at": "2026-07-27T00:00:00Z",
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
        "metadata": f"{SECRET}:{ABSOLUTE_PATH}",
    }


def test_legacy_contract_type_error_omits_invalid_value_markers() -> None:
    with pytest.raises(ContractValidationError) as caught:
        validate_task_envelope(_legacy_task())
    _assert_markers_absent(str(caught.value))


def test_mock_adapter_validation_error_omits_metadata_value_markers() -> None:
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
        "metadata": f"{SECRET}:{ABSOLUTE_PATH}",
    }
    with pytest.raises(MockAdapterError) as caught:
        build_task_envelope_from_mock_request(request)
    _assert_markers_absent(str(caught.value))


def test_dashboard_intake_type_error_omits_hostile_input_markers() -> None:
    with pytest.raises(TypeError) as caught:
        derive_intake_status_view(f"{SECRET}:{ABSOLUTE_PATH}")  # type: ignore[arg-type]
    _assert_markers_absent(str(caught.value))


@pytest.mark.parametrize(
    "builder",
    (
        build_mock_openclaw_response,
        build_hermes_strategy_suggestion,
        build_hermes_result_readback_advice,
    ),
)
def test_structured_rejections_omit_unrelated_markers(builder: object) -> None:
    rejected = builder(  # type: ignore[operator]
        {"untrusted_secret": SECRET, "private_path": ABSOLUTE_PATH}
    )
    assert rejected["accepted"] is False
    _assert_markers_absent(rejected)
