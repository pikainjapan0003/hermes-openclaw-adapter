"""Phase 9 preflight checklist rehearsal with no unlock or execution path."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import verify_bundle_hash


ROOT = Path(__file__).resolve().parent.parent
RUNBOOK = ROOT / "docs" / "agent_operating_system" / "09_N1_PREFLIGHT_RUNBOOK.md"
APPROVAL_SCHEMA = (
    ROOT / "docs" / "schemas" / "blackboard" / "approval_packet.schema.json"
)
AUDIT_WRITER = ROOT / "app" / "audit_writer_local.py"
EXECUTION_GATE = ROOT / "app" / "n1_execution_gate.py"


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
    assert all(not item.passed and item.disposition == "BLOCK" for item in checks[5:])
    assert report.endswith("FINAL | BLOCKED")
    assert "token_schema_allows_live_token | FAIL | BLOCK" in report
    assert "phase7_writer_exists | FAIL | BLOCK" in report
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
