"""v0.7.1-C — Dashboard Intake Status View Model（純函式、唯讀顯示推導）。

從一筆 Queue task row/dict 推導出**安全的唯讀顯示欄位**（mock / local-only / real、
intake mode、是否可被 worker 執行、approval / risk）。本模組：

  - 純函式：不寫 DB、不改 Queue 狀態、不連外。
  - 不 import app.main、不 import app.worker。
  - 不呼叫 OpenClaw / Google Sheets、不讀 secrets。
  - 僅用標準庫（json）。

保守原則：
  - 不能確定時一律回 "unknown"。
  - 絕不把 unknown 推成 true。
  - 絕不把 local-only 任務推成 executable_by_worker=true。

公開 API：
  derive_intake_status_view(task: dict) -> dict
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

# worker 不會 claim 的狀態（QueueStore.claim_next 只取 'queued'）。
NON_EXECUTABLE_STATUSES = {
    "waiting_review",
    "rejected",
    "cancelled",
    "archived",
    "completed",
    "failed",
}
LOCAL_INTAKE_SOURCE = "mock-adapter-local"


def _as_payload_dict(payload: Any) -> Dict[str, Any]:
    """payload 可能是 dict 或 JSON 字串；解析失敗回 {}。"""
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _extract_metadata(task: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """優先取 payload.metadata，其次 task.metadata（兩者皆為 dict 才採用）。"""
    md = payload.get("metadata")
    if isinstance(md, dict):
        return md
    md = task.get("metadata")
    return md if isinstance(md, dict) else {}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _derive_source_mode(metadata: Dict[str, Any]) -> str:
    """local-only（最具體）> mock > real（明確非 mock）> unknown。"""
    if metadata.get("intake_source") == LOCAL_INTAKE_SOURCE:
        return "local-only"
    mock = metadata.get("mock")
    if mock is True:
        return "mock"
    if mock is False:
        return "real"
    return "unknown"


def _derive_intake_mode(metadata: Dict[str, Any]) -> str:
    local_only = metadata.get("local_only")
    if local_only is True:
        return "local-only"
    if local_only is False:
        return "production"
    return "unknown"


def _derive_executable_by_worker(
    status: Optional[str],
    metadata: Dict[str, Any],
    *,
    is_local_only: bool,
) -> str:
    """回傳 'true' / 'false' / 'unknown'。保守：local-only 絕不為 true。"""
    base: Optional[bool]
    explicit = metadata.get("executable_by_worker")
    if isinstance(explicit, bool):
        base = explicit
    elif status == "queued":
        base = True
    elif status in NON_EXECUTABLE_STATUSES:
        base = False
    else:
        base = None  # unknown

    # 保守防線：local-only 任務絕不可被推成 executable=true。
    if is_local_only and base is True:
        base = False

    if base is True:
        return "true"
    if base is False:
        return "false"
    return "unknown"


def _derive_risk_level(
    task: Dict[str, Any], payload: Dict[str, Any], metadata: Dict[str, Any]
) -> Optional[int]:
    for candidate in (metadata.get("risk_level"), payload.get("risk_level"), task.get("safety_level")):
        if _is_int(candidate):
            return candidate
    return None


def _derive_approval_status(
    metadata: Dict[str, Any], status: Optional[str], safety_level: Optional[int]
) -> str:
    explicit = metadata.get("approval_status")
    if isinstance(explicit, str) and explicit:
        return explicit
    if status == "waiting_review":
        return "pending"
    if status == "queued" and _is_int(safety_level) and safety_level <= 2:
        return "not_required"
    return "unknown"


def derive_intake_status_view(task: Dict[str, Any]) -> Dict[str, Any]:
    """從 Queue task row/dict 推導唯讀顯示欄位（純函式，不寫 DB、不改狀態）。"""
    if not isinstance(task, dict):
        raise TypeError("task 必須為 dict")

    payload = _as_payload_dict(task.get("payload"))
    metadata = _extract_metadata(task, payload)
    status = task.get("status")
    safety_level = task.get("safety_level") if _is_int(task.get("safety_level")) else None

    source_mode = _derive_source_mode(metadata)
    intake_mode = _derive_intake_mode(metadata)
    is_local_only = (
        intake_mode == "local-only"
        or source_mode == "local-only"
        or metadata.get("local_only") is True
    )
    executable_by_worker = _derive_executable_by_worker(
        status, metadata, is_local_only=is_local_only
    )
    risk_level = _derive_risk_level(task, payload, metadata)
    approval_status = _derive_approval_status(metadata, status, safety_level)

    badges = []
    if source_mode != "unknown":
        badges.append(source_mode)
    if intake_mode == "local-only":
        badges.append("local-only-intake")
    if executable_by_worker == "false":
        badges.append("not-executable")
    elif executable_by_worker == "unknown":
        badges.append("exec-unknown")
    if approval_status == "pending":
        badges.append("approval-pending")
    if _is_int(risk_level):
        badges.append(f"risk:{risk_level}")

    return {
        "task_id": task.get("task_id"),
        "status": status,
        "source_mode": source_mode,
        "intake_mode": intake_mode,
        "executable_by_worker": executable_by_worker,
        "approval_status": approval_status,
        "risk_level": risk_level,
        "safety_level": safety_level,
        "display_badges": badges,
    }
