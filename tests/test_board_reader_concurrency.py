"""Concurrent callers observe the same immutable Blackboard board result."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import SCHEMA_FILES


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"


def _populate_valid_board(board: Path) -> None:
    for sequence, message_type in enumerate(sorted(SCHEMA_FILES), start=1):
        source = FIXTURE_DIR / f"{message_type}.valid.json"
        target = board / f"{sequence:04d}_{message_type}.json"
        target.write_bytes(source.read_bytes())


def _read_many(board: Path, count: int = 8) -> list[dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(read_blackboard_board, [board] * count))


def test_concurrent_readers_return_identical_valid_board_results(
    tmp_path: Path,
) -> None:
    _populate_valid_board(tmp_path)
    before = {
        child.name: child.read_bytes()
        for child in tmp_path.iterdir()
    }

    results = _read_many(tmp_path)

    assert len(results) == 8
    assert all(result == results[0] for result in results)
    assert results[0]["valid"] is True
    assert results[0]["entry_count"] == len(SCHEMA_FILES)
    assert {
        entry["message_type"]
        for entry in results[0]["entries"]
    } == set(SCHEMA_FILES)
    assert {
        child.name: child.read_bytes()
        for child in tmp_path.iterdir()
    } == before


def test_concurrent_readers_return_identical_structured_rejection(
    tmp_path: Path,
) -> None:
    source = FIXTURE_DIR / "task_draft.valid.json"
    (tmp_path / "0001_task_draft.json").write_bytes(source.read_bytes())
    marker = "FAKE-SECRET-NB13-CONCURRENT"
    broken = tmp_path / "0002_annotation.json"
    broken.write_text(f'{{"secret":"{marker}"', encoding="utf-8")

    results = _read_many(tmp_path)

    assert len(results) == 8
    assert all(result == results[0] for result in results)
    assert results[0]["valid"] is False
    assert results[0]["entry_count"] == 1
    assert results[0]["errors"] == [
        {
            "filename": broken.name,
            "code": "json_read_failed",
            "message": "entry could not be decoded: JSONDecodeError",
        }
    ]
    assert marker not in json.dumps(results[0], ensure_ascii=False, sort_keys=True)
