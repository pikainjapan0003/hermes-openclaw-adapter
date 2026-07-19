"""Deterministic systematic bad-input fuzzing for the three contract builders."""

from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import (
    ApprovalPacketBuildError,
    build_approval_packet,
)
from app.evidence_bundle_builder import (
    EvidenceBundleError,
    build_evidence_bundle,
    compute_bundle_hash,
    verify_bundle_hash,
)
from app.rollback_preview_builder import (
    RollbackPreviewBuildError,
    build_rollback_preview,
)
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


SEED = 20260721
ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE = ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _set(record: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    target = record
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = value


def _delete(record: dict[str, Any], path: tuple[str, ...]) -> None:
    target = record
    for component in path[:-1]:
        target = target[component]
    del target[path[-1]]


def _approval_sources() -> dict[str, Any]:
    return {
        "worker": _load(BLACKBOARD / "worker_dry_run.valid.json"),
        "result": _load(BLACKBOARD / "result_message.valid.json"),
        "kwargs": {
            "decision": "respond",
            "approval_timestamp": None,
            "prev_entry_hash": None,
        },
    }


def _approval_cases() -> list[tuple[str, str, tuple[str, ...], Any]]:
    cases: list[tuple[str, str, tuple[str, ...], Any]] = [
        ("set", "worker", (), []),
        ("set", "result", (), "not-an-object"),
        ("delete", "worker", ("message_type",), None),
        ("set", "worker", ("message_type",), "result_message"),
        ("delete", "result", ("message_type",), None),
        ("set", "result", ("message_type",), "worker_dry_run"),
        ("set", "kwargs", ("decision",), "execute"),
        ("set", "kwargs", ("decision",), None),
        ("set", "kwargs", ("approval_timestamp",), ""),
        ("set", "kwargs", ("approval_timestamp",), 7),
        ("set", "kwargs", ("prev_entry_hash",), "0" * 63),
        ("set", "kwargs", ("prev_entry_hash",), "G" * 64),
        ("set", "worker", ("safety_flags",), []),
        ("set", "result", ("safety_flags",), []),
        ("delete", "worker", ("schema_version",), None),
        ("set", "worker", ("schema_version",), 1),
        ("set", "result", ("schema_version",), "2.0"),
        ("set", "worker", ("execution_class",), "OWNER_APPROVAL"),
        ("set", "result", ("execution_class",), "OWNER_APPROVAL"),
        ("delete", "worker", ("task_id",), None),
        ("set", "worker", ("task_id",), 1),
        ("set", "result", ("task_id",), "task-unrelated"),
        ("delete", "worker", ("dry_run_id",), None),
        ("set", "worker", ("dry_run_id",), 1),
        ("set", "result", ("related_dry_run_id",), "dryrun-unrelated"),
        ("set", "result", ("parent_task_id",), "parent-unrelated"),
        ("set", "worker", ("preview_only",), False),
        ("set", "worker", ("dry_run_status",), "executed"),
        ("set", "worker", ("permissions",), []),
        ("set", "worker", ("runtime_state",), []),
        ("set", "result", ("result_status",), "completed"),
        ("set", "result", ("execution_mode",), "real"),
        ("set", "result", ("external_side_effects",), ["write"]),
        ("delete", "result", ("result_id",), None),
        ("set", "result", ("command_id",), None),
        ("set", "worker", ("proposed_worker_action",), ""),
        ("delete", "result", ("created_at",), None),
        ("set", "result", ("rollback_note",), 1),
        ("set", "result", ("audit_note",), ""),
    ]
    sources = _approval_sources()
    for owner in ("worker", "result"):
        for flag in sources[owner]["safety_flags"]:
            cases.append(("set", owner, ("safety_flags", flag), not sources[owner]["safety_flags"][flag]))
        cases.append(("set", owner, ("safety_flags", "extra_flag"), False))
    for field in sources["worker"]["permissions"]:
        cases.append(("set", "worker", ("permissions", field), True))
        cases.append(("delete", "worker", ("permissions", field), None))
    cases.append(("set", "worker", ("permissions", "extra_permission"), False))
    for field in sources["worker"]["runtime_state"]:
        cases.append(("set", "worker", ("runtime_state", field), True))
        cases.append(("delete", "worker", ("runtime_state", field), None))
    cases.append(("set", "worker", ("runtime_state", "extra_state"), False))
    return cases


def _apply_case(container: dict[str, Any], case: tuple[str, str, tuple[str, ...], Any]) -> None:
    operation, owner, path, value = case
    if not path:
        container[owner] = value
    elif operation == "set":
        _set(container[owner], path, value)
    else:
        _delete(container[owner], path)


def test_approval_packet_builder_rejects_systematic_bad_inputs_without_output() -> None:
    cases = _approval_cases()
    assert len(cases) >= 50
    random.Random(SEED).shuffle(cases)

    for case in cases:
        sources = _approval_sources()
        _apply_case(sources, case)
        output = None
        with pytest.raises(ApprovalPacketBuildError):
            output = build_approval_packet(
                sources["worker"], sources["result"], **sources["kwargs"]
            )
        assert output is None, case


def _evidence_sources() -> dict[str, Any]:
    task = _load(BLACKBOARD / "task_draft.valid.json")
    command = {
        "command_id": "cmd-fuzz-001",
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
    return {
        "task": task,
        "command": command,
        "mock": run_worker_to_mock_gateway_dry_run(command),
        "expected": [],
        "created_at": "2026-07-21T00:00:00Z",
    }


def _evidence_cases() -> list[tuple[str, str, tuple[str, ...], Any]]:
    cases: list[tuple[str, str, tuple[str, ...], Any]] = [
        ("set", "task", (), []),
        ("set", "command", (), []),
        ("set", "mock", (), []),
        ("set", "expected", (), "none"),
        ("set", "expected", (), ["write"]),
        ("set", "created_at", (), ""),
        ("set", "created_at", (), None),
        ("delete", "task", ("task_id",), None),
        ("set", "task", ("task_id",), 1),
        ("set", "task", ("task_type",), "code"),
        ("set", "task", ("target_runtime",), "openclaw"),
        ("set", "task", ("execution_class",), "OWNER_APPROVAL"),
        ("set", "task", ("title",), ""),
        ("set", "task", ("summary",), None),
        ("delete", "command", ("command_id",), None),
        ("set", "command", ("command_id",), 1),
        ("set", "command", ("task_id",), "task-unrelated"),
        ("set", "command", ("risk_level",), "high"),
        ("set", "command", ("execution_mode",), "real"),
        ("set", "command", ("dry_run",), False),
        ("set", "command", ("mock_only",), False),
        ("set", "command", ("external_touchpoints",), ["remote"]),
        ("set", "command", ("external_side_effects_allowed",), True),
        ("set", "command", ("tool_target",), ""),
        ("set", "command", ("requested_action",), None),
        ("set", "command", ("rollback_plan",), ""),
        ("set", "command", ("approval_snapshot",), []),
        ("set", "command", ("approval_snapshot", "owner_review_required"), False),
        ("set", "mock", ("gateway_response",), []),
        ("set", "mock", ("source",), "external"),
        ("set", "mock", ("accepted",), False),
        ("set", "mock", ("worker_dry_run",), False),
        ("set", "mock", ("mock_gateway_called",), False),
        ("set", "mock", ("gateway_response", "response_source"), "external"),
        ("set", "mock", ("gateway_response", "accepted"), False),
        ("set", "mock", ("gateway_response", "mock_gateway"), False),
        ("set", "mock", ("gateway_response", "task_id"), "task-unrelated"),
        ("set", "mock", ("gateway_response", "command_id"), "command-unrelated"),
        ("set", "mock", ("gateway_response", "tool_target"), "different.target"),
        ("set", "mock", ("gateway_response", "mock_response_summary"), ""),
    ]
    sources = _evidence_sources()
    for field in (
        "worker_loop_started",
        "worker_dispatched",
        "real_openclaw_called",
        "external_side_effects_performed",
        "queue_written",
        "audit_trail_written",
    ):
        cases.append(("set", "mock", (field,), True))
        cases.append(("delete", "mock", (field,), None))
    for field in (
        "production_gateway",
        "real_openclaw_called",
        "worker_dispatched",
        "external_side_effects_performed",
        "queue_written",
        "audit_trail_written",
    ):
        cases.append(("set", "mock", ("gateway_response", field), True))
        cases.append(("delete", "mock", ("gateway_response", field), None))
    for owner, path in (
        ("task", ("api_token",)),
        ("task", ("workspace_path",)),
        ("command", ("secret",)),
        ("command", ("environment",)),
        ("mock", ("private_key",)),
        ("mock", ("gateway_response", "credential")),
    ):
        cases.append(("set", owner, path, "redacted-but-forbidden-field"))
    assert sources["mock"]["accepted"] is True
    return cases


def test_evidence_bundle_builder_rejects_systematic_bad_inputs_without_output() -> None:
    cases = _evidence_cases()
    assert len(cases) >= 50
    random.Random(SEED).shuffle(cases)

    for case in cases:
        sources = _evidence_sources()
        _apply_case(sources, case)
        output = None
        with pytest.raises(EvidenceBundleError):
            output = build_evidence_bundle(
                sources["task"],
                sources["command"],
                sources["mock"],
                sources["expected"],
                created_at=sources["created_at"],
            )
        assert output is None, case


def _rollback_sources() -> dict[str, Any]:
    return {
        "audit": _load(BLACKBOARD / "audit_event.valid.json"),
        "bundle": _load(EVIDENCE),
        "result": _load(BLACKBOARD / "result_message.valid.json"),
    }


def _rollback_cases() -> list[tuple[str, str, tuple[str, ...], Any, bool]]:
    cases: list[tuple[str, str, tuple[str, ...], Any, bool]] = [
        ("set", "audit", (), [], False),
        ("set", "bundle", (), [], False),
        ("set", "result", (), [], False),
        ("delete", "audit", ("message_type",), None, False),
        ("set", "audit", ("message_type",), "result_message", False),
        ("set", "bundle", ("bundle_type",), "wrong", True),
        ("set", "result", ("message_type",), "audit_event", False),
        ("set", "audit", ("preview_only",), False, False),
        ("set", "audit", ("audit_status",), "persisted", False),
        ("set", "audit", ("persistence_target",), "file", False),
        ("set", "bundle", ("bundle_hash",), "0" * 64, False),
        ("delete", "bundle", ("bundle_hash",), None, False),
        ("set", "bundle", ("task",), [], True),
        ("set", "bundle", ("mock_result",), [], True),
        ("set", "bundle", ("expected_side_effects",), ["write"], True),
        ("set", "result", ("result_status",), "completed", False),
        ("set", "result", ("execution_mode",), "real", False),
        ("set", "result", ("external_side_effects",), ["write"], False),
        ("set", "audit", ("safety_flags",), [], False),
        ("set", "result", ("safety_flags",), [], False),
        ("set", "result", ("schema_version",), "2.0", False),
        ("set", "audit", ("execution_class",), "OWNER_APPROVAL", False),
        ("set", "result", ("execution_class",), "OWNER_APPROVAL", False),
        ("set", "bundle", ("task", "execution_class"), "OWNER_APPROVAL", True),
        ("set", "audit", ("parent_task_id",), "", False),
        ("set", "result", ("parent_task_id",), "parent-unrelated", False),
        ("delete", "audit", ("task_id",), None, False),
        ("set", "audit", ("task_id",), 1, False),
        ("set", "result", ("task_id",), "task-unrelated", False),
        ("set", "bundle", ("task", "task_id"), "task-unrelated", True),
        ("delete", "audit", ("related_result_id",), None, False),
        ("set", "result", ("result_id",), "result-unrelated", False),
        ("delete", "audit", ("audit_id",), None, False),
        ("set", "audit", ("audit_id",), "", False),
        ("delete", "audit", ("created_at",), None, False),
        ("set", "audit", ("created_at",), 1, False),
        ("set", "bundle", ("unexpected_extra",), True, False),
    ]
    sources = _rollback_sources()
    for owner in ("audit", "result"):
        for field in sources[owner]["safety_flags"]:
            cases.append(
                (
                    "set",
                    owner,
                    ("safety_flags", field),
                    not sources[owner]["safety_flags"][field],
                    False,
                )
            )
        cases.append(("set", owner, ("safety_flags", "extra_flag"), False, False))
    for field in (
        "external_side_effects_performed",
        "worker_dispatched",
        "real_openclaw_called",
        "queue_written",
        "audit_trail_written",
    ):
        cases.append(("set", "bundle", ("mock_result", field), True, True))
        cases.append(("delete", "bundle", ("mock_result", field), None, True))
    return cases


def test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output() -> None:
    cases = _rollback_cases()
    assert len(cases) >= 50
    random.Random(SEED).shuffle(cases)

    for operation, owner, path, value, rehash in cases:
        sources = _rollback_sources()
        _apply_case(sources, (operation, owner, path, value))
        if rehash and isinstance(sources["bundle"], dict):
            sources["bundle"]["bundle_hash"] = compute_bundle_hash(sources["bundle"])
        output = None
        with pytest.raises(RollbackPreviewBuildError):
            output = build_rollback_preview(
                sources["audit"], sources["bundle"], sources["result"]
            )
        assert output is None, (operation, owner, path)


def test_normal_builder_inputs_remain_valid_and_unmodified() -> None:
    approval = _approval_sources()
    approval_before = deepcopy(approval)
    packet = build_approval_packet(
        approval["worker"], approval["result"], **approval["kwargs"]
    )
    assert approval == approval_before
    assert packet["single_use_execution_token"] is None

    evidence = _evidence_sources()
    evidence_before = deepcopy(evidence)
    bundle = build_evidence_bundle(
        evidence["task"],
        evidence["command"],
        evidence["mock"],
        evidence["expected"],
        created_at=evidence["created_at"],
    )
    assert evidence == evidence_before
    assert verify_bundle_hash(bundle) is True

    rollback = _rollback_sources()
    rollback_before = deepcopy(rollback)
    preview = build_rollback_preview(
        rollback["audit"], rollback["bundle"], rollback["result"]
    )
    assert rollback == rollback_before
    assert preview["preview_only"] is True
