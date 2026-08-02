"""Seeded path-spelling and symlink fuzz for the F7 resolved-root invariant."""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from types import SimpleNamespace

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

SECOND_SEED = 20260805
SECOND_CASES_PER_CLASS = 10
SECOND_CATEGORIES = (
    "symlink_chain",
    "eloop",
    "relative_root",
    "trailing_slash",
    "case_insensitive_simulation",
)
SECOND_CASES = tuple(
    (category, index)
    for category in SECOND_CATEGORIES
    for index in range(1, SECOND_CASES_PER_CLASS + 1)
)


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


class _SimulatedCaseInsensitiveChild:
    """Minimal child facade for a deterministic case-insensitive FS simulation."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self._text = text

    def is_symlink(self) -> bool:
        return False

    def is_file(self) -> bool:
        return True

    def read_text(self, **_kwargs: object) -> str:
        return self._text

    def stat(self) -> SimpleNamespace:
        return SimpleNamespace(st_nlink=1)


def _make_link_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {type(exc).__name__}")


def test_second_realpath_fuzz_inventory_is_seeded_and_over_forty_cases() -> None:
    assert SECOND_SEED == 20260805
    assert len(SECOND_CASES) == 50
    assert {
        category: sum(case_category == category for case_category, _ in SECOND_CASES)
        for category in SECOND_CATEGORIES
    } == {category: SECOND_CASES_PER_CLASS for category in SECOND_CATEGORIES}


def test_second_symlink_chain_cases_reject_entry_links(tmp_path: Path) -> None:
    task = _task()
    for _category, index in SECOND_CASES:
        if _category != "symlink_chain":
            continue
        board = tmp_path / f"chain-board-{index:02d}"
        _write_board(board)
        outside = tmp_path / f"chain-target-{index:02d}.json"
        outside.write_text(json.dumps(task), encoding="utf-8")
        previous = outside
        for depth in range(3):
            link = tmp_path / f"chain-{index:02d}-{depth}.json"
            _make_link_or_skip(link, previous)
            previous = link
        entry = board / "0002_annotation.json"
        _make_link_or_skip(entry, previous)

        report = read_blackboard_board(board)

        assert report["valid"] is False
        assert report["entry_count"] == 1
        assert report["errors"] == [
            {
                "filename": entry.name,
                "code": "symlink_rejected",
                "message": "symlinks are not read",
            }
        ]


def test_second_eloop_cases_are_structurally_rejected(tmp_path: Path) -> None:
    for _category, index in SECOND_CASES:
        if _category != "eloop":
            continue
        first = tmp_path / f"eloop-{index:02d}-a"
        second = tmp_path / f"eloop-{index:02d}-b"
        _make_link_or_skip(first, second, directory=True)
        _make_link_or_skip(second, first, directory=True)

        report = read_blackboard_board(first)

        assert report["valid"] is False
        assert report["entry_count"] == 0
        assert report["errors"]
        assert report["errors"][0]["code"] in {
            "directory_missing",
            "not_a_directory",
            "directory_read_failed",
        }


def test_second_relative_root_cases_read_the_selected_board(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path.parent)
    for _category, index in SECOND_CASES:
        if _category != "relative_root":
            continue
        board = tmp_path / f"relative-board-{index:02d}"
        task = _write_board(board)
        relative = Path(tmp_path.name) / board.name / "."

        report = read_blackboard_board(relative)

        assert report["valid"] is True
        assert report["entries"][0]["message"] == task


def test_second_trailing_slash_cases_read_the_selected_board(tmp_path: Path) -> None:
    for _category, index in SECOND_CASES:
        if _category != "trailing_slash":
            continue
        board = tmp_path / f"slash-board-{index:02d}"
        task = _write_board(board)
        spelling = str(board) + (os.sep * (index % 3 + 1)) + "."

        report = read_blackboard_board(spelling)

        assert report["valid"] is True
        assert report["entries"][0]["message"] == task


def test_second_case_insensitive_cases_preserve_good_entry_and_reject_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    board = tmp_path / "case-simulation"
    task = _write_board(board)
    raw = json.dumps(task, ensure_ascii=False)
    original_iterdir = Path.iterdir

    def simulated_iterdir(path: Path):
        if path == board:
            return iter(
                (
                    board / "0001_task_draft.json",
                    _SimulatedCaseInsensitiveChild("0001_TASK_DRAFT.JSON", raw),
                )
            )
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", simulated_iterdir)
    report = read_blackboard_board(board)

    assert report["valid"] is False
    assert report["entry_count"] == 1
    assert report["entries"][0]["valid"] is True
    assert report["errors"] == [
        {
            "filename": "0001_TASK_DRAFT.JSON",
            "code": "invalid_filename",
            "message": "entry filename must be NNNN_message_type.json",
        }
    ]
