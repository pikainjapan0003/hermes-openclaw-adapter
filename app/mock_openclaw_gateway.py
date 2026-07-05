"""v0.8.5-B — OpenClaw Mock Gateway Helper（純函式、local-only、mock-only、dry-run-only）。

從一份 v0.8.5-A 定義的 OpenClaw Command Envelope dict，推導出 synthetic
local-only mock gateway response。本模組不呼叫真實 OpenClaw、不派工 Worker、
不讀寫 queue、不寫 audit trail、不新增任何 Dashboard control。

Mock gateway helper is not production gateway.
Mock gateway helper is not an OpenClaw call.
Mock gateway helper is not Worker dispatch.
Mock gateway response is not actual execution result.
Mock gateway response is not audit trail persistence.
Command envelope validation is not execution permission.
External side effects remain forbidden by default.

純 helper 邊界：
  - 不寫入任何檔案、不 mutate 輸入 envelope。
  - 不 import OpenClaw SDK、不 import app.main、不 import network client、不讀 secrets。
  - 不啟動 Worker、不呼叫 real OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不執行 subprocess、不執行 shell command、不做 network call。
  - 不觸碰 real queue DB、不觸碰 production/shared DB、不觸碰 Remote Blackboard API runtime。
  - 僅用標準庫（typing）。

公開 API：
  build_mock_openclaw_response(command_envelope: dict) -> dict
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

RESPONSE_SOURCE = "synthetic_local_only"

REQUIRED_ENVELOPE_FIELDS = (
    "command_id",
    "task_id",
    "tool_target",
    "requested_action",
    "risk_level",
    "approval_snapshot",
    "execution_mode",
    "dry_run",
    "mock_only",
    "external_touchpoints",
    "rollback_plan",
    "external_side_effects_allowed",
)

# Safety flags the envelope must satisfy before a mock response is built. Fields that
# are absent from the envelope are treated as their safe default (False) rather than
# causing a hard failure, so a v0.8.5-A envelope that never declares
# dispatch_allowed/worker_allowed/openclaw_allowed still passes safely.
REQUIRED_TRUE_FLAGS = ("mock_only", "dry_run")
REQUIRED_FALSE_FLAGS = (
    "external_side_effects_allowed",
    "dispatch_allowed",
    "worker_allowed",
    "openclaw_allowed",
)

REJECTION_RESPONSE_FIELDS = {
    "response_source": RESPONSE_SOURCE,
    "mock_gateway": True,
    "production_gateway": False,
    "real_openclaw_called": False,
    "worker_dispatched": False,
    "external_side_effects_performed": False,
    "queue_written": False,
    "audit_trail_written": False,
}


def _missing_required_fields(envelope: Mapping[str, Any]) -> list[str]:
    return [field for field in REQUIRED_ENVELOPE_FIELDS if field not in envelope]


def _unsafe_flag_violations(envelope: Mapping[str, Any]) -> list[str]:
    violations: list[str] = []
    for flag in REQUIRED_TRUE_FLAGS:
        if envelope.get(flag) is not True:
            violations.append(f"{flag} must be true")
    for flag in REQUIRED_FALSE_FLAGS:
        if envelope.get(flag, False) is not False:
            violations.append(f"{flag} must be false")
    return violations


def _rejection_response(reason: str, details: list[str]) -> Dict[str, Any]:
    response: Dict[str, Any] = dict(REJECTION_RESPONSE_FIELDS)
    response["accepted"] = False
    response["rejection_reason"] = reason
    response["rejection_details"] = list(details)
    return response


def build_mock_openclaw_response(command_envelope: Mapping[str, Any]) -> Dict[str, Any]:
    """從一份 command envelope 推導 synthetic local-only mock gateway response（純函式）。

    不 mutate 輸入、不寫入任何檔案、不連外、不派工、不呼叫 real OpenClaw。若必要欄位
    缺失，或安全旗標不符合（mock_only 非 true / dry_run 非 true /
    external_side_effects_allowed 或 dispatch_allowed / worker_allowed /
    openclaw_allowed 非 false），回傳一個標記 accepted=False 的 mock rejection
    response，而不是 raise，讓呼叫端可以安全地檢查結果。

    回傳的 response 恆標記 mock_gateway=True、production_gateway=False、
    real_openclaw_called=False、worker_dispatched=False、
    external_side_effects_performed=False、queue_written=False、
    audit_trail_written=False —— 無論 accepted 與否皆不變。
    """
    if not isinstance(command_envelope, Mapping):
        return _rejection_response(
            "command_envelope must be a mapping",
            ["command_envelope is not a dict/mapping"],
        )

    missing = _missing_required_fields(command_envelope)
    if missing:
        return _rejection_response(
            "missing required command envelope fields",
            [f"missing field: {field}" for field in missing],
        )

    violations = _unsafe_flag_violations(command_envelope)
    if violations:
        return _rejection_response("unsafe command envelope flags", violations)

    response: Dict[str, Any] = dict(REJECTION_RESPONSE_FIELDS)
    response["accepted"] = True
    response["rejection_reason"] = None
    response["rejection_details"] = []
    response["command_id"] = command_envelope.get("command_id")
    response["task_id"] = command_envelope.get("task_id")
    response["tool_target"] = command_envelope.get("tool_target")
    response["mock_response_summary"] = (
        "Synthetic local-only mock acknowledgement of a described command; no real "
        "OpenClaw call, no Worker dispatch, and no external side effect occurred."
    )
    return response
