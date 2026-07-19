"""Tests for the pure N=1 Blackboard board reader."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import SCHEMA_FILES


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, object]:
    return json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )


def _write_entry(
    board: Path,
    sequence: int,
    message_type: str,
    message: dict[str, object],
) -> None:
    target = board / f"{sequence:04d}_{message_type}.json"
    target.write_text(
        json.dumps(message, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def test_reader_validates_one_entry_for_all_ten_contracts(tmp_path: Path) -> None:
    for sequence, message_type in enumerate(SCHEMA_FILES, start=1):
        _write_entry(tmp_path, sequence, message_type, _fixture(message_type))

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is True
    assert result["board_name"] == tmp_path.name
    assert result["entry_count"] == 10
    assert result["errors"] == []
    assert [entry["sequence"] for entry in result["entries"]] == list(range(1, 11))
    assert {entry["message_type"] for entry in result["entries"]} == set(
        SCHEMA_FILES
    )
    assert all(entry["valid"] is True for entry in result["entries"])
    assert all(entry["errors"] == [] for entry in result["entries"])


def test_reader_returns_structured_rejection_without_invalid_payload(
    tmp_path: Path,
) -> None:
    message = deepcopy(_fixture("task_draft"))
    message.pop("role")
    _write_entry(tmp_path, 1, "task_draft", message)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entry_count"] == 1
    assert result["errors"] == [
        {
            "filename": "0001_task_draft.json",
            "code": "schema_rejected",
            "message": "entry failed its Blackboard schema",
        }
    ]
    entry = result["entries"][0]
    assert entry["valid"] is False
    assert "message" not in entry
    assert any(
        error["validator"] == "required" and "role" in error["message"]
        for error in entry["errors"]
    )


def test_empty_directory_is_a_valid_empty_board(tmp_path: Path) -> None:
    result = read_blackboard_board(tmp_path)

    assert result == {
        "valid": True,
        "board_name": tmp_path.name,
        "entry_count": 0,
        "entries": [],
        "errors": [],
    }


def test_reader_rejects_malformed_and_unexpected_entries(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("not a board entry", encoding="utf-8")
    (tmp_path / "0001_task_draft.json").write_text("{bad json", encoding="utf-8")

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert {error["code"] for error in result["errors"]} == {
        "invalid_filename",
        "json_read_failed",
    }
    assert result["entries"] == []


def test_missing_directory_returns_structured_error(tmp_path: Path) -> None:
    missing = tmp_path / "not-created"

    result = read_blackboard_board(missing)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"][0]["code"] == "directory_missing"
    assert not missing.exists()
