"""GET-only coverage for the adapter display surface.

The harness deliberately makes every worker, claim, dispatch, callback, and
background-task entry point raise.  Every HTTP request issued by this module is
GET, so this file cannot exercise the dashboard's existing POST controls.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def get_only_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Any, TestClient, Any]]:
    import app.main as main

    data_dir = tmp_path / "data"
    db_path = data_dir / "queue.sqlite3"
    monkeypatch.setattr(main, "DATA_DIR", data_dir)
    monkeypatch.setattr(main, "TASKS_PATH", data_dir / "tasks.jsonl")
    monkeypatch.setattr(main, "RESULTS_PATH", data_dir / "results.jsonl")
    monkeypatch.setattr(main, "QUEUE_DB_PATH", str(db_path))
    monkeypatch.setattr(main, "EXECUTION_MODE", "queue")
    monkeypatch.setattr(main, "HERMES_ADAPTER_TOKEN", "")
    monkeypatch.setattr(main, "DASHBOARD_AUTH_ENABLED", False)
    monkeypatch.setattr(main, "_queue_store", None)
    monkeypatch.setattr(main, "_blackboard_store", None)
    monkeypatch.setattr(main, "_health_store", None)

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("GET-only coverage reached claim/dispatch/execution")

    async def forbidden_async(*args: Any, **kwargs: Any) -> None:
        forbidden(*args, **kwargs)

    monkeypatch.setattr(main, "dispatch_task", forbidden_async)
    monkeypatch.setattr(main, "run_openclaw_cli", forbidden_async)
    monkeypatch.setattr(main, "run_openclaw_and_callback", forbidden_async)
    monkeypatch.setattr(main, "send_callback_to_hermes", forbidden_async)
    monkeypatch.setattr(main.BackgroundTasks, "add_task", forbidden)

    queue = main.get_queue()
    monkeypatch.setattr(queue, "claim_next", forbidden)
    for task_id, status in (
        ("task-get-queued", "queued"),
        ("task-get-review", "waiting_review"),
        ("task-get-failed", "queued"),
    ):
        row = queue.enqueue(
            task_id=task_id,
            title=f"title {task_id}",
            task_text=f"text {task_id}",
            safety_level=1,
            payload={
                "metadata": {
                    "synthetic_local_only": True,
                    "requires_confirmation": status == "waiting_review",
                    "worker_dispatch_allowed": False,
                }
            },
            initial_status=status,
        )
        assert row is not None
    assert queue.mark_failed("task-get-failed", error="synthetic failure")

    with TestClient(main.app) as client:
        yield main, client, queue

    main._queue_store = None
    main._blackboard_store = None
    main._health_store = None


def test_json_get_routes_cover_queue_and_system_views(get_only_harness) -> None:
    main, client, _queue = get_only_harness
    expectations = {
        "/health": 200,
        "/queue": 200,
        "/queue/overview": 200,
        "/queue/tasks?limit=999&offset=-5": 200,
        "/queue/tasks?status=not-a-status": 400,
        "/queue/recent-errors?limit=999": 200,
        "/queue/health": 200,
        "/queue/tasks/task-get-queued": 200,
        "/queue/tasks/missing": 404,
        "/tasks/task-get-queued": 200,
        "/tasks/task-get-queued/result": 200,
        "/tasks/missing": 404,
        "/tasks/missing/result": 404,
        "/tasks": 200,
        "/tasks/task-get-queued/comments": 200,
        "/tasks/missing/comments": 404,
        "/reviews/pending?limit=999&offset=-2": 200,
        "/system/health": 200,
        "/system/worker": 200,
    }
    for path, status in expectations.items():
        response = client.get(path)
        assert response.status_code == status, path

    assert client.get("/queue/tasks").json()["total"] == 3
    assert client.get("/queue/recent-errors").json()["items"][0]["task_id"] == "task-get-failed"
    assert client.get("/reviews/pending").json()["items"][0]["task_id"] == "task-get-review"
    assert main.EXECUTION_MODE == "queue"


def test_dashboard_get_routes_render_without_controls(get_only_harness) -> None:
    _main, client, _queue = get_only_harness
    expectations = {
        "/": 200,
        "/dashboard/login": 200,
        "/dashboard/logout": 200,
        "/dashboard": 200,
        "/dashboard/tasks?limit=1&offset=1": 200,
        "/dashboard/tasks?status=not-a-status": 200,
        "/dashboard/tasks/task-get-queued": 200,
        "/dashboard/tasks/missing": 404,
        "/dashboard/reviews?limit=1": 200,
        "/dashboard/system": 200,
    }
    for path, status in expectations.items():
        response = client.get(path, follow_redirects=True)
        assert response.status_code == status, path


def test_background_mode_get_branches_are_read_only(get_only_harness, monkeypatch) -> None:
    main, client, _queue = get_only_harness
    monkeypatch.setattr(main, "EXECUTION_MODE", "background")

    for path in (
        "/queue",
        "/queue/overview",
        "/queue/tasks",
        "/queue/recent-errors",
        "/queue/health",
        "/reviews/pending",
        "/dashboard",
        "/dashboard/tasks",
        "/dashboard/reviews",
        "/system/health",
    ):
        assert client.get(path).status_code == 200, path
    assert client.get("/queue/tasks/task-get-queued").status_code == 404
    assert client.get("/dashboard/tasks/task-get-queued").status_code == 404


def test_display_helpers_and_fail_closed_read_helpers(get_only_harness, monkeypatch) -> None:
    main, _client, queue = get_only_harness
    long_id = "abcdefghijklmno"
    assert main.short_task_id(None) == ""
    assert main.short_task_id("short") == "short"
    assert main.short_task_id(long_id, head=4, tail=3) != long_id
    assert main.truncate(None) == ""
    assert main.truncate("  one\ntwo  ", 20) == "one two"
    assert len(main.truncate("abcdefgh", 5)) == 5
    assert main.status_class(None).endswith("unknown")
    assert main.status_class(" queued ") == "badge badge-queued"
    assert main.format_empty(None, "fallback") == "fallback"
    assert main.format_empty("  ", "fallback") == "fallback"
    assert main.format_empty(" value ") == "value"
    assert main.yesno(True) == "yes"
    assert main.yesno(False) == "no"

    assert main._parse_payload_metadata(None) == {}
    assert main._parse_payload_metadata("{broken") == {}
    assert main._parse_payload_metadata("[]") == {}
    assert main._parse_payload_metadata('{"metadata": []}') == {}
    assert main._parse_payload_metadata('{"metadata": {"safe": true}}') == {"safe": True}
    assert main._obs_worker_status({"running": 1})["status"] == "online"
    assert main._obs_worker_status({})["status"] == "unknown"

    row = queue.get("task-get-queued")
    assert row is not None
    assert main._obs_task_summary(row)["task_id"] == "task-get-queued"
    assert main._obs_task_detail(row)["task_id"] == "task-get-queued"
    assert main._review_summary(row)["annotation"]["dispatch_allowed"] is False

    monkeypatch.setattr(main, "get_health", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    assert main._worker_snapshot()["status"] == "unknown"


def test_cli_probe_never_executes_and_auth_gate_is_get_only(
    get_only_harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    main, client, _queue = get_only_harness
    monkeypatch.setattr(main, "OPENCLAW_CLI_BIN", "missing-openclaw")
    monkeypatch.setattr("shutil.which", lambda _name: None)
    assert main._openclaw_cli_status()["cli_path_exists"] is False

    monkeypatch.setattr(main, "OPENCLAW_CLI_BIN", str(Path("missing") / "openclaw"))
    monkeypatch.setattr(main.os.path, "isfile", lambda _path: True)
    monkeypatch.setattr(main.os, "access", lambda *_args: True)
    assert main._openclaw_cli_status()["cli_path_exists"] is True

    monkeypatch.setattr(main, "DASHBOARD_AUTH_ENABLED", True)
    monkeypatch.setattr(main, "DASHBOARD_TOKEN", "")
    assert client.get("/dashboard", follow_redirects=False).status_code == 303
    assert client.get("/dashboard/login").status_code == 200

    monkeypatch.setattr(main, "DASHBOARD_TOKEN", "synthetic-dashboard-token")
    unauthenticated = client.get("/dashboard", follow_redirects=False)
    assert unauthenticated.status_code == 303
    authenticated = client.get(
        "/dashboard",
        headers={"X-Dashboard-Token": "synthetic-dashboard-token"},
    )
    assert authenticated.status_code == 200

    by_query = client.get("/dashboard?dashboard_token=synthetic-dashboard-token")
    assert by_query.status_code == 200


def test_queue_health_get_fails_closed_without_crashing(
    get_only_harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    main, client, queue = get_only_harness

    def unreadable_counts() -> dict[str, int]:
        raise RuntimeError("synthetic unreadable queue")

    monkeypatch.setattr(queue, "counts_by_status", unreadable_counts)
    response = client.get("/queue/health")
    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["counts"] == {}


def test_package_does_not_issue_post_or_touch_worker_contract(get_only_harness) -> None:
    main, _client, _queue = get_only_harness
    untouched_post_routes = sorted(
        (method, route.path)
        for route in main.app.routes
        for method in (getattr(route, "methods", set()) or set())
        if method in {"POST", "PUT", "PATCH", "DELETE"}
    )
    assert untouched_post_routes == [
        ("POST", "/dashboard/login"),
        ("POST", "/dashboard/tasks/{task_id}/approve"),
        ("POST", "/dashboard/tasks/{task_id}/archive"),
        ("POST", "/dashboard/tasks/{task_id}/cancel"),
        ("POST", "/dashboard/tasks/{task_id}/comments"),
        ("POST", "/dashboard/tasks/{task_id}/reject"),
        ("POST", "/dashboard/tasks/{task_id}/retry"),
        ("POST", "/tasks/dispatch"),
        ("POST", "/tasks/{task_id}/approve"),
        ("POST", "/tasks/{task_id}/archive"),
        ("POST", "/tasks/{task_id}/cancel"),
        ("POST", "/tasks/{task_id}/comments"),
        ("POST", "/tasks/{task_id}/reject"),
        ("POST", "/tasks/{task_id}/retry"),
    ]
