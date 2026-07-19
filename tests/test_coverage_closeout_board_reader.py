"""Remaining fail-closed branches for the read-only Blackboard board reader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import blackboard_board_reader as reader
from app.blackboard_validators import BlackboardSchemaError


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict:
    return json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )


def _write(board: Path, name: str, message_type: str = "task_draft") -> None:
    (board / name).write_text(
        json.dumps(_fixture(message_type), ensure_ascii=False), encoding="utf-8"
    )


def test_reader_rejects_file_path_and_nested_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "not-a-board"
    file_path.write_text("x", encoding="utf-8")
    assert reader.read_blackboard_board(file_path)["errors"][0]["code"] == "not_a_directory"

    nested = tmp_path / "nested"
    nested.mkdir()
    result = reader.read_blackboard_board(tmp_path)
    assert result["valid"] is False
    assert result["errors"][0]["code"] == "unexpected_entry"


def test_reader_rejects_duplicate_sequence_and_message_type(tmp_path: Path) -> None:
    _write(tmp_path, "0001_annotation.json", "annotation")
    _write(tmp_path, "0001_task_draft.json")
    _write(tmp_path, "0002_annotation.json", "annotation")

    result = reader.read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert {error["code"] for error in result["errors"]} == {
        "duplicate_sequence",
        "duplicate_message_type",
    }
    assert result["entry_count"] == 1


def test_reader_reports_directory_enumeration_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = Path.iterdir

    def synthetic_iterdir(path: Path):
        if path == tmp_path:
            raise OSError("synthetic enumeration failure")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", synthetic_iterdir)
    result = reader.read_blackboard_board(tmp_path)
    assert result["errors"][0]["code"] == "directory_read_failed"
    assert "OSError" in result["errors"][0]["message"]


def test_reader_reports_schema_unavailable_without_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path, "0001_task_draft.json")

    def unavailable(*_args, **_kwargs):
        raise BlackboardSchemaError("synthetic unavailable")

    monkeypatch.setattr(reader, "validate_blackboard_message", unavailable)
    result = reader.read_blackboard_board(tmp_path)
    assert result["valid"] is False
    assert result["entry_count"] == 0
    assert result["errors"][0]["code"] == "schema_unavailable"
    assert "BlackboardSchemaError" in result["errors"][0]["message"]
