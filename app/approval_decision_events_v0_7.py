"""v0.7.3-B — Approval Decision Event View（純函式、唯讀，display-only）。

從一筆既有 Queue task dict / row（含 payload.metadata.approval_decision_events）
推導出 Owner Review 介面可顯示的「Owner 決策紀錄」唯讀檢視。本模組只負責顯示推導，
不記錄事件、不寫入、不授予任何執行權限。

純 helper 邊界（approval decision event view is read-only）：
  - 不寫入 task、不寫入 QueueStore、不修改 metadata、不 mutate 輸入。
  - 不讀 .env、不讀 secrets、不連外。
  - 不 import app.main、不 import QueueStore、不 import worker。
  - 不啟動 Worker、不呼叫 OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 僅用標準庫（json / typing）。

決策／執行分離（核心安全規則）：
  approve is not execute.
  Owner decision event is not Worker dispatch.
  Owner approval does not automatically imply Worker execution.
  Decision and execution dispatch remain separate.
  Approval readiness is not execution permission.

因此回傳的 view 與每個 event 的 ``execution_permission`` / ``dispatch_allowed``
（含 *_at_decision 快照）恆為 ``False``。本段（v0.7.3-B）只讀顯示；
v0.7.3-C 才會規劃 local recorder。

公開 API：
  derive_approval_decision_event_view(task) -> dict
  normalize_payload_metadata(task) -> dict
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

EMPTY_STATE_MESSAGE = "尚無 Owner 決策事件紀錄"
EMPTY_STATE_NOTE = "v0.7.3-B 只讀顯示；v0.7.3-C 才會規劃 local recorder"

# 固定安全提醒（display-only；決策不等於執行）。
SAFETY_REMINDERS = (
    "approve is not execute",
    "Owner decision event is not Worker dispatch",
    "Owner approval does not automatically imply Worker execution",
    "Decision and execution dispatch remain separate",
    "Approval readiness is not execution permission",
)

# 每個 event 的 normalized 欄位（顯示用）。
_EVENT_STR_FIELDS = (
    "decision_id",
    "task_id",
    "decision_type",
    "decided_by",
    "decided_at",
    "decision_reason",
    "previous_status",
    "next_status",
    "approval_readiness_at_decision",
)


def _as_payload_dict(payload: Any) -> Dict[str, Any]:
    """payload 可能是 dict / JSON 字串 / None；無法解析回 {}（不 crash）。"""
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def normalize_payload_metadata(task: Mapping[str, Any]) -> Dict[str, Any]:
    """從 task 安全取出 metadata（唯讀）。

    優先 payload.metadata；其次 task.metadata；兩者皆非 dict → {}。
    payload 可能是 dict / JSON 字串 / None；缺失或型別錯皆不 crash。
    """
    if not isinstance(task, Mapping):
        return {}
    payload = _as_payload_dict(task.get("payload"))
    md = payload.get("metadata")
    if isinstance(md, dict):
        return md
    md = task.get("metadata")
    return md if isinstance(md, dict) else {}


def _safe_str_or_unknown(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return "unknown"


def _normalize_snapshot(value: Any) -> Any:
    """safety_snapshot / annotation_snapshot：dict 原樣（淺拷貝），其餘 → {}。"""
    if isinstance(value, dict):
        return dict(value)
    return {}


def _normalize_event(raw: Any) -> Dict[str, Any]:
    """把單筆 raw decision event 正規化成顯示用 dict（唯讀，不 mutate raw）。

    execution_permission_at_decision / dispatch_allowed_at_decision 恆為 False
    （快照只用於顯示，永不顯示為已授權）。
    """
    src = raw if isinstance(raw, Mapping) else {}
    event = {field: _safe_str_or_unknown(src.get(field)) for field in _EVENT_STR_FIELDS}
    event["execution_permission_at_decision"] = False
    event["dispatch_allowed_at_decision"] = False
    event["safety_snapshot"] = _normalize_snapshot(src.get("safety_snapshot"))
    event["annotation_snapshot"] = _normalize_snapshot(src.get("annotation_snapshot"))
    audit = src.get("audit_record")
    event["audit_record"] = dict(audit) if isinstance(audit, dict) else {}
    return event


def derive_approval_decision_event_view(task: Mapping[str, Any]) -> Dict[str, Any]:
    """從 Queue task dict / row 推導 Owner 決策紀錄唯讀檢視（純函式）。

    讀取 ``payload.metadata.approval_decision_events``（若不存在或型別錯 → empty state）。
    不 mutate task、不寫 queue、不連外。

    approve is not execute. Owner decision event is not Worker dispatch.
    回傳的 view 與每個 event 的 execution_permission / dispatch_allowed 恆為 False。
    """
    metadata = normalize_payload_metadata(task)
    raw_events = metadata.get("approval_decision_events")
    events: List[Dict[str, Any]] = []
    if isinstance(raw_events, list):
        for raw in raw_events:
            events.append(_normalize_event(raw))

    return {
        "events": events,
        "event_count": len(events),
        "has_events": len(events) > 0,
        "empty_state_message": EMPTY_STATE_MESSAGE,
        "empty_state_note": EMPTY_STATE_NOTE,
        "safety_reminders": list(SAFETY_REMINDERS),
        # 唯讀檢視永不授予執行 / 派工：恆為 False。
        "execution_permission": False,
        "dispatch_allowed": False,
    }
