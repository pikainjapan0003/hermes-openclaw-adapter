"""Mechanical fail-closed checks for the Phase 9 N=1 preflight gate.

These tests describe blockers only.  They do not issue tokens, authorize Phase 7,
create an audit writer, or provide any execution-unlock path.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
APPROVAL_SCHEMA = (
    ROOT / "docs" / "schemas" / "blackboard" / "approval_packet.schema.json"
)
PLAN = ROOT / "docs" / "agent_operating_system" / "05_VERIFIED_LONG_TERM_PLAN.md"
RUNBOOK = ROOT / "docs" / "agent_operating_system" / "09_N1_PREFLIGHT_RUNBOOK.md"
AUDIT_WRITER = ROOT / "app" / "audit_writer_local.py"
AUDIT_FILE = ROOT / "data" / "audit_dev.jsonl"


def _phase7_status() -> str:
    plan_text = PLAN.read_text(encoding="utf-8")
    match = re.search(
        r"^\| 7 \| (?P<status>[^|]+) \| \d{4}-\d{2}-\d{2} \|",
        plan_text,
        re.MULTILINE,
    )
    assert match is not None, "Phase 7 status row must remain mechanically discoverable"
    return match.group("status").strip()


def test_approval_packet_token_is_structurally_locked_to_null() -> None:
    schema = json.loads(APPROVAL_SCHEMA.read_text(encoding="utf-8"))
    token_schema = schema["properties"]["single_use_execution_token"]

    assert "single_use_execution_token" in schema["required"]
    assert token_schema["type"] == "null"
    assert "const" in token_schema
    assert token_schema["const"] is None


def test_phase7_audit_persistence_is_absent() -> None:
    assert not AUDIT_WRITER.exists(), (
        "Phase 9 must remain blocked while an audit writer is present without the "
        "separately authorized Phase 7 completion"
    )
    assert not AUDIT_FILE.exists(), (
        "Phase 9 preflight must not treat an audit artifact as authorized persistence"
    )


def test_phase7_plan_status_has_not_reached_completion() -> None:
    status = _phase7_status()

    assert status == "設計已備"
    assert "完成" not in status


def test_runbook_records_all_three_current_blockers() -> None:
    runbook_text = RUNBOOK.read_text(encoding="utf-8")
    normalized_runbook = re.sub(r"\s+", " ", runbook_text)
    blockers = {
        "token_locked_null": "approval-packet token remains structurally null"
        in normalized_runbook,
        "audit_writer_absent": "Phase 7 audit persistence is incomplete"
        in normalized_runbook,
        "phase7_not_complete": (
            _phase7_status() != "完成" and not AUDIT_WRITER.exists()
        ),
    }

    assert blockers == {
        "token_locked_null": True,
        "audit_writer_absent": True,
        "phase7_not_complete": True,
    }
    assert (
        "The present repository is not ready to run this procedure"
        in normalized_runbook
    )
    assert "If any Phase 7 item is incomplete, stop" in normalized_runbook
