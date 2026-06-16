#!/usr/bin/env python3
"""v0.5.3 — Blackboard / task comments 留言板測試。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證。
不啟動 worker、不呼叫真實 OpenClaw、不改 .env、不改 queue 狀態。

測試涵蓋：
1. 對存在 task 新增留言成功（201）
2. 對不存在 task 新增留言回 404（不建立孤兒留言）
3. 空 content 回 400 或 422
4. 非法 author_type 回 400 或 422
5. GET comments 可取回留言
6. 留言前後 queue task status 不變
7. 留言不會觸發 worker（無 worker 執行緒）
8. Dashboard task detail 顯示留言區
9. Dashboard 表單 POST 成功後可在頁面看到留言
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# --- 必須在 import app.main 之前設定環境 -------------------------------------
_TMP = tempfile.mkdtemp(prefix="bb_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""  # 測試不要求 token
os.environ["CALLBACK_ENABLED"] = "false"
# 雙保險：就算有人手滑呼叫 OpenClaw，也會指到不存在路徑。
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


def _seed_task() -> str:
    q = main.get_queue()
    q.enqueue(task_id="bb-1", title="留言測試任務", task_text="do work", safety_level=0,
              payload={"title": "留言測試任務", "metadata": {"safety_level": 0}})
    q.claim_next()  # queued -> running
    return "bb-1"


def main_test() -> int:
    task_id = _seed_task()
    q = main.get_queue()
    status_before = q.get(task_id)["status"]
    attempts_before = q.get(task_id)["attempts"]

    client = TestClient(main.app)

    print("[1] POST /tasks/{id}/comments — 對存在 task 新增成功")
    r = client.post(f"/tasks/{task_id}/comments", json={
        "author_type": "user",
        "author_name": "owner",
        "content": "這個任務可以查公開資料，但不要登入網站。",
        "metadata": {"k": "v"},
    })
    _check(r.status_code == 201, f"新增留言 201（實際 {r.status_code}）")
    c = r.json()
    _check(c.get("task_id") == task_id, "回傳 task_id 正確")
    _check(c.get("author_type") == "user", "回傳 author_type=user")
    _check(c.get("content") == "這個任務可以查公開資料，但不要登入網站。", "回傳 content 正確")
    _check(c.get("comment_id", "").startswith("cmt-"), "comment_id 有產生")
    _check(c.get("metadata") == {"k": "v"}, "metadata 正確帶回")

    print("[2] POST /tasks/{id}/comments — 對不存在 task 回 404")
    r = client.post("/tasks/no-such-task/comments", json={
        "author_type": "user", "content": "hi"})
    _check(r.status_code == 404, f"未知任務回 404（實際 {r.status_code}）")
    # 確認沒有建立孤兒留言
    _check(main.get_blackboard().count_for_task("no-such-task") == 0, "沒有建立孤兒留言")

    print("[3] POST 空 content -> 400 或 422")
    r = client.post(f"/tasks/{task_id}/comments", json={
        "author_type": "user", "content": ""})
    _check(r.status_code in (400, 422), f"空 content 被擋（{r.status_code}）")
    r = client.post(f"/tasks/{task_id}/comments", json={
        "author_type": "user", "content": "   "})
    _check(r.status_code in (400, 422), f"純空白 content 被擋（{r.status_code}）")

    print("[4] POST 非法 author_type -> 400 或 422")
    r = client.post(f"/tasks/{task_id}/comments", json={
        "author_type": "robot", "content": "hi"})
    _check(r.status_code in (400, 422), f"非法 author_type 被擋（{r.status_code}）")

    print("[5] GET /tasks/{id}/comments — 取回留言")
    r = client.get(f"/tasks/{task_id}/comments")
    _check(r.status_code == 200, "GET comments 200")
    body = r.json()
    _check(body.get("task_id") == task_id, "GET 回 task_id")
    items = body.get("items", [])
    _check(len(items) == 1, f"目前只有 1 則有效留言（實際 {len(items)}）")
    _check(items[0]["content"] == "這個任務可以查公開資料，但不要登入網站。", "留言內容正確")
    # 不存在 task 的 GET 也應 404
    r = client.get("/tasks/no-such-task/comments")
    _check(r.status_code == 404, "GET 不存在 task 的 comments 回 404")

    print("[6] 留言前後 queue task status / attempts 不變")
    status_after = q.get(task_id)["status"]
    attempts_after = q.get(task_id)["attempts"]
    _check(status_before == status_after, f"status 不變（{status_before}=={status_after}）")
    _check(attempts_before == attempts_after, f"attempts 不變（{attempts_before}=={attempts_after}）")

    print("[7] 留言不會觸發 worker（無 worker 執行緒）")
    import threading  # noqa: PLC0415
    worker_threads = [t for t in threading.enumerate() if "worker" in t.name.lower()]
    _check(not worker_threads, "沒有 worker 執行緒")

    print("[8] GET /dashboard/tasks/{id} — 顯示留言區")
    r = client.get(f"/dashboard/tasks/{task_id}")
    _check(r.status_code == 200, "詳情頁 200")
    page = r.text
    _check("Blackboard Comments" in page, "詳情頁有 Blackboard Comments 區")
    _check("這個任務可以查公開資料，但不要登入網站。" in page, "詳情頁顯示已存在的留言")
    _check('action="/dashboard/tasks/' in page, "詳情頁有新增留言表單")

    print("[9] Dashboard 表單 POST 成功後頁面可見新留言")
    r = client.post(
        f"/dashboard/tasks/{task_id}/comments",
        data={"author_type": "hermes", "author_name": "brain",
              "content": "Hermes 在此留言：請優先處理。"},
        follow_redirects=False,
    )
    _check(r.status_code == 303, f"表單 POST 後 303 redirect（實際 {r.status_code}）")
    _check(r.headers.get("location") == f"/dashboard/tasks/{task_id}", "redirect 回同一詳情頁")
    r = client.get(f"/dashboard/tasks/{task_id}")
    _check("Hermes 在此留言：請優先處理。" in r.text, "詳情頁可見表單新增的留言")
    _check("hermes" in r.text, "詳情頁顯示 author_type=hermes")

    print("[9b] Dashboard 表單空 content -> redirect 帶 error，且不新增")
    before = main.get_blackboard().count_for_task(task_id)
    r = client.post(
        f"/dashboard/tasks/{task_id}/comments",
        data={"author_type": "user", "author_name": "owner", "content": "   "},
        follow_redirects=False,
    )
    _check(r.status_code == 303, "空 content 表單仍 303（PRG）")
    _check("error=" in r.headers.get("location", ""), "redirect 帶 error 參數")
    after = main.get_blackboard().count_for_task(task_id)
    _check(before == after, "空 content 不新增留言")

    print("[10] 最終 queue status 仍未被任何留言操作改動")
    _check(q.get(task_id)["status"] == status_before, "最終 status 不變")

    if FAILURES:
        print(f"\n❌ Blackboard 留言板測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ Blackboard 留言板測試全數通過。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
