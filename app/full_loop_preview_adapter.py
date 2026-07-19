"""v1.0-RC-D — Full Loop Preview Adapter（純函式、local-only、mock-only、read-only）。

從一份本地 synthetic full-loop rehearsal fixture 檔案（`fixtures/local_mock_data/
hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json`）讀取資料，驗證頂層欄位、全域
安全旗標、timeline 存在性/順序/每步欄位與安全旗標，推導出一份 Dashboard 唯讀 Full Loop
Rehearsal Preview view model。本模組不實作真正的 Full Blackboard Loop、不寫
Blackboard、不寫 queue、不寫 audit trail、不派工、不呼叫 OpenClaw、不啟動 Hermes
runtime、不呼叫 connector、不新增 Dashboard control、不建立 route/endpoint/webhook。

Full Loop Preview Adapter Plan is not adapter implementation trigger for execution.
Full Loop Rehearsal Preview is read-only. Preview is not execution permission.
Timeline is not dispatch permission. Result status is not real execution success
without validation. Owner review required is not Owner approval. Hermes readback
is advisory only.

純 helper 邊界：
  - 只讀取本地 synthetic fixture 檔案；不 mutate 該檔案、不寫入任何檔案。
  - 不 import app.main、不 import Hermes runtime、不 import Worker runtime、不
    import OpenClaw runtime、不 import connector runtime、不 import network client。
  - 不做 network call、不讀 secrets、不讀 connector data、不讀 production data。
  - 不觸碰 real queue DB、不寫 audit trail、不寫 Blackboard、不建立 task。
  - 僅用標準庫（json / pathlib / typing）。

公開 API：
  load_full_loop_rehearsal_fixture() -> dict
  build_full_loop_rehearsal_preview_model() -> dict
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "local_mock_data"
    / "hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json"
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "fixture_id",
    "fixture_version",
    "fixture_kind",
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "created_for_phase",
    "source_baseline",
    "loop_summary",
    "safety_flags",
    "timeline",
    "artifacts",
    "validation_expectations",
    "fail_closed_rules",
    "non_goals",
    "next_owner_review_question",
)

REQUIRED_TRUE_TOP_LEVEL_FLAGS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
)

REQUIRED_FALSE_TOP_LEVEL_FLAGS = (
    "external_side_effects_allowed",
    "external_side_effects_occurred",
)

REQUIRED_TRUE_SAFETY_FLAGS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "read_only",
    "owner_review_required",
)

REQUIRED_FALSE_SAFETY_FLAGS = (
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "follow_up_task_creation_allowed",
    "dashboard_controls_allowed",
)

REQUIRED_TIMELINE_STEP_IDS = (
    "owner_rehearsal_request",
    "blackboard_task_draft",
    "annotation_preview",
    "approval_readiness_preview",
    "owner_decision_preview",
    "worker_dry_run_preview",
    "openclaw_mock_command_envelope",
    "openclaw_mock_gateway_result",
    "synthetic_result_message",
    "result_feedback_display_preview",
    "hermes_advisory_readback",
    "follow_up_suggestion_guard_output",
    "final_owner_review_summary",
)

REQUIRED_STEP_FIELDS = (
    "step_id",
    "step_order",
    "step_title",
    "source_component",
    "target_component",
    "synthetic_input",
    "synthetic_output",
    "allowed_behavior",
    "forbidden_behavior",
    "safety_flags",
    "validation_status",
    "owner_review_required",
    "next_step_allowed",
    "next_step_requires_owner_confirmation",
    "notes",
)

# Fields never trusted from the fixture record itself for the top-level output —
# this adapter always forces them on both accepted and rejected preview models.
FORCED_SAFE_FIELDS: Dict[str, bool] = {flag: True for flag in REQUIRED_TRUE_SAFETY_FLAGS}
FORCED_SAFE_FIELDS.update({flag: False for flag in REQUIRED_FALSE_SAFETY_FLAGS})

REQUIRED_OUTPUT_LABELS = (
    "FULL LOOP REHEARSAL PREVIEW",
    "READ ONLY",
    "SYNTHETIC / MOCK ONLY",
    "DRY RUN ONLY",
    "VALIDATED FIXTURE ONLY",
    "NO BLACKBOARD WRITE",
    "NO QUEUE WRITE",
    "NO AUDIT TRAIL WRITE",
    "NO WORKER DISPATCH",
    "NO OPENCLAW CALL",
    "NO HERMES RUNTIME",
    "NO CONNECTOR CALL",
    "NO EXTERNAL SIDE EFFECTS",
    "OWNER REVIEW REQUIRED",
    "PREVIEW IS NOT EXECUTION PERMISSION",
)

_WEBHOOK_URL_PATTERN = re.compile(r"https?://\S+/webhook\S*", re.IGNORECASE)
_PRODUCTION_ENDPOINT_PATTERN = re.compile(r"https?://(?!localhost|127\.0\.0\.1)\S+", re.IGNORECASE)
_SECRET_LIKE_PATTERN = re.compile(
    r"(sk-|ghp_|xox[baprs]-|AIza|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE
)
_FORBIDDEN_FIELD_NAME_MARKERS = (
    "password",
    "secret",
    "token",
    "post_body",
    "action_url",
    "webhook_url",
)


def load_full_loop_rehearsal_fixture() -> Dict[str, Any]:
    """讀取本地 synthetic fixture（純讀取，不寫入、不連外、不讀 secrets）。"""
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("fixture root must be a JSON object")
    return data


def _missing_top_level_fields(record: Mapping[str, Any]) -> List[str]:
    return [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record]


def _unsafe_top_level_flags(record: Mapping[str, Any]) -> List[str]:
    violations: List[str] = []
    for flag in REQUIRED_TRUE_TOP_LEVEL_FLAGS:
        if record.get(flag) is not True:
            violations.append(f"top-level {flag} must be true")
    for flag in REQUIRED_FALSE_TOP_LEVEL_FLAGS:
        if record.get(flag) is not False:
            violations.append(f"top-level {flag} must be false")
    return violations


def _unsafe_global_safety_flags(safety_flags: Any) -> List[str]:
    if not isinstance(safety_flags, Mapping):
        return ["safety_flags must be a mapping"]
    violations: List[str] = []
    for flag in REQUIRED_TRUE_SAFETY_FLAGS:
        if safety_flags.get(flag) is not True:
            violations.append(f"safety_flags.{flag} must be true")
    for flag in REQUIRED_FALSE_SAFETY_FLAGS:
        if safety_flags.get(flag) is not False:
            violations.append(f"safety_flags.{flag} must be false")
    return violations


def _contains_unsafe_text(value: Any) -> bool:
    if isinstance(value, str):
        return (
            bool(_WEBHOOK_URL_PATTERN.search(value))
            or bool(_PRODUCTION_ENDPOINT_PATTERN.search(value))
            or bool(_SECRET_LIKE_PATTERN.search(value))
        )
    if isinstance(value, Mapping):
        return any(_contains_unsafe_text(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_unsafe_text(v) for v in value)
    return False


def _contains_forbidden_field_names(value: Any) -> List[str]:
    found: List[str] = []
    if isinstance(value, Mapping):
        for key, sub_value in value.items():
            key_lower = str(key).lower()
            if any(marker in key_lower for marker in _FORBIDDEN_FIELD_NAME_MARKERS):
                found.append(str(key))
            found.extend(_contains_forbidden_field_names(sub_value))
    elif isinstance(value, list):
        for item in value:
            found.extend(_contains_forbidden_field_names(item))
    return found


def _validate_timeline(timeline: Any) -> List[str]:
    violations: List[str] = []
    if not isinstance(timeline, list) or not timeline:
        return ["timeline must be a non-empty list"]

    found_step_ids = []
    for index, step in enumerate(timeline):
        if not isinstance(step, Mapping):
            violations.append(f"timeline[{index}] must be a mapping")
            continue
        missing_step_fields = [f for f in REQUIRED_STEP_FIELDS if f not in step]
        if missing_step_fields:
            violations.append(f"timeline[{index}] missing fields: {missing_step_fields}")
            continue
        found_step_ids.append(step.get("step_id"))
        if step.get("step_order") != index + 1:
            violations.append(f"timeline[{index}] step_order must be {index + 1}, got {step.get('step_order')!r}")
        step_safety_flags = step.get("safety_flags")
        if not isinstance(step_safety_flags, Mapping):
            violations.append(f"timeline[{index}] safety_flags must be a mapping")
        else:
            for flag, value in step_safety_flags.items():
                if flag.endswith("_allowed") and value is not False and flag not in ("owner_review_required",):
                    violations.append(f"timeline[{index}] safety_flags.{flag} must be false, got {value!r}")

    missing_required_steps = [s for s in REQUIRED_TIMELINE_STEP_IDS if s not in found_step_ids]
    if missing_required_steps:
        violations.append(f"missing required timeline steps: {missing_required_steps}")

    if found_step_ids != list(REQUIRED_TIMELINE_STEP_IDS)[: len(found_step_ids)] and not missing_required_steps:
        if list(found_step_ids) != list(REQUIRED_TIMELINE_STEP_IDS):
            violations.append("timeline steps are out of the required deterministic order")

    return violations


def _summarize_step(step: Mapping[str, Any]) -> Dict[str, Any]:
    safety_flags = step.get("safety_flags")
    safety_flags_summary = (
        ", ".join(f"{k}={v}" for k, v in safety_flags.items())
        if isinstance(safety_flags, Mapping)
        else ""
    )
    return {
        "step_order": step.get("step_order"),
        "step_id": step.get("step_id"),
        "step_title": step.get("step_title"),
        "source_component": step.get("source_component"),
        "target_component": step.get("target_component"),
        "validation_status": step.get("validation_status"),
        "owner_review_required": step.get("owner_review_required"),
        "next_step_allowed": step.get("next_step_allowed"),
        "next_step_requires_owner_confirmation": step.get("next_step_requires_owner_confirmation"),
        "allowed_behavior_summary": step.get("allowed_behavior"),
        "forbidden_behavior_summary": step.get("forbidden_behavior"),
        "safety_flags_summary": safety_flags_summary,
        "synthetic_input_summary": step.get("synthetic_input"),
        "synthetic_output_summary": step.get("synthetic_output"),
        "notes": step.get("notes"),
    }


def _rejected_preview(reason: str, details: List[str]) -> Dict[str, Any]:
    preview: Dict[str, Any] = {
        "fixture_id": None,
        "fixture_version": None,
        "validation_status": "unsafe_rejected",
        "validation_summary": reason,
        "safety_summary": FORCED_SAFE_FIELDS,
        "timeline_preview": [],
        "artifact_preview": [],
        "owner_review_required": True,
        "next_owner_review_question": "HOLD: rehearsal preview rejected, awaiting Owner review of the failure reason.",
        "fail_closed_reasons": list(details) or [reason],
        "non_goals": [],
        "labels": list(REQUIRED_OUTPUT_LABELS),
        "accepted": False,
    }
    preview.update(FORCED_SAFE_FIELDS)
    return preview


def build_full_loop_rehearsal_preview_model() -> Dict[str, Any]:
    """從本地 synthetic full-loop fixture 推導 Dashboard 唯讀 Full Loop Rehearsal Preview（純函式，fail-closed）。

    不 mutate 任何狀態、不寫入任何檔案、不連外、不派工、不呼叫 Worker / OpenClaw、不
    啟動 Hermes runtime、不呼叫 connector、不寫 Blackboard / queue / audit trail。若
    fixture 讀取失敗、缺少必要欄位、safety flag 不安全、timeline 缺步驟或順序錯誤、
    或偵測到 raw/secret/webhook/production 內容，回傳 `validation_status=unsafe_rejected`
    的 rejection preview model，不顯示任何原始資料。
    """
    try:
        record = load_full_loop_rehearsal_fixture()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _rejected_preview(f"failed to load fixture: {exc}", [])

    missing_top_level = _missing_top_level_fields(record)
    if missing_top_level:
        return _rejected_preview(
            "missing required top-level fixture fields",
            [f"missing field: {f}" for f in missing_top_level],
        )

    top_level_violations = _unsafe_top_level_flags(record)
    if top_level_violations:
        return _rejected_preview("unsafe top-level fixture flags", top_level_violations)

    safety_flag_violations = _unsafe_global_safety_flags(record.get("safety_flags"))
    if safety_flag_violations:
        return _rejected_preview("unsafe global safety flags", safety_flag_violations)

    timeline_violations = _validate_timeline(record.get("timeline"))
    if timeline_violations:
        return _rejected_preview("unsafe or invalid timeline", timeline_violations)

    forbidden_field_names = _contains_forbidden_field_names(record)
    if forbidden_field_names:
        return _rejected_preview(
            "forbidden field names detected in fixture",
            [f"forbidden field name: {name}" for name in forbidden_field_names],
        )

    if _contains_unsafe_text(record):
        return _rejected_preview("unsafe text content detected in fixture (webhook URL or secret-like value)", [])

    timeline = record.get("timeline", [])
    timeline_preview = [_summarize_step(step) for step in timeline]

    preview: Dict[str, Any] = {
        "fixture_id": record.get("fixture_id"),
        "fixture_version": record.get("fixture_version"),
        "validation_status": "validated_preview",
        "validation_summary": "Fixture validated: all required fields present, all safety flags safe, timeline complete and ordered.",
        "safety_summary": dict(FORCED_SAFE_FIELDS),
        "timeline_preview": timeline_preview,
        "artifact_preview": list(record.get("artifacts", [])),
        "owner_review_required": True,
        "next_owner_review_question": record.get("next_owner_review_question"),
        "fail_closed_reasons": [],
        "non_goals": list(record.get("non_goals", [])),
        "labels": list(REQUIRED_OUTPUT_LABELS),
        "accepted": True,
    }
    preview.update(FORCED_SAFE_FIELDS)
    return preview
