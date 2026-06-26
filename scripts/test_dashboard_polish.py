#!/usr/bin/env python3
"""v0.5.7 — Dashboard Polish / UX Cleanup 測試。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證。
只驗證 UI 呈現與「不改任務狀態」，不啟動 worker、不呼叫 OpenClaw。

涵蓋任務要求 1–14。
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="polish_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""
os.environ["CALLBACK_ENABLED"] = "false"
os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app import main  # noqa: E402

FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    if cond:
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def main_test() -> int:
    q = main.get_queue()
    # 只放非 waiting_review 任務，讓 reviews 頁呈現空狀態。
    q.enqueue(task_id="p_queued", title="待跑任務", task_text="do something useful",
              safety_level=0, payload={"metadata": {}}, initial_status="queued")
    q.enqueue(task_id="p_done", title="完成任務", task_text="x", safety_level=0,
              payload={"metadata": {}}, initial_status="queued")
    q.claim_next()  # 把最舊的 p_queued 變 running？ 不一定——改用直接 setup
    # 為了穩定，直接把 p_done 設成 completed（測試夾具，不是被測邏輯）
    conn = q._connect()
    try:
        conn.execute("UPDATE queue SET status='completed' WHERE task_id='p_done'")
        conn.execute("UPDATE queue SET status='queued' WHERE task_id='p_queued'")
        conn.commit()
    finally:
        conn.close()

    counts_before = q.counts_by_status()

    client = TestClient(main.app)

    print("[1-3] /dashboard 控制台總覽")
    r = client.get("/dashboard")
    _check(r.status_code == 200, "/dashboard 200")
    body = r.text
    _check("Hermes x OpenClaw Queue Control Board" in body, "首頁含 Control Board 標題")
    _check("System Health" in body, "首頁含 System Health 卡")
    _check("Queue Counts" in body, "首頁含 Queue Counts 卡")
    _check("Quick Links" in body, "首頁含 Quick Links")
    _check("View Tasks" in body and "Pending Reviews" in body
           and "Recent Errors" in body, "Quick Links 含 View Tasks / Pending Reviews / Recent Errors")

    print("[4-5] /dashboard/tasks 狀態篩選")
    r = client.get("/dashboard/tasks")
    _check(r.status_code == 200, "/dashboard/tasks 200")
    body = r.text
    _check("filter-pill" in body, "tasks 頁含篩選 pill")
    for label in ("All", "Queued", "Running", "Waiting Review", "Failed",
                  "Completed", "Cancelled", "Rejected", "Archived"):
        _check(label in body, f"tasks 篩選含 {label}")
    _check('href="/dashboard/tasks?status=failed' in body, "篩選是連結（保留 query params）")

    print("[6-7] /dashboard/tasks/{id} 詳情分區")
    r = client.get("/dashboard/tasks/p_queued")
    _check(r.status_code == 200, "task detail 200")
    body = r.text
    for section in ("Summary", "Task Text", "Result", "Error", "Metadata",
                    "Blackboard Comments", "Safe Controls"):
        _check(section in body, f"detail 含分區 {section}")
    _check("No result yet." in body, "result 為空顯示 muted 'No result yet.'")
    _check("No error." in body, "error 為空顯示 muted 'No error.'")

    print("[8-9] /dashboard/reviews 空狀態")
    r = client.get("/dashboard/reviews")
    _check(r.status_code == 200, "/dashboard/reviews 200")
    body = r.text
    _check("Pending Reviews" in body, "reviews 頁含標題與 count")
    _check("目前沒有待審核任務" in body or "empty-state" in body, "reviews 空狀態訊息")

    print("[10-11] /dashboard/system")
    r = client.get("/dashboard/system")
    _check(r.status_code == 200, "/dashboard/system 200")
    body = r.text
    _check("checked without execution" in body, "system 顯示 checked without execution")
    _check("Worker Heartbeat" in body, "system 含 Worker Heartbeat 區")

    print("[12] Dashboard polish 不改 queue 任務狀態")
    counts_after = q.counts_by_status()
    _check(counts_before == counts_after, f"counts 不變（{counts_before} == {counts_after}）")
    _check(q.get("p_queued")["status"] == "queued", "p_queued 仍 queued")
    _check(q.get("p_done")["status"] == "completed", "p_done 仍 completed")

    print("[13] 不啟動 worker")
    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()],
           "沒有 worker 執行緒")

    print("[14] 不呼叫 OpenClaw CLI")
    _check(not main.RESULTS_PATH.exists() or main.RESULTS_PATH.stat().st_size == 0,
           "沒有 results.jsonl（沒有執行 OpenClaw）")

    if FAILURES:
        print(f"\n❌ Dashboard Polish 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Dashboard Polish / UX Cleanup 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
