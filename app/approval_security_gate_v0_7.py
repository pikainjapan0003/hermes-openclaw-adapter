"""v0.7.1-F — Approval-to-Queued Security Gate（純函式 helper，不接 route、不改狀態）。

在「waiting_review / pending_approval → queued」之前，應檢查的安全規則做成可測試純函式。
本版**只回決策**，不接 approve route、不改 QueueStore、不改 production 狀態機。

pure helper：
  - 不 import app.main / app.queue_store / app.worker / app.result_sink。
  - 不寫 DB、不改 Queue 狀態、不呼叫 approve / reject / enqueue / claim_next。
  - 不呼叫 OpenClaw / Google Sheets、不連外、不讀 secrets。
  - 僅 import app.security_gates_v0_7（純函式下層）與 stdlib（copy / json / typing）。

預設安全（fail-closed）：
  - approval_security_gates_enabled=False → allow（不破壞 production 既有 approve flow）。
  - enabled=True → 強制 fail-closed：local_only / mock / executable_by_worker=false /
    缺 requested_tools / 缺 allowed_tools / denylist 命中 / kill switch / 非 review 狀態 → reject。

公開 API：
  APPROVAL_SECURITY_GATES_ENABLED（文件化常數，預設 False；本版用函式參數控制，不接 env）
  evaluate_approval_to_queued(task_row, *, approval_security_gates_enabled=False,
                              global_kill_switch=False, layer_kill_switch=False) -> dict
  extract_payload / extract_metadata / extract_requested_tools / build_approval_audit_event
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.security_gates_v0_7 import build_audit_event, evaluate_security_gates

# 文件化預設：approval-to-queued security gate 預設關閉（接 route 時不破壞既有 approve flow）。
APPROVAL_SECURITY_GATES_ENABLED = False

# 允許進入 approve-to-queued 的「審核中」狀態。
REVIEW_STATUSES = {"waiting_review", "pending_approval"}


def extract_payload(task_row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """從 task_row 取出 payload（dict 或 JSON 字串）。無法解析 → None。"""
    payload = task_row.get("payload")
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def extract_metadata(task_row: Dict[str, Any]) -> Dict[str, Any]:
    """從 payload 取出 metadata（dict）。無則回 {}。"""
    payload = extract_payload(task_row)
    if not isinstance(payload, dict):
        return {}
    md = payload.get("metadata")
    return md if isinstance(md, dict) else {}


def extract_requested_tools(task_row: Dict[str, Any]) -> Any:
    """requested tools 來源固定為 payload.metadata.requested_tools（沿用 v0.7.1-E 裁定）。

    回傳原始值（可能 None / 非 list）；型別 / 空值由 evaluate_security_gates fail-closed 處理。
    """
    return extract_metadata(task_row).get("requested_tools")


def _decision(allowed: bool, reason: str, *, priority: str = "approval_gate",
              **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "allowed": allowed,
        "decision": "allow" if allowed else "reject",
        "reason": reason,
        "priority": priority,
    }
    out.update(extra)
    return out


def build_approval_audit_event(task_row: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    """observation-only audit event（不落地、不改狀態）。metadata 由 build_audit_event 遮罩。"""
    return build_audit_event(
        action="approval.security_gate",
        task_id=task_row.get("task_id"),
        correlation_id=task_row.get("correlation_id"),
        from_status=task_row.get("status"),
        to_status="queued",
        decision=decision.get("decision"),
        reason=decision.get("reason"),
        metadata=extract_metadata(task_row),
    )


def evaluate_approval_to_queued(
    task_row: Dict[str, Any],
    *,
    approval_security_gates_enabled: bool = False,
    global_kill_switch: bool = False,
    layer_kill_switch: bool = False,
) -> Dict[str, Any]:
    """評估 waiting_review 任務是否可安全轉 queued。純決策；不改 task_row、不寫狀態。

    回傳 dict：allowed / decision / reason / priority（+ 視情況 security_gate / audit_event）。
    """
    if not isinstance(task_row, dict):
        # 連 dict 都不是：直接保守 reject（不 mutate、不 raise，回決策）。
        return _decision(False, "task_row_not_dict")

    # disabled：維持既有 approve 行為（不強制 tool gate）。
    if not approval_security_gates_enabled:
        decision = _decision(True, "approval_security_gates_disabled")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    # 以下為 enabled 的 fail-closed 檢查。

    # 1) kill switch 最優先。
    if global_kill_switch:
        decision = _decision(False, "global_kill_switch_active", priority="global_kill_switch")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision
    if layer_kill_switch:
        decision = _decision(False, "layer_kill_switch_active", priority="layer_kill_switch")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    # 2) 必須處於審核中狀態。
    status = task_row.get("status")
    if status not in REVIEW_STATUSES:
        decision = _decision(False, "not_in_review_status")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    # 3) payload 必須可解析為 dict。
    payload = extract_payload(task_row)
    if payload is None:
        decision = _decision(False, "payload_missing_or_invalid")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    metadata = extract_metadata(task_row)

    # 4) local-only / mock / 不可執行 → 一律禁止 approve-to-queued。
    if metadata.get("local_only") is True:
        decision = _decision(False, "local_only_not_approvable")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision
    if metadata.get("mock") is True:
        decision = _decision(False, "mock_not_approvable")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision
    # executable_by_worker 必須明確為 True；False 或缺失 → fail-closed reject。
    if metadata.get("executable_by_worker") is not True:
        decision = _decision(False, "executable_by_worker_not_true")
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    # 5) tool-level security gate（reuse v0.7.1-D2 純函式；denylist 優先、空 allow/requested fail-closed）。
    gate = evaluate_security_gates(
        requested_tools=extract_requested_tools(task_row),
        allowed_tools=payload.get("allowed_tools"),
        denied_tools=payload.get("denied_tools"),
        # kill switch 已在步驟 1 處理；此處只做 tool denylist/allowlist 層。
        global_kill_switch=False,
        layer_kill_switch=False,
    )
    if not gate["allowed"]:
        decision = _decision(False, "tool_gate_rejected", priority=gate.get("priority", "allowlist"),
                             security_gate=gate)
        decision["audit_event"] = build_approval_audit_event(task_row, decision)
        return decision

    # 全部通過。
    decision = _decision(True, "approval_allowed", security_gate=gate)
    decision["audit_event"] = build_approval_audit_event(task_row, decision)
    return decision
