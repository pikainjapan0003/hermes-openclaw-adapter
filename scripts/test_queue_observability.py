#!/usr/bin/env python3
"""v0.5.1 — Queue Observability 唯讀 API smoke test。

完全離線：用一個暫存的 SQLite queue db + 暫存 DATA_DIR，
透過 FastAPI TestClient 驗證 /queue/* 觀測端點。

不啟動 worker、不呼叫 OpenClaw、不改 .env。

測試涵蓋：
- overview counts 正確
- tasks list 可依 status 篩選
- task detail 找得到
- task detail 找不到回 404
- recent-errors 只回 failed
- queue health 正常
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# --- 必須在 import app.main 之前設定環境（main 在 import 時就讀 env）---------
_TMP = tempfile.mkdtemp(prefix="obs_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""  # 測試不要求 token
os.environ["CALLBACK_ENABLED"] = "false"

# 讓 `python scripts/test_queue_observability.py` 也能 import app 套件。
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
    """造出 5 種狀態各一筆：completed / failed / running / cancelled / queued。"""
    q = main.get_queue()

    # A: completed
    q.enqueue(task_id="obs-A", title="任務A", task_text="do A", safety_level=0,
              payload={"title": "任務A", "metadata": {"safety_level": 0, "tag": "A"}})
    q.claim_next()  # 最舊 queued = A -> running
    q.mark_completed("obs-A", result_ref="x")

    # B: failed
    q.enqueue(task_id="obs-B", title="任務B", task_text="do B", safety_level=0,
              payload={"title": "任務B", "metadata": {"safety_level": 0}})
    q.claim_next()  # B -> running
    q.mark_failed("obs-B", error="OPENCLAW_TIMEOUT: 逾時")

    # C: running（claim 後不收尾）
    q.enqueue(task_id="obs-C", title="任務C", task_text="do C", safety_level=0,
              payload={"title": "任務C", "metadata": {}})
    q.claim_next()  # C -> running

    # D: cancelled（仍 queued 時取消）
    q.enqueue(task_id="obs-D", title="任務D", task_text="do D", safety_level=0,
              payload={"title": "任務D", "metadata": {}})
    q.cancel_if_queued("obs-D")

    # E: queued（保持不動）
    q.enqueue(task_id="obs-E", title="任務E", task_text="do E", safety_level=0,
              payload={"title": "任務E", "metadata": {}})

    return {"A": "obs-A", "B": "obs-B", "C": "obs-C", "D": "obs-D", "E": "obs-E"}


def main_test() -> int:
    ids = _seed()
    client = TestClient(main.app)

    print("[1] GET /queue/overview — counts 正確")
    r = client.get("/queue/overview")
    _check(r.status_code == 200, "overview 200")
    o = r.json()
    _check(o.get("version") == main.APP_VERSION, f"version={main.APP_VERSION}")
    _check(o.get("mode") == "queue-observability", "mode=queue-observability")
    c = o.get("counts", {})
    _check(c.get("queued") == 1, "queued=1")
    _check(c.get("running") == 1, "running=1")
    _check(c.get("completed") == 1, "completed=1")
    _check(c.get("failed") == 1, "failed=1")
    _check(c.get("cancelled") == 1, "cancelled=1")
    _check(o.get("total") == 5, "total=5")
    _check("worker" in o and "status" in o["worker"], "worker 區塊存在")
    _check("generated_at" in o, "generated_at 存在")

    print("[2] GET /queue/tasks — 全部與依 status 篩選")
    r = client.get("/queue/tasks")
    _check(r.status_code == 200, "tasks 200")
    body = r.json()
    _check(body.get("total") == 5, "tasks total=5")
    _check(len(body.get("items", [])) == 5, "tasks items=5")
    _check(body.get("limit") == 20 and body.get("offset") == 0, "預設 limit=20 offset=0")

    r = client.get("/queue/tasks", params={"status": "failed", "limit": 20, "offset": 0})
    body = r.json()
    _check(body.get("total") == 1, "failed total=1")
    _check(len(body["items"]) == 1, "failed items=1")
    _check(body["items"][0]["task_id"] == ids["B"], "failed item 是 B")
    _check(body["items"][0]["status"] == "failed", "failed item status=failed")

    r = client.get("/queue/tasks", params={"status": "completed"})
    _check(r.json()["items"][0]["task_id"] == ids["A"], "completed item 是 A")

    print("[2b] /queue/tasks 非法 status -> 400")
    r = client.get("/queue/tasks", params={"status": "bogus"})
    _check(r.status_code == 400, "非法 status 回 400")

    print("[2c] /queue/tasks 分頁 offset 生效")
    r = client.get("/queue/tasks", params={"limit": 2, "offset": 0})
    page1 = [i["task_id"] for i in r.json()["items"]]
    r = client.get("/queue/tasks", params={"limit": 2, "offset": 2})
    page2 = [i["task_id"] for i in r.json()["items"]]
    _check(len(page1) == 2 and len(page2) == 2, "兩頁各 2 筆")
    _check(set(page1).isdisjoint(set(page2)), "兩頁不重疊")

    print("[3] GET /queue/tasks/{id} — 找得到")
    r = client.get(f"/queue/tasks/{ids['B']}")
    _check(r.status_code == 200, "detail 200")
    d = r.json()
    _check(d["task_id"] == ids["B"], "detail task_id=B")
    _check(d["status"] == "failed", "detail status=failed")
    _check(d["title"] == "任務B", "detail title")
    _check(d["task_text"] == "do B", "detail task_text")
    _check(d["error_message"] == "OPENCLAW_TIMEOUT: 逾時", "detail error_message")
    _check(d["attempts"] == 1 and d["max_attempts"] == 3, "detail attempts/max")
    # detail 必含的鍵
    for k in ("created_at", "updated_at", "started_at", "finished_at",
              "result_text", "metadata"):
        _check(k in d, f"detail 含鍵 {k}")
    _check(d["metadata"] == {"safety_level": 0}, "detail metadata 來自 payload")

    print("[4] GET /queue/tasks/{id} — 找不到回 404")
    r = client.get("/queue/tasks/does-not-exist")
    _check(r.status_code == 404, "未知任務回 404")

    print("[5] GET /queue/recent-errors — 只回 failed")
    r = client.get("/queue/recent-errors")
    _check(r.status_code == 200, "recent-errors 200")
    items = r.json()["items"]
    _check(len(items) == 1, "recent-errors 只有 1 筆")
    _check(items[0]["task_id"] == ids["B"], "recent-errors 是 B")
    _check(items[0]["error_message"] == "OPENCLAW_TIMEOUT: 逾時", "recent-errors error_message")
    # 確認沒有 completed/queued/running/cancelled 混進來
    only_failed = all(it["task_id"] == ids["B"] for it in items)
    _check(only_failed, "recent-errors 不含非 failed 任務")

    r = client.get("/queue/recent-errors", params={"limit": 5})
    _check(r.status_code == 200, "recent-errors limit 參數可用")

    print("[6] GET /queue/health — 正常")
    r = client.get("/queue/health")
    _check(r.status_code == 200, "health 200")
    h = r.json()
    _check(h.get("ok") is True, "health ok=true")
    _check(h.get("queue_db_exists") is True, "queue_db_exists=true")
    _check(h.get("execution_mode") == "queue", "execution_mode=queue")
    _check(h.get("queue_db_path") == os.environ["QUEUE_DB_PATH"], "queue_db_path 正確")
    _check(isinstance(h.get("counts"), dict) and h["counts"].get("failed") == 1,
           "health counts 含 failed=1")

    if FAILURES:
        print(f"\n❌ Queue Observability 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Queue Observability 唯讀 API 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
