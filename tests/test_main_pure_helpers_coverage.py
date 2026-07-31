"""Coverage for the five explicitly authorized pure/read-only main helpers.

This module never invokes a POST route, command builder, callback, dispatch
helper, worker, or claim path.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

import app.main as main


pytestmark = pytest.mark.legacy


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({}, (0, True)),
        ({"safety_level": "  "}, (0, True)),
        ({"safety_level": "Level 3"}, (3, False)),
        ({"safety_level": "level_07"}, (7, False)),
        ({"safety_level": 2}, (2, False)),
        ({"safety_level": "unsafe"}, (99, False)),
    ],
)
def test_parse_safety_level_edges(
    metadata: dict[str, object],
    expected: tuple[int, bool],
) -> None:
    assert main.parse_safety_level(metadata) == expected


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        ({}, (False, False)),
        ({"requires_confirmation": True}, (True, True)),
        ({"requires_confirmation": "yes"}, (True, True)),
        ({"requires_confirmation": 1}, (True, True)),
        ({"requires_confirmation": object()}, (False, False)),
        ({"safety_level": "  "}, (False, False)),
        ({"safety_level": "Level 2"}, (False, False)),
        ({"safety_level": "Level 3"}, (True, False)),
        ({"safety_level": "unsafe"}, (False, False)),
    ],
)
def test_needs_human_review_edges(
    metadata: dict[str, object],
    expected: tuple[bool, bool],
) -> None:
    assert main.needs_human_review(metadata) == expected


def test_read_jsonl_is_read_only_and_skips_unusable_lines(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    assert main.read_jsonl(missing) == []
    assert not missing.exists()

    source = tmp_path / "input.jsonl"
    source.write_text(
        '\n{"task_id":"one"}\nnot-json\n[]\n{"task_id":"two"}\n',
        encoding="utf-8",
    )
    before = source.read_bytes()

    assert main.read_jsonl(source) == [
        {"task_id": "one"},
        [],
        {"task_id": "two"},
    ]
    assert source.read_bytes() == before


def test_task_exists_covers_background_queue_and_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main, "EXECUTION_MODE", "background")
    monkeypatch.setattr(
        main,
        "get_queue",
        lambda: (_ for _ in ()).throw(AssertionError("background queried queue")),
    )
    assert main._task_exists("task-1") is False

    class _Queue:
        def __init__(self, result: object) -> None:
            self.result = result

        def get(self, task_id: str) -> object:
            assert task_id == "task-1"
            return self.result

    monkeypatch.setattr(main, "EXECUTION_MODE", "queue")
    monkeypatch.setattr(main, "get_queue", lambda: _Queue({"task_id": "task-1"}))
    assert main._task_exists("task-1") is True

    monkeypatch.setattr(main, "get_queue", lambda: _Queue(None))
    assert main._task_exists("task-1") is False

    monkeypatch.setattr(
        main,
        "get_queue",
        lambda: (_ for _ in ()).throw(RuntimeError("synthetic queue failure")),
    )
    assert main._task_exists("task-1") is False


def test_require_token_accepts_disabled_and_exact_token_and_rejects_other(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main, "HERMES_ADAPTER_TOKEN", "")
    main.require_token(None)

    monkeypatch.setattr(main, "HERMES_ADAPTER_TOKEN", "synthetic-adapter-token")
    main.require_token("synthetic-adapter-token")

    with pytest.raises(HTTPException) as captured:
        main.require_token("wrong-token")
    assert captured.value.status_code == 401
    assert captured.value.detail == "Invalid or missing X-Adapter-Token"

