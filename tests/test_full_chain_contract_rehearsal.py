"""Pure in-memory rehearsal of the complete 12-step data-contract chain.

No step writes, dispatches, executes, or persists a hash-chain entry.  The
audit-event sequence uses the approved in-memory canonical hash calculation.
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
from app.hash_chain import entry_hash, verify_chain
from app.rollback_preview_builder import build_rollback_preview
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_SCHEMA = ROOT / "docs" / "schemas" / "evidence_bundle.json"

BLACKBOARD_PREFIX_ORDER = (
    "task_draft",
    "annotation",
    "approval_readiness",
    "owner_decision",
    "worker_dry_run",
    "openclaw_command_envelope",
    "result_message",
    "approval_packet",
)
FULL_CHAIN_ORDER = (
    *BLACKBOARD_PREFIX_ORDER,
    "evidence_bundle",
    "audit_event_genesis",
    "audit_event_linked",
    "rollback_preview",
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
        for message_type in BLACKBOARD_PREFIX_ORDER
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

    audit_genesis = _load_valid_fixture("audit_event")
    audit_genesis["prev_entry_hash"] = None
    audit_linked = copy.deepcopy(audit_genesis)
    audit_linked.update(
        {
            "audit_id": "audit-phase3-002",
            "event_id": "audit-event-phase3-002",
            "event_notes": "Linked synthetic preview event; nothing was persisted.",
            "prev_entry_hash": entry_hash(audit_genesis),
        }
    )
    messages["audit_event_genesis"] = audit_genesis
    messages["audit_event_linked"] = audit_linked
    messages["rollback_preview"] = build_rollback_preview(
        audit_linked,
        evidence_bundle,
        messages["result_message"],
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
    audit_genesis = messages["audit_event_genesis"]
    audit_linked = messages["audit_event_linked"]
    rollback = messages["rollback_preview"]

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

    assert audit_genesis["task_id"] == task_id
    assert audit_genesis["related_result_id"] == result["result_id"]
    assert audit_linked["task_id"] == task_id
    assert audit_linked["related_result_id"] == result["result_id"]
    assert rollback["task_id"] == task_id
    assert rollback["related_result_id"] == result["result_id"]
    assert rollback["source_audit_id"] == audit_linked["audit_id"]


def _validate_evidence_bundle(bundle: dict[str, Any]) -> list[Any]:
    schema = json.loads(EVIDENCE_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(validator.iter_errors(bundle), key=lambda error: list(error.path))


def test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed() -> None:
    messages, evidence_bundle = _build_full_chain()

    assert len(FULL_CHAIN_ORDER) == 12
    assert set(messages) == set(BLACKBOARD_PREFIX_ORDER) | {
        "audit_event_genesis",
        "audit_event_linked",
        "rollback_preview",
    }
    for message_type in BLACKBOARD_PREFIX_ORDER:
        message = messages[message_type]
        assert message["prev_entry_hash"] is None
        validation = validate_blackboard_message(message)
        assert validation["valid"] is True, validation["errors"]

    audit_sequence = [
        messages["audit_event_genesis"],
        messages["audit_event_linked"],
    ]
    assert audit_sequence[0]["prev_entry_hash"] is None
    assert audit_sequence[1]["prev_entry_hash"] == entry_hash(audit_sequence[0])
    assert verify_chain(audit_sequence) is True
    for audit_event in audit_sequence:
        validation = validate_blackboard_message(audit_event, "audit_event")
        assert validation["valid"] is True, validation["errors"]

    rollback_validation = validate_blackboard_message(
        messages["rollback_preview"], "rollback_event"
    )
    assert rollback_validation["valid"] is True, rollback_validation["errors"]

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
    messages["rollback_preview"]["source_audit_id"] = "audit-unrelated"
    return "rollback_event", messages["rollback_preview"]


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


def test_tampering_with_hashed_audit_event_breaks_the_chain() -> None:
    messages, _ = _build_full_chain()
    audit_sequence = [
        copy.deepcopy(messages["audit_event_genesis"]),
        copy.deepcopy(messages["audit_event_linked"]),
    ]
    audit_sequence[0]["event_notes"] = "Tampered after the link was calculated."

    assert verify_chain(audit_sequence) is False
