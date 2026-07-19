"""Branch coverage for the two alphabetically first zero-coverage app modules.

These legacy helpers are pure decision functions.  Tests assert their existing
fail-closed and observation-only behavior; they do not wire approval, queue, or
execution paths.
"""

from __future__ import annotations

import copy
import json

import pytest

from app import approval_security_gate_v0_7 as approval_gate
from app import auto_approval_policy_v0_7 as auto_policy


SAFE_POLICY = {
    "auto_approval_mode": "safe",
    "safe_autopilot_enabled": True,
    "low_risk_auto_approval_enabled": True,
    "auto_approval_policy": "safe",
}


def _approval_row(
    *,
    status: str = "waiting_review",
    payload: object | None = None,
) -> dict[str, object]:
    if payload is None:
        payload = {
            "allowed_tools": ["filesystem.read"],
            "denied_tools": [],
            "metadata": {
                "requested_tools": ["filesystem.read"],
                "local_only": False,
                "mock": False,
                "executable_by_worker": True,
            },
        }
    return {
        "task_id": "task-legacy",
        "correlation_id": "corr-legacy",
        "status": status,
        "payload": payload,
    }


def _evaluate_approval(row: object, **overrides: bool) -> dict[str, object]:
    return approval_gate.evaluate_approval_to_queued(
        row,  # type: ignore[arg-type]
        approval_security_gates_enabled=True,
        **overrides,
    )


def _policy_row(**values: object) -> dict[str, object]:
    metadata_keys = {
        "task_type",
        "safety_level",
        "requested_tools",
        "requested_operations",
        "touched_files",
        "requires_confirmation",
    }
    metadata = {key: value for key, value in values.items() if key in metadata_keys}
    payload: dict[str, object] = {"metadata": metadata}
    for key in ("allowed_tools", "denied_tools"):
        if key in values:
            payload[key] = values[key]
    return {
        "task_id": "task-policy",
        "correlation_id": "corr-policy",
        "status": "waiting_review",
        "payload": payload,
    }


def _evaluate_policy(row: object, **overrides: object) -> dict[str, object]:
    options = {**SAFE_POLICY, **overrides}
    return auto_policy.evaluate_auto_approval(row, **options)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"metadata": {}}, {"metadata": {}}),
        ('{"metadata": {}}', {"metadata": {}}),
        ("[]", None),
        ("{broken", None),
        (7, None),
    ],
)
def test_approval_payload_extraction_variants(payload, expected) -> None:
    assert approval_gate.extract_payload({"payload": payload}) == expected


def test_approval_metadata_and_requested_tools_fail_closed() -> None:
    assert approval_gate.extract_metadata({"payload": None}) == {}
    assert approval_gate.extract_metadata({"payload": {"metadata": "bad"}}) == {}
    row = {"payload": {"metadata": {"requested_tools": ["read"]}}}
    assert approval_gate.extract_metadata(row) == {"requested_tools": ["read"]}
    assert approval_gate.extract_requested_tools(row) == ["read"]


def test_approval_disabled_and_non_dict_decisions_are_observation_only() -> None:
    row = _approval_row()
    disabled = approval_gate.evaluate_approval_to_queued(row)
    rejected = approval_gate.evaluate_approval_to_queued("not-a-row")  # type: ignore[arg-type]

    assert disabled["allowed"] is True
    assert disabled["reason"] == "approval_security_gates_disabled"
    assert disabled["audit_event"]["observation_only"] is True
    assert rejected == {
        "allowed": False,
        "decision": "reject",
        "reason": "task_row_not_dict",
        "priority": "approval_gate",
    }


@pytest.mark.parametrize(
    ("row", "overrides", "reason", "priority"),
    [
        (_approval_row(), {"global_kill_switch": True}, "global_kill_switch_active", "global_kill_switch"),
        (_approval_row(), {"layer_kill_switch": True}, "layer_kill_switch_active", "layer_kill_switch"),
        (_approval_row(status="completed"), {}, "not_in_review_status", "approval_gate"),
        (_approval_row(payload="{bad"), {}, "payload_missing_or_invalid", "approval_gate"),
        (
            _approval_row(
                payload={
                    "allowed_tools": ["read"],
                    "metadata": {
                        "requested_tools": ["read"],
                        "local_only": True,
                        "mock": False,
                        "executable_by_worker": True,
                    },
                }
            ),
            {},
            "local_only_not_approvable",
            "approval_gate",
        ),
        (
            _approval_row(
                payload={
                    "allowed_tools": ["read"],
                    "metadata": {
                        "requested_tools": ["read"],
                        "local_only": False,
                        "mock": True,
                        "executable_by_worker": True,
                    },
                }
            ),
            {},
            "mock_not_approvable",
            "approval_gate",
        ),
        (
            _approval_row(
                payload={
                    "allowed_tools": ["read"],
                    "metadata": {
                        "requested_tools": ["read"],
                        "local_only": False,
                        "mock": False,
                    },
                }
            ),
            {},
            "executable_by_worker_not_true",
            "approval_gate",
        ),
    ],
)
def test_approval_gate_rejection_precedence(row, overrides, reason, priority) -> None:
    result = _evaluate_approval(row, **overrides)

    assert result["allowed"] is False
    assert result["reason"] == reason
    assert result["priority"] == priority
    assert result["audit_event"]["observation_only"] is True


@pytest.mark.parametrize(
    "payload",
    [
        {
            "allowed_tools": ["read"],
            "metadata": {
                "local_only": False,
                "mock": False,
                "executable_by_worker": True,
            },
        },
        {
            "allowed_tools": [],
            "metadata": {
                "requested_tools": ["read"],
                "local_only": False,
                "mock": False,
                "executable_by_worker": True,
            },
        },
        {
            "allowed_tools": ["read"],
            "denied_tools": ["read"],
            "metadata": {
                "requested_tools": ["read"],
                "local_only": False,
                "mock": False,
                "executable_by_worker": True,
            },
        },
    ],
)
def test_approval_tool_gate_rejections_are_structured(payload) -> None:
    result = _evaluate_approval(_approval_row(payload=payload))

    assert result["reason"] == "tool_gate_rejected"
    assert result["security_gate"]["allowed"] is False


def test_approval_success_accepts_json_and_does_not_mutate() -> None:
    row = _approval_row()
    row["payload"] = json.dumps(row["payload"])
    snapshot = copy.deepcopy(row)

    result = _evaluate_approval(row)

    assert result["allowed"] is True
    assert result["reason"] == "approval_allowed"
    assert result["security_gate"]["allowed"] is True
    assert result["audit_event"]["action"] == "approval.security_gate"
    assert row == snapshot


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (" YES ", True),
        ("n", False),
        ("unknown", None),
        (1, None),
    ],
)
def test_auto_policy_bool_coercion(value, expected) -> None:
    assert auto_policy._coerce_bool(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(False, None), (1, 1), (" -2 ", -2), ("1.0", None), (None, None)],
)
def test_auto_policy_safety_level_parsing(value, expected) -> None:
    assert auto_policy._parse_safety_level({"safety_level": value}) == expected


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (None, False),
        ("", False),
        ("./app/main.py", True),
        ("templates/review.html", True),
        ("app/hermes_client.py", True),
        ("docs/hermes_notes.md", False),
        ("src/free.py", False),
    ],
)
def test_auto_policy_protected_path_rules(path, expected) -> None:
    assert auto_policy._is_protected_file(path) is expected


def test_auto_policy_string_list_parser() -> None:
    value = ["one", "two"]
    assert auto_policy._as_str_list(value) is value
    assert auto_policy._as_str_list(["one", 2]) is None
    assert auto_policy._as_str_list("one") is None


@pytest.mark.parametrize(
    ("overrides", "decision", "reason"),
    [
        ({"global_kill_switch": True}, "rejected", "global_kill_switch_active"),
        ({"auto_approval_kill_switch": True}, "rejected", "auto_approval_kill_switch_active"),
        ({"auto_approval_mode": "off"}, "needs_owner_approval", "auto_approval_mode_off"),
        ({"auto_approval_mode": "unknown"}, "needs_owner_approval", "unsupported_auto_approval_mode"),
        ({"auto_approval_policy": "loose"}, "needs_owner_approval", "unsupported_auto_approval_policy"),
        ({"safe_autopilot_enabled": False}, "needs_owner_approval", "safe_autopilot_disabled"),
        ({"low_risk_auto_approval_enabled": False}, "needs_owner_approval", "low_risk_auto_approval_disabled"),
    ],
)
def test_auto_policy_control_precedence(overrides, decision, reason) -> None:
    row = _policy_row(
        task_type="test",
        safety_level=0,
        requested_tools=["run_tests"],
        allowed_tools=["run_tests"],
    )

    result = _evaluate_policy(row, **overrides)

    assert result["policy_decision"] == decision
    assert result["reason"] == reason
    assert result["can_execute"] is False
    assert result["queue_transition_allowed"] is False
    assert result["observation_only"] is True


def test_auto_policy_invalid_row_and_payload_fail_closed() -> None:
    invalid_row = _evaluate_policy("not-a-row")
    invalid_payload = _evaluate_policy({"task_id": "x", "payload": "bad"})

    assert invalid_row["reason"] == "task_row_not_dict"
    assert invalid_payload["reason"] == "payload_missing_or_invalid"


@pytest.mark.parametrize(
    ("changes", "decision", "reason", "level"),
    [
        ({"requested_operations": "bad"}, "needs_owner_approval", "invalid_requested_operations", None),
        ({"requested_operations": ["git_push"]}, "prohibited", "forbidden_operation", 3),
        ({"touched_files": "bad"}, "needs_owner_approval", "invalid_touched_files", None),
        ({"touched_files": ["app/main.py"]}, "needs_owner_approval", "protected_file_touched", 2),
        ({"denied_tools": ["run_tests"]}, "prohibited", "denied_tool_matched", 3),
        ({"task_type": "deploy"}, "needs_owner_approval", "task_type_not_in_safe_allowlist", 2),
        ({"requested_tools": []}, "needs_owner_approval", "requested_tools_empty", None),
        ({"requested_tools": ["shell"] , "allowed_tools": ["shell"]}, "needs_owner_approval", "requested_tool_not_in_safe_allowlist", None),
        ({"allowed_tools": []}, "needs_owner_approval", "tool_gate_allowed_tools_empty", None),
        ({"safety_level": None}, "needs_owner_approval", "missing_or_invalid_safety_level", None),
        ({"safety_level": 2}, "needs_owner_approval", "safety_level_too_high", None),
        ({"requires_confirmation": True}, "needs_owner_approval", "requires_confirmation", None),
    ],
)
def test_auto_policy_fail_closed_matrix(changes, decision, reason, level) -> None:
    values = {
        "task_type": "test",
        "safety_level": 0,
        "requested_tools": ["run_tests"],
        "allowed_tools": ["run_tests"],
        **changes,
    }

    result = _evaluate_policy(_policy_row(**values))

    assert result["policy_decision"] == decision
    assert result["reason"] == reason
    assert result["matched_level"] == level
    assert result["audit_event"]["observation_only"] is True


@pytest.mark.parametrize(
    ("task_type", "safety_level", "tool", "level"),
    [
        ("test", 0, "run_tests", 0),
        ("compile", "0", "compile", 0),
        ("read_only_query", 0, "search", 0),
        ("docs_only", 1, "read_file", 1),
        ("pure_helper_local", 1, "grep", 1),
    ],
)
def test_auto_policy_safe_results_never_authorize_execution(
    task_type, safety_level, tool, level
) -> None:
    row = _policy_row(
        task_type=task_type,
        safety_level=safety_level,
        requested_tools=[tool],
        allowed_tools=[tool],
    )
    snapshot = copy.deepcopy(row)

    result = _evaluate_policy(row)

    assert result["policy_decision"] == "auto_approved"
    assert result["matched_level"] == level
    assert result["can_auto_approve"] is True
    assert result["can_execute"] is False
    assert result["queue_transition_allowed"] is False
    assert result["audit_event"]["observation_only"] is True
    assert row == snapshot
