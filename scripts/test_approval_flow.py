#!/usr/bin/env python3
"""v0.5.4 — Approval Flow 測試。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證。
不啟動 worker、不呼叫真實 OpenClaw、不改 .env。

測試涵蓋（對應任務要求 1–20）：
  1–3  safety_level 0/1/2 -> queued
  4–5  safety_level 3/4   -> waiting_review
  6    requires_confirmation=true -> waiting_review
  7    worker（claim_next）不會 claim waiting_review
  8    approve waiting_review -> queued（attempts 不變）
  9    approve 後 worker 才能 claim
  10   reject waiting_review -> rejected
  11   worker 不會 claim rejected
  12   approve 不存在 task -> 404
  13   reject 不存在 task -> 404
  14   approve 非 waiting_review -> 409
  15   reject 非 waiting_review -> 409
  16   GET /reviews/pending 只列 waiting_review
  17   GET /dashboard/reviews -> 200
  18   Dashboard approve form 可運作
  19   Dashboard reject form 可運作
  20   approve/reject 不會呼叫 OpenClaw CLI（無 results、無 worker thread）
另含向後相容：無 metadata / 無法解析 safety_level -> queued。
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="approval_test_")
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


def _dispatch(client: TestClient, task_id: str, metadata: dict) -> dict:
    body = {
        "task_id": task_id,
        "title": f"任務 {task_id}",
        "goal": "g",
        "task_text": f"do {task_id}",
        "metadata": metadata,
    }
    r = client.post("/tasks/dispatch", json=body)
    assert r.status_code == 200, (task_id, r.status_code, r.text)
    return r.json()


def _status(task_id: str) -> str | None:
    item = main.get_queue().get(task_id)
    return item["status"] if item else None


def _drain_claims() -> list[str]:
    """把所有可 claim（queued）的任務領出來，回傳 task_id 清單。"""
    q = main.get_queue()
    claimed: list[str] = []
    while True:
        it = q.claim_next()
        if it is None:
            break
        claimed.append(it["task_id"])
    return claimed


def main_test() -> int:
    client = TestClient(main.app)

    print("[1-3] safety_level 0/1/2 -> queued")
    for lvl in (0, 1, 2):
        tid = f"lvl{lvl}"
        resp = _dispatch(client, tid, {"safety_level": lvl})
        _check(resp.get("status") == "accepted", f"lvl{lvl} dispatch=accepted")
        _check(_status(tid) == "queued", f"lvl{lvl} queue status=queued")

    print("[4-5] safety_level 3/4 -> waiting_review")
    for lvl in (3, 4):
        tid = f"lvl{lvl}"
        resp = _dispatch(client, tid, {"safety_level": lvl})
        _check(resp.get("status") == "waiting_review", f"lvl{lvl} dispatch=waiting_review")
        _check(_status(tid) == "waiting_review", f"lvl{lvl} queue status=waiting_review")

    print("[6] requires_confirmation=true -> waiting_review（即使 level 低）")
    resp = _dispatch(client, "needconf", {"safety_level": 0, "requires_confirmation": True})
    _check(resp.get("status") == "waiting_review", "requires_confirmation dispatch=waiting_review")
    _check(_status("needconf") == "waiting_review", "requires_confirmation status=waiting_review")

    print("[bc] 向後相容：無 metadata / 無法解析 safety_level -> queued")
    resp = _dispatch(client, "legacy", {})
    _check(_status("legacy") == "queued", "無 metadata -> queued")
    resp = _dispatch(client, "badlvl", {"safety_level": "不知道"})
    _check(_status("badlvl") == "queued", "無法解析 safety_level -> queued")

    print("[10] reject waiting_review -> rejected（帶 reason）")
    r = client.post("/tasks/needconf/reject", json={"reason": "不允許登入網站"})
    _check(r.status_code == 200, "reject 200")
    _check(_status("needconf") == "rejected", "needconf -> rejected")
    _check(main.get_queue().get("needconf").get("error") == "不允許登入網站", "reject reason 記到 error")

    print("[8] approve waiting_review -> queued（attempts 不變）")
    attempts_before = main.get_queue().get("lvl3").get("attempts")
    r = client.post("/tasks/lvl3/approve")
    _check(r.status_code == 200, "approve 200")
    _check(_status("lvl3") == "queued", "lvl3 -> queued")
    _check(main.get_queue().get("lvl3").get("attempts") == attempts_before == 0,
           "approve 不增加 attempts（維持 0）")

    print("[12-13] approve/reject 不存在 task -> 404")
    _check(client.post("/tasks/nope/approve").status_code == 404, "approve 不存在 -> 404")
    _check(client.post("/tasks/nope/reject", json={}).status_code == 404, "reject 不存在 -> 404")

    print("[14-15] approve/reject 非 waiting_review -> 409")
    _check(client.post("/tasks/lvl0/approve").status_code == 409, "approve queued 任務 -> 409")
    _check(client.post("/tasks/lvl0/reject", json={}).status_code == 409, "reject queued 任務 -> 409")
    _check(client.post("/tasks/needconf/approve").status_code == 409, "approve rejected 任務 -> 409")

    print("[16] GET /reviews/pending 只列 waiting_review")
    r = client.get("/reviews/pending")
    _check(r.status_code == 200, "reviews/pending 200")
    items = r.json().get("items", [])
    ids = {i["task_id"] for i in items}
    # 此刻 waiting_review 只剩 lvl4（lvl3 已 approve、needconf 已 reject）
    _check(ids == {"lvl4"}, f"pending 只有 lvl4（實際 {ids}）")
    _check(all(i["status"] == "waiting_review" for i in items), "pending 全是 waiting_review")
    _check(items[0].get("safety_level") == 4, "pending 帶 safety_level")
    _check("requires_confirmation" in items[0], "pending 帶 requires_confirmation")

    print("[17] GET /dashboard/reviews -> 200 且含 lvl4")
    r = client.get("/dashboard/reviews")
    _check(r.status_code == 200, "/dashboard/reviews 200")
    _check("lvl4" in r.text and "Pending Reviews" in r.text, "reviews 頁含 lvl4")

    print("[19] Dashboard reject form 可運作")
    _dispatch(client, "dashrej", {"safety_level": 4})
    r = client.post("/dashboard/tasks/dashrej/reject",
                    data={"reason": "dashboard 拒絕"}, follow_redirects=False)
    _check(r.status_code == 303, "dashboard reject 303")
    _check(_status("dashrej") == "rejected", "dashboard reject -> rejected")

    print("[18] Dashboard approve form 可運作")
    _dispatch(client, "dashapp", {"safety_level": 3})
    r = client.post("/dashboard/tasks/dashapp/approve", follow_redirects=False)
    _check(r.status_code == 303, "dashboard approve 303")
    _check(_status("dashapp") == "queued", "dashboard approve -> queued")

    print("[20] approve/reject 不呼叫 OpenClaw（無 results.jsonl、無 worker thread）")
    _check(not main.RESULTS_PATH.exists() or main.RESULTS_PATH.stat().st_size == 0,
           "沒有任何 results.jsonl 輸出（worker 未跑）")
    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()],
           "沒有 worker 執行緒")

    print("[7,9,11] claim_next 行為：只 claim queued，跳過 waiting_review / rejected")
    # 目前 queued: lvl0,1,2,legacy,badlvl,lvl3(approved),dashapp(approved)
    # waiting_review: lvl4 ；rejected: needconf,dashrej
    claimed = set(_drain_claims())
    _check("lvl4" not in claimed, "[7] waiting_review(lvl4) 不會被 claim")
    _check("needconf" not in claimed and "dashrej" not in claimed,
           "[11] rejected(needconf/dashrej) 不會被 claim")
    _check("lvl3" in claimed, "[9] approve 後 lvl3 可被 claim")
    _check("dashapp" in claimed, "[9] dashboard-approve 後 dashapp 可被 claim")
    _check({"lvl0", "lvl1", "lvl2", "legacy", "badlvl"} <= claimed, "一般 queued 任務都可被 claim")
    # claim 之後，lvl4 仍是 waiting_review、rejected 仍 rejected（沒被狀態機誤動）
    _check(_status("lvl4") == "waiting_review", "claim 後 lvl4 仍 waiting_review")
    _check(_status("needconf") == "rejected", "claim 後 needconf 仍 rejected")

    if FAILURES:
        print(f"\n❌ Approval Flow 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Approval Flow 測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
