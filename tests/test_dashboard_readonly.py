from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient


EXPLICIT_DASHBOARD_ROUTE_ALLOWLIST = {
    ("GET", "/dashboard/login"),
    ("POST", "/dashboard/login"),
    ("GET", "/dashboard/logout"),
    ("GET", "/dashboard"),
    ("GET", "/dashboard/tasks"),
    ("GET", "/dashboard/tasks/{task_id}"),
    ("POST", "/dashboard/tasks/{task_id}/comments"),
    ("GET", "/dashboard/reviews"),
    ("POST", "/dashboard/tasks/{task_id}/approve"),
    ("POST", "/dashboard/tasks/{task_id}/reject"),
    ("POST", "/dashboard/tasks/{task_id}/cancel"),
    ("POST", "/dashboard/tasks/{task_id}/retry"),
    ("POST", "/dashboard/tasks/{task_id}/archive"),
    ("GET", "/dashboard/system"),
}

EXPLICIT_POST_EXCEPTIONS = {
    "/dashboard/login",
    "/dashboard/tasks/{task_id}/comments",
    "/dashboard/tasks/{task_id}/approve",
    "/dashboard/tasks/{task_id}/reject",
    "/dashboard/tasks/{task_id}/cancel",
    "/dashboard/tasks/{task_id}/retry",
    "/dashboard/tasks/{task_id}/archive",
}

GET_CONTROL_SURFACE_EXCEPTIONS = {
    "/dashboard/login",  # existing login form
    "/dashboard/logout",  # existing GET logout redirect
    "/dashboard/tasks",  # existing GET-only filter form
    "/dashboard/tasks/{task_id}",  # existing named task controls
    "/dashboard/reviews",  # existing approve/reject controls
}


@dataclass
class DashboardHarness:
    main: ModuleType
    client: TestClient
    queue: Any
    status_events: list[tuple[str, str, dict[str, Any]]]


def _dashboard_route_inventory(app: Any) -> set[tuple[str, str]]:
    inventory: set[tuple[str, str]] = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        if not path.startswith("/dashboard"):
            continue
        for method in getattr(route, "methods", set()) or set():
            if method in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                inventory.add((method, path))
    return inventory


def _assert_readonly_html(html: str) -> None:
    normalized = html.lower()
    assert "<form" not in normalized
    assert "<button" not in normalized
    assert 'method="post"' not in normalized
    assert "method='post'" not in normalized


def _payload(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("payload")
    if isinstance(value, str):
        parsed = json.loads(value)
        assert isinstance(parsed, dict)
        return parsed
    assert isinstance(value, dict)
    return value


def _latest_decision_event(row: dict[str, Any]) -> dict[str, Any]:
    events = _payload(row)["metadata"]["approval_decision_events"]
    assert isinstance(events, list) and events
    event = events[-1]
    assert isinstance(event, dict)
    return event


@pytest.fixture
def dashboard_harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[DashboardHarness]:
    import app.main as main

    db_path = tmp_path / "dashboard-readonly.sqlite3"
    monkeypatch.setattr(main, "QUEUE_DB_PATH", str(db_path))
    monkeypatch.setattr(main, "EXECUTION_MODE", "queue")
    monkeypatch.setattr(main, "DASHBOARD_AUTH_ENABLED", False)
    monkeypatch.setattr(main, "_queue_store", None)
    monkeypatch.setattr(main, "_blackboard_store", None)
    monkeypatch.setattr(main, "_health_store", None)

    status_events: list[tuple[str, str, dict[str, Any]]] = []

    def capture_status(task_id: str, status: str, **extra: Any) -> None:
        status_events.append((task_id, status, extra))

    def forbidden_sync(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("dashboard control reached a dispatch/execution path")

    async def forbidden_async(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("dashboard control reached a dispatch/execution path")

    monkeypatch.setattr(main, "append_task_status", capture_status)
    monkeypatch.setattr(main, "run_openclaw_cli", forbidden_async)
    monkeypatch.setattr(main, "run_openclaw_and_callback", forbidden_async)
    monkeypatch.setattr(main, "send_callback_to_hermes", forbidden_async)
    monkeypatch.setattr(main, "dispatch_task", forbidden_async)
    monkeypatch.setattr(main.BackgroundTasks, "add_task", forbidden_sync)

    queue = main.get_queue()
    monkeypatch.setattr(queue, "claim_next", forbidden_sync)

    with TestClient(main.app) as client:
        yield DashboardHarness(main, client, queue, status_events)

    main._queue_store = None
    main._blackboard_store = None
    main._health_store = None


def _enqueue(harness: DashboardHarness, task_id: str, *, status: str = "queued") -> None:
    created = harness.queue.enqueue(
        task_id=task_id,
        title="synthetic dashboard safety test",
        task_text="synthetic local-only task",
        safety_level=1,
        payload={
            "metadata": {
                "synthetic_local_only": True,
                "worker_dispatch_allowed": False,
            }
        },
        initial_status=status,
    )
    assert created is not None


def test_dashboard_route_inventory_is_exact_and_dynamic(dashboard_harness: DashboardHarness) -> None:
    inventory = _dashboard_route_inventory(dashboard_harness.main.app)

    assert inventory == EXPLICIT_DASHBOARD_ROUTE_ALLOWLIST
    assert {path for method, path in inventory if method == "POST"} == EXPLICIT_POST_EXCEPTIONS


def test_non_control_dashboard_get_routes_are_readonly(dashboard_harness: DashboardHarness) -> None:
    inventory = _dashboard_route_inventory(dashboard_harness.main.app)
    readonly_gets = sorted(
        path
        for method, path in inventory
        if method == "GET" and path not in GET_CONTROL_SURFACE_EXCEPTIONS
    )

    assert readonly_gets == ["/dashboard", "/dashboard/system"]
    for path in readonly_gets:
        response = dashboard_harness.client.get(path)
        assert response.status_code == 200, path
        _assert_readonly_html(response.text)


def test_in_memory_button_injection_proves_readonly_guard_fails(
    dashboard_harness: DashboardHarness,
) -> None:
    response = dashboard_harness.client.get("/dashboard")
    assert response.status_code == 200
    _assert_readonly_html(response.text)

    injected = response.text.replace("</main>", '<button type="submit">injected</button></main>')
    with pytest.raises(AssertionError):
        _assert_readonly_html(injected)


def test_review_approve_records_inert_decision_without_dispatch(
    dashboard_harness: DashboardHarness,
) -> None:
    task_id = "task-dashboard-approve-readonly"
    _enqueue(dashboard_harness, task_id, status="waiting_review")

    response = dashboard_harness.client.post(
        f"/dashboard/tasks/{task_id}/approve", follow_redirects=False
    )

    assert response.status_code == 303
    row = dashboard_harness.queue.get(task_id)
    assert row is not None
    assert row["status"] == "queued"
    assert row["attempts"] == 0
    event = _latest_decision_event(row)
    assert event["decision_type"] == "approve"
    assert event["execution_permission_at_decision"] is False
    assert event["dispatch_allowed_at_decision"] is False
    assert event["audit_record"]["append_only"] is True
    assert dashboard_harness.status_events == [
        (task_id, "queued", {"via": "dashboard-approve"})
    ]


def test_comment_exception_writes_comment_only_without_dispatch(
    dashboard_harness: DashboardHarness,
) -> None:
    task_id = "task-dashboard-comment-readonly"
    _enqueue(dashboard_harness, task_id, status="waiting_review")
    before = dashboard_harness.queue.get(task_id)

    response = dashboard_harness.client.post(
        f"/dashboard/tasks/{task_id}/comments",
        data={
            "author_type": "user",
            "author_name": "owner",
            "content": "synthetic review note",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    after = dashboard_harness.queue.get(task_id)
    assert before is not None and after is not None
    assert after["status"] == before["status"]
    assert after["attempts"] == before["attempts"] == 0
    comments = dashboard_harness.main.get_blackboard().list_for_task(task_id)
    assert len(comments) == 1
    assert comments[0]["content"] == "synthetic review note"
    assert dashboard_harness.status_events == []


@pytest.mark.parametrize(
    "action,source_status,expected_status",
    (
        ("cancel", "queued", "cancelled"),
        ("retry", "failed", "queued"),
        ("archive", "completed", "archived"),
    ),
)
def test_named_control_exceptions_transition_only_and_never_dispatch(
    dashboard_harness: DashboardHarness,
    action: str,
    source_status: str,
    expected_status: str,
) -> None:
    task_id = f"task-dashboard-{action}-readonly"
    _enqueue(dashboard_harness, task_id)
    if source_status == "failed":
        assert dashboard_harness.queue.mark_failed(task_id, error="synthetic failure")
    elif source_status == "completed":
        assert dashboard_harness.queue.mark_completed(task_id)

    response = dashboard_harness.client.post(
        f"/dashboard/tasks/{task_id}/{action}",
        data={"reason": "synthetic owner control"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    row = dashboard_harness.queue.get(task_id)
    assert row is not None
    assert row["status"] == expected_status
    assert row["attempts"] == 0
    event = _latest_decision_event(row)
    assert event["decision_type"] == action
    assert event["execution_permission_at_decision"] is False
    assert event["dispatch_allowed_at_decision"] is False
    assert event["audit_record"]["append_only"] is True
    assert dashboard_harness.status_events == [
        (
            task_id,
            expected_status,
            {"via": f"dashboard-{action}", "reason": "synthetic owner control"},
        )
    ]
