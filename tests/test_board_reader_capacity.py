"""Informational 500-message capacity probe for the N=1 board reader."""

from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path

import pytest

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import SCHEMA_FILES


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"
BOARD_COUNT = 50
MESSAGES_PER_BOARD = len(SCHEMA_FILES)
TOTAL_MESSAGES = BOARD_COUNT * MESSAGES_PER_BOARD
pytestmark = pytest.mark.slow


def _fixture_text(message_type: str) -> str:
    source = FIXTURES / f"{message_type}.valid.json"
    message = json.loads(source.read_text(encoding="utf-8"))
    return json.dumps(message, ensure_ascii=False, sort_keys=True)


def test_reader_capacity_probe_reports_runtime_and_peak_memory(
    tmp_path: Path,
) -> None:
    """Measure 50 legal N=1 boards; do not impose a CI performance threshold."""

    fixture_text = {
        message_type: _fixture_text(message_type)
        for message_type in SCHEMA_FILES
    }
    boards: list[Path] = []
    for board_index in range(BOARD_COUNT):
        board = tmp_path / f"board-{board_index:03d}"
        board.mkdir()
        boards.append(board)
        for sequence, message_type in enumerate(SCHEMA_FILES, start=1):
            (board / f"{sequence:04d}_{message_type}.json").write_text(
                fixture_text[message_type],
                encoding="utf-8",
            )

    tracemalloc.start()
    started = time.perf_counter()
    results = [read_blackboard_board(board) for board in boards]
    elapsed_seconds = time.perf_counter() - started
    _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert TOTAL_MESSAGES == 500
    assert len(results) == BOARD_COUNT
    assert all(result["valid"] is True for result in results)
    assert sum(result["entry_count"] for result in results) == TOTAL_MESSAGES
    assert elapsed_seconds >= 0
    assert peak_bytes > 0

    print(
        "board_reader_capacity "
        f"boards={BOARD_COUNT} messages={TOTAL_MESSAGES} "
        f"runtime_seconds={elapsed_seconds:.6f} peak_bytes={peak_bytes}"
    )

