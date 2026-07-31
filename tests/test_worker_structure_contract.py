"""Static worker contract tests; this module never starts or runs a worker.

The present worker has only two structural preconditions before its OpenClaw
call: ``QueueStore.claim_next`` must return a row selected from ``queued``, and
the row payload must construct ``adapter.TaskEnvelope``.  There is no Phase 9
execution-token or safety-flag gate yet; these tests document that fact without
authorizing or exercising the execution path.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
WORKER_PATH = ROOT / "app" / "worker.py"
QUEUE_STORE_PATH = ROOT / "app" / "queue_store.py"


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    assert len(matches) == 1
    return matches[0]


def _call_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Name):
            names.append(child.func.id)
        elif isinstance(child.func, ast.Attribute):
            names.append(child.func.attr)
    return names


def test_claim_next_query_is_structurally_limited_to_queued() -> None:
    tree = _tree(QUEUE_STORE_PATH)
    queue_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "QueueStore"
    )
    claim = _function(ast.Module(body=queue_class.body, type_ignores=[]), "claim_next")

    select_literals = [
        node.value
        for node in ast.walk(claim)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and "SELECT task_id FROM queue" in node.value
    ]
    assert len(select_literals) == 1
    normalized = " ".join(select_literals[0].split())
    assert "WHERE status=?" in normalized
    assert "ORDER BY created_at ASC LIMIT 1" in normalized

    queued_arguments = [
        node
        for node in ast.walk(claim)
        if isinstance(node, ast.Tuple)
        and any(isinstance(value, ast.Name) and value.id == "QUEUED" for value in node.elts)
    ]
    assert queued_arguments


def test_worker_loop_claims_only_through_queue_store() -> None:
    loop = _function(_tree(WORKER_PATH), "main_loop")
    claim_calls = [
        node
        for node in ast.walk(loop)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "claim_next"
    ]
    assert len(claim_calls) == 1
    assert isinstance(claim_calls[0].func.value, ast.Name)
    assert claim_calls[0].func.value.id == "queue"


def test_dispatch_path_has_only_the_documented_pre_phase9_preconditions() -> None:
    process_item = _function(_tree(WORKER_PATH), "process_item")
    calls = _call_names(process_item)
    assert calls.count("TaskEnvelope") == 1
    assert calls.count("run_openclaw_cli") == 1
    assert calls.index("TaskEnvelope") < calls.index("run_openclaw_cli")

    source = ast.get_source_segment(
        WORKER_PATH.read_text(encoding="utf-8"), process_item
    )
    assert source is not None
    for absent_gate in (
        "single_use_execution_token",
        "execution_class",
        "worker_dispatch_allowed",
        "openclaw_call_allowed",
    ):
        assert absent_gate not in source


def test_worker_import_cannot_start_loop_or_claim(
    monkeypatch: Any,
) -> None:
    import asyncio
    import signal

    from app.queue_store import QueueStore

    calls: list[str] = []

    def forbidden(name: str):
        def fail(*_args: Any, **_kwargs: Any) -> None:
            calls.append(name)
            raise AssertionError(f"worker import reached {name}")

        return fail

    monkeypatch.setattr(asyncio, "run", forbidden("asyncio.run"))
    monkeypatch.setattr(signal, "signal", forbidden("signal.signal"))
    monkeypatch.setattr(QueueStore, "claim_next", forbidden("QueueStore.claim_next"))
    sys.modules.pop("app.worker", None)

    module = importlib.import_module("app.worker")
    assert module._stop is False
    assert calls == []


def test_main_entrypoint_is_guarded_by_dunder_main() -> None:
    tree = _tree(WORKER_PATH)
    guards = [
        node
        for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
    ]
    assert len(guards) == 1
    assert _call_names(guards[0]) == ["main"]
