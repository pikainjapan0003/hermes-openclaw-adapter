"""v0.7.4-D — Audit Trail Display（純函式、唯讀，display-only）。

從一筆既有 Queue task dict / row（含 payload.metadata.approval_decision_events）
推導出 Dashboard 可顯示的「任務生命週期 / 黑板訊息 / Owner Decision audit trail」唯讀
檢視。本模組只負責顯示推導，不記錄事件、不寫入、不授予任何執行權限、不派工。

純 helper 邊界（Audit Trail Display is read-only）：
  - 不寫入 task、不寫入 payload、不寫入 metadata、不 mutate 輸入。
  - 不呼叫 QueueStore、不 import app.main、不 import database / sqlite / network / secrets。
  - 不啟動 Worker、不呼叫 OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 僅用標準庫（json / typing）。

決策／執行分離（核心安全規則）：
  approve is not execute.
  Owner decision event is not Worker dispatch.
  Displayed lifecycle state does not change task status.
  Displayed lifecycle state does not enforce guard.
  Displayed lifecycle state does not grant execution permission.
  Displayed lifecycle state does not dispatch Worker.

因此回傳 view 的固定安全旗標恆為 False（read_only 恆為 True）。Result Message /
Advice Message 在 v0.7.4-D 皆為 future-only，count 恆為 0。

公開 API：
  derive_audit_trail_display_view(task) -> dict
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

# Result / Advice Message 在本段為 future-only（顯示佔位，count 恆 0）。
RESULT_MESSAGE_FUTURE_NOTE = "Result Message display is future-only in v0.7.4-D."
ADVICE_MESSAGE_FUTURE_NOTE = "Advice Message display is future-only in v0.7.4-D."

# 顯示用 lifecycle 標籤（read-only 衍生；不等於 runtime status）。
_LIFECYCLE_LABELS = {
    "draft_or_created": "草稿 / 已建立",
    "annotated": "已標註",
    "owner_review": "等待 Owner 審核",
    "owner_decided": "Owner 已決策",
    "archived_or_closed": "已封存 / 已關閉",
}

# task.status 看起來屬於「封存 / 關閉 / 取消」類型的關鍵字（保守比對）。
_ARCHIVED_STATUS_HINTS = (
    "archiv",
    "closed",
    "close",
    "cancel",
    "done",
    "completed",
    "complete",
    "rejected",
)

# Displayed lifecycle state 的固定安全註記（display-only）。
LIFECYCLE_DISPLAY_NOTES = (
    "Displayed lifecycle state is derived read-only.",
    "Displayed lifecycle state does not change task status.",
    "Displayed lifecycle state does not enforce guard.",
    "Displayed lifecycle state does not grant execution permission.",
    "Displayed lifecycle state does not dispatch Worker.",
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


def _normalize_metadata(task: Mapping[str, Any]) -> Dict[str, Any]:
    """從 task 安全取出 metadata（唯讀）：優先 payload.metadata，其次 task.metadata。"""
    if not isinstance(task, Mapping):
        return {}
    payload = _as_payload_dict(task.get("payload"))
    md = payload.get("metadata")
    if isinstance(md, dict):
        return md
    md = task.get("metadata")
    return md if isinstance(md, dict) else {}


def _count_decision_events(metadata: Mapping[str, Any]) -> int:
    """Decision Message = len(payload.metadata.approval_decision_events)（型別錯 → 0）。"""
    raw = metadata.get("approval_decision_events")
    if isinstance(raw, list):
        return len(raw)
    return 0


def _status_looks_archived(status: Any) -> bool:
    if not isinstance(status, str):
        return False
    low = status.strip().lower()
    if not low:
        return False
    return any(hint in low for hint in _ARCHIVED_STATUS_HINTS)


def _status_looks_review(status: Any) -> bool:
    if not isinstance(status, str):
        return False
    low = status.strip().lower()
    return "review" in low or "waiting" in low or "pending" in low


def _has_annotation_signal(metadata: Mapping[str, Any]) -> bool:
    """是否有 annotation / safety_snapshot / approval_readiness 類資訊。"""
    for key in ("approval_readiness", "safety_snapshot", "annotation", "safety_level"):
        if metadata.get(key) not in (None, "", {}, []):
            return True
    return False


def _derive_lifecycle_state(
    task: Mapping[str, Any],
    metadata: Mapping[str, Any],
    decision_count: int,
) -> str:
    """保守 read-only 衍生顯示用 lifecycle state（不改 task status、不 enforce guard）。"""
    status = task.get("status") if isinstance(task, Mapping) else None
    if _status_looks_archived(status):
        return "archived_or_closed"
    if decision_count > 0:
        return "owner_decided"
    has_readiness = metadata.get("approval_readiness") not in (None, "", {}, [])
    if has_readiness or _status_looks_review(status):
        return "owner_review"
    if _has_annotation_signal(metadata):
        return "annotated"
    return "draft_or_created"


def _build_timeline_items(
    task_present: bool,
    metadata: Mapping[str, Any],
    decision_count: int,
) -> List[Dict[str, Any]]:
    """純 read-only 衍生 timeline（不讀外部、不寫入）。"""
    items: List[Dict[str, Any]] = []
    if task_present:
        items.append(
            {"kind": "task_message", "label": "Task Message observed", "observed": True}
        )
    if _has_annotation_signal(metadata):
        items.append(
            {
                "kind": "annotation",
                "label": "Annotation / approval readiness observed",
                "observed": True,
            }
        )
    if decision_count > 0:
        items.append(
            {
                "kind": "decision_message",
                "label": "Owner Decision Messages observed",
                "observed": True,
                "count": decision_count,
            }
        )
    items.append(
        {
            "kind": "result_message",
            "label": "Result Message future-only",
            "observed": False,
            "future_only": True,
        }
    )
    items.append(
        {
            "kind": "advice_message",
            "label": "Advice Message future-only",
            "observed": False,
            "future_only": True,
        }
    )
    return items


def derive_audit_trail_display_view(task: Mapping[str, Any]) -> Dict[str, Any]:
    """從 Queue task dict / row 推導 Audit Trail 唯讀檢視（純函式）。

    讀取 ``payload.metadata.approval_decision_events`` 計算 Decision Message 數；
    Result / Advice Message 在 v0.7.4-D 皆 future-only（count 恆 0）。
    不 mutate task、不寫 queue、不連外、不 dispatch。

    回傳 view 的固定安全旗標（execution_permission / dispatch_allowed /
    worker_dispatch_enabled / openclaw_call_enabled / hermes_call_enabled /
    google_sheets_write_enabled）恆為 False；read_only 恆為 True。
    """
    metadata = _normalize_metadata(task)
    task_present = isinstance(task, Mapping) and bool(task)
    decision_count = _count_decision_events(metadata)
    result_count = 0  # Result Message display is future-only in v0.7.4-D.
    advice_count = 0  # Advice Message display is future-only in v0.7.4-D.

    lifecycle_state = _derive_lifecycle_state(task, metadata, decision_count)

    message_family_counts = {
        "task_message": 1 if task_present else 0,
        "decision_message": decision_count,
        "result_message": result_count,
        "advice_message": advice_count,
    }

    timeline_items = _build_timeline_items(task_present, metadata, decision_count)

    return {
        "lifecycle_state": lifecycle_state,
        "lifecycle_state_label": _LIFECYCLE_LABELS.get(lifecycle_state, lifecycle_state),
        "message_family_counts": message_family_counts,
        "timeline_items": timeline_items,
        "decision_message_count": decision_count,
        "result_message_count": result_count,
        "advice_message_count": advice_count,
        "task_message_present": task_present,
        "result_message_future_note": RESULT_MESSAGE_FUTURE_NOTE,
        "advice_message_future_note": ADVICE_MESSAGE_FUTURE_NOTE,
        "lifecycle_display_notes": list(LIFECYCLE_DISPLAY_NOTES),
        # 唯讀檢視永不授予執行 / 派工 / 外部呼叫：固定安全旗標恆為 False。
        "execution_permission": False,
        "dispatch_allowed": False,
        "worker_dispatch_enabled": False,
        "openclaw_call_enabled": False,
        "hermes_call_enabled": False,
        "google_sheets_write_enabled": False,
        "read_only": True,
    }
