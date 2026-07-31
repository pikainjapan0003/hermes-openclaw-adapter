"""Contract lock for mixed schema versions in one read-only board."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import validate_blackboard_message


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, Any]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def _write(board: Path, sequence: int, message_type: str, value: object) -> None:
    (board / f"{sequence:04d}_{message_type}.json").write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def test_mixed_schema_version_board_preserves_each_explicit_version_marker(
    tmp_path: Path,
) -> None:
    current = _fixture("task_draft")
    future = _fixture("annotation")
    future["schema_version"] = "2.0"
    _write(tmp_path, 1, "task_draft", current)
    _write(tmp_path, 2, "annotation", future)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is True
    assert result["entry_count"] == 2
    assert result["errors"] == []
    by_type = {entry["message_type"]: entry for entry in result["entries"]}
    assert by_type["task_draft"]["valid"] is True
    assert by_type["task_draft"]["message"] == current
    assert by_type["annotation"]["valid"] is True
    assert by_type["annotation"]["message"] == future
    assert {
        entry["message"]["schema_version"] for entry in result["entries"]
    } == {"1.0", "2.0"}


def test_validator_accepts_nonempty_version_and_preserves_it() -> None:
    message = _fixture("result_message")
    message["schema_version"] = "1.1"

    result = validate_blackboard_message(message, "result_message")

    assert result["valid"] is True
    assert result["errors"] == []


def test_invalid_version_type_still_fails_closed() -> None:
    message = _fixture("result_message")
    message["schema_version"] = 2

    result = validate_blackboard_message(message, "result_message")

    assert result["valid"] is False
    assert any(error["validator"] == "type" for error in result["errors"])


def test_current_single_version_board_remains_valid(tmp_path: Path) -> None:
    for sequence, message_type in enumerate(
        ("task_draft", "annotation", "approval_readiness"), start=1
    ):
        _write(tmp_path, sequence, message_type, _fixture(message_type))

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is True
    assert result["entry_count"] == 3
    assert {entry["message"]["schema_version"] for entry in result["entries"]} == {
        "1.0"
    }
