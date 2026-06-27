"""v0.7.0-D — mock E2E dry-run 單元測試（純 mock，不連任何系統）。

執行： python scripts/test_mock_e2e_v0_7_d.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.contracts_v0_7 import validate_callback_event, validate_task_envelope  # noqa: E402
from app.mock_e2e_v0_7 import (  # noqa: E402
    InMemoryMockQueue,
    MockE2EError,
    apply_callback_to_mock_task,
    mock_worker_process_task,
    run_mock_e2e_dry_run,
)

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {msg}")
    _ok(msg)


def mock_request(**overrides) -> dict:
    base = {
        "request_id": "mock-e2e-001",
        "requested_by": "owner",
        "intent": "summarize",
        "goal": "Summarize a mock document",
        "task_type": "mock.summarize",
        "risk_level": 0,
        "approval_required": False,
        "input_summary": "Mock input only",
        "target_runtime": "mock",
        "target_workspace": "local",
        "priority": "normal",
        "metadata": {"mock": True},
    }
    base.update(overrides)
    return base


def main() -> int:
    print("[1] low risk request → completed")
    r = run_mock_e2e_dry_run(mock_request(risk_level=0))
    _assert(r["dry_run"] is True, "dry_run_result contains dry_run=true")
    _assert(isinstance(r.get("task_id"), str) and r["task_id"], "dry_run_result contains task_id")
    _assert(isinstance(r.get("events"), list) and r["events"], "dry_run_result contains events list")
    _assert(r["initial_status"] == "queued", "low risk initial_status queued")
    _assert(r["final_status"] == "completed", "final_status is completed for normal queued mock task")
    _assert(r["callback_event"] is not None, "queued task produces a callback_event")
    validate_callback_event(r["callback_event"])
    _ok("CallbackEvent passes validate_callback_event")

    print("[2] risk_level 3 → stops at approval_gate")
    r = run_mock_e2e_dry_run(mock_request(risk_level=3))
    _assert(r["final_status"] == "pending_approval", "risk_level 3 → pending_approval")
    _assert(r["stopped_at"] == "approval_gate", "risk_level 3 → stopped_at approval_gate")
    _assert(r["callback_event"] is None, "pending_approval task does not produce completed callback")

    print("[3] approval_required true → stops at approval_gate")
    r = run_mock_e2e_dry_run(mock_request(risk_level=1, approval_required=True))
    _assert(r["final_status"] == "pending_approval", "approval_required true → pending_approval")
    _assert(r["stopped_at"] == "approval_gate", "approval_required true → stopped_at approval_gate")
    _assert(r["callback_event"] is None, "approval_required true → no callback_event")

    print("[4] mock.fail request → failed callback")
    r = run_mock_e2e_dry_run(mock_request(task_type="mock.fail", risk_level=0))
    _assert(r["final_status"] == "failed", "final_status is failed for mock.fail task")
    cb = r["callback_event"]
    _assert(cb is not None and cb["status"] == "failed", "mock.fail → failed CallbackEvent")
    _assert(cb["retryable"] is True, "mock.fail callback retryable=true")
    _assert(cb["error_code"] == "MOCK_FAILURE", "mock.fail callback error_code MOCK_FAILURE")
    validate_callback_event(cb)
    _ok("mock.fail CallbackEvent passes validate_callback_event")

    print("[5] final task envelope passes validate_task_envelope")
    r = run_mock_e2e_dry_run(mock_request(risk_level=0))
    # 重建最終 task 來驗證（dry_run_result 不直接帶 envelope，故用 worker + apply 流程重驗）
    from app.mock_adapter_v0_7 import prepare_queue_candidate_from_mock_request  # noqa: E402
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=0))
    validate_task_envelope(cand)
    cb = mock_worker_process_task(cand)
    updated = apply_callback_to_mock_task(cand, cb)
    validate_task_envelope(updated)
    _ok("TaskEnvelope passes validate_task_envelope")

    print("[6] InMemoryMockQueue 行為（純記憶體，不寫 DB）")
    q = InMemoryMockQueue()
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=0))
    q.enqueue(cand)
    claimed = q.claim_next()
    _assert(claimed is not None and claimed["status"] == "running", "claim_next 標記 running")
    _assert(q.claim_next() is None, "queue 沒有其他 queued 任務時 claim_next 回 None")
    cb = mock_worker_process_task(claimed)
    q.mark_completed(cand["task_id"], cb)
    _assert(q.get_task(cand["task_id"])["status"] == "completed", "mark_completed 更新狀態")
    # InMemoryMockQueue 不寫 DB：確認沒有 sqlite/檔案相關屬性
    _assert(not hasattr(q, "conn") and not hasattr(q, "db_path"),
            "InMemoryMockQueue does not write DB（無 conn / db_path）")

    print("[7] apply_callback_to_mock_task 不就地修改輸入")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=0))
    before = cand["status"]
    cb = mock_worker_process_task(cand)
    apply_callback_to_mock_task(cand, cb)
    _assert(cand["status"] == before, "apply_callback_to_mock_task 不修改輸入 task")

    print("[8] 非預期 mock request 缺欄位 → 失敗")
    bad = mock_request()
    del bad["request_id"]
    try:
        run_mock_e2e_dry_run(bad)
    except Exception as exc:  # noqa: BLE001
        _ok(f"缺欄位 mock request 觸發錯誤（{type(exc).__name__}）")
    else:
        raise AssertionError("FAIL: 缺欄位 mock request 應該失敗")

    print(f"\n✅ test_mock_e2e_v0_7_d 全數通過（{PASSED} 項，純 mock，未連任何系統）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
