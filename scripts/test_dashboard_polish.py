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
# v0.7.2-UI-E-B-R：開啟 dashboard auth gate（未登入 redirect，登入才看 markers）。
_DASH_TOKEN = "ui-e-b-r-test-token"
os.environ["DASHBOARD_AUTH_ENABLED"] = "true"
os.environ["DASHBOARD_TOKEN"] = _DASH_TOKEN

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
    # 另外放一筆 failed，讓 overview 的「Owner 待處理」焦點面板呈現群組（非空態）。
    q.enqueue(task_id="p_queued", title="待跑任務", task_text="do something useful",
              safety_level=0, payload={"metadata": {}}, initial_status="queued")
    q.enqueue(task_id="p_done", title="完成任務", task_text="x", safety_level=0,
              payload={"metadata": {}}, initial_status="queued")
    q.enqueue(task_id="p_failed", title="失敗任務", task_text="x", safety_level=0,
              payload={"metadata": {}}, initial_status="queued")
    q.claim_next()  # 把最舊的 p_queued 變 running？ 不一定——改用直接 setup
    # 為了穩定，直接設定固定狀態（測試夾具，不是被測邏輯）
    conn = q._connect()
    try:
        conn.execute("UPDATE queue SET status='completed' WHERE task_id='p_done'")
        conn.execute("UPDATE queue SET status='queued' WHERE task_id='p_queued'")
        conn.execute("UPDATE queue SET status='failed' WHERE task_id='p_failed'")
        conn.commit()
    finally:
        conn.close()

    counts_before = q.counts_by_status()

    print("[0] auth gate：未登入 /dashboard 應 redirect 到 login")
    unauth = TestClient(main.app)
    r = unauth.get("/dashboard", follow_redirects=False)
    _check(r.status_code in (303, 307), f"未登入 /dashboard redirect（status={r.status_code}）")
    _check("/dashboard/login" in r.headers.get("location", ""), "redirect 指向 /dashboard/login")

    # 已登入 client：帶 X-Dashboard-Token 才能讀 dashboard markers。
    client = TestClient(main.app)
    client.headers.update({"X-Dashboard-Token": _DASH_TOKEN})

    print("[1-3] /dashboard 控制台總覽（已登入）")
    r = client.get("/dashboard")
    _check(r.status_code == 200, "/dashboard 200")
    body = r.text
    _check("Hermes x OpenClaw Queue Control Board" in body, "首頁含 Control Board 標題")
    _check("系統健康" in body, "首頁含 系統健康（System Health）卡")
    _check("工單統計" in body, "首頁含 工單統計（Queue Counts）卡")
    _check("快速連結" in body, "首頁含 快速連結（Quick Links）")
    _check("查看任務" in body and "待審核項目" in body
           and "最近錯誤" in body, "快速連結 含 查看任務 / 待審核項目 / 最近錯誤")
    # UI-E-B：Owner 待處理 焦點面板與群組。
    for marker in ("Owner 待處理", "待審核任務", "最近錯誤", "需要人工確認", "下一步建議"):
        _check(marker in body, f"首頁 Owner 待處理 含 {marker}")

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
    # UI-E-B：任務詳情 Owner 審核面板。
    for marker in ("Owner 審核面板", "是否可核准", "安全邊界"):
        _check(marker in body, f"task detail 含 Owner 審核面板 marker {marker}")

    print("[8-9] /dashboard/reviews 空狀態")
    r = client.get("/dashboard/reviews")
    _check(r.status_code == 200, "/dashboard/reviews 200")
    body = r.text
    _check("Pending Reviews" in body, "reviews 頁含標題與 count")
    _check("目前沒有待審核任務" in body or "empty-state" in body, "reviews 空狀態訊息")
    # UI-E-B：Owner 審核佇列 面板與安全提醒（空狀態也會顯示）。
    for marker in ("Owner 審核佇列", "核准前請確認風險", "拒絕會保留任務記錄"):
        _check(marker in body, f"reviews 含 Owner 審核佇列 marker {marker}")

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
