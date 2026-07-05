"""v0.9-B — Hermes Strategy Suggestion Model（純函式、local-only、mock-only、advisory-only）。

從一份 synthetic source context dict，建立一份 Hermes Strategy Suggestion dict，並提供
一個獨立的 validator 檢查任意 suggestion dict 是否符合強制安全值。本模組不啟動 Hermes
runtime、不讀 Hermes memory、不呼叫 Hermes tool、不寫 Blackboard、不讀寫 queue、不寫
audit trail、不呼叫 Worker、不呼叫 OpenClaw、不碰 Google Sheets、不新增任何 Dashboard
control。

Strategy suggestion model is not Hermes activation.
Strategy suggestion model is not mock Hermes generator.
Hermes suggestion is not Blackboard write.
Hermes advice is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes strategy suggestion is not Worker dispatch.
Hermes strategy suggestion is not OpenClaw call.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

純 helper 邊界：
  - 不寫入任何檔案、不 mutate 輸入的 source_context / suggestion。
  - 不 import Hermes runtime、不 import app.main、不 import network client、不讀 secrets。
  - 不啟動 Worker、不呼叫 real OpenClaw、不呼叫 Hermes、不寫 Google Sheets。
  - 不執行 subprocess、不執行 shell command、不做 network call。
  - 不觸碰 real queue DB、不觸碰 production/shared DB、不觸碰 Remote Blackboard API runtime。
  - 僅用標準庫（typing）。

公開 API：
  build_hermes_strategy_suggestion(source_context: dict) -> dict
  validate_hermes_strategy_suggestion(suggestion: dict) -> dict
"""
from __future__ import annotations

from typing import Any, Dict, Mapping

SUGGESTION_SOURCE = "synthetic_local_only"

REQUIRED_SOURCE_CONTEXT_FIELDS = (
    "task_id",
    "source_message_ids",
    "source_result_ids",
    "source_decision_ids",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
)

# Safety fields are never sourced from caller input — they are always forced to these
# values by the model itself, regardless of what a source_context or an externally
# constructed suggestion dict claims.
FORCED_SAFETY_FIELDS: Dict[str, bool] = {
    "must_not_execute": True,
    "requires_owner_confirmation": True,
    "blackboard_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "external_side_effects_allowed": False,
}

REQUIRED_SUGGESTION_FIELDS = (
    "suggestion_id",
    "task_id",
    "source_message_ids",
    "source_result_ids",
    "source_decision_ids",
    "strategy_summary",
    "recommended_action",
    "risk_assessment",
    "missing_information",
    "owner_question",
    "suggested_next_step",
    "confidence",
) + tuple(FORCED_SAFETY_FIELDS)


def _missing_required_fields(context: Mapping[str, Any]) -> list[str]:
    return [field for field in REQUIRED_SOURCE_CONTEXT_FIELDS if field not in context]


def _rejection_suggestion(reason: str, details: list[str]) -> Dict[str, Any]:
    suggestion: Dict[str, Any] = {
        "suggestion_source": SUGGESTION_SOURCE,
        "accepted": False,
        "rejection_reason": reason,
        "rejection_details": list(details),
    }
    suggestion.update(FORCED_SAFETY_FIELDS)
    return suggestion


def build_hermes_strategy_suggestion(source_context: Mapping[str, Any]) -> Dict[str, Any]:
    """從一份 synthetic source context 建立 Hermes Strategy Suggestion（純函式）。

    不 mutate 輸入、不寫入任何檔案、不連外、不派工、不呼叫 real OpenClaw、不寫
    Blackboard。若 source_context 不是 mapping，或缺少必要欄位（task_id /
    source_message_ids / source_result_ids / source_decision_ids / strategy_summary /
    recommended_action / risk_assessment / missing_information / owner_question /
    suggested_next_step / confidence），回傳一個標記 accepted=False 的 rejection
    suggestion，而不是 raise。

    `suggestion_id` 由 `task_id` 決定性推導（`f"suggestion-{task_id}"`），不使用亂數或
    時間戳，維持 deterministic。六個安全欄位（must_not_execute /
    requires_owner_confirmation / blackboard_write_allowed / worker_dispatch_allowed /
    openclaw_call_allowed / external_side_effects_allowed）恆由本模組強制設定為安全值，
    不論 source_context 是否嘗試覆寫。
    """
    if not isinstance(source_context, Mapping):
        return _rejection_suggestion(
            "source_context must be a mapping",
            ["source_context is not a dict/mapping"],
        )

    missing = _missing_required_fields(source_context)
    if missing:
        return _rejection_suggestion(
            "missing required source context fields",
            [f"missing field: {field}" for field in missing],
        )

    task_id = source_context["task_id"]
    suggestion: Dict[str, Any] = {
        "suggestion_source": SUGGESTION_SOURCE,
        "accepted": True,
        "rejection_reason": None,
        "rejection_details": [],
        "suggestion_id": f"suggestion-{task_id}",
        "task_id": task_id,
        "source_message_ids": list(source_context["source_message_ids"]),
        "source_result_ids": list(source_context["source_result_ids"]),
        "source_decision_ids": list(source_context["source_decision_ids"]),
        "strategy_summary": source_context["strategy_summary"],
        "recommended_action": source_context["recommended_action"],
        "risk_assessment": source_context["risk_assessment"],
        "missing_information": source_context["missing_information"],
        "owner_question": source_context["owner_question"],
        "suggested_next_step": source_context["suggested_next_step"],
        "confidence": source_context["confidence"],
    }
    suggestion.update(FORCED_SAFETY_FIELDS)
    return suggestion


def validate_hermes_strategy_suggestion(suggestion: Mapping[str, Any]) -> Dict[str, Any]:
    """檢查任意 suggestion dict 是否符合強制安全值與必要欄位（純函式、fail-safe）。

    不 raise：若輸入不是 mapping、缺少必要欄位、或六個安全欄位有任何一個不符合強制安全
    值，回傳 `{"valid": False, "violations": [...]}`；否則回傳 `{"valid": True,
    "violations": []}`。本函式從不因為輸入本身不安全而執行、派工、或寫入任何東西 ——
    它只回報檢查結果。
    """
    if not isinstance(suggestion, Mapping):
        return {"valid": False, "violations": ["suggestion must be a mapping"]}

    violations: list[str] = []
    missing = [field for field in REQUIRED_SUGGESTION_FIELDS if field not in suggestion]
    violations.extend(f"missing field: {field}" for field in missing)

    for field, safe_value in FORCED_SAFETY_FIELDS.items():
        if field in suggestion and suggestion[field] is not safe_value:
            violations.append(f"{field} must be {safe_value!r}")

    return {"valid": not violations, "violations": violations}
