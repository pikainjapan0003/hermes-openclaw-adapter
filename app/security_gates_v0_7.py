"""v0.7.1-D2 — Local-only Security Gates（純函式、可測試；不接任何真路徑）。

把 v0.7.1-D 規格（kill switch / per-tool allowlist / audit log）做成獨立、local-only、
純函式模組。本模組：

  - 不 import app.main / app.worker / app.queue_store / app.result_sink。
  - 不寫 DB、不改 Queue 狀態、不呼叫 OpenClaw CLI、不呼叫 Google client、不連外、不讀 secrets。
  - 僅用標準庫（os / json / datetime / hashlib / uuid / re / typing）。

安全原則（fail-closed）：
  - kill switch 優先於 allowlist；denylist 優先於 allowlist。
  - allowed_tools / requested_tools 為空或 None → reject。
  - unknown / 格式不合法的 tool name → reject。
  - 無法判定的 kill switch（None）→ 視為 active（reject）。
  - audit event 為 observation-only，不改任何狀態；不得含原始 secret（一律遮罩）。

公開 API：
  evaluate_kill_switch(...)        -> dict
  evaluate_tool_allowlist(...)     -> dict
  evaluate_security_gates(...)     -> dict
  redact_audit_metadata(metadata)  -> dict
  build_audit_event(...)           -> dict
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

REDACTED = "***REDACTED***"

# 合法 tool name 格式（保守）。
TOOL_NAME_RE = re.compile(r"^[a-zA-Z0-9_.:-]{1,64}$")

# audit metadata 中視為敏感、需遮罩的 key 子字串（小寫比對）。
SENSITIVE_KEY_SUBSTRINGS = (
    "refresh_token",
    "client_secret",
    "access_token",
    "private_key",
    "credentials",
    "token",
    "spreadsheet_id",
    "google_sheets_url",
    "secret",
    "password",
)

# value 內若出現這些格式（完整 spreadsheet id / url / token 前綴 / private key）→ 整段遮罩。
_RE_SPREADSHEET_URL = re.compile(r"spreadsheets/d/[A-Za-z0-9_-]{20,}")
_RE_TOKEN_PREFIX = re.compile(r"(ya29\.[A-Za-z0-9_-]{10,}|1//[A-Za-z0-9_-]{10,}|" + "goc" + r"spx-[A-Za-z0-9_-]{10,})")
_RE_PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_RE_LONG_ID = re.compile(r"^[A-Za-z0-9_-]{30,}$")  # 疑似長 id（保守遮罩）


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _decision(allowed: bool, reason: str, priority: str, **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "allowed": allowed,
        "decision": "allow" if allowed else "reject",
        "reason": reason,
        "priority": priority,
    }
    out.update(extra)
    return out


def evaluate_kill_switch(
    *,
    global_kill_switch: Optional[bool] = None,
    layer_kill_switch: Optional[bool] = None,
) -> Dict[str, Any]:
    """評估 kill switch。active（True）或無法判定（None）一律 reject（fail-closed）。

    只有兩者皆明確為 False 才 allow。
    """
    if global_kill_switch is True:
        return _decision(False, "global_kill_switch_active", "global_kill_switch")
    if global_kill_switch is None:
        return _decision(False, "global_kill_switch_unknown", "global_kill_switch")
    if layer_kill_switch is True:
        return _decision(False, "layer_kill_switch_active", "layer_kill_switch")
    if layer_kill_switch is None:
        return _decision(False, "layer_kill_switch_unknown", "layer_kill_switch")
    return _decision(True, "kill_switch_clear", "kill_switch")


def evaluate_tool_allowlist(
    *,
    requested_tools: Optional[List[str]],
    allowed_tools: Optional[List[str]],
    denied_tools: Optional[List[str]],
) -> Dict[str, Any]:
    """評估 per-tool allowlist。denylist 優先；空 allowed_tools / requested_tools → fail-closed reject。"""
    denied = list(denied_tools or [])
    allowed = list(allowed_tools or [])
    requested = requested_tools if isinstance(requested_tools, list) else None

    # requested 為空 / None → reject。
    if not requested:
        return _decision(False, "requested_tools_empty", "allowlist",
                         matched_denied_tools=[], missing_allowed_tools=[])

    # tool name 格式檢查（任一不合法即 reject）。
    invalid = [t for t in requested if not (isinstance(t, str) and TOOL_NAME_RE.match(t))]
    if invalid:
        return _decision(False, "invalid_tool_name", "allowlist",
                         matched_denied_tools=[], missing_allowed_tools=[],
                         invalid_tools=[str(t)[:64] for t in invalid])

    # denylist 優先。
    matched_denied = [t for t in requested if t in denied]
    if matched_denied:
        return _decision(False, "denied_tool_matched", "denylist",
                         matched_denied_tools=matched_denied, missing_allowed_tools=[])

    # allowed_tools 空 → fail-closed reject。
    if not allowed:
        return _decision(False, "allowed_tools_empty", "allowlist",
                         matched_denied_tools=[], missing_allowed_tools=list(requested))

    # 每個 requested 都必須在 allowed 內。
    missing = [t for t in requested if t not in allowed]
    if missing:
        return _decision(False, "tool_not_in_allowlist", "allowlist",
                         matched_denied_tools=[], missing_allowed_tools=missing)

    return _decision(True, "all_tools_allowed", "allowlist",
                     matched_denied_tools=[], missing_allowed_tools=[])


def evaluate_security_gates(
    *,
    requested_tools: Optional[List[str]],
    allowed_tools: Optional[List[str]],
    denied_tools: Optional[List[str]],
    global_kill_switch: Optional[bool] = None,
    layer_kill_switch: Optional[bool] = None,
) -> Dict[str, Any]:
    """依優先序套用：1) global kill switch 2) layer kill switch 3) denylist 4) allowlist。"""
    ks = evaluate_kill_switch(
        global_kill_switch=global_kill_switch, layer_kill_switch=layer_kill_switch
    )
    if not ks["allowed"]:
        return _decision(False, ks["reason"], ks["priority"],
                         matched_denied_tools=[], missing_allowed_tools=[])

    return evaluate_tool_allowlist(
        requested_tools=requested_tools,
        allowed_tools=allowed_tools,
        denied_tools=denied_tools,
    )


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        if (_RE_SPREADSHEET_URL.search(value) or _RE_TOKEN_PREFIX.search(value)
                or _RE_PRIVATE_KEY.search(value) or _RE_LONG_ID.match(value)):
            return REDACTED
        return value
    if isinstance(value, dict):
        return redact_audit_metadata(value)
    if isinstance(value, list):
        return [_redact_value(v) for v in value]
    return value


def redact_audit_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """回傳遮罩後的 metadata 副本。敏感 key 直接遮罩；可疑值（id/url/token/private key）亦遮罩。"""
    if not isinstance(metadata, dict):
        return {}
    out: Dict[str, Any] = {}
    for key, value in metadata.items():
        key_l = str(key).lower()
        if any(sub in key_l for sub in SENSITIVE_KEY_SUBSTRINGS):
            out[key] = REDACTED
        else:
            out[key] = _redact_value(value)
    return out


def _mask_actor_id(actor_id: Optional[str]) -> Optional[str]:
    if not actor_id:
        return None
    digest = hashlib.sha256(str(actor_id).encode("utf-8")).hexdigest()[:12]
    return f"actor-{digest}"


def build_audit_event(
    *,
    action: str,
    task_id: Optional[str] = None,
    actor_type: str = "system",
    actor_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    from_status: Optional[str] = None,
    to_status: Optional[str] = None,
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    risk_level: Optional[int] = None,
    source_mode: Optional[str] = None,
    intake_mode: Optional[str] = None,
    tool_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """建立 observation-only audit event（純資料；不寫 DB、不改 queue 狀態）。

    actor_id 一律 mask/hash；metadata 一律 redact；不含任何原始 secret。
    """
    return {
        "event_id": f"audit-{uuid.uuid4()}",
        "created_at": _utc_now_iso(),
        "actor_type": actor_type,
        "actor_id_masked": _mask_actor_id(actor_id),
        "action": action,
        "task_id": task_id,
        "correlation_id": correlation_id,
        "from_status": from_status,
        "to_status": to_status,
        "decision": decision,
        "reason": reason,
        "risk_level": risk_level,
        "source_mode": source_mode,
        "intake_mode": intake_mode,
        "tool_name": tool_name,
        "metadata_redacted": redact_audit_metadata(metadata),
        "observation_only": True,
    }
