"""v0.7.1-F — Approval-to-Queued Security Gate pure helper 單元測試（純函式，不寫 DB / 不改狀態）。

執行： python scripts/test_approval_security_gate_v0_7_1_f.py
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.approval_security_gate_v0_7 import evaluate_approval_to_queued  # noqa: E402

# 測試 #19：import helper 不得拉進 main / worker / queue_store / result_sink。
_IMPORT_SAFE = all(
    m not in sys.modules
    for m in ("app.main", "app.worker", "app.queue_store", "app.result_sink")
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


def task_row(*, status="waiting_review", payload="__default__", as_str=False):
    if payload == "__default__":
        payload = {
            "allowed_tools": ["filesystem.read"],
            "denied_tools": [],
            "metadata": {
                "requested_tools": ["filesystem.read"],
                "local_only": False,
                "mock": False,
                "executable_by_worker": True,
            },
        }
    row = {"task_id": "t-1", "status": status, "correlation_id": "c-1", "payload": payload}
    if as_str and isinstance(row["payload"], dict):
        row["payload"] = json.dumps(row["payload"])
    return row


def _ev(row, **kw):
    kw.setdefault("approval_security_gates_enabled", True)
    return evaluate_approval_to_queued(row, **kw)


def main() -> int:
    _assert(_IMPORT_SAFE, "import helper 未拉進 main / worker / queue_store / result_sink")

    print("[1] gates disabled → allow (approval_security_gates_disabled)")
    r = evaluate_approval_to_queued(task_row(), approval_security_gates_enabled=False)
    _assert(r["allowed"] is True and r["reason"] == "approval_security_gates_disabled",
            "disabled → allow / reason approval_security_gates_disabled")

    print("[2] status 不是 review → reject")
    _assert(_ev(task_row(status="completed"))["allowed"] is False, "status completed → reject")
    _assert(_ev(task_row(status="queued"))["reason"] == "not_in_review_status", "status queued → not_in_review_status")

    print("[3] payload 缺失 / 非 dict / JSON 壞 → reject")
    _assert(_ev(task_row(payload=None))["reason"] == "payload_missing_or_invalid", "payload None → reject")
    _assert(_ev(task_row(payload="{not json"))["reason"] == "payload_missing_or_invalid", "payload 壞 JSON → reject")
    _assert(_ev(task_row(payload=123))["reason"] == "payload_missing_or_invalid", "payload 非 dict → reject")

    print("[4] local_only=true → reject")
    p = {"allowed_tools": ["read"], "metadata": {"requested_tools": ["read"], "local_only": True,
         "mock": False, "executable_by_worker": True}}
    _assert(_ev(task_row(payload=p))["reason"] == "local_only_not_approvable", "local_only → reject")

    print("[5] mock=true → reject")
    p = {"allowed_tools": ["read"], "metadata": {"requested_tools": ["read"], "local_only": False,
         "mock": True, "executable_by_worker": True}}
    _assert(_ev(task_row(payload=p))["reason"] == "mock_not_approvable", "mock → reject")

    print("[6] executable_by_worker=false → reject")
    p = {"allowed_tools": ["read"], "metadata": {"requested_tools": ["read"], "local_only": False,
         "mock": False, "executable_by_worker": False}}
    _assert(_ev(task_row(payload=p))["reason"] == "executable_by_worker_not_true", "executable false → reject")

    print("[7] executable_by_worker 缺失 → reject (fail-closed)")
    p = {"allowed_tools": ["read"], "metadata": {"requested_tools": ["read"], "local_only": False, "mock": False}}
    _assert(_ev(task_row(payload=p))["reason"] == "executable_by_worker_not_true", "executable 缺失 → reject")

    print("[8] requested_tools 缺失 / 空 / 非 list[str] → reject")
    base_md = {"local_only": False, "mock": False, "executable_by_worker": True}
    _assert(_ev(task_row(payload={"allowed_tools": ["read"], "metadata": dict(base_md)}))["reason"] == "tool_gate_rejected",
            "requested_tools 缺失 → tool_gate_rejected")
    _assert(_ev(task_row(payload={"allowed_tools": ["read"], "metadata": {**base_md, "requested_tools": []}}))["allowed"] is False,
            "requested_tools 空 → reject")
    _assert(_ev(task_row(payload={"allowed_tools": ["read"], "metadata": {**base_md, "requested_tools": "read"}}))["allowed"] is False,
            "requested_tools 非 list → reject")

    print("[9] allowed_tools 缺失 / 空 → reject")
    _assert(_ev(task_row(payload={"metadata": {**base_md, "requested_tools": ["read"]}}))["allowed"] is False,
            "allowed_tools 缺失 → reject")
    _assert(_ev(task_row(payload={"allowed_tools": [], "metadata": {**base_md, "requested_tools": ["read"]}}))["allowed"] is False,
            "allowed_tools 空 → reject")

    print("[10] denied_tools 命中 → reject (denylist priority)")
    p = {"allowed_tools": ["read"], "denied_tools": ["read"],
         "metadata": {**base_md, "requested_tools": ["read"]}}
    r = _ev(task_row(payload=p))
    _assert(r["allowed"] is False and r.get("security_gate", {}).get("priority") == "denylist",
            "denied 命中 → reject (denylist)")

    print("[11] requested tool 不在 allowed_tools → reject")
    p = {"allowed_tools": ["read"], "metadata": {**base_md, "requested_tools": ["write"]}}
    _assert(_ev(task_row(payload=p))["allowed"] is False, "tool 不在 allowlist → reject")

    print("[12] invalid tool name → reject")
    p = {"allowed_tools": ["bad tool!"], "metadata": {**base_md, "requested_tools": ["bad tool!"]}}
    _assert(_ev(task_row(payload=p))["allowed"] is False, "invalid tool name → reject")

    print("[13] global kill switch → reject")
    _assert(_ev(task_row(), global_kill_switch=True)["reason"] == "global_kill_switch_active", "global kill → reject")

    print("[14] layer kill switch → reject")
    _assert(_ev(task_row(), layer_kill_switch=True)["reason"] == "layer_kill_switch_active", "layer kill → reject")

    print("[15] 全部 OK → allow")
    r = _ev(task_row())
    _assert(r["allowed"] is True and r["reason"] == "approval_allowed", "全部條件 OK → allow")

    print("[16] payload JSON 字串可被解析")
    r = _ev(task_row(as_str=True))
    _assert(r["allowed"] is True and r["reason"] == "approval_allowed", "JSON 字串 payload → allow")

    print("[17] task_row 不被 mutate")
    row = task_row()
    snapshot = copy.deepcopy(row)
    _ev(row)
    _assert(row == snapshot, "evaluate_approval_to_queued 不修改 task_row")

    print("[18] audit_event observation_only=true")
    r = _ev(task_row())
    _assert(r["audit_event"]["observation_only"] is True, "audit_event observation_only=true")
    _assert(r["audit_event"]["action"] == "approval.security_gate", "audit action=approval.security_gate")

    print("[19]/[20] import / 呼叫安全")
    _ok("已驗證未 import main / worker / queue_store / result_sink（見開頭）")
    src = (Path(__file__).resolve().parent.parent / "app" / "approval_security_gate_v0_7.py").read_text(encoding="utf-8")
    for pat in (".approve(", ".reject(", "enqueue(", ".claim_next(", "run_openclaw_cli(",
                "googleapiclient", "import google"):
        _assert(pat not in src, f"helper 原始碼無呼叫痕跡「{pat}」")

    print(f"\n✅ test_approval_security_gate_v0_7_1_f 全數通過（{PASSED} 項，純函式，未寫 DB / 未改狀態）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
