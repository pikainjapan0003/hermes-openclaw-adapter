"""v0.7.0-C — 純 mock Adapter + Approval Gate（進 Queue 前的「安全櫃台」）。

模擬 Hermes 送任務進來後，Adapter 做的事：
  1. 把 mock request 轉成 v0.7.0-B TaskEnvelope（補齊 id / 時間戳 / 策略等欄位）。
  2. 用 v0.7.0-B validator 檢查格式。
  3. 依 risk_level / approval_required 判斷狀態。
  4. 產生 queued 或 pending_approval 的 TaskEnvelope（queue candidate）。

mock-only：
  - 不接真 Hermes / 真 OpenClaw / 真 webhook。
  - 不寫 Queue DB、不呼叫 Worker、不寫 Result Sink、不寫 Google Sheets。
  - 不讀任何環境 secret；僅用標準庫（uuid / hashlib / datetime）。

公開 API：
  class MockAdapterError(Exception)
  build_task_envelope_from_mock_request(request: dict) -> dict
  apply_approval_gate(task_envelope: dict) -> dict
  prepare_queue_candidate_from_mock_request(request: dict) -> dict
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from app.contracts_v0_7 import validate_task_envelope

# mock request 中必須由呼叫端提供的欄位（其餘欄位由 adapter 補預設值）。
MOCK_REQUEST_REQUIRED = (
    "request_id",
    "requested_by",
    "intent",
    "goal",
    "task_type",
    "risk_level",
    "input_summary",
    "target_runtime",
    "target_workspace",
)

DEFAULT_MAX_RETRIES = 3
DEFAULT_RESULT_POLICY: Dict[str, Any] = {"mode": "ledger"}
DEFAULT_CALLBACK_POLICY: Dict[str, Any] = {"mode": "ledger_only"}


class MockAdapterError(Exception):
    """mock adapter 處理 mock request 失敗時 raise（格式錯誤 / 缺欄位）。"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _idempotency_key(request: Dict[str, Any]) -> str:
    """以 mock request 內容衍生穩定去重鍵（相同 request → 相同 key）。"""
    basis = "|".join(
        str(request.get(field, "")) for field in ("request_id", "task_type", "goal")
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]
    return f"idem-{digest}"


def build_task_envelope_from_mock_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """把 mock Hermes request 轉成 v0.7.0-B TaskEnvelope（初始 status=draft）。"""
    if not isinstance(request, dict):
        raise MockAdapterError("mock request 必須為 dict")

    missing = [field for field in MOCK_REQUEST_REQUIRED if field not in request]
    if missing:
        raise MockAdapterError("mock request 缺少必要欄位：" + ", ".join(missing))

    metadata = request.get("metadata", {})
    if not isinstance(metadata, dict):
        raise MockAdapterError("metadata 必須為 dict")

    approval_required = bool(request.get("approval_required", False))

    envelope: Dict[str, Any] = {
        "task_id": f"task-{uuid.uuid4()}",
        "created_at": _utc_now_iso(),
        "created_by": str(request.get("created_by", "hermes-mock")),
        "source": str(request.get("source", "hermes-mock")),
        "requested_by": request["requested_by"],
        "risk_level": request["risk_level"],
        "approval_required": approval_required,
        "approval_status": "not_required",
        "intent": request["intent"],
        "goal": request["goal"],
        "task_type": request["task_type"],
        "priority": str(request.get("priority", "normal")),
        "input_summary": request["input_summary"],
        "target_runtime": request["target_runtime"],
        "target_workspace": request["target_workspace"],
        "idempotency_key": _idempotency_key(request),
        "max_retries": int(request.get("max_retries", DEFAULT_MAX_RETRIES)),
        "retry_count": 0,
        "status": "draft",
        "result_policy": dict(request.get("result_policy", DEFAULT_RESULT_POLICY)),
        "callback_policy": dict(request.get("callback_policy", DEFAULT_CALLBACK_POLICY)),
        "metadata": dict(metadata),
    }

    # 選填欄位：原樣帶過（型別交給 validator 把關）。
    for opt in ("input_payload_ref", "allowed_tools", "denied_tools"):
        if opt in request:
            envelope[opt] = request[opt]

    # 用 v0.7.0-B validator 把關格式（risk_level 越界等會 raise ContractValidationError）。
    validate_task_envelope(envelope)
    return envelope


def apply_approval_gate(task_envelope: Dict[str, Any]) -> Dict[str, Any]:
    """依 risk_level / approval_required 判斷狀態，回傳新的 TaskEnvelope（不就地修改輸入）。

    規則：
      risk_level 3,4               → pending_approval、approval_required=true、approval_status=pending
      approval_required=true       → pending_approval、approval_status=pending
      risk_level 0,1,2 且未要求批准 → queued、approval_status=not_required
    """
    if not isinstance(task_envelope, dict):
        raise MockAdapterError("task_envelope 必須為 dict")
    if "risk_level" not in task_envelope:
        raise MockAdapterError("task_envelope 缺少 risk_level")

    env = dict(task_envelope)
    risk_level = env["risk_level"]

    if isinstance(risk_level, int) and not isinstance(risk_level, bool) and risk_level >= 3:
        env["approval_required"] = True
        env["approval_status"] = "pending"
        env["status"] = "pending_approval"
    elif bool(env.get("approval_required")):
        env["approval_status"] = "pending"
        env["status"] = "pending_approval"
    else:
        env["approval_status"] = "not_required"
        env["status"] = "queued"

    return env


def prepare_queue_candidate_from_mock_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """mock request → envelope → validate → approval gate → validate → 回傳 queue candidate。

    僅產生 queue candidate；不寫 Queue DB、不呼叫 Worker。
    """
    envelope = build_task_envelope_from_mock_request(request)
    validate_task_envelope(envelope)
    gated = apply_approval_gate(envelope)
    validate_task_envelope(gated)
    return gated
