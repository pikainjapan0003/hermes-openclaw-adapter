"""N=1 ten-message Blackboard board round-trip rehearsal.

The evidence bundle remains an in-memory, off-board artifact.  The only board
audit record is the genesis preview.  All filesystem writes use ``tmp_path``.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import SCHEMA_FILES, validate_blackboard_message
from app.evidence_bundle_builder import verify_bundle_hash


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE_FIXTURE = (
    ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"
)
EVIDENCE_SCHEMA = ROOT / "docs" / "schemas" / "evidence_bundle.json"

LAYOUT_ORDER = (
    "task_draft",
    "annotation",
    "approval_readiness",
    "owner_decision",
    "worker_dry_run",
    "openclaw_command_envelope",
    "result_message",
    "approval_packet",
    "audit_event",
    "rollback_event",
)


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _message(message_type: str) -> dict[str, Any]:
    return _json(FIXTURES / f"{message_type}.valid.json")


def _write(
    board: Path,
    sequence: int,
    message_type: str,
    message: dict[str, Any],
) -> None:
    (board / f"{sequence:04d}_{message_type}.json").write_text(
        json.dumps(message, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def _validate_evidence_in_memory(bundle: dict[str, Any]) -> None:
    schema = _json(EVIDENCE_SCHEMA)
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(bundle),
        key=lambda error: list(error.path),
    )
    assert errors == []
    assert verify_bundle_hash(bundle) is True


def test_ten_contract_board_round_trips_exactly_and_evidence_stays_off_board(
    tmp_path: Path,
) -> None:
    assert set(SCHEMA_FILES) == set(LAYOUT_ORDER)
    originals = {message_type: _message(message_type) for message_type in LAYOUT_ORDER}
    originals["audit_event"]["prev_entry_hash"] = None

    for sequence, message_type in enumerate(LAYOUT_ORDER, start=1):
        _write(tmp_path, sequence, message_type, originals[message_type])

    evidence = _json(EVIDENCE_FIXTURE)
    _validate_evidence_in_memory(evidence)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is True
    assert result["entry_count"] == 10
    assert result["errors"] == []
    assert [entry["message_type"] for entry in result["entries"]] == list(
        LAYOUT_ORDER
    )
    assert {
        entry["message_type"]: entry["message"] for entry in result["entries"]
    } == originals
    assert sum(
        entry["message_type"] == "audit_event" for entry in result["entries"]
    ) == 1
    assert result["entries"][8]["message"]["prev_entry_hash"] is None
    assert not any(path.name.endswith("evidence_bundle.json") for path in tmp_path.iterdir())


@pytest.mark.parametrize(
    ("bad_name", "bad_bytes", "expected_code"),
    (
        ("0002_annotation.json", b"{truncated", "json_read_failed"),
        (
            "0002_annotation.json",
            json.dumps(_message("task_draft")).encode("utf-8"),
            "schema_rejected",
        ),
        ("bad-name.json", b"{}", "invalid_filename"),
    ),
    ids=("truncated", "wrong-schema", "wrong-filename"),
)
def test_bad_file_is_structurally_rejected_without_hiding_good_entry(
    tmp_path: Path,
    bad_name: str,
    bad_bytes: bytes,
    expected_code: str,
) -> None:
    good = deepcopy(_message("task_draft"))
    _write(tmp_path, 1, "task_draft", good)
    (tmp_path / bad_name).write_bytes(bad_bytes)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert expected_code in {error["code"] for error in result["errors"]}
    good_entry = next(
        entry for entry in result["entries"] if entry["message_type"] == "task_draft"
    )
    assert good_entry["valid"] is True
    assert good_entry["message"] == good
    assert validate_blackboard_message(good)["valid"] is True
