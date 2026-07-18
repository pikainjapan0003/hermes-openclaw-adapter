"""Pure in-memory rehearsal of the complete data-contract chain.

No step writes, dispatches, executes, or creates a real hash-chain entry.
Until the Phase 7 canonicalization design is approved for implementation,
every Blackboard ``prev_entry_hash`` remains the schema-supported null value.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from app.approval_packet_builder import build_approval_packet
from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import build_evidence_bundle, verify_bundle_hash
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_SCHEMA = ROOT / "docs" / "schemas" / "evidence_bundle.json"

BLACKBOARD_ORDER = (
    "task_draft",
    "annotation",
    "approval_readiness",
    "owner_decision",
    "worker_dry_run",
    "openclaw_command_envelope",
    "result_message",
    "approval_packet",
    "audit_event",
    "rollback_event",
)
FULL_CHAIN_ORDER = (
    *BLACKBOARD_ORDER[:8],
    "evidence_bundle",
    *BLACKBOARD_ORDER[8:],
)


def _load_valid_fixture(message_type: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{message_type}.valid.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _evidence_command(
    task: dict[str, Any], command_envelope: dict[str, Any]
) -> dict[str, Any]:
    """Project the Blackboard preview into the Phase 5 N=1 builder input."""

    return {
        "command_id": command_envelope["command_id"],
        "task_id": task["task_id"],
        "tool_target": "synthetic.adapter.status",
        "requested_action": command_envelope["input_summary"],
        "risk_level": "low",
        "approval_snapshot": {"owner_review_required": True},
        "execution_mode": "mock_only",
        "dry_run": True,
        "mock_only": True,
        "external_touchpoints": [],
        "rollback_plan": "No rollback is required; nothing is executed.",
        "external_side_effects_allowed": False,
    }


def _build_full_chain() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    messages = {
        message_type: _load_valid_fixture(message_type)
        for message_type in BLACKBOARD_ORDER
        if message_type != "approval_packet"
    }
    for message in messages.values():
        message["prev_entry_hash"] = None

    messages["approval_packet"] = build_approval_packet(
        messages["worker_dry_run"],
        messages["result_message"],
        decision="approve",
        approval_timestamp="2026-07-18T10:07:00Z",
        prev_entry_hash=None,
    )

    evidence_command = _evidence_command(
        messages["task_draft"], messages["openclaw_command_envelope"]
    )
    mock_result = run_worker_to_mock_gateway_dry_run(evidence_command)
    evidence_bundle = build_evidence_bundle(
        messages["task_draft"],
        evidence_command,
        mock_result,
        [],
        created_at="2026-07-18T10:06:30Z",
    )
    return messages, evidence_bundle


def _assert_reference_chain(
    messages: dict[str, dict[str, Any]], evidence_bundle: dict[str, Any]
) -> None:
    task = messages["task_draft"]
    annotation = messages["annotation"]
    readiness = messages["approval_readiness"]
    decision = messages["owner_decision"]
    dry_run = messages["worker_dry_run"]
    command = messages["openclaw_command_envelope"]
    result = messages["result_message"]
    packet = messages["approval_packet"]
    audit = messages["audit_event"]
    rollback = messages["rollback_event"]

    task_id = task["task_id"]
    assert annotation["task_id"] == task_id
    assert readiness["task_id"] == task_id
    assert readiness["annotation_id"] == annotation["annotation_id"]
    assert decision["task_id"] == task_id
    assert decision["readiness_id"] == readiness["readiness_id"]
    assert dry_run["task_id"] == task_id
    assert dry_run["decision_id"] == decision["decision_id"]
    assert command["task_id"] == task_id
    assert command["dry_run_id"] == dry_run["dry_run_id"]
    assert result["task_id"] == task_id
    assert result["command_id"] == command["command_id"]
    assert result["related_dry_run_id"] == dry_run["dry_run_id"]

    assert packet["task_id"] == task_id
    assert packet["exact_target"]["task_id"] == task_id
    assert packet["exact_target"]["command_id"] == command["command_id"]
    assert packet["dry_run_evidence"]["dry_run_id"] == dry_run["dry_run_id"]
    assert packet["dry_run_evidence"]["result_id"] == result["result_id"]

    assert evidence_bundle["task"]["task_id"] == task_id
    assert evidence_bundle["command_envelope"]["task_id"] == task_id
    assert (
        evidence_bundle["command_envelope"]["command_id"]
        == command["command_id"]
    )
    assert (
        evidence_bundle["mock_result"]["gateway_response"]["task_id"]
        == task_id
    )
    assert (
        evidence_bundle["mock_result"]["gateway_response"]["command_id"]
        == command["command_id"]
    )

    assert audit["task_id"] == task_id
    assert audit["related_result_id"] == result["result_id"]
    assert rollback["task_id"] == task_id
    assert rollback["related_result_id"] == result["result_id"]
    assert rollback["source_audit_id"] == audit["audit_id"]


def _validate_evidence_bundle(bundle: dict[str, Any]) -> list[Any]:
    schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(bundle), key=lambda error: list(error.path))


def test_complete_eleven_step_contract_chain_is_valid_and_linked() -> None:
    messages, evidence_bundle = _build_full_chain()

    assert len(FULL_CHAIN_ORDER) == 11
    assert set(messages) == set(BLACKBOARD_ORDER)
    for message_type in BLACKBOARD_ORDER:
        message = messages[message_type]
        assert message["prev_entry_hash"] is None
        validation = validate_blackboard_message(message)
        assert validation["valid"] is True, validation["errors"]

    assert _validate_evidence_bundle(evidence_bundle) == []
    assert verify_bundle_hash(evidence_bundle) is True
    _assert_reference_chain(messages, evidence_bundle)


def _break_annotation_task(
    messages: dict[str, dict[str, Any]], evidence_bundle: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    del evidence_bundle
    messages["annotation"]["task_id"] = "task-unrelated"
    return "annotation", messages["annotation"]


def _break_result_command(
    messages: dict[str, dict[str, Any]], evidence_bundle: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    del evidence_bundle
    messages["result_message"]["command_id"] = "cmd-unrelated"
    return "result_message", messages["result_message"]


def _break_rollback_audit(
    messages: dict[str, dict[str, Any]], evidence_bundle: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    del evidence_bundle
    messages["rollback_event"]["source_audit_id"] = "audit-unrelated"
    return "rollback_event", messages["rollback_event"]


@pytest.mark.parametrize(
    "breaker",
    (_break_annotation_task, _break_result_command, _break_rollback_audit),
    ids=("task-link", "command-link", "audit-link"),
)
def test_schema_valid_but_cross_linked_bad_data_is_rejected(
    breaker: Callable[
        [dict[str, dict[str, Any]], dict[str, Any]], tuple[str, dict[str, Any]]
    ],
) -> None:
    messages, evidence_bundle = _build_full_chain()
    broken_type, broken_message = breaker(messages, evidence_bundle)

    schema_validation = validate_blackboard_message(broken_message, broken_type)
    assert schema_validation["valid"] is True
    with pytest.raises(AssertionError):
        _assert_reference_chain(messages, evidence_bundle)
