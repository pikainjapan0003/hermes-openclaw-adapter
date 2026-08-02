"""Concurrent read-only rehearsal against one 500-file synthetic board."""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from app.blackboard_board_reader import read_blackboard_board
from app.blackboard_validators import SCHEMA_FILES


pytestmark = pytest.mark.contract
ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"


def _fixture(message_type: str) -> dict[str, Any]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def _fingerprints(board: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(board.iterdir())
    }


@pytest.mark.slow
def test_eight_concurrent_readers_return_the_same_500_file_result(
    tmp_path: Path,
) -> None:
    message_types = tuple(SCHEMA_FILES)
    assert len(message_types) == 10
    for sequence in range(1, 501):
        message_type = message_types[(sequence - 1) % len(message_types)]
        (tmp_path / f"{sequence:04d}_{message_type}.json").write_text(
            json.dumps(_fixture(message_type), ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
    before = _fingerprints(tmp_path)
    assert len(before) == 500

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: read_blackboard_board(tmp_path), range(8)))
    elapsed_seconds = time.perf_counter() - started

    assert all(result == results[0] for result in results[1:])
    assert results[0]["valid"] is False
    assert results[0]["entry_count"] == 10
    assert len(results[0]["errors"]) == 490
    assert {error["code"] for error in results[0]["errors"]} == {
        "duplicate_message_type"
    }
    assert _fingerprints(tmp_path) == before
    assert elapsed_seconds >= 0
