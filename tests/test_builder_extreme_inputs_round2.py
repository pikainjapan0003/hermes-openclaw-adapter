"""Second-round boundary coverage for every pure contract builder."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import build_evidence_bundle, verify_bundle_hash
from app.rollback_preview_builder import build_rollback_preview
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE = ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
BOUNDARY_LENGTH = 32_768
UNICODE_FRAGMENT = "N=1 • 演習 • e\u0301 • 🔒"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture(message_type: str) -> dict[str, Any]:
    return _load(BLACKBOARD / f"{message_type}.valid.json")


def _long_text() -> str:
    repeats = (BOUNDARY_LENGTH // len(UNICODE_FRAGMENT)) + 1
    value = (UNICODE_FRAGMENT * repeats)[:BOUNDARY_LENGTH]
    assert len(value) == BOUNDARY_LENGTH
    return value


def _deep_value(depth: int = 120) -> dict[str, Any]:
    root: dict[str, Any] = {}
    cursor = root
    for index in range(depth):
        child: dict[str, Any] = {"depth": index}
        cursor["layer"] = child
        cursor = child
    cursor["value"] = "synthetic-boundary"
    return root


def _evidence_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    task = _fixture("task_draft")
    command = {
        "command_id": "cmd-extreme-round2-001",
        "task_id": task["task_id"],
        "tool_target": "synthetic.adapter.status",
        "requested_action": "read one synthetic adapter status value",
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "nothing executed",
        "external_side_effects_allowed": False,
    }
    return task, command, run_worker_to_mock_gateway_dry_run(command)


def test_approval_builder_accepts_long_unicode_and_deep_ignored_input() -> None:
    text = _long_text()
    worker = _fixture("worker_dry_run")
    result = _fixture("result_message")
    worker["proposed_worker_action"] = text
    worker["deep_boundary_probe"] = _deep_value()
    result["rollback_note"] = text
    result["audit_note"] = text
    before = copy.deepcopy((worker, result))

    first = build_approval_packet(
        worker,
        result,
        decision="respond",
        approval_timestamp="9999-12-31T23:59:59.999999Z",
        prev_entry_hash="a" * 64,
    )
    second = build_approval_packet(
        worker,
        result,
        decision="respond",
        approval_timestamp="9999-12-31T23:59:59.999999Z",
        prev_entry_hash="a" * 64,
    )

    assert first == second
    assert (worker, result) == before
    assert first["action_summary"] == text
    assert validate_blackboard_message(first, "approval_packet")["valid"] is True


def test_evidence_builder_accepts_deep_unicode_boundaries_and_rehashes() -> None:
    text = _long_text()
    task, command, mock_result = _evidence_inputs()
    task["title"] = text
    task["summary"] = text
    task["deep_boundary_probe"] = _deep_value()
    command["requested_action"] = text
    command["rollback_plan"] = text
    mock_result["gateway_response"]["mock_response_summary"] = text
    before = copy.deepcopy((task, command, mock_result))

    first = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="9999-12-31T23:59:59.999999Z",
    )
    second = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at="9999-12-31T23:59:59.999999Z",
    )

    assert first == second
    assert (task, command, mock_result) == before
    assert first["task"]["title"] == text
    assert verify_bundle_hash(first) is True
    assert _load(EVIDENCE)["bundle_type"] == first["bundle_type"]


def test_rollback_builder_accepts_large_identifiers_without_io() -> None:
    text = _long_text()
    audit = _fixture("audit_event")
    bundle = _load(EVIDENCE)
    result = _fixture("result_message")
    audit["audit_id"] = "audit-" + text
    audit["event_id"] = "event-" + text
    audit["related_result_id"] = "result-" + text
    result["result_id"] = "result-" + text
    before = copy.deepcopy((audit, bundle, result))

    preview = build_rollback_preview(audit, bundle, result)

    assert (audit, bundle, result) == before
    assert preview["source_audit_id"] == "audit-" + text
    assert len(preview["rollback_id"]) > BOUNDARY_LENGTH
    assert validate_blackboard_message(preview, "rollback_event")["valid"] is True
