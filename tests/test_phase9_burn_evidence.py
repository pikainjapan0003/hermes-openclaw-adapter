"""Contract and no-leak tests for the pure Phase 9 burn evidence builder."""

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pytest

from app.blackboard_validators import validate_blackboard_message
from app.phase9_burn_evidence import (
    BurnEvidenceBuildError,
    build_phase9_burn_evidence,
    validate_phase9_burn_evidence,
)
from app.phase9_gate import BurnRecord


pytestmark = pytest.mark.contract

RAW_TOKEN_MARKER = "RAW-TOKEN-MUST-NEVER-APPEAR"


def _burn_record() -> BurnRecord:
    return BurnRecord(
        rehearsal_id="rehearsal-phase9-001",
        approval_packet_hash="a" * 64,
        action_hash="b" * 64,
        token_digest="c" * 64,
        binding_hash="d" * 64,
        burned_at=datetime(2026, 8, 6, 9, 30, tzinfo=timezone.utc),
        attempt_number=1,
        owner_presence_demonstrated=True,
        owner_verbatim_authorization_verified=True,
        owner_instruction_digest="e" * 64,
        authorization_record_id="owner-audit-auth-001",
    )


def _event() -> dict[str, object]:
    return build_phase9_burn_evidence(
        _burn_record(),
        audit_id="audit-phase9-001",
        event_id="audit-event-phase9-burn-001",
        task_id="task-phase9-001",
        related_result_id="result-phase9-planned-001",
        prev_entry_hash="f" * 64,
    )


def test_burn_evidence_is_schema_valid_and_contains_no_token_material() -> None:
    event = _event()

    assert validate_blackboard_message(event, "audit_event")["valid"] is True
    assert event["execution_class"] == "OWNER_MANUAL"
    assert event["preview_only"] is False
    assert event["audit_status"] == "persisted"
    serialized = json.dumps(event, sort_keys=True)
    assert RAW_TOKEN_MARKER not in serialized
    assert _burn_record().token_digest not in serialized
    assert _burn_record().binding_hash not in serialized


FLAG_RATIONALES = (
    ("synthetic_local_only", False, "the event describes a real rehearsal boundary"),
    ("mock_only", False, "the evidence is not limited to a mock executor"),
    ("dry_run", False, "burn consumes a real one-shot authorization"),
    ("owner_review_required", True, "Phase 9 remains Owner-supervised"),
    (
        "external_side_effects_allowed",
        False,
        "this event authorizes only the audit append, not the later call",
    ),
    (
        "external_side_effects_occurred",
        False,
        "the executor has not been called at the burn-evidence boundary",
    ),
    ("blackboard_write_allowed", False, "the audit append is not a board write"),
    ("queue_write_allowed", False, "the gate never writes the queue here"),
    (
        "audit_trail_write_allowed",
        True,
        "05 section 6.19 authorizes this exact pre-call audit record",
    ),
    ("worker_dispatch_allowed", False, "the N=1 path does not dispatch a worker"),
    (
        "openclaw_call_allowed",
        False,
        "the evidence append must finish before a distinct call capability exists",
    ),
    ("hermes_runtime_allowed", False, "the evidence layer has no Hermes runtime"),
    ("connector_call_allowed", False, "the evidence layer calls no connector"),
    (
        "google_sheets_write_allowed",
        False,
        "the authorization excludes Google Sheets writes",
    ),
    ("follow_up_allowed", False, "no automatic follow-up or retry is allowed"),
    (
        "follow_up_requires_owner_confirmation",
        True,
        "any later ceremony requires fresh Owner confirmation",
    ),
)


@pytest.mark.parametrize(
    ("flag", "expected", "rationale"),
    FLAG_RATIONALES,
    ids=[item[0] for item in FLAG_RATIONALES],
)
def test_each_safety_flag_has_an_explicit_posture_and_reason(
    flag: str,
    expected: bool,
    rationale: str,
) -> None:
    flags = _event()["safety_flags"]

    assert isinstance(flags, dict)
    assert flags[flag] is expected, rationale
    assert rationale


def _add_raw_token(event: dict[str, object]) -> None:
    event["raw_token"] = RAW_TOKEN_MARKER


def _remove_required_field(event: dict[str, object]) -> None:
    del event["event_id"]


def _add_unknown_field(event: dict[str, object]) -> None:
    event["unexpected"] = "not allowed"


def _make_preview(event: dict[str, object]) -> None:
    event["preview_only"] = True


def _make_unpersisted(event: dict[str, object]) -> None:
    event["audit_status"] = "preview_audit_not_persisted"


@pytest.mark.parametrize(
    "mutate",
    (
        _add_raw_token,
        _remove_required_field,
        _add_unknown_field,
        _make_preview,
        _make_unpersisted,
    ),
)
def test_forbidden_or_incomplete_evidence_is_rejected(
    mutate: Callable[[dict[str, object]], None],
) -> None:
    event = _event()
    mutate(event)

    with pytest.raises(BurnEvidenceBuildError):
        validate_phase9_burn_evidence(event)
    if mutate in {_add_raw_token, _remove_required_field, _add_unknown_field}:
        assert validate_blackboard_message(event, "audit_event")["valid"] is False


def test_builder_rejects_invalid_identifiers_and_chain_predecessor() -> None:
    with pytest.raises(BurnEvidenceBuildError, match="event_id"):
        build_phase9_burn_evidence(
            _burn_record(),
            audit_id="audit-phase9-001",
            event_id="",
            task_id="task-phase9-001",
            related_result_id="result-phase9-planned-001",
            prev_entry_hash="f" * 64,
        )
    with pytest.raises(BurnEvidenceBuildError, match="prev_entry_hash"):
        build_phase9_burn_evidence(
            _burn_record(),
            audit_id="audit-phase9-001",
            event_id="audit-event-phase9-burn-001",
            task_id="task-phase9-001",
            related_result_id="result-phase9-planned-001",
            prev_entry_hash="NOT-A-HASH",
        )


def test_builder_source_is_pure_and_does_not_import_the_writer() -> None:
    source_path = Path(__file__).parents[1] / "app" / "phase9_burn_evidence.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    import_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    calls = {
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else node.func.id
        if isinstance(node.func, ast.Name)
        else ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }

    assert "app.audit_writer_local" not in imports | import_from_modules
    assert not {"open", "write_text", "write_bytes", "mkdir", "unlink"} & calls
