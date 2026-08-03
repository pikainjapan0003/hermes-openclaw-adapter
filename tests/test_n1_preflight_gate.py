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
OWNER_ACCEPTANCE = (
    ROOT
    / "docs"
    / "agent_operating_system"
    / "research"
    / "PHASE7_OWNER_ACCEPTANCE.md"
)


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


def test_phase7_audit_persistence_is_signed_off_with_committed_evidence() -> None:
    assert AUDIT_WRITER.exists(), "Phase 7 writer should exist after authorization"
    acceptance = OWNER_ACCEPTANCE.read_text(encoding="utf-8")
    assert all(f"RECORD_{index}=" in acceptance for index in range(1, 4))
    assert (
        "FILE_SHA256=eef4d7db225c5df929abcc92e4152aa2aaf14cccc17f5bdd86361bbedc85efc2"
        in acceptance
    )
    # Owner sign-off recorded 2026-08-03; every acceptance box must be checked.
    assert "[ ]" not in acceptance
    assert "已由 Owner 於 2026-08-03 簽核" in acceptance


def test_phase7_plan_status_is_complete() -> None:
    status = _phase7_status().replace("**", "")

    assert status == "完成"


def test_phase7_signoff_does_not_unlock_phase9() -> None:
    """Phase 7 closing must leave every Phase 9 blocker fail-closed."""

    runbook_text = RUNBOOK.read_text(encoding="utf-8")
    normalized_runbook = re.sub(r"\s+", " ", runbook_text)
    schema = json.loads(APPROVAL_SCHEMA.read_text(encoding="utf-8"))

    blockers = {
        "token_locked_null": schema["properties"]["single_use_execution_token"][
            "const"
        ]
        is None,
        "runbook_states_not_ready": "The present repository is not ready to run"
        " this procedure" in normalized_runbook,
        "signoff_not_an_unlock": "does not unlock Phase 9" in normalized_runbook,
        "owner_not_present": "the Owner is not synchronously present"
        in normalized_runbook,
        "no_fresh_token": "no fresh single-use token has been issued"
        in normalized_runbook,
        "runtime_not_authorized": "runtime rehearsal is not authorized"
        in normalized_runbook,
    }

    assert all(blockers.values()), blockers
    assert "If any Phase 7 item is incomplete, stop" in normalized_runbook
