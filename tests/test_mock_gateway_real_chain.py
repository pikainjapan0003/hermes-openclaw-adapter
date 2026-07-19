"""In-memory contract chain driven by the real local mock-gateway helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from app.approval_packet_builder import build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import build_evidence_bundle, verify_bundle_hash
from app.rollback_preview_builder import build_rollback_preview
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD_FIXTURES = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_SCHEMA = ROOT / "docs" / "schemas" / "evidence_bundle.json"


def _fixture(name: str) -> dict[str, Any]:
    value = json.loads(
        (BLACKBOARD_FIXTURES / f"{name}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def _gateway_command(task_id: str, command_id: str) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "task_id": task_id,
        "tool_target": "synthetic.adapter.status",
        "requested_action": "read one synthetic adapter status value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "No rollback is required; nothing is executed.",
        "external_side_effects_allowed": False,
    }


def test_real_mock_gateway_output_forms_schema_valid_contract_chain() -> None:
    task = _fixture("task_draft")
    worker_dry_run = _fixture("worker_dry_run")
    result = _fixture("result_message")
    audit = _fixture("audit_event")
    command = _gateway_command(task["task_id"], result["command_id"])

    mock_result = run_worker_to_mock_gateway_dry_run(command)
    assert mock_result["accepted"] is True
    assert mock_result["mock_gateway_called"] is True
    assert mock_result["worker_dispatched"] is False
    assert mock_result["real_openclaw_called"] is False
    assert mock_result["external_side_effects_performed"] is False
    assert mock_result["gateway_response"]["task_id"] == task["task_id"]
    assert mock_result["gateway_response"]["command_id"] == result["command_id"]

    bundle = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="2026-07-21T00:00:00Z",
    )
    evidence_schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    errors = list(
        Draft202012Validator(
            evidence_schema, format_checker=FormatChecker()
        ).iter_errors(bundle)
    )
    assert errors == []
    assert verify_bundle_hash(bundle) is True
    assert bundle["mock_result"]["gateway_response"]["task_id"] == task["task_id"]

    packet = build_approval_packet(
        worker_dry_run,
        result,
        decision="respond",
        approval_timestamp=None,
    )
    assert validate_blackboard_message(packet)["valid"] is True
    assert packet["task_id"] == bundle["task"]["task_id"]
    assert packet["exact_target"]["command_id"] == bundle["command_envelope"]["command_id"]

    rollback = build_rollback_preview(audit, bundle, result)
    assert validate_blackboard_message(rollback)["valid"] is True
    assert rollback["task_id"] == packet["task_id"]
    assert rollback["related_result_id"] == packet["dry_run_evidence"]["result_id"]
    assert rollback["preview_only"] is True
    assert rollback["rollback_required"] is False
