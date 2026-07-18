from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

import pytest

import app.approval_packet_builder as builder_module
from app.approval_packet_builder import (
    DECISION_VERBS,
    ApprovalPacketBuildError,
    build_approval_packet,
    build_dashboard_approval_packet_preview,
)
from app.blackboard_validators import validate_blackboard_message


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"


def load_fixture(message_type: str, case: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{message_type}.{case}.json"
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, dict)
    return data


def test_approval_packet_positive_fixture_is_valid() -> None:
    packet = load_fixture("approval_packet", "valid")

    assert validate_blackboard_message(packet) == {
        "valid": True,
        "message_type": "approval_packet",
        "schema_file": "approval_packet.schema.json",
        "errors": [],
    }
    assert packet["single_use_execution_token"] is None
    assert packet["expected_side_effects"] == []


@pytest.mark.parametrize(
    "case,validator,path",
    (
        ("invalid_missing_common", "required", "$"),
        ("invalid_extra_safety_flag", "additionalProperties", "$.safety_flags"),
    ),
)
def test_approval_packet_negative_fixtures_are_rejected(
    case: str, validator: str, path: str
) -> None:
    result = validate_blackboard_message(load_fixture("approval_packet", case))

    assert result["valid"] is False
    assert any(
        error["validator"] == validator and error["path"] == path
        for error in result["errors"]
    )


def test_non_null_execution_token_is_rejected() -> None:
    packet = load_fixture("approval_packet", "valid")
    packet["single_use_execution_token"] = "phase-9-token-must-not-exist"

    result = validate_blackboard_message(packet)

    assert result["valid"] is False
    assert any(
        error["path"] == "$.single_use_execution_token"
        and error["validator"] in {"const", "type"}
        for error in result["errors"]
    )


def test_builder_reproduces_valid_fixture_without_mutating_sources() -> None:
    worker_dry_run = load_fixture("worker_dry_run", "valid")
    result_message = load_fixture("result_message", "valid")
    worker_before = copy.deepcopy(worker_dry_run)
    result_before = copy.deepcopy(result_message)

    packet = build_approval_packet(
        worker_dry_run,
        result_message,
        decision="approve",
        approval_timestamp="2026-07-18T10:07:00Z",
        prev_entry_hash="1" * 64,
    )

    assert packet == load_fixture("approval_packet", "valid")
    assert worker_dry_run == worker_before
    assert result_message == result_before


@pytest.mark.parametrize("decision", DECISION_VERBS)
def test_builder_supports_only_inert_phase4_decision_verbs(decision: str) -> None:
    packet = build_approval_packet(
        load_fixture("worker_dry_run", "valid"),
        load_fixture("result_message", "valid"),
        decision=decision,
    )

    assert packet["decision"] == decision
    assert packet["single_use_execution_token"] is None
    assert packet["safety_flags"]["worker_dispatch_allowed"] is False
    assert packet["safety_flags"]["external_side_effects_allowed"] is False


def test_builder_fails_closed_on_mismatched_or_executed_evidence() -> None:
    worker_dry_run = load_fixture("worker_dry_run", "valid")
    result_message = load_fixture("result_message", "valid")
    result_message["related_dry_run_id"] = "different-dry-run"

    with pytest.raises(ApprovalPacketBuildError, match="source dry_run_id"):
        build_approval_packet(worker_dry_run, result_message)

    result_message = load_fixture("result_message", "valid")
    result_message["external_side_effects"] = ["unexpected write"]
    with pytest.raises(ApprovalPacketBuildError, match="no external side effects"):
        build_approval_packet(worker_dry_run, result_message)


def test_dashboard_preview_is_schema_valid_and_pending() -> None:
    packet = build_dashboard_approval_packet_preview()

    assert validate_blackboard_message(packet)["valid"] is True
    assert packet["decision"] == "respond"
    assert packet["approval_timestamp"] is None
    assert packet["single_use_execution_token"] is None


def test_approve_packet_has_no_path_to_dispatch_or_execution() -> None:
    source = Path(builder_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    assert imported_roots <= {"__future__", "typing"}

    forbidden_call_fragments = {
        "dispatch",
        "execute",
        "enqueue",
        "dequeue",
        "run_worker",
        "openclaw",
        "subprocess",
        "request",
        "write",
        "send",
        "post",
        "put",
        "delete",
        "commit",
    }
    call_names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            call_names.append(node.func.id.lower())
        elif isinstance(node.func, ast.Attribute):
            call_names.append(node.func.attr.lower())
    assert not {
        name
        for name in call_names
        if any(fragment in name for fragment in forbidden_call_fragments)
    }

    approved_packet = build_approval_packet(
        load_fixture("worker_dry_run", "valid"),
        load_fixture("result_message", "valid"),
        decision="approve",
        approval_timestamp="2026-07-18T10:07:00Z",
    )
    assert approved_packet["decision"] == "approve"
    assert approved_packet["single_use_execution_token"] is None
    assert approved_packet["safety_flags"]["worker_dispatch_allowed"] is False


def test_dashboard_integration_is_existing_get_only_display_without_controls() -> None:
    main_tree = ast.parse((ROOT / "app" / "main.py").read_text(encoding="utf-8"))
    review_function = next(
        node
        for node in main_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "dashboard_reviews"
    )
    assert any(
        isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr == "get"
        and decorator.args
        and isinstance(decorator.args[0], ast.Constant)
        and decorator.args[0].value == "/dashboard/reviews"
        for decorator in review_function.decorator_list
    )
    assert sum(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "build_dashboard_approval_packet_preview"
        for node in ast.walk(review_function)
    ) == 1

    partial = (ROOT / "templates" / "approval_packet.html").read_text(
        encoding="utf-8"
    )
    assert "single_use_execution_token" in partial
    assert "<form" not in partial
    assert "<button" not in partial
    assert 'method="post"' not in partial.lower()
