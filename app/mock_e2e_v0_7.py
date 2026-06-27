"""v0.7.0-D — 純 mock 的 End-to-End dry-run（假任務跑一圈，不接任何真系統）。

讓 mock Hermes request 走完整一圈：
  mock request
    → mock Adapter（prepare_queue_candidate_from_mock_request，v0.7.0-C）
    → 若 pending_approval：停在 approval gate，不進 worker
    → 若 queued：InMemoryMockQueue → mock worker → mock CallbackEvent → 更新 task
  最後回傳可驗證的 dry-run 結果。

mock-only：
  - 不接真 Hermes / 真 OpenClaw / 真 webhook。
  - 不寫真 Queue DB、不 import queue_store / sqlite3、不 import / 啟動真 worker。
  - 不寫 Result Sink、不寫 Google Sheets、不讀任何 secret、不做 network call。
  - 僅用標準庫（uuid / datetime）與 in-memory 結構（list / dict）。

公開 API：
  class MockE2EError(Exception)
  class InMemoryMockQueue
  mock_worker_process_task(task_envelope: dict) -> dict
  apply_callback_to_mock_task(task_envelope: dict, callback_event: dict) -> dict
  run_mock_e2e_dry_run(request: dict) -> dict
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.contracts_v0_7 import validate_callback_event, validate_task_envelope
from app.mock_adapter_v0_7 import prepare_queue_candidate_from_mock_request

MOCK_WORKER_SOURCE = "mock-openclaw-worker"


class MockE2EError(Exception):
    """mock E2E dry-run 流程錯誤時 raise。"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class InMemoryMockQueue:
    """純 in-memory mock queue（list + dict）。不是真 Queue DB，不落地、不連任何系統。"""

    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._order: List[str] = []

    def enqueue(self, task_envelope: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(task_envelope, dict) or "task_id" not in task_envelope:
            raise MockE2EError("enqueue 需要含 task_id 的 task_envelope")
        task_id = task_envelope["task_id"]
        self._tasks[task_id] = dict(task_envelope)
        self._order.append(task_id)
        return self._tasks[task_id]

    def claim_next(self) -> Optional[Dict[str, Any]]:
        """取出最舊的 queued 任務，標為 running，回傳其 copy（無則回 None）。"""
        for task_id in self._order:
            task = self._tasks.get(task_id)
            if task is not None and task.get("status") == "queued":
                task["status"] = "running"
                return dict(task)
        return None

    def mark_completed(self, task_id: str, callback_event: Dict[str, Any]) -> Dict[str, Any]:
        return self._mark(task_id, "completed", callback_event)

    def mark_failed(self, task_id: str, callback_event: Dict[str, Any]) -> Dict[str, Any]:
        return self._mark(task_id, "failed", callback_event)

    def _mark(self, task_id: str, status: str, callback_event: Dict[str, Any]) -> Dict[str, Any]:
        if task_id not in self._tasks:
            raise MockE2EError(f"mark：找不到 task_id {task_id}")
        self._tasks[task_id]["status"] = status
        self._tasks[task_id]["last_callback_event_id"] = callback_event.get("event_id")
        return dict(self._tasks[task_id])

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        return dict(task) if task is not None else None


def mock_worker_process_task(task_envelope: Dict[str, Any]) -> Dict[str, Any]:
    """假 Worker：依 task_type 產生 completed 或 failed 的 CallbackEvent（不做任何真事）。

    task_type = mock.fail → failed callback（retryable=true, error_code=MOCK_FAILURE）
    其他                  → completed callback（retryable=false）
    """
    if not isinstance(task_envelope, dict) or "task_id" not in task_envelope:
        raise MockE2EError("mock_worker_process_task 需要含 task_id 的 task_envelope")

    task_id = task_envelope["task_id"]
    base: Dict[str, Any] = {
        "event_id": f"event-{uuid.uuid4()}",
        "task_id": task_id,
        "source": MOCK_WORKER_SOURCE,
        "created_at": _utc_now_iso(),
        "metadata": {"mock": True, "dry_run": True},
    }

    if task_envelope.get("task_type") == "mock.fail":
        callback = {
            **base,
            "event_type": "failed",
            "status": "failed",
            "summary": "Mock worker reported a (requested) failure.",
            "retryable": True,
            "error_code": "MOCK_FAILURE",
            "error_message": "Mock failure requested",
            "duration_ms": 1,
        }
    else:
        callback = {
            **base,
            "event_type": "completed",
            "status": "completed",
            "summary": "Mock worker completed the task (dry-run, no real work).",
            "retryable": False,
            "result_ref": None,
            "duration_ms": 1,
        }

    validate_callback_event(callback)
    return callback


def apply_callback_to_mock_task(
    task_envelope: Dict[str, Any], callback_event: Dict[str, Any]
) -> Dict[str, Any]:
    """依 callback 結果更新 task 的 copy（不寫 DB、不就地修改輸入）。

    completed → completed；failed → failed；cancelled → cancelled；其他 → callback_received
    """
    if not isinstance(task_envelope, dict):
        raise MockE2EError("task_envelope 必須為 dict")
    if not isinstance(callback_event, dict):
        raise MockE2EError("callback_event 必須為 dict")

    status_map = {
        "completed": "completed",
        "failed": "failed",
        "cancelled": "cancelled",
    }
    new_status = status_map.get(callback_event.get("status"), "callback_received")

    updated = dict(task_envelope)
    updated["status"] = new_status
    updated["last_callback_event_id"] = callback_event.get("event_id")
    validate_task_envelope(updated)
    return updated


def run_mock_e2e_dry_run(request: Dict[str, Any]) -> Dict[str, Any]:
    """跑完整 mock E2E dry-run，回傳可驗證的結果 dict。

    pending_approval 任務停在 approval gate（不進 worker、不產生 completed callback）；
    queued 任務才會進 mock worker，產生 CallbackEvent 並更新 task。
    """
    candidate = prepare_queue_candidate_from_mock_request(request)
    validate_task_envelope(candidate)

    task_id = candidate["task_id"]
    initial_status = candidate["status"]
    events: List[str] = [f"adapter.candidate:{initial_status}"]

    result: Dict[str, Any] = {
        "dry_run": True,
        "task_id": task_id,
        "initial_status": initial_status,
        "final_status": initial_status,
        "approval_required": candidate.get("approval_required"),
        "approval_status": candidate.get("approval_status"),
        "callback_event": None,
        "events": events,
        "stopped_at": None,
        "summary": "",
        "metadata": {"mock": True, "dry_run": True},
    }

    if initial_status == "pending_approval":
        events.append("approval_gate.stopped")
        result["stopped_at"] = "approval_gate"
        result["final_status"] = "pending_approval"
        result["summary"] = (
            "Mock E2E dry-run 停在 approval gate：任務需 Owner 批准，未進 mock worker。"
        )
        return result

    if initial_status != "queued":
        raise MockE2EError(f"非預期的初始 status：{initial_status}")

    queue = InMemoryMockQueue()
    queue.enqueue(candidate)
    events.append("queue.enqueued")

    claimed = queue.claim_next()
    if claimed is None:
        raise MockE2EError("claim_next 取不到 queued 任務")
    events.append("worker.claimed")

    callback = mock_worker_process_task(claimed)
    events.append(f"worker.callback:{callback['status']}")

    updated = apply_callback_to_mock_task(claimed, callback)
    if callback["status"] == "completed":
        queue.mark_completed(task_id, callback)
    elif callback["status"] == "failed":
        queue.mark_failed(task_id, callback)
    events.append(f"task.{updated['status']}")

    result["callback_event"] = callback
    result["final_status"] = updated["status"]
    result["summary"] = (
        f"Mock E2E dry-run 完成：task {task_id} 最終狀態 {updated['status']}（純 mock，未連任何系統）。"
    )
    return result
