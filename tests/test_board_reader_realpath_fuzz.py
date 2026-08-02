"""Seeded path-spelling and symlink fuzz for the F7 resolved-root invariant."""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from app.blackboard_board_reader import read_blackboard_board


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
TASK_FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "task_draft.valid.json"
SEED = 20260804
CASES_PER_CLASS = 15


@dataclass(frozen=True)
class PathCase:
    category: str
    index: int


def _cases() -> tuple[PathCase, ...]:
    cases = [
        PathCase(category, index)
        for category in (
            "dot_and_parent",
            "repeated_separator",
            "root_symlink_chain",
            "entry_symlink_chain",
        )
        for index in range(1, CASES_PER_CLASS + 1)
    ]
    random.Random(SEED).shuffle(cases)
    return tuple(cases)


CASES = _cases()


def _task() -> dict[str, Any]:
    value = json.loads(TASK_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_board(board: Path) -> dict[str, Any]:
    board.mkdir()
    task = _task()
    (board / "0001_task_draft.json").write_text(
        json.dumps(task, ensure_ascii=False), encoding="utf-8"
    )
    return task


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {type(exc).__name__}")


def test_realpath_fuzz_inventory_is_seeded_and_balanced() -> None:
    assert SEED == 20260804
    assert len(CASES) == 60
    assert {
        category: sum(case.category == category for case in CASES)
        for category in (
            "dot_and_parent",
            "repeated_separator",
            "root_symlink_chain",
            "entry_symlink_chain",
        )
    } == {
        "dot_and_parent": 15,
        "repeated_separator": 15,
        "root_symlink_chain": 15,
        "entry_symlink_chain": 15,
    }


def test_non_symlink_path_spellings_resolve_to_the_caller_selected_root(
    tmp_path: Path,
) -> None:
    board = tmp_path / "board"
    task = _write_board(board)

    cases = [case for case in CASES if "symlink" not in case.category]
    assert len(cases) == 30
    for case in cases:
        if case.category == "dot_and_parent":
            if case.index % 2:
                suffix = os.sep.join(["."] * case.index)
                spelling = f"{board}{os.sep}{suffix}"
            else:
                suffix = os.sep.join(["."] * (case.index // 2))
                spelling = (
                    f"{board}{os.sep}..{os.sep}{board.name}{os.sep}{suffix}"
                )
        else:
            spelling = str(board).replace(os.sep, os.sep * 2)
            spelling += os.sep * (case.index % 3 + 1) + "."

        report = read_blackboard_board(spelling)
        assert Path(spelling).resolve() == board.resolve()
        assert report["valid"] is True, (case, report["errors"])
        assert report["entry_count"] == 1
        assert report["entries"][0]["message"] == task


def test_root_symlink_chains_are_caller_selected_roots_and_entry_links_fail_closed(
    tmp_path: Path,
) -> None:
    board = tmp_path / "canonical-board"
    task = _write_board(board)
    outside = tmp_path / "outside-task.json"
    outside.write_text(json.dumps(task), encoding="utf-8")

    root_cases = [case for case in CASES if case.category == "root_symlink_chain"]
    entry_cases = [case for case in CASES if case.category == "entry_symlink_chain"]
    assert len(root_cases) == len(entry_cases) == 15

    previous_root = board
    for case in root_cases:
        alias = tmp_path / f"root-alias-{case.index:02d}"
        _symlink_or_skip(alias, previous_root, directory=True)
        report = read_blackboard_board(alias)
        assert alias.resolve() == board.resolve()
        assert report["valid"] is True, (case, report["errors"])
        assert report["entries"][0]["message"] == task
        previous_root = alias

    previous_target = outside
    for case in entry_cases:
        fuzz_board = tmp_path / f"entry-board-{case.index:02d}"
        fuzz_board.mkdir()
        chained_target = tmp_path / f"outside-link-{case.index:02d}.json"
        _symlink_or_skip(chained_target, previous_target)
        entry = fuzz_board / "0001_task_draft.json"
        _symlink_or_skip(entry, chained_target)

        report = read_blackboard_board(fuzz_board)
        assert entry.resolve() == outside.resolve()
        assert report["valid"] is False
        assert report["entry_count"] == 0
        assert [error["code"] for error in report["errors"]] == [
            "symlink_rejected"
        ]
        previous_target = chained_target
