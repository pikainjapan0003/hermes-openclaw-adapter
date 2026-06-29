"""v0.7.3-C — Local Approval Event Recorder（純本地 helper，append-only，no dispatch）。

把一筆 Owner decision event 建立並 append 到 Queue task 的
``payload.metadata.approval_decision_events``（local audit metadata）。本模組只做
local append-only 記錄；它不 dispatch Worker、不呼叫外部、不授予任何執行權限。

純 helper 邊界：
  - 只產生 / append local audit metadata；不寫 DB、不接外部。
  - 不 import app.main、不 import QueueStore、不 import worker。
  - 不啟動 Worker、不呼叫 OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不讀 .env、不讀 secrets。
  - 僅 import 標準庫與純函式 app.queue_task_annotation_v0_7（產生 annotation snapshot）。

append-only 保證：
  - 保留既有 approval_decision_events list。
  - 新 event append 到 list 尾端。
  - 不覆蓋 / 不刪除 / 不修改既有 events。
  - 不修改 unrelated metadata（copy-on-write，不 mutate 輸入）。

決策／執行分離（核心安全規則，恆成立）：
  approve is not execute.
  Owner decision event is not Worker dispatch.
  Owner approval does not automatically imply Worker execution.
  Decision and execution dispatch remain separate.
  Approval readiness is not execution permission.

固定安全值：
  execution_permission_at_decision = False
  dispatch_allowed_at_decision = False

公開 API：
  build_approval_decision_event(task, *, decision_type, previous_status, next_status, ...) -> dict
  append_approval_decision_event_to_payload(payload, event) -> dict
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any, Dict, Mapping
from uuid import uuid4

from app.queue_task_annotation_v0_7 import derive_queue_task_annotation

RECORDER_VERSION = "v0.7.3-C"


def _utc_now_iso() -> str:
    """UTC ISO-8601 timestamp（Z 結尾）。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _metadata_of(task: Mapping[str, Any]) -> Dict[str, Any]:
    payload = _as_payload_dict(task.get("payload")) if isinstance(task, Mapping) else {}
    md = payload.get("metadata")
    if isinstance(md, dict):
        return md
    md = task.get("metadata") if isinstance(task, Mapping) else None
    return md if isinstance(md, dict) else {}


def _safe_int(value: Any) -> Any:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _build_safety_snapshot(task: Mapping[str, Any], metadata: Mapping[str, Any]) -> Dict[str, Any]:
    """從既有 task / metadata 派生 safety snapshot（不讀 secrets）。"""
    safety_level = _safe_int(task.get("safety_level")) if isinstance(task, Mapping) else None
    if safety_level is None:
        safety_level = _safe_int(metadata.get("safety_level"))
    return {
        "safety_level": safety_level,
        "requires_confirmation": metadata.get("requires_confirmation"),
        # 目前安全姿態（display-only；不啟用任何東西）。
        "worker": "off",
        "openclaw": "not_connected",
        "hermes": "not_connected",
        "google_sheets": "disabled",
    }


def build_approval_decision_event(
    task: Mapping[str, Any],
    *,
    decision_type: str,
    previous_status: Any,
    next_status: Any,
    decided_by: str = "owner",
    decision_reason: str = "",
    via: str | None = None,
) -> Dict[str, Any]:
    """建立一筆 Owner approval decision event（v0.7.3-A contract，local audit）。

    execution_permission_at_decision / dispatch_allowed_at_decision 恆為 False。
    不 mutate task、不讀 secrets、不接外部。
    """
    metadata = _metadata_of(task)
    annotation = derive_queue_task_annotation(task) if isinstance(task, Mapping) else {}
    reason = decision_reason if isinstance(decision_reason, str) and decision_reason.strip() else "not_provided"
    return {
        "decision_id": uuid4().hex,
        "task_id": task.get("task_id") if isinstance(task, Mapping) else None,
        "decision_type": decision_type,
        "decided_by": decided_by or "owner",
        "decided_at": _utc_now_iso(),
        "decision_reason": reason,
        "previous_status": previous_status,
        "next_status": next_status,
        "approval_readiness_at_decision": annotation.get("approval_readiness", "not_ready"),
        # 固定安全值：決策事件絕不授予執行 / 派工。
        "execution_permission_at_decision": False,
        "dispatch_allowed_at_decision": False,
        "safety_snapshot": _build_safety_snapshot(task, metadata),
        "annotation_snapshot": annotation,
        "audit_record": {
            "recorder_version": RECORDER_VERSION,
            "source": "local-dashboard",
            "via": via or f"dashboard-{decision_type}",
            "append_only": True,
            "note": "local audit record; not a dispatch command",
        },
    }


def append_approval_decision_event_to_payload(payload: Any, event: Mapping[str, Any]) -> Dict[str, Any]:
    """回傳「append 了 event 的新 payload dict」（copy-on-write，append-only）。

    - 不 mutate 輸入 payload。
    - 保留既有 approval_decision_events 並把 event append 到尾端。
    - 保留 unrelated metadata。
    """
    base = _as_payload_dict(payload)
    new_payload = copy.deepcopy(base)
    md = new_payload.get("metadata")
    if not isinstance(md, dict):
        md = {}
    events = md.get("approval_decision_events")
    if not isinstance(events, list):
        events = []
    events.append(copy.deepcopy(dict(event)))
    md["approval_decision_events"] = events
    new_payload["metadata"] = md
    return new_payload
