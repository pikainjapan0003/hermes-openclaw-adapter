#!/usr/bin/env python3
"""v0.7.2-F-C — Display Annotation in Owner Review Panel 顯示測試（唯讀，不寫 queue 外部）。

完全離線：暫存 SQLite db + 暫存 DATA_DIR，透過 FastAPI TestClient 驗證 review surfaces
（task detail / reviews）是否正確顯示 derive_queue_task_annotation 推導出的唯讀 annotation。

只驗證 UI 呈現與「不改任務狀態」，不啟動 worker、不呼叫 OpenClaw / Hermes / Google Sheets。
不寫 Replit queue；fixture 一律寫入測試專用的本地暫存 SQLite。

安全邊界（display-only）：
  - No QueueStore runtime behavior changes.
  - No approval wiring changes.
  - No Worker execution.
  - No OpenClaw call.
  - No Hermes call.
  - No Google Sheets write.
  - No external side effects.

執行： python scripts/test_dashboard_annotation_display_readonly_v0_7_2_f_c.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="fc_annotation_test_")
os.environ["EXECUTION_MODE"] = "queue"
os.environ["DATA_DIR"] = _TMP
os.environ["QUEUE_DB_PATH"] = str(Path(_TMP) / "queue.db")
os.environ["HERMES_ADAPTER_TOKEN"] = ""
os.environ["CALLBACK_ENABLED"] = "false"
os.environ["OPENCLAW_CLI_BIN"] = "/nonexistent/openclaw-should-never-be-called"
_DASH_TOKEN = "f-c-annotation-test-token"
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

    # waiting_review demo-like task：帶完整 annotation metadata。
    q.enqueue(
        task_id="fc-review-annotated",
        title="DEMO 審核任務（含 annotation）",
        task_text="這是 F-C 顯示測試用任務。",
        safety_level=3,
        payload={
            "metadata": {
                "requires_confirmation": True,
                "task_origin": "owner-cli",
                "requested_by": "owner",
                "request_channel": "local",
                "owner_reason": "此任務需要 Owner 在執行前確認風險。",
                "approval_readiness": "ready_for_owner_decision",
                "risk_summary": "可能變更本地檔案；風險中等。",
                "side_effect_summary": "本地 dry-run，無外部寫入。",
                "next_step_if_approved": "核准後狀態轉 queued；Worker 仍關閉。",
                "execution_mode": "dry-run",
                "external_touchpoints": ["none"],
                "dry_run_available": True,
                "mock_available": True,
                "rollback_note": "可重跑；不會自動 undo。",
                "human_readable_summary": "Owner 審核用 demo 任務，僅供觀察，不會自動執行。",
            }
        },
        initial_status="waiting_review",
    )
    # legacy task（waiting_review）：完全沒有 annotation metadata，畫面不得壞掉。
    # waiting_review 狀態下保守推導為 owner_review_required（仍顯示 fallback 文案）。
    q.enqueue(
        task_id="fc-legacy-bare",
        title="LEGACY 任務（無 annotation）",
        task_text="legacy task without annotation metadata",
        safety_level=3,
        payload={"metadata": {}},
        initial_status="waiting_review",
    )
    # legacy task（queued）：無 annotation 且非審核狀態 → 保守 fallback not_ready。
    q.enqueue(
        task_id="fc-legacy-queued",
        title="LEGACY 任務（queued，無 annotation）",
        task_text="legacy queued task without annotation metadata",
        safety_level=0,
        payload={"metadata": {}},
        initial_status="queued",
    )

    counts_before = q.counts_by_status()

    client = TestClient(main.app)
    client.headers.update({"X-Dashboard-Token": _DASH_TOKEN})

    print("[1] task detail / reviews / dashboard rendering 不因 annotation 壞掉（200）")
    r_detail = client.get("/dashboard/tasks/fc-review-annotated")
    _check(r_detail.status_code == 200, "annotated task detail 200")
    r_legacy = client.get("/dashboard/tasks/fc-legacy-bare")
    _check(r_legacy.status_code == 200, "legacy task detail 200（無 annotation 不壞）")
    r_reviews = client.get("/dashboard/reviews")
    _check(r_reviews.status_code == 200, "reviews 200")
    r_home = client.get("/dashboard")
    _check(r_home.status_code == 200, "dashboard home 200")

    detail = r_detail.text
    legacy = r_legacy.text
    reviews = r_reviews.text

    print("[2] waiting_review task 可顯示 annotation block")
    _check("審核準備狀態" in detail, "detail 含 annotation block 標題（審核準備狀態）")
    _check("Annotation / Approval Readiness" in detail, "detail 含英文 sublabel")

    print("[3] human_readable_summary 出現在 HTML")
    _check("Owner 審核用 demo 任務，僅供觀察，不會自動執行。" in detail, "detail 顯示 human_readable_summary 文字")
    _check("human_readable_summary" in detail, "detail 含 human_readable_summary code 標籤")

    print("[4] approval_readiness 出現在 HTML")
    _check("approval_readiness" in detail, "detail 含 approval_readiness code 標籤")
    _check("ready_for_owner_decision" in detail, "detail 顯示 approval_readiness 值")
    _check("可由 Owner 決定" in reviews or "可由 Owner 決定" in detail or "資訊足夠，可由 Owner 決定" in detail,
           "annotated task 顯示中文 readiness 標籤")

    print("[5] execution_permission / dispatch_allowed 顯示為未授權 / 未允許")
    _check("執行權限：未授權" in detail, "detail 顯示 執行權限：未授權")
    _check("派工允許：未允許" in detail, "detail 顯示 派工允許：未允許")
    _check("execution_permission = False" in detail, "detail 顯示 execution_permission = False")
    _check("dispatch_allowed = False" in detail, "detail 顯示 dispatch_allowed = False")
    _check("執行權限：未授權" in reviews, "reviews 也顯示 執行權限：未授權")

    print("[6] 安全提醒文字存在（decision/execution 分離）")
    for marker in ("審核準備狀態不是執行權限", "Owner 核准不等於 Worker 執行", "Decision 與 dispatch 仍然分離"):
        _check(marker in detail, f"detail 含安全提醒：{marker}")
        _check(marker in reviews, f"reviews 含安全提醒：{marker}")

    print("[7] legacy task fallback 顯示（不壞、顯示保守 fallback）")
    # waiting_review legacy：保守推導 owner_review_required，但仍用 fallback 文案。
    _check("需要 Owner 審核" in legacy or "owner_review_required" in legacy,
           "legacy(waiting_review) 顯示 owner_review_required readiness")
    _check("資訊不足，Owner 不應直接核准。" in legacy, "legacy 顯示 fallback owner_reason")
    _check("未提供完整風險說明。" in legacy, "legacy 顯示 fallback risk_summary")
    _check("執行權限：未授權" in legacy, "legacy 仍顯示 執行權限：未授權")
    # queued legacy：非審核狀態 + 無 annotation → 保守 fallback not_ready。
    r_legacy_q = client.get("/dashboard/tasks/fc-legacy-queued")
    _check(r_legacy_q.status_code == 200, "legacy queued task detail 200")
    legacy_q = r_legacy_q.text
    _check("not_ready" in legacy_q or "資訊不足（不可核准）" in legacy_q,
           "legacy(queued) 顯示 not_ready fallback readiness")

    print("[8] reviews 列表含 readiness 欄位與 annotated task")
    _check("審核準備狀態" in reviews, "reviews 含 審核準備狀態 欄位")
    _check("fc-review-annotated"[:8] in reviews or "DEMO 審核任務" in reviews, "reviews 列出 annotated task")

    print("[9] 顯示推導不改 queue 任務狀態（read-only 保證）")
    counts_after = q.counts_by_status()
    _check(counts_before == counts_after, f"counts 不變（{counts_before} == {counts_after}）")
    _check(q.get("fc-review-annotated")["status"] == "waiting_review", "annotated task 仍 waiting_review")
    _check(q.get("fc-legacy-bare")["status"] == "waiting_review", "legacy task 仍 waiting_review")

    print("[10] 不啟動 worker / 不呼叫 OpenClaw（無 results.jsonl）")
    import threading  # noqa: PLC0415
    worker_threads = [t for t in threading.enumerate() if "worker" in t.name.lower()]
    _check(not worker_threads, "沒有 worker 執行緒")
    _check(not (Path(_TMP) / "results.jsonl").exists(), "沒有 results.jsonl（未執行 OpenClaw）")

    if FAILURES:
        print(f"\n❌ F-C annotation display 測試失敗 {len(FAILURES)} 項：")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print("\n✅ test_dashboard_annotation_display_readonly_v0_7_2_f_c 全數通過（唯讀顯示，未寫 Replit queue）。")
    return 0


if __name__ == "__main__":
    sys.exit(main_test())
