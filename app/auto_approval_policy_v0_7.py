"""v0.7.2-B — Auto-Approval Policy / Safe Autopilot（純函式 helper，observation-only）。

在「是否可低風險自動通過（policy 層）」這個問題上，做成可測試的純函式。
本 helper **只回 policy 決策**，不接 route、不寫 DB、不改 Queue 狀態、不執行 Worker、
不呼叫 OpenClaw / Hermes、不寫 Google Sheets、不讀 secrets。

固定安全保證（所有回傳恆為）：
  can_execute = False
  queue_transition_allowed = False
  observation_only = True

policy_decision enum：
  auto_approved          僅代表 policy 層低風險可自動通過；仍不可執行、不可 queued
  needs_owner_approval   需要 Owner 決定（unknown / missing / Level 2 / mode off / flags off）
  rejected               kill switch / fail-closed
  prohibited             Level 3 / forbidden operations / denied dangerous operations

import 邊界：
  只 import app.security_gates_v0_7（純函式下層）與 app.approval_security_gate_v0_7（純抽取）。
  不 import app.main / app.queue_store / app.worker / app.result_sink。
  不 import 本地 DB 驅動、HTTP client、子行程或任何雲端 client。
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from typing import Any, Dict, List, Optional

from app.approval_security_gate_v0_7 import extract_metadata, extract_payload
from app.security_gates_v0_7 import build_audit_event, evaluate_security_gates

# 文件化常數：auto-approval 預設關閉；mode 只支援 off | safe。
SUPPORTED_MODES = ("off", "safe")

# 風險上限：safety_level <= 此值 才可能進入 auto-approval（沿用 v0.5.4 既有語意）。
MAX_AUTO_SAFETY_LEVEL = 1

# Level 0：唯讀 / report / test / compile（無寫檔、無外部副作用）。
LEVEL0_TASK_TYPES = {"read_only_query", "report", "test", "compile", "readiness_check"}
# Level 1：local-only docs / plan / pure helper（audited）。
LEVEL1_TASK_TYPES = {"docs_only", "plan_only", "pure_helper_local"}
SAFE_TASK_TYPES = LEVEL0_TASK_TYPES | LEVEL1_TASK_TYPES

# 安全 requested_tools allowlist（唯讀 / 本地）。
SAFE_REQUESTED_TOOLS = {"read_file", "list_files", "grep", "search", "compile", "run_tests"}

# Protected files（命中 → Level 2 needs_owner_approval）。
EXACT_PROTECTED_FILES = {
    "app/main.py",
    "app/queue_store.py",
    "app/worker.py",
    "app/result_sink.py",
    "app/approval_security_gate_v0_7.py",
    "app/security_gates_v0_7.py",
    "app/queue_intake_bridge_v0_7.py",
    "app/dashboard_intake_view_v0_7.py",
    "scripts/start_worker.sh",
}
DIR_PROTECTED_PATTERNS = ("templates/*", "static/*")
# 廣義 live client patterns：只對 app/ 或 scripts/ 下的程式碼套用，避免把 docs 標題誤判為 client。
CLIENT_PROTECTED_PATTERNS = ("*google_sheets*", "*openclaw*", "*hermes*")

# Forbidden operations（命中 → Level 3 prohibited）。
FORBIDDEN_OPERATIONS = {
    "read_secrets",
    "display_secrets",
    "write_production_db",
    "start_worker",
    "call_openclaw",
    "call_hermes",
    "create_webhook",
    "git_push",
    "git_tag",
    "delete_file",
    "enable_google_sheets_live_write",
    "google_sheets_live_write",
}

_SAFETY_INT_RE = re.compile(r"^-?\d+$")


def _coerce_bool(value: Any) -> Optional[bool]:
    """寬鬆轉 bool。無法判定 → None。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes", "y"):
            return True
        if v in ("false", "0", "no", "n"):
            return False
    return None


def _parse_safety_level(metadata: Dict[str, Any]) -> Optional[int]:
    """回傳可解析的整數 safety_level；缺失 / 不可解析 → None（fail-closed 由呼叫端處理）。"""
    raw = metadata.get("safety_level")
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and _SAFETY_INT_RE.match(raw.strip()):
        return int(raw.strip())
    return None


def _normalize_path(path: Any) -> Optional[str]:
    if not isinstance(path, str):
        return None
    return path.strip().replace("\\", "/").lstrip("./")


def _is_protected_file(path: Any) -> bool:
    p = _normalize_path(path)
    if not p:
        return False
    if p in EXACT_PROTECTED_FILES:
        return True
    for pat in DIR_PROTECTED_PATTERNS:
        if fnmatch(p, pat):
            return True
    # 廣義 client patterns 只套用於 app/ 或 scripts/ 下的程式碼（不含 docs）。
    if p.startswith("app/") or p.startswith("scripts/"):
        for pat in CLIENT_PROTECTED_PATTERNS:
            if fnmatch(p, pat):
                return True
    return False


def _as_str_list(value: Any) -> Optional[List[str]]:
    """list[str] → 原樣；其他 → None（讓呼叫端 fail-closed）。"""
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return value
    return None


def _result(
    policy_decision: str,
    reason: str,
    *,
    matched_level: Optional[int],
    task_row: Dict[str, Any],
    task_type: Any,
    safety_level: Optional[int],
    requires_confirmation: Optional[bool],
    requested_tools: Any,
    allowed_tools: Any,
    denied_tools: Any,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """建立 observation-only policy 決策 dict。固定 can_execute/queue_transition_allowed=False。"""
    audit_event = build_audit_event(
        action="auto_approval.policy_decision",
        task_id=task_row.get("task_id") if isinstance(task_row, dict) else None,
        correlation_id=task_row.get("correlation_id") if isinstance(task_row, dict) else None,
        decision=policy_decision,
        reason=reason,
        risk_level=safety_level if isinstance(safety_level, int) else None,
        metadata=metadata,
    )
    return {
        "policy_decision": policy_decision,
        "reason": reason,
        "matched_level": matched_level,
        "can_auto_approve": policy_decision == "auto_approved",
        "can_execute": False,
        "queue_transition_allowed": False,
        "requires_owner_approval": policy_decision == "needs_owner_approval",
        "prohibited": policy_decision == "prohibited",
        "observation_only": True,
        "task_type": task_type,
        "safety_level": safety_level,
        "requires_confirmation": requires_confirmation,
        "requested_tools": requested_tools,
        "allowed_tools": allowed_tools,
        "denied_tools": denied_tools,
        "audit_event": audit_event,
    }


def evaluate_auto_approval(
    task_row: Dict[str, Any],
    *,
    auto_approval_mode: str = "off",
    safe_autopilot_enabled: bool = False,
    low_risk_auto_approval_enabled: bool = False,
    auto_approval_policy: str = "safe",
    global_kill_switch: bool = False,
    auto_approval_kill_switch: bool = False,
) -> Dict[str, Any]:
    """評估任務是否可安全 auto-approve（policy 層）。純決策；不 mutate task_row、不寫狀態。

    回傳 dict 永遠帶 can_execute=False / queue_transition_allowed=False / observation_only=True。
    auto_approved 僅代表 policy 層放行，**不代表 queued、不代表執行**。
    """
    # 抽取（純讀；非 dict 時以空 metadata 處理，最終 fail-closed）。
    metadata = extract_metadata(task_row) if isinstance(task_row, dict) else {}
    payload = extract_payload(task_row) if isinstance(task_row, dict) else None
    task_type = metadata.get("task_type")
    safety_level = _parse_safety_level(metadata)
    requires_confirmation = _coerce_bool(metadata.get("requires_confirmation"))
    requested_tools = metadata.get("requested_tools")
    allowed_tools = payload.get("allowed_tools") if isinstance(payload, dict) else None
    denied_tools = payload.get("denied_tools") if isinstance(payload, dict) else None
    requested_operations = metadata.get("requested_operations")
    touched_files = metadata.get("touched_files")

    def out(decision: str, reason: str, *, level: Optional[int] = None) -> Dict[str, Any]:
        return _result(
            decision, reason, matched_level=level, task_row=task_row if isinstance(task_row, dict) else {},
            task_type=task_type, safety_level=safety_level, requires_confirmation=requires_confirmation,
            requested_tools=requested_tools, allowed_tools=allowed_tools, denied_tools=denied_tools,
            metadata=metadata,
        )

    # 0) task_row 必須是 dict。
    if not isinstance(task_row, dict):
        return out("needs_owner_approval", "task_row_not_dict")

    # 1) global kill switch。
    if global_kill_switch:
        return out("rejected", "global_kill_switch_active")
    # 2) auto-approval layer kill switch。
    if auto_approval_kill_switch:
        return out("rejected", "auto_approval_kill_switch_active")

    # 3) mode 必須 off | safe；off → needs_owner；unsupported → fail-closed needs_owner。
    if auto_approval_mode == "off":
        return out("needs_owner_approval", "auto_approval_mode_off")
    if auto_approval_mode not in SUPPORTED_MODES:
        return out("needs_owner_approval", "unsupported_auto_approval_mode")

    # 4) policy / autopilot flags。
    if auto_approval_policy != "safe":
        return out("needs_owner_approval", "unsupported_auto_approval_policy")
    if not safe_autopilot_enabled:
        return out("needs_owner_approval", "safe_autopilot_disabled")
    if not low_risk_auto_approval_enabled:
        return out("needs_owner_approval", "low_risk_auto_approval_disabled")

    # 5) payload 必須可解析為 dict。
    if payload is None:
        return out("needs_owner_approval", "payload_missing_or_invalid")

    # 6) forbidden operations → prohibited（Level 3）。
    ops = _as_str_list(requested_operations)
    if requested_operations is not None and ops is None:
        return out("needs_owner_approval", "invalid_requested_operations")
    if ops:
        hit = [o for o in ops if o in FORBIDDEN_OPERATIONS]
        if hit:
            return out("prohibited", "forbidden_operation", level=3)

    # 7) protected files → needs_owner（Level 2）。
    tf = _as_str_list(touched_files)
    if touched_files is not None and tf is None:
        return out("needs_owner_approval", "invalid_touched_files")
    if tf:
        if any(_is_protected_file(f) for f in tf):
            return out("needs_owner_approval", "protected_file_touched", level=2)

    # 8) denied_tools / denylist → prohibited（denylist 覆蓋 allowlist）。
    requested_list = _as_str_list(requested_tools)
    denied_list = _as_str_list(denied_tools) or []
    if requested_list:
        denied_hit = [t for t in requested_list if t in denied_list]
        if denied_hit:
            return out("prohibited", "denied_tool_matched", level=3)

    # 9) task_type allowlist。
    if not isinstance(task_type, str) or task_type not in SAFE_TASK_TYPES:
        return out("needs_owner_approval", "task_type_not_in_safe_allowlist", level=2)

    # 10) requested_tools allowlist（空 / 未知 / 非安全 → fail-closed）。
    if not requested_list:
        return out("needs_owner_approval", "requested_tools_empty")
    not_safe = [t for t in requested_list if t not in SAFE_REQUESTED_TOOLS]
    if not_safe:
        return out("needs_owner_approval", "requested_tool_not_in_safe_allowlist")
    # 重用 v0.7.1-D2 純函式做 task 自身 allowed/denied 強制（空 allowed_tools → fail-closed）。
    gate = evaluate_security_gates(
        requested_tools=requested_list,
        allowed_tools=_as_str_list(allowed_tools),
        denied_tools=denied_list,
        global_kill_switch=False,
        layer_kill_switch=False,
    )
    if not gate["allowed"]:
        if gate.get("priority") == "denylist":
            return out("prohibited", "denied_tool_matched", level=3)
        return out("needs_owner_approval", f"tool_gate_{gate['reason']}")

    # 11) risk level gate：safety_level 必須存在且 <= 上限。
    if safety_level is None:
        return out("needs_owner_approval", "missing_or_invalid_safety_level")
    if safety_level > MAX_AUTO_SAFETY_LEVEL:
        return out("needs_owner_approval", "safety_level_too_high")

    # 12) requires_confirmation=True → needs_owner。
    if requires_confirmation is True:
        return out("needs_owner_approval", "requires_confirmation")

    # 13) local_only / mock / executable_by_worker boundary：observation-only（不阻擋，記錄於 audit）。
    #     auto-approval 永不執行，故 boundary 僅供觀察；can_execute 已恆為 False。

    # 14) 全數通過 → auto_approved（Level 0 / Level 1）。
    level = 0 if task_type in LEVEL0_TASK_TYPES else 1
    return out("auto_approved", "auto_approved_low_risk", level=level)
