"""Phase 9 preflight checklist rehearsal with no unlock or execution path."""

from __future__ import annotations

import ast
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import verify_bundle_hash


ROOT = Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "docs" / "agent_operating_system" / "09_N1_PREFLIGHT_RUNBOOK.md"
APPROVAL_SCHEMA = (
    ROOT / "docs" / "schemas" / "blackboard" / "approval_packet.schema.json"
)
AUDIT_WRITER = ROOT / "app" / "audit_writer_local.py"
EXECUTION_GATE = ROOT / "app" / "n1_execution_gate.py"
BLOCKER_NAMES = (
    "token_schema_allows_live_token",
    "packet_contains_live_token",
    "phase7_writer_exists",
    "phase9_gate_exists",
    "owner_synchronously_present",
    "fresh_owner_token_supplied",
    "runtime_rehearsal_authorized",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    disposition: str


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def evaluate_preflight() -> list[Check]:
    """Evaluate current static inputs; this function cannot change any state."""

    approval = _load(
        ROOT / "fixtures" / "blackboard_contract" / "approval_packet.valid.json"
    )
    evidence = _load(
        ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
    )
    token_schema = _load(APPROVAL_SCHEMA)["properties"][
        "single_use_execution_token"
    ]
    packet_validation = validate_blackboard_message(approval)

    return [
        Check("blackboard_contract", packet_validation["valid"], "READY"),
        Check("approval_exact_target", bool(approval.get("exact_target")), "READY"),
        Check("dry_run_result_refs", all(approval["dry_run_evidence"].values()), "READY"),
        Check("evidence_hash", verify_bundle_hash(evidence), "READY"),
        Check("expected_side_effects_empty", evidence["expected_side_effects"] == [], "READY"),
        Check("token_schema_allows_live_token", token_schema.get("const") is not None, "BLOCK"),
        Check("packet_contains_live_token", approval["single_use_execution_token"] is not None, "BLOCK"),
        Check("phase7_writer_exists", AUDIT_WRITER.is_file(), "BLOCK"),
        Check("phase9_gate_exists", EXECUTION_GATE.is_file(), "BLOCK"),
        Check("owner_synchronously_present", False, "BLOCK"),
        Check("fresh_owner_token_supplied", False, "BLOCK"),
        Check("runtime_rehearsal_authorized", False, "BLOCK"),
    ]


def render_preflight_report(checks: list[Check]) -> str:
    lines = ["Phase 9 N=1 preflight (read-only)", "name | result | disposition"]
    for check in checks:
        result = "PASS" if check.passed else "FAIL"
        lines.append(f"{check.name} | {result} | {check.disposition}")
    lines.append("FINAL | BLOCKED" if any(not item.passed for item in checks) else "FINAL | READY")
    return "\n".join(lines)


def test_current_preflight_runs_every_check_and_fails_closed(capsys) -> None:
    checks = evaluate_preflight()
    report = render_preflight_report(checks)
    print(report)

    assert len(checks) == 12
    assert [item.name for item in checks] == [
        "blackboard_contract",
        "approval_exact_target",
        "dry_run_result_refs",
        "evidence_hash",
        "expected_side_effects_empty",
        "token_schema_allows_live_token",
        "packet_contains_live_token",
        "phase7_writer_exists",
        "phase9_gate_exists",
        "owner_synchronously_present",
        "fresh_owner_token_supplied",
        "runtime_rehearsal_authorized",
    ]
    assert all(item.passed for item in checks[:5])
    assert all(
        (item.passed if item.name == "phase7_writer_exists" else not item.passed)
        and item.disposition == "BLOCK"
        for item in checks[5:]
    )
    assert report.endswith("FINAL | BLOCKED")
    assert "token_schema_allows_live_token | FAIL | BLOCK" in report
    assert "phase7_writer_exists | PASS | BLOCK" in report
    assert "owner_synchronously_present | FAIL | BLOCK" in report
    assert "FINAL | READY" not in report
    assert "Phase 9 N=1 preflight" in capsys.readouterr().out


def test_runbook_sequence_is_complete_but_never_entered() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    for number in range(1, 11):
        assert f"{number}. **" in text
    report = render_preflight_report(evaluate_preflight())
    assert "FINAL | BLOCKED" in report
    assert "ALLOW exactly one approved query attempt" in text


@pytest.mark.parametrize("satisfied_blocker", BLOCKER_NAMES)
def test_one_hypothetically_satisfied_blocker_still_cannot_make_ready(
    satisfied_blocker: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A test-only single-condition change cannot bypass the all-of gate."""

    current = evaluate_preflight()
    simulated = [
        replace(check, passed=True)
        if check.name == satisfied_blocker
        else check
        for check in current
    ]
    monkeypatch.setattr(
        sys.modules[__name__],
        "evaluate_preflight",
        lambda: simulated,
    )

    report = render_preflight_report(evaluate_preflight())
    assert f"{satisfied_blocker} | PASS | BLOCK" in report
    assert report.endswith("FINAL | BLOCKED")
    assert "FINAL | READY" not in report
    assert any(
        not check.passed
        for check in simulated
        if check.name in BLOCKER_NAMES and check.name != satisfied_blocker
    )


def test_only_test_memory_can_render_the_all_conditions_true_counterfactual(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prove AND semantics without creating a repository path that can unlock it."""

    current = evaluate_preflight()
    assert render_preflight_report(current).endswith("FINAL | BLOCKED")
    assert all(
        not check.passed
        for check in current
        if check.name in BLOCKER_NAMES and check.name != "phase7_writer_exists"
    )

    counterfactual = [replace(check, passed=True) for check in current]
    monkeypatch.setattr(
        sys.modules[__name__],
        "evaluate_preflight",
        lambda: counterfactual,
    )
    assert render_preflight_report(evaluate_preflight()).endswith("FINAL | READY")

    monkeypatch.undo()
    restored = evaluate_preflight()
    assert render_preflight_report(restored).endswith("FINAL | BLOCKED")
    assert all(
        not check.passed
        for check in restored
        if check.name in BLOCKER_NAMES and check.name != "phase7_writer_exists"
    )


def test_every_non_green_condition_combination_is_blocked() -> None:
    """Exhaust the 2^N truth table entirely inside test memory."""

    baseline = evaluate_preflight()
    condition_count = len(baseline)
    all_green_mask = (1 << condition_count) - 1
    blocked_combinations = 0

    for mask in range(all_green_mask):
        simulated = [
            replace(check, passed=bool(mask & (1 << index)))
            for index, check in enumerate(baseline)
        ]
        report = render_preflight_report(simulated)
        assert report.endswith("FINAL | BLOCKED"), mask
        assert "FINAL | READY" not in report
        blocked_combinations += 1

    all_green = [replace(check, passed=True) for check in baseline]
    assert render_preflight_report(all_green).endswith("FINAL | READY")
    assert condition_count == 12
    assert blocked_combinations == (2**condition_count) - 1 == 4095


def test_preflight_test_contains_no_unlock_or_execution_calls() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    forbidden_names = {
        "claim_next",
        "dispatch",
        "execute",
        "open",
        "run_openclaw_cli",
        "send",
        "write",
        "write_text",
    }
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = (
            node.func.attr
            if isinstance(node.func, ast.Attribute)
            else node.func.id
            if isinstance(node.func, ast.Name)
            else ""
        )
        if name in forbidden_names:
            calls.append((node.lineno, name))
    assert calls == []
