"""Branch coverage for the legacy SQLite Blackboard comment store."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.blackboard_store import (
    MAX_AUTHOR_NAME_LEN,
    MAX_CONTENT_LEN,
    BlackboardStore,
    CommentValidationError,
)


@pytest.mark.parametrize(
    "overrides",
    (
        {"author_type": "unknown"},
        {"content": None},
        {"content": "   "},
        {"content": "x" * (MAX_CONTENT_LEN + 1)},
        {"author_name": "x" * (MAX_AUTHOR_NAME_LEN + 1)},
        {"metadata": []},
    ),
)
def test_add_comment_rejects_each_closed_input_boundary(
    tmp_path: Path,
    overrides: dict[str, Any],
) -> None:
    store = BlackboardStore(tmp_path / "comments.db")
    arguments: dict[str, Any] = {
        "task_id": "task-coverage",
        "author_type": " user ",
        "content": " safe comment ",
        "author_name": " owner ",
        "metadata": {"source": "coverage"},
    }
    arguments.update(overrides)

    with pytest.raises(CommentValidationError):
        store.add_comment(**arguments)

    assert store.count_for_task("task-coverage") == 0


def test_add_get_list_and_count_cover_normalization_and_missing_row(
    tmp_path: Path,
) -> None:
    store = BlackboardStore(tmp_path / "nested" / "comments.db")

    first = store.add_comment(
        task_id="task-coverage",
        author_type=" user ",
        content=" first ",
        author_name="   ",
        metadata=None,
    )
    second = store.add_comment(
        task_id="task-coverage",
        author_type="system",
        content="second",
        author_name=" guard ",
        metadata={"attempt": 2},
    )
    third = store.add_comment(
        task_id="task-coverage",
        author_type="hermes",
        content="third",
        author_name=None,
        metadata={},
    )

    assert first["author_name"] is None
    assert first["content"] == "first"
    assert first["metadata"] == {}
    assert second["author_name"] == "guard"
    assert second["metadata"] == {"attempt": 2}
    assert third["author_name"] is None
    assert store.get("missing-comment") is None
    assert store.count_for_task("task-coverage") == 3
    assert store.count_for_task("other-task") == 0
    assert {item["comment_id"] for item in store.list_for_task("task-coverage")} == {
        first["comment_id"],
        second["comment_id"],
        third["comment_id"],
    }
    assert store.list_for_task("other-task") == []


def test_row_decoder_fail_closes_for_non_object_and_malformed_metadata(
    tmp_path: Path,
) -> None:
    store = BlackboardStore(tmp_path / "comments.db")
    conn = store._connect()
    try:
        for index, metadata_json in enumerate((None, "[]", "{malformed"), start=1):
            conn.execute(
                """INSERT INTO task_comments
                   (comment_id, task_id, author_type, author_name,
                    content, created_at, metadata_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    f"raw-{index}",
                    "task-raw",
                    "system",
                    None,
                    "raw metadata case",
                    f"2026-07-22T00:00:0{index}+00:00",
                    metadata_json,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    rows = store.list_for_task("task-raw")

    assert len(rows) == 3
    assert all(row["metadata"] == {} for row in rows)
