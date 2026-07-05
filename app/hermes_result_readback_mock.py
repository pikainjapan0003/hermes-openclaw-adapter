"""v0.9-E — Hermes Reads Result Message Mock（純函式、local-only、mock-only、readback-only）。

從一份 synthetic mock result message dict，經由本地 v0.9-C ``mock_hermes_generator``
推導出一份 synthetic Hermes result readback advice。本模組不啟動 Hermes runtime、不讀
Hermes memory、不呼叫 Hermes tool、不寫 Blackboard、不讀寫 queue、不寫 audit trail、不
自動建立 follow-up task、不呼叫 Worker、不呼叫 OpenClaw、不碰 Google Sheets、不新增任何
Dashboard control。

Hermes result readback mock is not Hermes activation.
Hermes result readback mock is not real Hermes readback.
Hermes result readback mock does not read Hermes memory.
Hermes result readback mock does not call Hermes tools.
Hermes readback is not Blackboard write.
Hermes readback is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes readback is not automatic follow-up task creation.
Hermes readback is not Worker dispatch.
Hermes readback is not OpenClaw call.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

純 helper 邊界：
  - 不寫入任何檔案、不 mutate 輸入的 result_message / readback advice。
  - 不 import Hermes runtime、不 import app.main、不 import network client、不讀 secrets。
  - 不啟動 Worker、不呼叫 real OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不執行 subprocess、不執行 shell command、不做 network call。
  - 不觸碰 real queue DB、不觸碰 production/shared DB、不觸碰 Remote Blackboard API runtime。
  - 僅用標準庫（typing / importlib / pathlib）；本地載入同目錄下的
    ``mock_hermes_generator.py``，不透過套件層級 import，維持模組獨立可載入。

公開 API：
  build_hermes_result_readback_advice(result_message: dict) -> dict
  validate_hermes_result_readback_advice(readback_advice: dict) -> dict
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Mapping

READBACK_SOURCE = "synthetic_local_only"
REQUIRED_RESULT_MESSAGE_SOURCE = "synthetic_local_only"

_GENERATOR_MODULE_PATH = Path(__file__).resolve().parent / "mock_hermes_generator.py"

REQUIRED_RESULT_MESSAGE_FIELDS = (
    "result_id",
    "task_id",
    "status",
    "source",
    "mock_gateway",
    "worker_dry_run",
    "real_openclaw_called",
    "worker_dispatched",
    "external_side_effects_performed",
    "queue_written",
    "audit_trail_written",
)

# Safety flags a result message must satisfy before it is treated as a trustworthy
# synthetic mock result. Presence of the correct `source` value is checked separately.
REQUIRED_RESULT_MESSAGE_TRUE_FLAGS = ("mock_gateway", "worker_dry_run")
REQUIRED_RESULT_MESSAGE_FALSE_FLAGS = (
    "real_openclaw_called",
    "worker_dispatched",
    "external_side_effects_performed",
    "queue_written",
    "audit_trail_written",
)

# Fields never sourced from the result message or from the underlying advice — this
# readback mock always forces them itself, on both accepted and rejected readback advice.
FORCED_READBACK_SAFETY_FIELDS: Dict[str, bool] = {
    "mock_hermes": True,
    "real_hermes_called": False,
    "hermes_runtime_activated": False,
    "hermes_memory_read": False,
    "hermes_tool_called": False,
    "result_readback_only": True,
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "follow_up_task_auto_create_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}

REQUIRED_READBACK_ADVICE_FIELDS = (
    "readback_id",
    "advice_id",
    "suggestion_id",
    "task_id",
    "source_result_id",
    "source_result_status",
    "readback_source",
    "readback_summary",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
) + tuple(FORCED_READBACK_SAFETY_FIELDS)


def _load_generator_module():
    spec = importlib.util.spec_from_file_location(
        "mock_hermes_generator_v0_9_e", _GENERATOR_MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _missing_required_result_message_fields(result_message: Mapping[str, Any]) -> list[str]:
    return [field for field in REQUIRED_RESULT_MESSAGE_FIELDS if field not in result_message]


def _unsafe_result_message_violations(result_message: Mapping[str, Any]) -> list[str]:
    violations: list[str] = []
    if result_message.get("source") != REQUIRED_RESULT_MESSAGE_SOURCE:
        violations.append(f"source must be {REQUIRED_RESULT_MESSAGE_SOURCE!r}")
    for flag in REQUIRED_RESULT_MESSAGE_TRUE_FLAGS:
        if result_message.get(flag) is not True:
            violations.append(f"{flag} must be true")
    for flag in REQUIRED_RESULT_MESSAGE_FALSE_FLAGS:
        if result_message.get(flag) is not False:
            violations.append(f"{flag} must be false")
    return violations


def _rejected_readback(
    reason: str,
    details: list[str],
    *,
    task_id: Any = None,
    result_id: Any = None,
    status: Any = None,
) -> Dict[str, Any]:
    readback: Dict[str, Any] = {
        "readback_id": None,
        "advice_id": None,
        "suggestion_id": None,
        "task_id": task_id,
        "source_result_id": result_id,
        "source_result_status": status,
        "readback_source": READBACK_SOURCE,
        "accepted": False,
        "rejection_reason": reason,
        "rejection_details": list(details),
    }
    readback.update(FORCED_READBACK_SAFETY_FIELDS)
    return readback


def build_hermes_result_readback_advice(result_message: Mapping[str, Any]) -> Dict[str, Any]:
    """從一份 synthetic mock result message 建立 Hermes result readback advice（純函式）。

    不 mutate 輸入、不寫入任何檔案、不連外、不派工、不呼叫 real OpenClaw、不寫
    Blackboard、不啟動 Hermes runtime、不讀 Hermes memory、不呼叫 Hermes tool、不自動
    建立 follow-up task。本函式先確認 result_message 本身是可信的 synthetic mock 結果
    （``source == "synthetic_local_only"``、``mock_gateway`` / ``worker_dry_run`` 為
    true、``real_openclaw_called`` / ``worker_dispatched`` /
    ``external_side_effects_performed`` / ``queue_written`` / ``audit_trail_written``
    為 false）；若不符合，直接回傳一個標記 accepted=False 的 rejection readback，完全
    不呼叫本地 v0.9-C mock Hermes generator。

    若符合，才把 result_message 包裝成一份 synthetic source context，呼叫本地
    ``app/mock_hermes_generator.build_mock_hermes_advice()``（同目錄動態載入，不透過
    套件層級 import）。若底層 advice 本身被拒絕，直接反映其 rejection_reason /
    rejection_details。若 advice 被接受，才把 advice 的欄位包裝成 readback advice
    dict，並附加 `readback_id`（由 `result_id` 決定性推導：
    `f"readback-{result_id}"`）。

    十五個安全欄位（mock_hermes / real_hermes_called / hermes_runtime_activated /
    hermes_memory_read / hermes_tool_called / result_readback_only /
    must_not_execute / requires_owner_confirmation / blackboard_write_allowed /
    queue_write_allowed / audit_trail_write_allowed /
    follow_up_task_auto_create_allowed / worker_dispatch_allowed /
    openclaw_call_allowed / external_side_effects_allowed）恆由本模組強制設定為安全
    值，不論 result_message 或底層 advice 是否嘗試覆寫。
    """
    if not isinstance(result_message, Mapping):
        return _rejected_readback(
            "result_message must be a mapping",
            ["result_message is not a dict/mapping"],
        )

    task_id = result_message.get("task_id")
    result_id = result_message.get("result_id")
    status = result_message.get("status")

    missing = _missing_required_result_message_fields(result_message)
    if missing:
        return _rejected_readback(
            "missing required result message fields",
            [f"missing field: {field}" for field in missing],
            task_id=task_id,
            result_id=result_id,
            status=status,
        )

    violations = _unsafe_result_message_violations(result_message)
    if violations:
        return _rejected_readback(
            "unsafe result message flags",
            violations,
            task_id=task_id,
            result_id=result_id,
            status=status,
        )

    source_context = {
        "task_id": task_id,
        "source_message_ids": [f"msg-readback-{result_id}"],
        "source_result_ids": [result_id],
        "source_decision_ids": [],
        "strategy_summary": (
            f"Synthetic readback of mock result {result_id} (status={status}); "
            "advisory only, no automatic follow-up."
        ),
        "recommended_action": (
            "review the mock result and decide whether any real follow-up is "
            "warranted; no action taken automatically"
        ),
        "risk_assessment": "low",
        "missing_information": "none",
        "owner_question": (
            f"does the Owner want to define a real follow-up task based on mock "
            f"result {result_id}?"
        ),
        "suggested_next_step": "await Owner confirmation before any follow-up task is created",
        "confidence": "medium",
    }

    generator_module = _load_generator_module()
    advice = generator_module.build_mock_hermes_advice(source_context)

    if not advice.get("accepted"):
        return _rejected_readback(
            advice.get("rejection_reason") or "underlying mock Hermes advice rejected",
            list(advice.get("rejection_details", [])),
            task_id=task_id,
            result_id=result_id,
            status=status,
        )

    readback: Dict[str, Any] = {
        "readback_id": f"readback-{result_id}",
        "advice_id": advice["advice_id"],
        "suggestion_id": advice["suggestion_id"],
        "task_id": advice["task_id"],
        "source_result_id": result_id,
        "source_result_status": status,
        "readback_source": READBACK_SOURCE,
        "accepted": True,
        "rejection_reason": None,
        "rejection_details": [],
        "readback_summary": (
            f"Synthetic readback of mock result {result_id} status={status}; "
            "advisory only, no automatic follow-up."
        ),
        "strategy_summary": advice["strategy_summary"],
        "recommended_action": advice["recommended_action"],
        "risk_assessment": advice["risk_assessment"],
        "missing_information": advice["missing_information"],
        "owner_question": advice["owner_question"],
        "suggested_next_step": advice["suggested_next_step"],
        "confidence": advice["confidence"],
    }
    readback.update(FORCED_READBACK_SAFETY_FIELDS)
    return readback


def validate_hermes_result_readback_advice(readback_advice: Mapping[str, Any]) -> Dict[str, Any]:
    """檢查任意 readback advice dict 是否符合強制安全值與必要欄位（純函式、fail-safe）。

    不 raise：若輸入不是 mapping、缺少必要欄位、或十五個安全欄位有任何一個不符合強制
    安全值，回傳 `{"valid": False, "violations": [...]}`；否則回傳 `{"valid": True,
    "violations": []}`。本函式從不因為輸入本身不安全而執行、派工、或寫入任何東西 ——
    它只回報檢查結果。
    """
    if not isinstance(readback_advice, Mapping):
        return {"valid": False, "violations": ["readback_advice must be a mapping"]}

    violations: list[str] = []
    missing = [field for field in REQUIRED_READBACK_ADVICE_FIELDS if field not in readback_advice]
    violations.extend(f"missing field: {field}" for field in missing)

    for field, safe_value in FORCED_READBACK_SAFETY_FIELDS.items():
        if field in readback_advice and readback_advice[field] is not safe_value:
            violations.append(f"{field} must be {safe_value!r}")

    return {"valid": not violations, "violations": violations}
