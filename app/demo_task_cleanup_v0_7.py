"""v0.7.4-F — Safe Local Cleanup Tool helper（純函式、dry-run-only）。

從一份明確傳入的 task list（synthetic / 已讀入的 dict list）推導出一份 demo task
cleanup **dry-run candidate report**。本模組只做唯讀分類與報表推導：它不刪除 task、
不 archive task、不修改 payload / status、不 mutate 輸入、不讀真實 queue DB、不寫檔、
不連外、不提供任何 apply path。

純 helper 邊界（dry-run-only）：
  - 不 import app.main、不 import QueueStore。
  - 不 import sqlite / requests / urllib / socket / subprocess / secrets。
  - 不讀 .env、不讀真實 queue DB、不寫檔。
  - 不刪除 / archive / 修改 task，不 mutate 輸入。
  - 不啟動 Worker、不呼叫 OpenClaw / Hermes / Google Sheets。
  - 僅用標準庫（json / uuid / datetime / typing）。

安全合約（v0.7.4-E）：
  Cleanup Plan is not cleanup apply.
  Cleanup dry-run is not cleanup apply.
  Cleanup apply requires separate Owner approval.

因此回傳 report 的固定安全值恆為：
  execution_mode = "dry_run_only", dry_run = True,
  apply_requested = False, apply_allowed = False,
  would_delete = False, would_archive = False, would_modify = False,
  external_side_effects = False, owner_approval_required = True.

公開 API：
  derive_demo_task_cleanup_dry_run_report(tasks, *, source_queue, target_environment) -> dict
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

# 只能根據 explicit metadata marker 分類（不得只靠 task_id / title / summary 名稱）。
_CLASSIFICATION_VALUES = ("demo", "sample", "preview", "test")

# 允許的 target environment（其它一律 blocked）。
_ALLOWED_TARGET_ENVIRONMENTS = ("local", "preview")

# secret-like metadata key（出現即 blocked，且絕不印出 value）。
_SECRET_LIKE_KEYS = (
    "secret",
    "secrets",
    "token",
    "client_secret",
    "refresh_token",
    "private_key",
    "password",
    "api_key",
    "apikey",
)

SAFETY_NOTES = (
    "This is a dry-run-only report.",
    "No task was deleted.",
    "No task was archived.",
    "No queue data was modified.",
    "No real queue DB was read.",
    "Cleanup apply requires separate Owner approval.",
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


def _coerce_bool(value: Any) -> bool:
    """寬鬆解讀布林 marker：True / "true" / "yes" / "1" → True。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1")
    if isinstance(value, (int, float)):
        return value == 1
    return False


def _classification_value(metadata: Mapping[str, Any], key: str) -> str:
    raw = metadata.get(key)
    if isinstance(raw, str):
        return raw.strip().lower()
    return ""


def _has_demo_marker(metadata: Mapping[str, Any]) -> bool:
    """是否有 explicit demo / sample / preview / test marker（唯讀）。"""
    if (
        _coerce_bool(metadata.get("demo_task"))
        or _coerce_bool(metadata.get("sample_task"))
        or _coerce_bool(metadata.get("preview_task"))
        or _coerce_bool(metadata.get("test_task"))
    ):
        return True
    if _classification_value(metadata, "cleanup_classification") in _CLASSIFICATION_VALUES:
        return True
    if _classification_value(metadata, "task_classification") in _CLASSIFICATION_VALUES:
        return True
    return False


def _demo_marker_label(metadata: Mapping[str, Any]) -> str:
    for key in ("demo_task", "sample_task", "preview_task", "test_task"):
        if _coerce_bool(metadata.get(key)):
            return key
    for key in ("cleanup_classification", "task_classification"):
        val = _classification_value(metadata, key)
        if val in _CLASSIFICATION_VALUES:
            return f"{key}={val}"
    return ""


def _has_production_marker(metadata: Mapping[str, Any]) -> bool:
    if _coerce_bool(metadata.get("production")) or _coerce_bool(metadata.get("production_task")):
        return True
    if _classification_value(metadata, "cleanup_classification") == "production":
        return True
    if _classification_value(metadata, "task_classification") == "production":
        return True
    return False


def _has_external_side_effect_marker(metadata: Mapping[str, Any]) -> bool:
    for key in (
        "external_side_effect",
        "has_external_side_effect",
        "external_side_effect_history",
        "external_execution",
    ):
        if _coerce_bool(metadata.get(key)):
            return True
    return False


def _has_secret_like_marker(metadata: Mapping[str, Any]) -> bool:
    if _coerce_bool(metadata.get("contains_secret")) or _coerce_bool(metadata.get("secret_like")):
        return True
    for key in metadata.keys():
        if isinstance(key, str) and key.strip().lower() in _SECRET_LIKE_KEYS:
            return True
    return False


def _origin_is_unknown(metadata: Mapping[str, Any]) -> bool:
    """origin 明確標記為 unknown / unclear，或 origin_unclear marker → 視為不明。"""
    if _coerce_bool(metadata.get("origin_unclear")):
        return True
    origin = _classification_value(metadata, "origin")
    if origin in ("unknown", "unclear"):
        return True
    return False


def _is_active_validation(metadata: Mapping[str, Any]) -> bool:
    for key in ("active_validation", "needed_for_active_validation", "in_active_validation"):
        if _coerce_bool(metadata.get(key)):
            return True
    return False


def _safe_task_id(task: Mapping[str, Any], index: int) -> str:
    if isinstance(task, Mapping):
        tid = task.get("task_id") or task.get("id")
        if isinstance(tid, str) and tid.strip():
            return tid
    return f"index-{index}"


def _evaluate_task(
    task: Any,
    index: int,
    target_env_ok: bool,
) -> Dict[str, Any]:
    """唯讀評估單筆 task → candidate 或 blocked entry（不 mutate 原 task）。

    回傳 {"kind": "candidate"|"blocked", "entry": {...}}。
    """
    task_id = _safe_task_id(task, index) if isinstance(task, Mapping) else f"index-{index}"
    metadata = _normalize_metadata(task) if isinstance(task, Mapping) else {}

    # 全域：target environment 不是 local / preview → 一律 blocked。
    if not target_env_ok:
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "target_environment is not local or preview"},
        }

    if not _has_demo_marker(metadata):
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "no explicit demo/sample/preview/test marker"},
        }
    if _has_production_marker(metadata):
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "production marker present"},
        }
    if _has_external_side_effect_marker(metadata):
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "external side effect marker present"},
        }
    if _has_secret_like_marker(metadata):
        # 絕不印出任何 secret value，只記錄 reason。
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "secret-like marker present"},
        }
    if _origin_is_unknown(metadata):
        return {
            "kind": "blocked",
            "entry": {"task_id": task_id, "reason": "origin unknown"},
        }
    if _is_active_validation(metadata) and not _coerce_bool(metadata.get("owner_approved_replacement")):
        return {
            "kind": "blocked",
            "entry": {
                "task_id": task_id,
                "reason": "needed for active validation without owner_approved_replacement",
            },
        }

    return {
        "kind": "candidate",
        "entry": {
            "task_id": task_id,
            "classification": _demo_marker_label(metadata),
            "reason": "explicit demo/sample/preview/test marker (dry-run candidate only)",
        },
    }


def derive_demo_task_cleanup_dry_run_report(
    tasks: Any,
    *,
    source_queue: str = "synthetic",
    target_environment: str = "local",
) -> Dict[str, Any]:
    """從明確傳入的 task list 推導 demo task cleanup **dry-run** report（純函式）。

    只做唯讀分類與報表推導。不刪除 / archive / 修改任何 task，不 mutate 輸入，不讀真實
    queue DB，不寫檔，不連外，不提供 apply path。

    固定安全值恆為：execution_mode = "dry_run_only", dry_run = True,
    apply_requested = False, apply_allowed = False, would_delete = False,
    would_archive = False, would_modify = False, external_side_effects = False,
    owner_approval_required = True.
    """
    target_env = target_environment if isinstance(target_environment, str) else ""
    target_env_ok = target_env in _ALLOWED_TARGET_ENVIRONMENTS

    task_list: List[Any] = list(tasks) if isinstance(tasks, (list, tuple)) else []

    candidates: List[Dict[str, Any]] = []
    blocked_items: List[Dict[str, Any]] = []
    for index, task in enumerate(task_list):
        result = _evaluate_task(task, index, target_env_ok)
        if result["kind"] == "candidate":
            candidates.append(result["entry"])
        else:
            blocked_items.append(result["entry"])

    return {
        "report_id": f"dry-run-{uuid.uuid4().hex}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        # --- 固定安全值（恆定，dry-run-only）---
        "execution_mode": "dry_run_only",
        "dry_run": True,
        "apply_requested": False,
        "apply_allowed": False,
        "would_delete": False,
        "would_archive": False,
        "would_modify": False,
        "external_side_effects": False,
        "owner_approval_required": True,
        # --- 報表內容 ---
        "candidate_count": len(candidates),
        "blocked_count": len(blocked_items),
        "candidates": candidates,
        "blocked_items": blocked_items,
        "source_queue": source_queue if isinstance(source_queue, str) else "synthetic",
        "target_environment": target_env,
        "rollback_note": "No change was made; dry-run report only, nothing to roll back.",
        "safety_notes": list(SAFETY_NOTES),
    }
