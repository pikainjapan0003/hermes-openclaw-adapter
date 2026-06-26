#!/usr/bin/env python3
"""v0.5.5 — Limited Control Actions（Cancel / Retry / Archive）測試。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證。
不啟動 worker、不呼叫真實 OpenClaw、不改 .env。

狀態 setup 用直接 SQL（測試夾具），但「被測邏輯」一律走 API / QueueStore 狀態機。
涵蓋任務要求 1–32。
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="control_test_")
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


def seed(tid: str, status: str, attempts: int = 0, max_attempts: int = 3,
         error: str | None = None) -> str:
    """測試夾具：把任務直接寫成指定狀態（僅 setup，不是被測邏輯）。"""
    q = main.get_queue()
    if q.get(tid) is None:
        q.enqueue(task_id=tid, title=tid, task_text=f"do {tid}", safety_level=0,
                  payload={"title": tid, "metadata": {}}, initial_status="queued")
    conn = q._connect()
    try:
        conn.execute(
            "UPDATE queue SET status=?, attempts=?, max_attempts=?, error=? WHERE task_id=?",
            (status, attempts, max_attempts, error, tid),
        )
        conn.commit()
    finally:
        conn.close()
    return tid


def st(tid: str) -> str | None:
    item = main.get_queue().get(tid)
    return item["status"] if item else None


def main_test() -> int:
    client = TestClient(main.app)

    def post(action: str, tid: str, reason: str | None = None):
        body = {"reason": reason} if reason is not None else {}
        return client.post(f"/tasks/{tid}/{action}", json=body)

    print("[Cancel 1-2] queued / waiting_review 可 cancel -> cancelled")
    seed("c_q", "queued")
    r = post("cancel", "c_q", reason="使用者取消")
    _check(r.status_code == 200 and st("c_q") == "cancelled", "queued -> cancelled")
    _check(main.get_queue().get("c_q").get("error") == "使用者取消", "cancel reason 記到 error")
    seed("c_wr", "waiting_review")
    r = post("cancel", "c_wr")
    _check(r.status_code == 200 and st("c_wr") == "cancelled", "waiting_review -> cancelled")

    print("[Cancel 3-7] running/completed/failed/rejected/archived 不可 cancel -> 409")
    for state in ("running", "completed", "failed", "rejected", "archived"):
        tid = seed(f"c_{state}", state)
        r = post("cancel", tid)
        _check(r.status_code == 409, f"cancel {state} -> 409")
        _check(st(tid) == state, f"cancel {state} 狀態不變")
    # cancelled 不可再 cancel
    seed("c_cancelled", "cancelled")
    _check(post("cancel", "c_cancelled").status_code == 409, "cancel cancelled -> 409")

    print("[Retry 8] failed 可 retry -> queued（attempts 不歸零）")
    seed("r_failed", "failed", attempts=3, max_attempts=3, error="boom")
    r = post("retry", "r_failed", reason="手動重試")
    _check(r.status_code == 200 and st("r_failed") == "queued", "failed -> queued")
    item = main.get_queue().get("r_failed")
    _check(item.get("attempts") == 3, "retry 不歸零 attempts（維持 3）")
    _check(item.get("error") is None, "retry 清空 error（retry 原因記到 ledger/comment）")

    print("[Retry 9-15] 非 failed 不可 retry -> 409")
    for state in ("queued", "running", "completed", "waiting_review",
                  "rejected", "cancelled", "archived"):
        tid = seed(f"rr_{state}", state)
        r = post("retry", tid)
        _check(r.status_code == 409, f"retry {state} -> 409")
        _check(st(tid) == state, f"retry {state} 狀態不變")

    print("[Retry 16] retry 後不直接啟動 worker")
    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()],
           "retry 後沒有 worker 執行緒")

    print("[Archive 17-20] completed/failed/cancelled/rejected 可 archive -> archived")
    for state in ("completed", "failed", "cancelled", "rejected"):
        tid = seed(f"a_{state}", state, error="orig" if state == "failed" else None)
        r = post("archive", tid, reason="已處理")
        _check(r.status_code == 200 and st(tid) == "archived", f"{state} -> archived")
    _check(main.get_queue().get("a_failed").get("error") == "orig",
           "archive 保留原本 error（不刪資料）")

    print("[Archive 21-24] queued/running/waiting_review/archived 不可 archive -> 409")
    for state in ("queued", "running", "waiting_review", "archived"):
        tid = seed(f"aa_{state}", state)
        r = post("archive", tid)
        _check(r.status_code == 409, f"archive {state} -> 409")
        _check(st(tid) == state, f"archive {state} 狀態不變")

    print("[25] 不存在 task cancel/retry/archive -> 404")
    for action in ("cancel", "retry", "archive"):
        _check(post(action, "no-such-task").status_code == 404, f"{action} 不存在 -> 404")

    print("[26] Dashboard task detail 依狀態顯示正確控制按鈕")
    def detail(tid):
        return client.get(f"/dashboard/tasks/{tid}").text
    seed("d_queued", "queued")
    body = detail("d_queued")
    _check("/cancel" in body and "/retry" not in body and "/archive" not in body,
           "queued 只顯示 Cancel")
    seed("d_failed", "failed")
    body = detail("d_failed")
    _check("/retry" in body and "/archive" in body and "/cancel" not in body,
           "failed 顯示 Retry + Archive（不顯示 Cancel）")
    seed("d_completed", "completed")
    body = detail("d_completed")
    _check("/archive" in body and "/retry" not in body and "/cancel" not in body,
           "completed 只顯示 Archive")
    seed("d_running", "running")
    body = detail("d_running")
    _check("/cancel" not in body and "/retry" not in body and "/archive" not in body,
           "running 不顯示任何控制")
    seed("d_archived", "archived")
    body = detail("d_archived")
    _check("/cancel" not in body and "/retry" not in body and "/archive" not in body,
           "archived 不顯示任何控制")

    print("[27-29] Dashboard cancel/retry/archive 表單可運作")
    seed("f_cancel", "queued")
    r = client.post("/dashboard/tasks/f_cancel/cancel",
                    data={"reason": "dash 取消"}, follow_redirects=False)
    _check(r.status_code == 303 and st("f_cancel") == "cancelled", "dashboard cancel form -> cancelled")
    seed("f_retry", "failed", attempts=1)
    r = client.post("/dashboard/tasks/f_retry/retry",
                    data={"reason": "dash 重試"}, follow_redirects=False)
    _check(r.status_code == 303 and st("f_retry") == "queued", "dashboard retry form -> queued")
    seed("f_archive", "completed")
    r = client.post("/dashboard/tasks/f_archive/archive",
                    data={"reason": "dash 封存"}, follow_redirects=False)
    _check(r.status_code == 303 and st("f_archive") == "archived", "dashboard archive form -> archived")

    print("[30] 控制前後不呼叫 OpenClaw CLI（無 results.jsonl、無 worker thread）")
    _check(not main.RESULTS_PATH.exists() or main.RESULTS_PATH.stat().st_size == 0,
           "沒有 results.jsonl 輸出")
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()],
           "沒有 worker 執行緒")

    print("[31] worker 不會 claim cancelled / archived / rejected / waiting_review")
    for state in ("cancelled", "archived", "rejected", "waiting_review"):
        seed(f"w_{state}", state)
    seed("w_retry_src", "failed")
    post("retry", "w_retry_src")  # failed -> queued（[32] 預備）
    claimed: set[str] = set()
    q = main.get_queue()
    while True:
        it = q.claim_next()
        if it is None:
            break
        claimed.add(it["task_id"])
    for state in ("cancelled", "archived", "rejected", "waiting_review"):
        _check(f"w_{state}" not in claimed, f"[31] worker 不 claim {state}")
    print("[32] retry failed -> queued 後 worker 才能自然 claim")
    _check("w_retry_src" in claimed, "[32] retry 後的任務可被 claim")

    if FAILURES:
        print(f"\n❌ Limited Control Actions 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Limited Control Actions 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
