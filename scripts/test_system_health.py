#!/usr/bin/env python3
"""v0.5.6 — System Health / Worker Heartbeat 測試。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證。
不啟動 worker、不呼叫真實 OpenClaw、不改 .env。

涵蓋任務要求 1–12。
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="health_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""
os.environ["CALLBACK_ENABLED"] = "false"
# OpenClaw CLI 指向不存在路徑：health 只能檢查路徑、絕不執行。
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


def _iso_ago(seconds: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


def main_test() -> int:
    client = TestClient(main.app)
    wid = main.WORKER_ID

    print("[1] 沒有 heartbeat 時 /system/worker -> unknown")
    r = client.get("/system/worker")
    _check(r.status_code == 200, "/system/worker 200")
    w = r.json()
    _check(w.get("status") == "unknown", f"無心跳 status=unknown（實際 {w.get('status')}）")
    _check(w.get("raw_status") is None, "無心跳 raw_status=None")
    _check(w.get("last_seen_at") is None, "無心跳 last_seen_at=None")

    print("[9] health store record / update 正常運作")
    h = main.get_health()
    rec = h.record(wid, status="starting", pid=4321, hostname="testhost")
    _check(rec.get("status") == "starting" and rec.get("pid") == 4321, "record 寫入 starting/pid")
    rec2 = h.record(wid, status="idle")  # 部分更新：pid 應沿用
    _check(rec2.get("status") == "idle" and rec2.get("pid") == 4321,
           "update 只改 status，pid 沿用")

    print("[2] last_seen_at 很新 -> worker online")
    h.record(wid, status="idle", last_seen_at=datetime.now(timezone.utc).isoformat())
    w = client.get("/system/worker").json()
    _check(w.get("status") == "online", f"新心跳 -> online（實際 {w.get('status')}）")
    _check(w.get("raw_status") == "idle", "raw_status=idle")

    print("[3] last_seen_at 過舊 -> worker stale")
    h.record(wid, status="idle", last_seen_at=_iso_ago(120))
    w = client.get("/system/worker").json()
    _check(w.get("status") == "stale", f"舊心跳 -> stale（實際 {w.get('status')}）")

    print("[4] GET /system/health -> 200")
    # 先放一些 queue 任務，讓 counts 有內容
    q = main.get_queue()
    q.enqueue(task_id="h1", title="t", task_text="t", safety_level=0,
              payload={"metadata": {}}, initial_status="queued")
    q.enqueue(task_id="h2", title="t", task_text="t", safety_level=0,
              payload={"metadata": {}}, initial_status="waiting_review")
    r = client.get("/system/health")
    _check(r.status_code == 200, "/system/health 200")
    data = r.json()
    _check(data.get("ok") is True, "health ok=true")
    _check(data.get("version") == main.APP_VERSION, f"version={main.APP_VERSION}")
    _check(data.get("adapter", {}).get("status") == "online", "adapter online")

    print("[5] /system/health 含 queue counts（8 種狀態）")
    counts = data.get("queue", {}).get("counts", {})
    for k in ("queued", "running", "completed", "failed", "cancelled",
              "waiting_review", "rejected", "archived"):
        _check(k in counts, f"counts 含 {k}")
    _check(counts.get("queued") == 1 and counts.get("waiting_review") == 1,
           "counts 數值正確（queued=1, waiting_review=1）")
    _check(data.get("queue", {}).get("db_exists") is True, "queue db_exists=true")

    print("[6] /system/health 檢查 OpenClaw CLI path 但不執行")
    oc = data.get("openclaw", {})
    _check(oc.get("cli_checked_without_execution") is True, "cli_checked_without_execution=true")
    _check(oc.get("cli_path_exists") is False, "不存在路徑 -> cli_path_exists=false")
    _check(oc.get("cli_bin") == os.environ["OPENCLAW_CLI_BIN"], "回報的 cli_bin 正確")
    # 確認沒有任何 OpenClaw 執行痕跡（無 results.jsonl）
    _check(not main.RESULTS_PATH.exists() or main.RESULTS_PATH.stat().st_size == 0,
           "沒有 results.jsonl（沒有執行 OpenClaw）")

    print("[7] GET /dashboard/system -> 200")
    r = client.get("/dashboard/system")
    _check(r.status_code == 200, "/dashboard/system 200")
    body = r.text
    _check("System Health" in body, "system 頁有標題")
    _check("Worker Heartbeat" in body, "system 頁有 Worker Heartbeat 區")
    _check("OpenClaw CLI" in body, "system 頁有 OpenClaw CLI 區")

    print("[8] heartbeat 寫入不會改 queue task status")
    before = q.get("h1")["status"]
    h.record(wid, status="running", current_task_id="h1",
             current_task_started_at=datetime.now(timezone.utc).isoformat())
    after = q.get("h1")["status"]
    _check(before == after == "queued", f"heartbeat 不改任務狀態（{before}=={after}）")
    # 反向確認：worker snapshot 看得到 current_task_id，但那只是觀測
    w = client.get("/system/worker").json()
    _check(w.get("current_task_id") == "h1", "snapshot 反映 current_task_id（純觀測）")

    print("[11] 既有 worker claim 行為不變：只 claim queued，不 claim waiting_review")
    claimed = q.claim_next()
    _check(claimed is not None and claimed["task_id"] == "h1", "claim 到 queued 的 h1")
    _check(claimed["status"] == "running", "claim 後 h1 -> running")
    nxt = q.claim_next()
    _check(nxt is None, "沒有其他 queued 可 claim（waiting_review 的 h2 不被 claim）")
    _check(q.get("h2")["status"] == "waiting_review", "h2 仍 waiting_review")

    print("[12] 不啟動真實 OpenClaw（無 worker 執行緒、無 results）")
    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()],
           "沒有 worker 執行緒")
    _check(not main.RESULTS_PATH.exists() or main.RESULTS_PATH.stat().st_size == 0,
           "仍然沒有 results.jsonl")

    print("[10] FastAPI import — 本測試能 import app.main 即已驗證")
    _check(hasattr(main, "app"), "app.main.app 可用")

    if FAILURES:
        print(f"\n❌ System Health 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ System Health / Worker Heartbeat 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
