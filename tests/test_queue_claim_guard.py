"""Guard the current queue-claim boundary without changing application behavior.

Known risk: approving a task moves it to ``queued``; if an external process
starts the Worker, that task can then be claimed.  The execution gate belongs
to Phase 9 and does not exist yet.
"""

from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from app.queue_store import QueueStore


ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"
RISKY_ATTRIBUTE_CALLS = {"claim_next", "start", "run_forever"}
MOCK_EXCEPTION_PATH = Path("app/mock_e2e_v0_7.py")
MOCK_QUEUE_CLASS = "InMemoryMockQueue"


def _is_worker_import(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(
            alias.name == "app.worker" or alias.name.startswith("app.worker.")
            for alias in node.names
        )
    if isinstance(node, ast.ImportFrom) and node.module:
        return node.module == "app.worker" or node.module.startswith("app.worker.")
    return False


def _locally_instantiated_receivers(
    tree: ast.Module, required_class_name: str
) -> set[str]:
    receivers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
            continue
        if value.func.id != required_class_name:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        receivers.update(
            target.id for target in targets if isinstance(target, ast.Name)
        )
    return receivers


def _is_exact_in_memory_mock_exception(
    relative_path: Path,
    call: ast.Call,
    local_class_names: set[str],
    local_receivers: set[str],
) -> bool:
    if relative_path != MOCK_EXCEPTION_PATH:
        return False
    if MOCK_QUEUE_CLASS not in local_class_names:
        return False
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr != "claim_next" or not isinstance(call.func.value, ast.Name):
        return False
    return call.func.value.id in local_receivers


def test_ast_allows_only_the_exact_local_in_memory_claim_exception() -> None:
    violations: list[str] = []
    for source_path in sorted(APP_DIR.rglob("*.py")):
        relative_path = source_path.relative_to(ROOT)
        if relative_path == Path("app/worker.py"):
            continue

        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        local_class_names = {
            node.name for node in tree.body if isinstance(node, ast.ClassDef)
        }
        local_receivers = _locally_instantiated_receivers(tree, MOCK_QUEUE_CLASS)

        for node in ast.walk(tree):
            if _is_worker_import(node):
                violations.append(f"{relative_path}:{node.lineno}: app.worker import")
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in RISKY_ATTRIBUTE_CALLS:
                continue
            if _is_exact_in_memory_mock_exception(
                relative_path, node, local_class_names, local_receivers
            ):
                continue
            violations.append(
                f"{relative_path}:{node.lineno}: .{node.func.attr}(...) call"
            )

    assert violations == []


def _dashboard_get_paths(app: Any, task_id: str) -> list[str]:
    paths: list[str] = []
    for route in app.routes:
        route_path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()
        if route_path.startswith("/dashboard") and "GET" in methods:
            paths.append(route_path.replace("{task_id}", task_id))
    return sorted(paths)


def test_app_import_all_dashboard_gets_and_approve_never_claim(
    tmp_path: Path, monkeypatch: Any
) -> None:
    claim_attempts: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def forbidden_claim(*args: Any, **kwargs: Any) -> None:
        claim_attempts.append((args, kwargs))
        raise AssertionError("dashboard/import path reached QueueStore.claim_next")

    monkeypatch.setattr(QueueStore, "claim_next", forbidden_claim)
    sys.modules.pop("app.main", None)
    main = importlib.import_module("app.main")

    monkeypatch.setattr(main, "QUEUE_DB_PATH", str(tmp_path / "queue-guard.sqlite3"))
    monkeypatch.setattr(main, "EXECUTION_MODE", "queue")
    monkeypatch.setattr(main, "DASHBOARD_AUTH_ENABLED", False)
    monkeypatch.setattr(main, "_queue_store", None)
    monkeypatch.setattr(main, "_blackboard_store", None)
    monkeypatch.setattr(main, "_health_store", None)

    queue = main.get_queue()
    task_id = "task-queue-claim-guard"
    queue.enqueue(
        task_id=task_id,
        title="synthetic queue claim guard",
        task_text="synthetic local-only review task",
        safety_level=1,
        payload={
            "metadata": {
                "synthetic_local_only": True,
                "worker_dispatch_allowed": False,
            }
        },
        initial_status="waiting_review",
    )

    with TestClient(main.app) as client:
        get_paths = _dashboard_get_paths(main.app, task_id)
        assert get_paths
        for path in get_paths:
            response = client.get(path, follow_redirects=False)
            assert response.status_code in {200, 303}, path

        response = client.post(
            f"/dashboard/tasks/{task_id}/approve", follow_redirects=False
        )
        assert response.status_code == 303

    row = queue.get(task_id)
    assert row is not None
    assert row["status"] == "queued"
    assert row["attempts"] == 0
    payload = row["payload"]
    if isinstance(payload, str):
        payload = json.loads(payload)
    event = payload["metadata"]["approval_decision_events"][-1]
    assert event["dispatch_allowed_at_decision"] is False
    assert event["execution_permission_at_decision"] is False
    assert claim_attempts == []

    main._queue_store = None
    main._blackboard_store = None
    main._health_store = None
