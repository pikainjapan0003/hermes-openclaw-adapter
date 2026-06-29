#!/usr/bin/env python3
"""v0.7.3-B — Read-only Approval Event View 測試（純函式 + 唯讀顯示，不寫 queue 外部）。

涵蓋：
  - helper 在 empty metadata 時 has_events False / event_count 0。
  - helper 不修改輸入 task（immutability）。
  - helper 回傳 execution_permission False / dispatch_allowed False。
  - helper 不 import app.main / app.queue_store / app.worker。
  - 含 events metadata 時可正規化，且每個 event 的 execution_permission/dispatch_allowed False。
  - template markers（task_detail / reviews）存在。
  - 透過 FastAPI TestClient 以本地暫存 SQLite 驗證頁面渲染（不 seed Replit queue、不 --apply）。

執行： python scripts/test_approval_decision_event_view_readonly_v0_7_3_b.py
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 先 import helper（純函式），確認不會拉進 app.main / app.queue_store / app.worker。
from app.approval_decision_events_v0_7 import (  # noqa: E402
    derive_approval_decision_event_view,
)

_IMPORT_SAFE = (
    "app.main" not in sys.modules
    and "app.queue_store" not in sys.modules
    and "app.worker" not in sys.modules
)

PASSED = 0
FAILURES: list[str] = []


def _check(cond: bool, label: str) -> None:
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok: {label}")
    else:
        print(f"  ❌ FAIL: {label}")
        FAILURES.append(label)


def _pure_helper_tests() -> None:
    print("[1] empty metadata → has_events False / event_count 0 / empty state")
    v = derive_approval_decision_event_view({"task_id": "t-empty"})
    _check(v["has_events"] is False, "empty → has_events False")
    _check(v["event_count"] == 0, "empty → event_count 0")
    _check(v["events"] == [], "empty → events []")
    _check(v["empty_state_message"] == "尚無 Owner 決策事件紀錄", "empty → empty_state_message")
    _check("v0.7.3-C 才會規劃 local recorder" in v["empty_state_note"], "empty → empty_state_note 提到 v0.7.3-C")

    print("[2] execution_permission / dispatch_allowed 恆 False")
    _check(v["execution_permission"] is False, "view execution_permission False")
    _check(v["dispatch_allowed"] is False, "view dispatch_allowed False")

    print("[3] import safety（helper 不拉進 app.main / queue_store / worker）")
    _check(_IMPORT_SAFE, "import helper 不會拉進 app.main / app.queue_store / app.worker")

    print("[4] 含 events metadata → 正規化，event 的 permission/dispatch False")
    task = {
        "task_id": "t-events",
        "payload": {
            "metadata": {
                "approval_decision_events": [
                    {
                        "decision_id": "d-1",
                        "task_id": "t-events",
                        "decision_type": "approve",
                        "decided_by": "owner",
                        "decided_at": "2026-06-29T00:00:00Z",
                        "decision_reason": "looks safe",
                        "previous_status": "waiting_review",
                        "next_status": "queued",
                        "approval_readiness_at_decision": "ready_for_owner_decision",
                        # 即使來源宣稱 True，view 也必須顯示 False。
                        "execution_permission_at_decision": True,
                        "dispatch_allowed_at_decision": True,
                        "safety_snapshot": {"safety_level": 3},
                        "annotation_snapshot": {"task_origin": "owner-cli"},
                        "audit_record": {"k": "v"},
                    }
                ]
            }
        },
    }
    v = derive_approval_decision_event_view(task)
    _check(v["has_events"] is True, "events → has_events True")
    _check(v["event_count"] == 1, "events → event_count 1")
    ev = v["events"][0]
    _check(ev["decision_type"] == "approve", "event decision_type 帶出")
    _check(ev["previous_status"] == "waiting_review" and ev["next_status"] == "queued", "event 狀態轉換帶出")
    _check(ev["execution_permission_at_decision"] is False, "event execution_permission_at_decision 強制 False")
    _check(ev["dispatch_allowed_at_decision"] is False, "event dispatch_allowed_at_decision 強制 False")
    _check(ev["safety_snapshot"] == {"safety_level": 3}, "event safety_snapshot 帶出")

    print("[5] immutability：derive 不 mutate 輸入 task")
    snapshot = copy.deepcopy(task)
    derive_approval_decision_event_view(task)
    _check(task == snapshot, "derive 不 mutate 輸入 task")
    # 改動回傳 events 不回寫原 task。
    v2 = derive_approval_decision_event_view(task)
    v2["events"].append({"x": 1})
    v2["safety_reminders"].append("mutated")
    _check(task == snapshot, "改動回傳 list 不回寫原 task")

    print("[6] JSON string payload / 壞 JSON 不 crash")
    v = derive_approval_decision_event_view(
        {"task_id": "t-json", "payload": json.dumps({"metadata": {"approval_decision_events": []}})}
    )
    _check(v["has_events"] is False, "JSON 字串 payload 空 events → has_events False")
    v = derive_approval_decision_event_view({"task_id": "t-bad", "payload": "{not json"})
    _check(v["has_events"] is False, "壞 JSON payload → fallback empty（不 crash）")


def _template_marker_tests() -> None:
    print("[7] template markers 存在")
    root = Path(__file__).resolve().parents[1]
    detail = (root / "templates" / "task_detail.html").read_text(encoding="utf-8")
    reviews = (root / "templates" / "reviews.html").read_text(encoding="utf-8")
    for token in ("Owner 決策紀錄", "Approval Decision Events", "只讀顯示",
                  "approve is not execute", "Owner decision event is not Worker dispatch",
                  "execution_permission = False", "dispatch_allowed = False"):
        _check(token in detail, f"task_detail.html 含「{token}」")
    for token in ("決策紀錄", "只讀", "未派工"):
        _check(token in reviews, f"reviews.html 含「{token}」")


def _render_tests() -> None:
    print("[8] FastAPI TestClient 渲染（本地暫存 SQLite，不 seed Replit queue）")
    tmp = tempfile.mkdtemp(prefix="fb3_decision_test_")
    os.environ["EXECUTION_MODE"] = "queue"
    os.environ["DATA_DIR"] = tmp
    os.environ["QUEUE_DB_PATH"] = str(Path(tmp) / "queue.db")
    os.environ["HERMES_ADAPTER_TOKEN"] = ""
    os.environ["CALLBACK_ENABLED"] = "false"
    os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"
    dash_token = "f-3-b-decision-test-token"
    os.environ["DASHBOARD_AUTH_ENABLED"] = "true"
    os.environ["DASHBOARD_TOKEN"] = dash_token

    from fastapi.testclient import TestClient  # noqa: PLC0415
    from app import main  # noqa: PLC0415

    q = main.get_queue()
    q.enqueue(
        task_id="fb3-review-task",
        title="DEMO 決策紀錄唯讀測試",
        task_text="read-only decision events view test",
        safety_level=3,
        payload={"metadata": {"requires_confirmation": True}},
        initial_status="waiting_review",
    )
    counts_before = q.counts_by_status()

    client = TestClient(main.app)
    client.headers.update({"X-Dashboard-Token": dash_token})

    r_detail = client.get("/dashboard/tasks/fb3-review-task")
    _check(r_detail.status_code == 200, "task detail 200")
    detail = r_detail.text
    _check("Owner 決策紀錄" in detail, "detail 含 Owner 決策紀錄")
    _check("尚無 Owner 決策事件紀錄" in detail, "detail 空狀態：尚無 Owner 決策事件紀錄")
    _check("approve is not execute" in detail, "detail 含 approve is not execute")
    _check("execution_permission = False" in detail, "detail 含 execution_permission = False")
    _check("dispatch_allowed = False" in detail, "detail 含 dispatch_allowed = False")

    r_reviews = client.get("/dashboard/reviews")
    _check(r_reviews.status_code == 200, "reviews 200")
    reviews = r_reviews.text
    _check("決策紀錄" in reviews, "reviews 含 決策紀錄 indicator")
    _check("未派工" in reviews, "reviews 含 未派工")

    counts_after = q.counts_by_status()
    _check(counts_before == counts_after, f"read-only：counts 不變（{counts_before} == {counts_after}）")
    _check(q.get("fb3-review-task")["status"] == "waiting_review", "task 仍 waiting_review")

    import threading  # noqa: PLC0415
    _check(not [t for t in threading.enumerate() if "worker" in t.name.lower()], "沒有 worker 執行緒")
    _check(not (Path(tmp) / "results.jsonl").exists(), "沒有 results.jsonl（未執行 OpenClaw）")


def main_test() -> int:
    _pure_helper_tests()
    _template_marker_tests()
    _render_tests()
    if FAILURES:
        print(f"\n❌ v0.7.3-B 唯讀檢視測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print(f"\n✅ test_approval_decision_event_view_readonly_v0_7_3_b 全數通過（{PASSED} 項，唯讀，未寫 Replit queue）。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
