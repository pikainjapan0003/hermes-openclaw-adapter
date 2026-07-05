"""v0.9-C — Mock Hermes Generator（純函式、local-only、mock-only、advisory-only）。

從一份 synthetic source context dict，經由本地 v0.9-B
``hermes_strategy_suggestion_model`` 推導出一份 synthetic mock Hermes advice。本模組不
啟動 Hermes runtime、不讀 Hermes memory、不呼叫 Hermes tool、不寫 Blackboard、不讀寫
queue、不寫 audit trail、不呼叫 Worker、不呼叫 OpenClaw、不碰 Google Sheets、不新增任何
Dashboard control。

Mock Hermes generator is not Hermes activation.
Mock Hermes generator is not real Hermes.
Mock Hermes advice is not Blackboard write.
Mock Hermes advice is not Owner approval.
Mock Hermes advice is not automatic follow-up execution.
Mock Hermes advice is not Worker dispatch.
Mock Hermes advice is not OpenClaw call.
Mock Hermes cannot bypass Owner Review.
Mock Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

純 helper 邊界：
  - 不寫入任何檔案、不 mutate 輸入的 source_context / advice。
  - 不 import Hermes runtime、不 import app.main、不 import network client、不讀 secrets。
  - 不啟動 Worker、不呼叫 real OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不執行 subprocess、不執行 shell command、不做 network call。
  - 不觸碰 real queue DB、不觸碰 production/shared DB、不觸碰 Remote Blackboard API runtime。
  - 僅用標準庫（typing / importlib / pathlib）；本地載入同目錄下的
    ``hermes_strategy_suggestion_model.py``，不透過套件層級 import，維持模組獨立可載入。

公開 API：
  build_mock_hermes_advice(source_context: dict) -> dict
  validate_mock_hermes_advice(advice: dict) -> dict
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Mapping

ADVICE_SOURCE = "synthetic_local_only"

_SUGGESTION_MODEL_PATH = Path(__file__).resolve().parent / "hermes_strategy_suggestion_model.py"

# Fields never sourced from caller input or from the underlying suggestion — this
# generator always forces them itself, on both accepted and rejected advice.
FORCED_ADVICE_SAFETY_FIELDS: Dict[str, bool] = {
    "mock_hermes": True,
    "real_hermes_called": False,
    "hermes_runtime_activated": False,
    "hermes_memory_read": False,
    "hermes_tool_called": False,
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}

REQUIRED_ADVICE_FIELDS = (
    "advice_id",
    "suggestion_id",
    "task_id",
    "source_message_ids",
    "source_result_ids",
    "source_decision_ids",
    "advice_source",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
) + tuple(FORCED_ADVICE_SAFETY_FIELDS)


def _load_suggestion_model_module():
    spec = importlib.util.spec_from_file_location(
        "hermes_strategy_suggestion_model_v0_9_c", _SUGGESTION_MODEL_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rejected_advice(reason: str, details: list[str], *, task_id: Any = None) -> Dict[str, Any]:
    advice: Dict[str, Any] = {
        "advice_id": None,
        "suggestion_id": None,
        "task_id": task_id,
        "advice_source": ADVICE_SOURCE,
        "accepted": False,
        "rejection_reason": reason,
        "rejection_details": list(details),
    }
    advice.update(FORCED_ADVICE_SAFETY_FIELDS)
    return advice


def build_mock_hermes_advice(source_context: Mapping[str, Any]) -> Dict[str, Any]:
    """從一份 synthetic source context 建立 mock Hermes advice（純函式）。

    不 mutate 輸入、不寫入任何檔案、不連外、不派工、不呼叫 real OpenClaw、不寫
    Blackboard、不啟動 Hermes runtime、不讀 Hermes memory、不呼叫 Hermes tool。本函式先
    呼叫本地 v0.9-B ``build_hermes_strategy_suggestion`` 推導 suggestion；若該 suggestion
    本身被拒絕（缺欄位或非 mapping），直接回傳一個標記 accepted=False 的 rejection
    advice，不額外處理。若 suggestion 被接受，才把 suggestion 的欄位包裝成 advice dict，
    並附加 `advice_id`（由 `suggestion_id` 決定性推導：`f"advice-{suggestion_id}"`）。

    十三個安全欄位（mock_hermes / real_hermes_called / hermes_runtime_activated /
    hermes_memory_read / hermes_tool_called / must_not_execute /
    requires_owner_confirmation / blackboard_write_allowed / queue_write_allowed /
    audit_trail_write_allowed / worker_dispatch_allowed / openclaw_call_allowed /
    external_side_effects_allowed）恆由本模組強制設定為安全值，不論 source_context 或
    底層 suggestion 是否嘗試覆寫。
    """
    if not isinstance(source_context, Mapping):
        return _rejected_advice(
            "source_context must be a mapping",
            ["source_context is not a dict/mapping"],
        )

    suggestion_model = _load_suggestion_model_module()
    suggestion = suggestion_model.build_hermes_strategy_suggestion(source_context)

    if not suggestion.get("accepted"):
        return _rejected_advice(
            suggestion.get("rejection_reason") or "underlying strategy suggestion rejected",
            list(suggestion.get("rejection_details", [])),
            task_id=source_context.get("task_id"),
        )

    advice: Dict[str, Any] = {
        "advice_id": f"advice-{suggestion['suggestion_id']}",
        "suggestion_id": suggestion["suggestion_id"],
        "task_id": suggestion["task_id"],
        "source_message_ids": list(suggestion["source_message_ids"]),
        "source_result_ids": list(suggestion["source_result_ids"]),
        "source_decision_ids": list(suggestion["source_decision_ids"]),
        "advice_source": ADVICE_SOURCE,
        "accepted": True,
        "rejection_reason": None,
        "rejection_details": [],
        "strategy_summary": suggestion["strategy_summary"],
        "recommended_action": suggestion["recommended_action"],
        "risk_assessment": suggestion["risk_assessment"],
        "missing_information": suggestion["missing_information"],
        "owner_question": suggestion["owner_question"],
        "suggested_next_step": suggestion["suggested_next_step"],
        "confidence": suggestion["confidence"],
    }
    advice.update(FORCED_ADVICE_SAFETY_FIELDS)
    return advice


def validate_mock_hermes_advice(advice: Mapping[str, Any]) -> Dict[str, Any]:
    """檢查任意 mock Hermes advice dict 是否符合強制安全值與必要欄位（純函式、fail-safe）。

    不 raise：若輸入不是 mapping、缺少必要欄位、或十三個安全欄位有任何一個不符合強制
    安全值，回傳 `{"valid": False, "violations": [...]}`；否則回傳 `{"valid": True,
    "violations": []}`。本函式從不因為輸入本身不安全而執行、派工、或寫入任何東西 ——
    它只回報檢查結果。
    """
    if not isinstance(advice, Mapping):
        return {"valid": False, "violations": ["advice must be a mapping"]}

    violations: list[str] = []
    missing = [field for field in REQUIRED_ADVICE_FIELDS if field not in advice]
    violations.extend(f"missing field: {field}" for field in missing)

    for field, safe_value in FORCED_ADVICE_SAFETY_FIELDS.items():
        if field in advice and advice[field] is not safe_value:
            violations.append(f"{field} must be {safe_value!r}")

    return {"valid": not violations, "violations": violations}
