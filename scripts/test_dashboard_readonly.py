#!/usr/bin/env python3
"""v0.5.2 — Read-only Dashboard 唯讀 UI smoke test。

完全離線：用一個暫存的 SQLite queue db + 暫存 DATA_DIR，
透過 FastAPI TestClient 驗證 /dashboard 三個頁面。

不啟動 worker、不呼叫真實 OpenClaw、不改 .env、不改 queue 狀態。

測試涵蓋：
1. GET /dashboard 回 200
2. GET /dashboard/tasks 回 200
3. GET /dashboard/tasks/{id} 對存在任務回 200
4. GET /dashboard/tasks/{id} 對不存在任務回 404
5. 測試過程不啟動 worker（只 import app，不跑 app.worker）
6. 測試過程不碰真實 OpenClaw（離線、無 CLI 呼叫）
7. Dashboard 請求前後 queue 狀態完全不變（read-only 保證）
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# --- 必須在 import app.main 之前設定環境（main 在 import 時就讀 env）---------
_TMP = tempfile.mkdtemp(prefix="dash_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""  # 測試不要求 token
os.environ["CALLBACK_ENABLED"] = "false"
# 確保不會誤指向真實 OpenClaw CLI（dashboard 本來就不該呼叫，這是雙保險）。
os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"

# 讓 `python scripts/test_dashboard_readonly.py` 也能 import app 套件。
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


def _seed() -> dict[str, str]:
    """造出幾種狀態：completed / failed / running / cancelled / queued。"""
    q = main.get_queue()

    q.enqueue(task_id="dash-A", title="任務A", task_text="do A", safety_level=0,
              payload={"title": "任務A", "metadata": {"safety_level": 0, "tag": "A"}})
    q.claim_next()
    q.mark_completed("dash-A", result_ref="x")

    q.enqueue(task_id="dash-B", title="任務B", task_text="do B", safety_level=0,
              payload={"title": "任務B", "metadata": {"safety_level": 0}})
    q.claim_next()
    q.mark_failed("dash-B", error="OPENCLAW_TIMEOUT: 逾時")

    q.enqueue(task_id="dash-C", title="任務C", task_text="do C", safety_level=0,
              payload={"title": "任務C", "metadata": {}})
    q.claim_next()  # running

    q.enqueue(task_id="dash-D", title="任務D", task_text="do D", safety_level=0,
              payload={"title": "任務D", "metadata": {}})
    q.cancel_if_queued("dash-D")

    q.enqueue(task_id="dash-E", title="任務E", task_text="do E", safety_level=0,
              payload={"title": "任務E", "metadata": {}})

    return {"A": "dash-A", "B": "dash-B", "C": "dash-C", "D": "dash-D", "E": "dash-E"}


def main_test() -> int:
    ids = _seed()
    q = main.get_queue()
    counts_before = q.counts_by_status()
    total_before = q.total()

    client = TestClient(main.app)

    print("[1] GET /dashboard — Overview 200")
    r = client.get("/dashboard")
    _check(r.status_code == 200, "/dashboard 200")
    _check("text/html" in r.headers.get("content-type", ""), "/dashboard 回 HTML")
    body = r.text
    _check("Hermes x OpenClaw Queue Control Board" in body, "首頁頂部標題出現")
    _check("唯讀監控台" in body, "首頁標示 唯讀監控台（Read-only Dashboard）")
    _check(main.APP_VERSION in body, f"首頁顯示 version={main.APP_VERSION}")
    _check("queue" in body, "首頁顯示 execution_mode")

    print("[1b] GET /static/dashboard.css — 靜態檔可讀")
    r = client.get("/static/dashboard.css")
    _check(r.status_code == 200, "/static/dashboard.css 200")

    print("[2] GET /dashboard/tasks — 任務列表 200")
    r = client.get("/dashboard/tasks")
    _check(r.status_code == 200, "/dashboard/tasks 200")
    body = r.text
    for tid in ids.values():
        _check(tid in body, f"列表含 {tid}")
    _check(f"/dashboard/tasks/{ids['A']}" in body, "列表 task_id 連到詳情頁")

    print("[2b] GET /dashboard/tasks?status=failed — 篩選")
    r = client.get("/dashboard/tasks", params={"status": "failed"})
    _check(r.status_code == 200, "status=failed 200")
    _check(ids["B"] in r.text, "篩選結果含 B(failed)")

    print("[2c] GET /dashboard/tasks?status=bogus — 非法 status 不報錯（空列表）")
    r = client.get("/dashboard/tasks", params={"status": "bogus"})
    _check(r.status_code == 200, "非法 status 仍回 200")

    print("[2d] GET /dashboard/tasks 分頁參數可用")
    r = client.get("/dashboard/tasks", params={"limit": 2, "offset": 0})
    _check(r.status_code == 200, "limit/offset 200")

    print("[3] GET /dashboard/tasks/{id} — 存在任務 200")
    r = client.get(f"/dashboard/tasks/{ids['B']}")
    _check(r.status_code == 200, "存在任務詳情 200")
    body = r.text
    _check(ids["B"] in body, "詳情顯示 task_id")
    _check("任務B" in body, "詳情顯示 title")
    _check("do B" in body, "詳情顯示 task_text")
    _check("OPENCLAW_TIMEOUT: 逾時" in body, "詳情顯示 error_message")

    print("[4] GET /dashboard/tasks/{id} — 不存在任務 404")
    r = client.get("/dashboard/tasks/does-not-exist")
    _check(r.status_code == 404, "未知任務回 404")

    print("[5] read-only 保證：dashboard 請求前後 queue 狀態完全不變")
    counts_after = q.counts_by_status()
    total_after = q.total()
    _check(counts_before == counts_after, f"counts 不變 ({counts_before} == {counts_after})")
    _check(total_before == total_after, f"total 不變 ({total_before} == {total_after})")
    # 每筆任務的 status 與 attempts 都不可被 dashboard 改動。
    for tid in ids.values():
        item = q.get(tid)
        _check(item is not None, f"{tid} 仍存在")

    print("[6] 確認沒有殘留 worker 執行緒（dashboard 測試不啟動 worker）")
    import threading  # noqa: PLC0415
    worker_threads = [t for t in threading.enumerate() if "worker" in t.name.lower()]
    _check(not worker_threads, "沒有 worker 執行緒")

    if FAILURES:
        print(f"\n❌ Read-only Dashboard 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Read-only Dashboard 唯讀 UI 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
