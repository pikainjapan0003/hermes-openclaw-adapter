"""Malicious-path boundaries for the read-only Blackboard board reader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.blackboard_board_reader import read_blackboard_board


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, object]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def test_reader_rejects_symlink_without_reading_outside_board(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside_marker = "OUTSIDE-BOARD-SECRET-MUST-NOT-BE-READ"
    outside = tmp_path.parent / f"{tmp_path.name}-outside.json"
    outside.write_text(outside_marker, encoding="utf-8")
    link = tmp_path / "0001_task_draft.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"platform cannot create test symlink: {type(exc).__name__}")

    original_read_text = Path.read_text
    read_paths: list[Path] = []

    def recording_read_text(path: Path, *args: object, **kwargs: object) -> str:
        read_paths.append(path.resolve())
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", recording_read_text)
    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    assert result["errors"] == [
        {
            "filename": link.name,
            "code": "symlink_rejected",
            "message": "symlinks are not read",
        }
    ]
    assert read_paths == []
    assert outside.read_text(encoding="utf-8") == outside_marker
    assert outside_marker not in json.dumps(result, ensure_ascii=False)


def test_reader_structurally_rejects_hostile_entry_shapes(tmp_path: Path) -> None:
    # Long enough to stress the contract filename matcher while remaining
    # creatable under Windows' legacy aggregate path limit.
    long_name = ("x" * 96) + ".json"
    (tmp_path / long_name).write_text("long filename payload", encoding="utf-8")
    (tmp_path / "0001-task_draft.json").write_text(
        "illegal contract filename payload", encoding="utf-8"
    )
    (tmp_path / ".hidden.json").write_text("hidden payload", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "0001_task_draft.json").write_text(
        "nested payload must not be read", encoding="utf-8"
    )
    (tmp_path / "0002_task_draft.json").write_bytes(b"")
    bom_payload = json.dumps(
        _fixture("annotation"), ensure_ascii=False, sort_keys=True
    ).encode("utf-8-sig")
    (tmp_path / "0003_annotation.json").write_bytes(bom_payload)

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["entries"] == []
    codes = [error["code"] for error in result["errors"]]
    assert codes.count("invalid_filename") == 3
    assert codes.count("unexpected_entry") == 1
    assert codes.count("json_read_failed") == 2
    assert {error["filename"] for error in result["errors"]} == {
        long_name,
        "0001-task_draft.json",
        ".hidden.json",
        "nested",
        "0002_task_draft.json",
        "0003_annotation.json",
    }
    serialized = json.dumps(result, ensure_ascii=False)
    assert "nested payload must not be read" not in serialized
    assert "illegal contract filename payload" not in serialized
