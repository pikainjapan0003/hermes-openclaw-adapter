"""v0.7.0-C — mock adapter + approval gate 單元測試（純 mock，不連任何系統）。

執行： python scripts/test_mock_adapter_v0_7_c.py
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.contracts_v0_7 import ContractValidationError, validate_task_envelope  # noqa: E402
from app.mock_adapter_v0_7 import (  # noqa: E402
    MockAdapterError,
    apply_approval_gate,
    build_task_envelope_from_mock_request,
    prepare_queue_candidate_from_mock_request,
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


def _expect_fail(fn, payload, exc, msg: str) -> None:
    try:
        fn(payload)
    except exc:
        _ok(msg)
        return
    raise AssertionError(f"FAIL（預期失敗卻通過）: {msg}")


def mock_request(**overrides) -> dict:
    base = {
        "request_id": "mock-001",
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
    print("[1] low risk → queued + not_required")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=0))
    _assert(cand["status"] == "queued", "low risk → status queued")
    _assert(cand["approval_status"] == "not_required", "low risk → approval_status not_required")

    print("[2] risk_level 2 且未要求批准 → queued")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=2))
    _assert(cand["status"] == "queued", "risk_level 2 → queued")
    _assert(cand["approval_status"] == "not_required", "risk_level 2 → not_required")

    print("[3] risk_level 3 → pending_approval + pending")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=3))
    _assert(cand["status"] == "pending_approval", "risk_level 3 → pending_approval")
    _assert(cand["approval_status"] == "pending", "risk_level 3 → approval_status pending")
    _assert(cand["approval_required"] is True, "risk_level 3 → approval_required true")

    print("[4] risk_level 4 → pending_approval + pending")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=4))
    _assert(cand["status"] == "pending_approval", "risk_level 4 → pending_approval")
    _assert(cand["approval_status"] == "pending", "risk_level 4 → approval_status pending")
    _assert(cand["approval_required"] is True, "risk_level 4 → approval_required true")

    print("[5] approval_required true（低風險也要批准）→ pending_approval")
    cand = prepare_queue_candidate_from_mock_request(
        mock_request(risk_level=1, approval_required=True)
    )
    _assert(cand["status"] == "pending_approval", "approval_required true → pending_approval")
    _assert(cand["approval_status"] == "pending", "approval_required true → approval_status pending")

    print("[6] 缺 mock 必要欄位 → MockAdapterError")
    bad = mock_request()
    del bad["request_id"]
    _expect_fail(prepare_queue_candidate_from_mock_request, bad, MockAdapterError,
                 "missing required mock request field fails")

    print("[7] 不合法 risk_level → ContractValidationError")
    _expect_fail(prepare_queue_candidate_from_mock_request, mock_request(risk_level=9),
                 ContractValidationError, "invalid risk_level fails")

    print("[8] 最終輸出通過 validate_task_envelope")
    cand = prepare_queue_candidate_from_mock_request(mock_request(risk_level=0))
    validate_task_envelope(cand)
    _ok("final output passes validate_task_envelope")

    print("[9] idempotency_key 存在；metadata.mock = true")
    _assert(isinstance(cand.get("idempotency_key"), str) and cand["idempotency_key"],
            "idempotency_key exists（非空字串）")
    _assert(cand.get("metadata", {}).get("mock") is True, "metadata.mock = true")

    print("[10] apply_approval_gate 不就地修改輸入")
    env = build_task_envelope_from_mock_request(mock_request(risk_level=3))
    snapshot = deepcopy(env)
    apply_approval_gate(env)
    _assert(env == snapshot, "apply_approval_gate 不修改輸入 envelope")

    print("[11] 相同 request → 相同 idempotency_key")
    a = build_task_envelope_from_mock_request(mock_request(request_id="same-1"))
    b = build_task_envelope_from_mock_request(mock_request(request_id="same-1"))
    _assert(a["idempotency_key"] == b["idempotency_key"], "相同 request 產生相同 idempotency_key")

    print(f"\n✅ test_mock_adapter_v0_7_c 全數通過（{PASSED} 項，純 mock，未連任何系統）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
