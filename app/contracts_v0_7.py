"""v0.7.0-B — Hermes ↔ OpenClaw 契約 schema 載入 + 純 Python validator。

純驗證器，mock-only：
  - 不 import Google API / OpenClaw client / Hermes client。
  - 不讀任何環境 secret、不碰 Queue DB、不寫 Result Sink。
  - 不新增 dependency；僅用 Python 標準庫（json / pathlib）做基本 validation。

公開 API：
  load_json_schema(name)        -> dict
  validate_task_envelope(payload)   -> payload（通過時原樣回傳）
  validate_callback_event(payload)  -> payload（通過時原樣回傳）
  ContractValidationError           -> 驗證失敗時 raise
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "docs" / "schemas"

TASK_ENVELOPE_SCHEMA = "task_envelope_v0_7"
CALLBACK_EVENT_SCHEMA = "callback_event_v0_7"


class ContractValidationError(ValueError):
    """契約驗證失敗時 raise。"""


# --- enum / 邊界（與 docs/schemas/*.json 對齊；validator 不依賴 jsonschema 套件） ---

TASK_STATUS_VALUES = {
    "draft",
    "pending_approval",
    "queued",
    "dispatching",
    "running",
    "callback_received",
    "completed",
    "failed",
    "cancelled",
    "dead_letter",
}

APPROVAL_STATUS_VALUES = {"not_required", "pending", "approved", "rejected"}

CALLBACK_EVENT_TYPE_VALUES = {
    "accepted",
    "started",
    "progress",
    "completed",
    "failed",
    "cancelled",
    "artifact_ready",
    "approval_required",
}

CALLBACK_STATUS_VALUES = {"ok", "running", "completed", "failed", "cancelled", "rejected"}

TASK_REQUIRED_FIELDS = (
    "task_id",
    "created_at",
    "created_by",
    "source",
    "requested_by",
    "risk_level",
    "approval_required",
    "approval_status",
    "intent",
    "goal",
    "task_type",
    "priority",
    "input_summary",
    "target_runtime",
    "target_workspace",
    "idempotency_key",
    "max_retries",
    "retry_count",
    "status",
    "result_policy",
    "callback_policy",
    "metadata",
)

CALLBACK_REQUIRED_FIELDS = (
    "event_id",
    "task_id",
    "source",
    "created_at",
    "event_type",
    "status",
    "summary",
    "retryable",
    "metadata",
)


def load_json_schema(name: str) -> Dict[str, Any]:
    """載入 docs/schemas/<name>.schema.json。name 可省略 .schema.json 後綴。"""
    stem = name
    for suffix in (".schema.json", ".json"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    path = SCHEMA_DIR / f"{stem}.schema.json"
    if not path.is_file():
        raise ContractValidationError(f"schema not found: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - 防禦性
        raise ContractValidationError(f"schema not valid JSON: {path.name}: {exc}") from exc


# --- 基本型別輔助（注意：bool 是 int 的子類，整數欄位必須排除 bool） ---


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_str(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(payload.get(field), str):
        errors.append(f"{field} 必須為 string")


def _require_bool(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(payload.get(field), bool):
        errors.append(f"{field} 必須為 boolean")


def _require_non_negative_int(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    value = payload.get(field)
    if not _is_int(value):
        errors.append(f"{field} 必須為 integer")
    elif value < 0:
        errors.append(f"{field} 必須為非負整數")


def _require_object(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(payload.get(field), dict):
        errors.append(f"{field} 必須為 object（dict）")


def _require_array(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(payload.get(field), list):
        errors.append(f"{field} 必須為 array（list）")


def _check_required(payload: Dict[str, Any], required: tuple[str, ...], errors: list[str]) -> None:
    for field in required:
        if field not in payload:
            errors.append(f"缺少必要欄位：{field}")


def _opt_str_or_null(payload: Dict[str, Any], field: str, errors: list[str]) -> None:
    if field in payload and not (payload[field] is None or isinstance(payload[field], str)):
        errors.append(f"{field} 必須為 string 或 null")


def _raise_if(errors: list[str], kind: str) -> None:
    if errors:
        raise ContractValidationError(f"{kind} 驗證失敗：" + "；".join(errors))


def validate_task_envelope(payload: Any) -> Dict[str, Any]:
    """驗證 TaskEnvelope v0.7。通過回傳 payload，否則 raise ContractValidationError。"""
    if not isinstance(payload, dict):
        raise ContractValidationError("TaskEnvelope 必須為 object（dict）")

    errors: list[str] = []
    _check_required(payload, TASK_REQUIRED_FIELDS, errors)

    for field in (
        "task_id",
        "created_at",
        "created_by",
        "source",
        "requested_by",
        "approval_status",
        "intent",
        "goal",
        "task_type",
        "priority",
        "input_summary",
        "target_runtime",
        "target_workspace",
        "idempotency_key",
        "status",
    ):
        if field in payload:
            _require_str(payload, field, errors)

    if "approval_required" in payload:
        _require_bool(payload, "approval_required", errors)

    if "risk_level" in payload:
        rl = payload.get("risk_level")
        if not _is_int(rl):
            errors.append("risk_level 必須為 integer")
        elif rl < 0 or rl > 4:
            errors.append("risk_level 必須介於 0..4")

    if "max_retries" in payload:
        _require_non_negative_int(payload, "max_retries", errors)
    if "retry_count" in payload:
        _require_non_negative_int(payload, "retry_count", errors)

    if "status" in payload and isinstance(payload.get("status"), str):
        if payload["status"] not in TASK_STATUS_VALUES:
            errors.append(f"status 不是合法值：{payload['status']}")

    if "approval_status" in payload and isinstance(payload.get("approval_status"), str):
        if payload["approval_status"] not in APPROVAL_STATUS_VALUES:
            errors.append(f"approval_status 不是合法值：{payload['approval_status']}")

    for field in ("result_policy", "callback_policy", "metadata"):
        if field in payload:
            _require_object(payload, field, errors)

    # 可選欄位型別
    _opt_str_or_null(payload, "input_payload_ref", errors)
    for field in ("allowed_tools", "denied_tools"):
        if field in payload:
            value = payload[field]
            if not isinstance(value, list):
                errors.append(f"{field} 必須為 array（list of strings）")
            elif not all(isinstance(item, str) for item in value):
                errors.append(f"{field} 內每個元素都必須為 string")

    _raise_if(errors, "TaskEnvelope")
    return payload


def validate_callback_event(payload: Any) -> Dict[str, Any]:
    """驗證 CallbackEvent v0.7。通過回傳 payload，否則 raise ContractValidationError。"""
    if not isinstance(payload, dict):
        raise ContractValidationError("CallbackEvent 必須為 object（dict）")

    errors: list[str] = []
    _check_required(payload, CALLBACK_REQUIRED_FIELDS, errors)

    for field in (
        "event_id",
        "task_id",
        "source",
        "created_at",
        "event_type",
        "status",
        "summary",
    ):
        if field in payload:
            _require_str(payload, field, errors)

    if "retryable" in payload:
        _require_bool(payload, "retryable", errors)

    if "metadata" in payload:
        _require_object(payload, "metadata", errors)

    if "event_type" in payload and isinstance(payload.get("event_type"), str):
        if payload["event_type"] not in CALLBACK_EVENT_TYPE_VALUES:
            errors.append(f"event_type 不是合法值：{payload['event_type']}")

    if "status" in payload and isinstance(payload.get("status"), str):
        if payload["status"] not in CALLBACK_STATUS_VALUES:
            errors.append(f"status 不是合法值：{payload['status']}")

    # 可選欄位型別
    for field in ("flow_id", "result_ref", "error_code", "error_message"):
        _opt_str_or_null(payload, field, errors)

    if "duration_ms" in payload and payload["duration_ms"] is not None:
        if not _is_int(payload["duration_ms"]):
            errors.append("duration_ms 必須為 integer 或 null")
        elif payload["duration_ms"] < 0:
            errors.append("duration_ms 必須為非負整數")

    if "artifacts" in payload:
        _require_array(payload, "artifacts", errors)

    _raise_if(errors, "CallbackEvent")
    return payload
