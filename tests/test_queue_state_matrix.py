"""Exhaustive queue-control transition matrix using only tmp_path SQLite."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Callable

import pytest

import app.queue_store as queue_store_module
from app.queue_store import (
    ALL_STATUSES,
    ARCHIVED,
    CANCELLED,
    COMPLETED,
    FAILED,
    QUEUED,
    REJECTED,
    WAITING_REVIEW,
    QueueStore,
)


TRANSITIONS: dict[str, tuple[set[str], str]] = {
    "approve": ({WAITING_REVIEW}, QUEUED),
    "reject": ({WAITING_REVIEW}, REJECTED),
    "cancel_control": ({QUEUED, WAITING_REVIEW}, CANCELLED),
    "retry_failed": ({FAILED}, QUEUED),
    "archive": ({COMPLETED, FAILED, CANCELLED, REJECTED}, ARCHIVED),
}
MATRIX = tuple(
    (operation_name, initial_status)
    for operation_name in TRANSITIONS
    for initial_status in ALL_STATUSES
)


def _store_with_status(tmp_path: Path, initial_status: str) -> tuple[QueueStore, str]:
    store = QueueStore(tmp_path / f"queue-{initial_status}.db")
    task_id = f"matrix-{initial_status}"
    row = store.enqueue(
        task_id=task_id,
        title="Synthetic matrix task",
        task_text="No execution; transition test only.",
        safety_level=0,
        payload={"synthetic": True},
    )
    assert row is not None
    assert store._update(task_id, status=initial_status) is not None
    return store, task_id


@pytest.mark.parametrize(
    ("operation_name", "initial_status"),
    MATRIX,
    ids=(f"{operation}-{status}" for operation, status in MATRIX),
)
def test_queue_control_transition_matrix_is_atomic_and_does_not_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation_name: str,
    initial_status: str,
) -> None:
    store, task_id = _store_with_status(tmp_path, initial_status)
    allowed_from, target_status = TRANSITIONS[operation_name]
    claim_calls = 0

    def forbidden_claim(_store: QueueStore) -> None:
        nonlocal claim_calls
        claim_calls += 1
        raise AssertionError("control transition must not claim")

    monkeypatch.setattr(QueueStore, "claim_next", forbidden_claim)
    operation: Callable[..., dict | None] = getattr(store, operation_name)
    before = store.get(task_id)
    assert before is not None

    result = operation(task_id)
    after = store.get(task_id)
    assert after is not None

    if initial_status in allowed_from:
        assert result is not None
        assert after["status"] == target_status
    else:
        assert result is None
        assert after["status"] == initial_status
    assert after["attempts"] == before["attempts"] == 0
    assert claim_calls == 0


def test_control_methods_have_no_dispatch_or_claim_call_site() -> None:
    """Static backstop for the zero-claim/zero-dispatch matrix guarantee."""

    source = inspect.getsource(queue_store_module)
    tree = ast.parse(source)
    controlled_methods = set(TRANSITIONS)
    forbidden_calls: list[tuple[str, str]] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "QueueStore":
            continue
        for child in node.body:
            if not isinstance(child, ast.FunctionDef) or child.name not in controlled_methods:
                continue
            for descendant in ast.walk(child):
                if isinstance(descendant, ast.Call) and isinstance(
                    descendant.func, ast.Attribute
                ):
                    called = descendant.func.attr
                    if called == "claim_next" or "dispatch" in called.lower():
                        forbidden_calls.append((child.name, called))

    assert forbidden_calls == []
