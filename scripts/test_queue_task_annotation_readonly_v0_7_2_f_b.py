"""v0.7.2-F-B — Queue Task Annotation Deriver 單元測試（純函式，唯讀，不寫檔）。

執行： python scripts/test_queue_task_annotation_readonly_v0_7_2_f_b.py

不依賴 QueueStore / Worker / app.main / Replit queue，也不寫任何檔案。
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.queue_task_annotation_v0_7 import (  # noqa: E402
    derive_queue_task_annotation,
    normalize_approval_readiness,
)

# import deriver 不得拉進 app.main / app.queue_store / app.worker。
_IMPORT_SAFE = (
    "app.main" not in sys.modules
    and "app.queue_store" not in sys.modules
    and "app.worker" not in sys.modules
)

# derive_queue_task_annotation() 必須輸出的欄位。
EXPECTED_FIELDS = (
    "task_origin",
    "requested_by",
    "request_channel",
    "owner_reason",
    "approval_readiness",
    "approval_blockers",
    "risk_summary",
    "side_effect_summary",
    "next_step_if_approved",
    "execution_mode",
    "external_touchpoints",
    "dry_run_available",
    "mock_available",
    "rollback_note",
    "human_readable_summary",
    "execution_permission",
    "dispatch_allowed",
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


def task(*, status=None, metadata=None, payload=None, payload_as_str=False, **top):
    """建立測試用 task row。預設 payload = {"metadata": metadata}。"""
    if payload is None:
        payload = {"metadata": metadata if metadata is not None else {}}
    row = {"task_id": "t-1", "status": status, "payload": payload}
    if payload_as_str and isinstance(row["payload"], (dict, list)):
        row["payload"] = json.dumps(row["payload"])
    row.update(top)
    return row


def main() -> int:
    _assert(_IMPORT_SAFE, "import deriver 不會拉進 app.main / app.queue_store / app.worker")

    print("[1] minimal legacy task：缺 payload / metadata，不 crash，not_ready，dispatch False")
    a = derive_queue_task_annotation({"task_id": "legacy-1"})
    _assert(a["approval_readiness"] == "not_ready", "缺 payload → approval_readiness not_ready")
    _assert(a["dispatch_allowed"] is False, "缺 payload → dispatch_allowed False")
    _assert(a["execution_permission"] is False, "缺 payload → execution_permission False")
    _assert(a["task_origin"] == "unknown", "缺 payload → task_origin unknown")
    _assert(a["approval_blockers"] == ["missing_annotation"], "缺註解 → blockers missing_annotation")
    # 完全空 dict 也不 crash。
    b = derive_queue_task_annotation({})
    _assert(b["approval_readiness"] == "not_ready", "空 dict → not_ready，不 crash")

    print("[2] waiting_review demo task：safety_level=3 / requires_confirmation=true → owner_review_required")
    t2 = task(
        status="waiting_review",
        metadata={"safety_level": 3, "requires_confirmation": True},
    )
    a = derive_queue_task_annotation(t2)
    _assert(a["approval_readiness"] == "owner_review_required", "waiting_review → owner_review_required")
    _assert(a["dispatch_allowed"] is False, "waiting_review → dispatch_allowed False")
    _assert(a["execution_permission"] is False, "waiting_review → execution_permission False")

    print("[3] explicit ready metadata：ready_for_owner_decision → 顯示 ready 但仍不放行")
    t3 = task(
        status="waiting_review",
        metadata={
            "approval_readiness": "ready_for_owner_decision",
            "task_origin": "owner-cli",
            "requested_by": "owner",
            "request_channel": "local",
        },
    )
    a = derive_queue_task_annotation(t3)
    _assert(a["approval_readiness"] == "ready_for_owner_decision", "explicit ready → ready_for_owner_decision")
    _assert(a["execution_permission"] is False, "ready → execution_permission 仍 False")
    _assert(a["dispatch_allowed"] is False, "ready → dispatch_allowed 仍 False")
    _assert(a["task_origin"] == "owner-cli", "task_origin 帶出 metadata 值")

    print("[4] prohibited metadata → 推導 prohibited")
    a = derive_queue_task_annotation(task(metadata={"approval_readiness": "prohibited"}))
    _assert(a["approval_readiness"] == "prohibited", "explicit approval_readiness prohibited → prohibited")
    a = derive_queue_task_annotation(task(metadata={"policy_decision": "prohibited"}))
    _assert(a["approval_readiness"] == "prohibited", "policy_decision prohibited → prohibited")
    a = derive_queue_task_annotation(task(metadata={"approval_status": "prohibited"}))
    _assert(a["approval_readiness"] == "prohibited", "approval_status prohibited → prohibited")
    # prohibited 優先於 explicit ready（限制性高者優先）。
    a = derive_queue_task_annotation(
        task(metadata={"approval_readiness": "ready_for_owner_decision", "prohibited": True})
    )
    _assert(a["approval_readiness"] == "prohibited", "prohibited 旗標覆蓋 explicit ready")
    _assert(a["dispatch_allowed"] is False, "prohibited → dispatch_allowed False")

    print("[5] blocked_by_policy metadata → 推導 blocked_by_policy")
    a = derive_queue_task_annotation(task(metadata={"approval_readiness": "blocked_by_policy"}))
    _assert(a["approval_readiness"] == "blocked_by_policy", "explicit blocked_by_policy → blocked_by_policy")
    a = derive_queue_task_annotation(task(metadata={"blocked_by_policy": True}))
    _assert(a["approval_readiness"] == "blocked_by_policy", "blocked_by_policy 旗標 → blocked_by_policy")
    a = derive_queue_task_annotation(task(metadata={"policy_blocked": True}))
    _assert(a["approval_readiness"] == "blocked_by_policy", "policy_blocked 旗標 → blocked_by_policy")

    print("[6] JSON string payload：可解析 metadata")
    t6 = task(
        status="waiting_review",
        metadata={"task_origin": "hermes-intake", "approval_readiness": "ready_for_owner_decision"},
        payload_as_str=True,
    )
    _assert(isinstance(t6["payload"], str), "前置：payload 確實是 JSON 字串")
    a = derive_queue_task_annotation(t6)
    _assert(a["task_origin"] == "hermes-intake", "JSON 字串 payload → 解析出 task_origin")
    _assert(a["approval_readiness"] == "ready_for_owner_decision", "JSON 字串 payload → 解析出 readiness")

    print("[7] invalid JSON payload：不 crash，fallback not_ready")
    t7 = {"task_id": "bad-json", "status": "waiting_review", "payload": "{not valid json"}
    a = derive_queue_task_annotation(t7)
    _assert(a["approval_readiness"] == "owner_review_required", "壞 JSON + waiting_review → owner_review_required（不 crash）")
    _assert(a["task_origin"] == "unknown", "壞 JSON → metadata 視為空 → task_origin unknown")
    # 壞 JSON 且非審核狀態 → not_ready。
    a = derive_queue_task_annotation({"task_id": "bad-json-2", "status": "queued", "payload": "%%%"})
    _assert(a["approval_readiness"] == "not_ready", "壞 JSON + 非審核 → fallback not_ready")

    print("[8] input immutability：derive 後原 task 不變")
    t8 = task(status="waiting_review", metadata={"task_origin": "demo", "external_touchpoints": ["none"]})
    snapshot = copy.deepcopy(t8)
    derive_queue_task_annotation(t8)
    _assert(t8 == snapshot, "derive 不 mutate 輸入 task")
    # 改動回傳的 list 不應影響原 metadata。
    a = derive_queue_task_annotation(t8)
    a["external_touchpoints"].append("mutated")
    a["approval_blockers"].append("mutated")
    _assert(t8 == snapshot, "改動回傳 list 不回寫原 task")

    print("[9] annotation fields 全部存在")
    a = derive_queue_task_annotation(task(status="waiting_review", metadata={}))
    for field in EXPECTED_FIELDS:
        _assert(field in a, f"annotation 含欄位 {field}")
    _assert(a["execution_permission"] is False, "execution_permission 恆為 False")
    _assert(a["dispatch_allowed"] is False, "dispatch_allowed 恆為 False")

    print("[10] normalize_approval_readiness：合法→正規化，不合法→空字串")
    _assert(normalize_approval_readiness("PROHIBITED") == "prohibited", "大小寫正規化")
    _assert(normalize_approval_readiness("  owner_review_required ") == "owner_review_required", "去空白")
    _assert(normalize_approval_readiness("bogus") == "", "不合法 enum → 空字串")
    _assert(normalize_approval_readiness(None) == "", "None → 空字串")
    _assert(normalize_approval_readiness(3) == "", "非字串 → 空字串")

    print("[11] 不需要 QueueStore / Worker / app.main（import 後仍未載入）")
    _assert(
        "app.main" not in sys.modules
        and "app.queue_store" not in sys.modules
        and "app.worker" not in sys.modules,
        "deriver 全程不載入 app.main / app.queue_store / app.worker",
    )

    print(f"\n✅ test_queue_task_annotation_readonly_v0_7_2_f_b 全數通過（{PASSED} 項，純函式，未寫檔）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
