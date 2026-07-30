"""Mechanical path and inventory checks for the contract schema index."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "docs" / "schemas" / "blackboard" / "INDEX.md"
ROW_PATTERN = re.compile(
    r"^\| `(?P<contract>[^`]+)` \| (?P<purpose>[^|]+) "
    r"\| `(?P<artifact>[^`]+)` \| `(?P<reference>[^`]+)` "
    r"\| `(?P<test>[^`]+)` \|$",
    re.MULTILINE,
)

EXPECTED_CONTRACTS = {
    "task_draft",
    "annotation",
    "approval_readiness",
    "owner_decision",
    "worker_dry_run",
    "openclaw_command_envelope",
    "result_message",
    "audit_event",
    "rollback_event",
    "approval_packet",
    "evidence_bundle",
    "remote_readonly_projection",
    "rollback_preview_builder",
    "hash_chain",
    "hash_chain_vectors",
    "blackboard_board_reader",
    "mirror_drift_readonly",
    "three_source_readonly",
    "n1_preflight_runbook",
}


def test_contract_index_inventory_and_all_referenced_paths_exist() -> None:
    index_text = INDEX_PATH.read_text(encoding="utf-8")
    rows = [match.groupdict() for match in ROW_PATTERN.finditer(index_text)]

    assert len(rows) == 19
    assert {row["contract"] for row in rows} == EXPECTED_CONTRACTS
    assert len({row["artifact"] for row in rows}) == 19
    for row in rows:
        assert row["purpose"].strip().endswith(".")
        for path_field in ("artifact", "reference", "test"):
            referenced_path = ROOT / row[path_field]
            if (
                row["contract"] == "hash_chain_vectors"
                and path_field == "artifact"
            ):
                path_exists_as_expected = referenced_path.is_dir()
            else:
                path_exists_as_expected = referenced_path.is_file()
            assert path_exists_as_expected, (
                f"{row['contract']} references missing {path_field}: "
                f"{row[path_field]}"
            )
