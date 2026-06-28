"""v0.7.2-F-B — Queue Task Annotation Deriver（純函式、唯讀，observation-only）。

從一筆既有的 Queue task dict / row（含 payload.metadata）推導出 Owner Review Panel
未來可顯示的 annotation 集合與 approval readiness 訊號。本模組只負責「顯示推導」，
不授予任何執行權限。

純 helper 邊界：
  - 不寫 queue、不改 task、不 mutate 輸入。
  - 不讀 .env、不讀 secrets、不連外。
  - 不 import app.main、不 import QueueStore、不 import worker。
  - 不啟動 Worker、不呼叫 OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 僅用標準庫（json / copy / typing）。

安全邊界（本模組只做唯讀 annotation，永不放行執行）：
  - No QueueStore runtime behavior changes.
  - No approval wiring changes.
  - No schema migration.
  - No Worker execution.
  - No OpenClaw call.
  - No Hermes call.
  - No Google Sheets write.
  - No external side effects.

決策／執行分離（核心安全規則）：
  Approval readiness is not execution permission.
  Owner approval does not automatically imply Worker execution.
  Decision and execution dispatch must remain separate.

因此回傳 dict 內 ``execution_permission`` 與 ``dispatch_allowed`` 恆為 ``False``。

公開 API：
  derive_queue_task_annotation(task) -> dict
  normalize_payload_metadata(task) -> dict
  normalize_approval_readiness(value) -> str
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping

# approval_readiness enum（顯示用；不是執行權限）。
READINESS_NOT_READY = "not_ready"
READINESS_OWNER_REVIEW_REQUIRED = "owner_review_required"
READINESS_READY_FOR_OWNER_DECISION = "ready_for_owner_decision"
READINESS_BLOCKED_BY_POLICY = "blocked_by_policy"
READINESS_PROHIBITED = "prohibited"

VALID_READINESS = (
    READINESS_NOT_READY,
    READINESS_OWNER_REVIEW_REQUIRED,
    READINESS_READY_FOR_OWNER_DECISION,
    READINESS_BLOCKED_BY_POLICY,
    READINESS_PROHIBITED,
)

# 缺註解時的保守 fallback 文案（中文優先）。
_FALLBACK_OWNER_REASON = "資訊不足，Owner 不應直接核准。"
_FALLBACK_RISK_SUMMARY = "未提供完整風險說明。"
_FALLBACK_SIDE_EFFECT_SUMMARY = "未提供外部影響說明。"
_FALLBACK_NEXT_STEP = "核准後仍不得自動執行；需等待後續 dispatch approval。"
_FALLBACK_ROLLBACK_NOTE = "未提供 rollback 說明。"
_FALLBACK_HUMAN_SUMMARY = "這個任務缺少足夠註解，僅可觀察，不應放行。"


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


def normalize_approval_readiness(value: Any) -> str:
    """把任意值正規化成合法的 approval_readiness enum 字串；不合法回 ""（唯讀）。"""
    if isinstance(value, str):
        v = value.strip().lower()
        if v in VALID_READINESS:
            return v
    return ""


def _safe_str(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback


def _safe_bool(value: Any) -> bool:
    """保守：只有明確的 bool True 才算 True；其餘（含字串 'true'）一律 False。"""
    return value is True


def _safe_str_list(value: Any) -> List[str]:
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return list(value)
    return []


def _equals_ci(value: Any, target: str) -> bool:
    return isinstance(value, str) and value.strip().lower() == target


def _signals_prohibited(metadata: Mapping[str, Any]) -> bool:
    """metadata 是否明確宣告 prohibited（最具限制性，優先）。"""
    if normalize_approval_readiness(metadata.get("approval_readiness")) == READINESS_PROHIBITED:
        return True
    if metadata.get("prohibited") is True:
        return True
    for key in ("policy_decision", "approval_status"):
        if _equals_ci(metadata.get(key), READINESS_PROHIBITED):
            return True
    return False


def _signals_blocked_by_policy(metadata: Mapping[str, Any]) -> bool:
    """metadata 是否明確宣告 policy blocker。"""
    if normalize_approval_readiness(metadata.get("approval_readiness")) == READINESS_BLOCKED_BY_POLICY:
        return True
    if metadata.get("blocked_by_policy") is True or metadata.get("policy_blocked") is True:
        return True
    for key in ("policy_decision", "approval_status"):
        if _equals_ci(metadata.get(key), READINESS_BLOCKED_BY_POLICY):
            return True
    return False


def _derive_approval_readiness(metadata: Mapping[str, Any], status: Any) -> str:
    """保守推導 approval_readiness（顯示用，永不轉成執行權限）。

    優先序（限制性高者優先）：
      1. prohibited 明確宣告 → prohibited。
      2. policy blocker 明確宣告 → blocked_by_policy。
      3. metadata.approval_readiness 是合法 enum → 採用（含 ready_for_owner_decision，
         但僅由 metadata 明確宣告才會出現，不靠猜測自動升級）。
      4. status == waiting_review → owner_review_required。
      5. 資訊不足 → not_ready（fail-safe 預設）。
    """
    if _signals_prohibited(metadata):
        return READINESS_PROHIBITED
    if _signals_blocked_by_policy(metadata):
        return READINESS_BLOCKED_BY_POLICY
    explicit = normalize_approval_readiness(metadata.get("approval_readiness"))
    if explicit:
        return explicit
    if status == "waiting_review":
        return READINESS_OWNER_REVIEW_REQUIRED
    return READINESS_NOT_READY


def _derive_approval_blockers(metadata: Mapping[str, Any], readiness: str) -> List[str]:
    """推導 approval_blockers（顯示用）。優先採用明確 metadata.approval_blockers。"""
    explicit = metadata.get("approval_blockers")
    if isinstance(explicit, list) and all(isinstance(x, str) for x in explicit):
        return list(explicit)
    if readiness == READINESS_PROHIBITED:
        return [READINESS_PROHIBITED]
    if readiness == READINESS_BLOCKED_BY_POLICY:
        return [READINESS_BLOCKED_BY_POLICY]
    if readiness == READINESS_NOT_READY:
        return ["missing_annotation"]
    if readiness == READINESS_OWNER_REVIEW_REQUIRED:
        return [READINESS_OWNER_REVIEW_REQUIRED]
    return []


def derive_queue_task_annotation(task: Mapping[str, Any]) -> Dict[str, Any]:
    """從 Queue task dict / row 推導 Owner Review Panel 可顯示的 annotation（純函式）。

    不 mutate ``task``、不寫 queue、不連外。legacy / 缺註解任務一律回安全 fallback。

    Approval readiness is not execution permission.
    Owner approval does not automatically imply Worker execution.
    回傳 dict 內 ``execution_permission`` 與 ``dispatch_allowed`` 恆為 ``False``。
    """
    metadata = normalize_payload_metadata(task)
    status = task.get("status") if isinstance(task, Mapping) else None

    readiness = _derive_approval_readiness(metadata, status)
    approval_blockers = _derive_approval_blockers(metadata, readiness)

    return {
        "task_origin": _safe_str(metadata.get("task_origin"), "unknown"),
        "requested_by": _safe_str(metadata.get("requested_by"), "unknown"),
        "request_channel": _safe_str(metadata.get("request_channel"), "unknown"),
        "owner_reason": _safe_str(metadata.get("owner_reason"), _FALLBACK_OWNER_REASON),
        "approval_readiness": readiness,
        "approval_blockers": approval_blockers,
        "risk_summary": _safe_str(metadata.get("risk_summary"), _FALLBACK_RISK_SUMMARY),
        "side_effect_summary": _safe_str(
            metadata.get("side_effect_summary"), _FALLBACK_SIDE_EFFECT_SUMMARY
        ),
        "next_step_if_approved": _safe_str(
            metadata.get("next_step_if_approved"), _FALLBACK_NEXT_STEP
        ),
        "execution_mode": _safe_str(metadata.get("execution_mode"), "unknown"),
        "external_touchpoints": _safe_str_list(metadata.get("external_touchpoints")),
        "dry_run_available": _safe_bool(metadata.get("dry_run_available")),
        "mock_available": _safe_bool(metadata.get("mock_available")),
        "rollback_note": _safe_str(metadata.get("rollback_note"), _FALLBACK_ROLLBACK_NOTE),
        "human_readable_summary": _safe_str(
            metadata.get("human_readable_summary"), _FALLBACK_HUMAN_SUMMARY
        ),
        # 唯讀 annotation 永不授予執行權限：恆為 False。
        "execution_permission": False,
        "dispatch_allowed": False,
    }
