"""v0.7.0-B — contracts_v0_7 validator 單元測試（純 mock，不連任何系統）。

執行： python scripts/test_contracts_v0_7_b.py
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.contracts_v0_7 import (  # noqa: E402
    ContractValidationError,
    validate_callback_event,
    validate_task_envelope,
)

PASSED = 0


def _ok(msg: str) -> None:
    global PASSED
    PASSED += 1
    print(f"  ok: {msg}")


def _expect_pass(fn, payload, msg: str) -> None:
    try:
        fn(payload)
    except ContractValidationError as exc:  # noqa: BLE001
        raise AssertionError(f"FAIL（預期通過卻失敗）: {msg}: {exc}") from exc
    _ok(msg)


def _expect_fail(fn, payload, msg: str) -> None:
    try:
        fn(payload)
    except ContractValidationError:
        _ok(msg)
        return
    raise AssertionError(f"FAIL（預期失敗卻通過）: {msg}")


def valid_task() -> dict:
    return {
        "task_id": "t-001",
        "created_at": "2026-06-27T00:00:00Z",
        "created_by": "hermes",
        "source": "hermes-agent",
        "requested_by": "owner",
        "risk_level": 1,
        "approval_required": False,
        "approval_status": "not_required",
        "intent": "查詢狀態",
        "goal": "回報目前 queue 狀態",
        "task_type": "query",
        "priority": "normal",
        "input_summary": "list queue",
        "target_runtime": "mock",
        "target_workspace": "default",
        "idempotency_key": "idem-001",
        "max_retries": 3,
        "retry_count": 0,
        "status": "queued",
        "result_policy": {"mode": "ledger"},
        "callback_policy": {"mode": "ledger_only"},
        "metadata": {},
    }


def valid_callback() -> dict:
    return {
        "event_id": "e-001",
        "task_id": "t-001",
        "source": "openclaw-worker",
        "created_at": "2026-06-27T00:01:00Z",
        "event_type": "completed",
        "status": "completed",
        "summary": "done",
        "retryable": False,
        "metadata": {},
    }


def main() -> int:
    print("[1] TaskEnvelope 測試")
    _expect_pass(validate_task_envelope, valid_task(), "valid TaskEnvelope passes")

    t = valid_task()
    del t["task_id"]
    _expect_fail(validate_task_envelope, t, "missing required field fails")

    t = valid_task()
    t["status"] = "not_a_status"
    _expect_fail(validate_task_envelope, t, "invalid status fails")

    t = valid_task()
    t["risk_level"] = 7
    _expect_fail(validate_task_envelope, t, "risk_level out of range fails")

    t = valid_task()
    t["risk_level"] = -1
    _expect_fail(validate_task_envelope, t, "risk_level negative fails")

    t = valid_task()
    t["approval_required"] = True
    t["approval_status"] = "pending"
    t["risk_level"] = 3
    _expect_pass(validate_task_envelope, t, "approval_required true + approval_status pending passes")

    t = valid_task()
    t["retry_count"] = -2
    _expect_fail(validate_task_envelope, t, "negative retry_count fails")

    t = valid_task()
    t["metadata"] = ["not", "a", "dict"]
    _expect_fail(validate_task_envelope, t, "metadata not object fails")

    t = valid_task()
    t["approval_required"] = "yes"
    _expect_fail(validate_task_envelope, t, "approval_required non-bool fails")

    t = valid_task()
    t["allowed_tools"] = ["bash", "read"]
    t["denied_tools"] = []
    t["input_payload_ref"] = None
    _expect_pass(validate_task_envelope, t, "optional fields (tools / payload_ref null) pass")

    print("[2] CallbackEvent 測試")
    _expect_pass(validate_callback_event, valid_callback(), "valid CallbackEvent passes")

    c = valid_callback()
    del c["task_id"]
    _expect_fail(validate_callback_event, c, "missing task_id fails")

    c = valid_callback()
    c["event_type"] = "exploded"
    _expect_fail(validate_callback_event, c, "invalid event_type fails")

    c = valid_callback()
    c["event_type"] = "failed"
    c["status"] = "failed"
    c["retryable"] = True
    c["error_code"] = "E_TIMEOUT"
    c["error_message"] = "execution timed out"
    c["duration_ms"] = 1234
    _expect_pass(validate_callback_event, c, "failed callback with error_code/error_message passes")

    c = valid_callback()
    c["status"] = "weird"
    _expect_fail(validate_callback_event, c, "invalid callback status fails")

    c = valid_callback()
    c["artifacts"] = {"not": "a list"}
    _expect_fail(validate_callback_event, c, "artifacts not array fails")

    c = valid_callback()
    c["duration_ms"] = -5
    _expect_fail(validate_callback_event, c, "negative duration_ms fails")

    # 確認 validator 不會就地修改輸入
    original = valid_task()
    snapshot = deepcopy(original)
    validate_task_envelope(original)
    if original != snapshot:
        raise AssertionError("FAIL: validator 不應修改輸入 payload")
    _ok("validator 不修改輸入 payload")

    print(f"\n✅ test_contracts_v0_7_b 全數通過（{PASSED} 項，純 mock，未連任何系統）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
