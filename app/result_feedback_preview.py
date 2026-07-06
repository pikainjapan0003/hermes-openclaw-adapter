"""v0.9.6-D — Result Feedback Preview（純函式、local-only、mock-only、read-only）。

從一份本地 synthetic fixture 檔案（`fixtures/local_mock_data/
hermes_result_feedback_preview_v0_9_6_d.json`）讀取資料，驗證必要欄位與安全旗標，
推導出一份 Dashboard 唯讀 Result Feedback Preview view model。本模組不實作 callback
receiver、不開 webhook、不新增 route/endpoint、不讀取真實 external callback、不寫
Blackboard、不寫 queue、不寫 audit trail、不觸發 follow-up task、不呼叫 Worker、不
呼叫 OpenClaw、不啟動 Hermes runtime。

Result Feedback Display Plan is not display implementation trigger for execution.
Result Feedback Preview is read-only. Result Feedback Preview is not execution
permission. Result message is not next dispatch permission. Result status is not
real execution success without validation. Owner review required is not Owner
approval. Hermes readback is advisory only.

純 helper 邊界：
  - 只讀取本地 synthetic fixture 檔案；不 mutate 該檔案、不寫入任何檔案。
  - 不 import app.main、不 import Hermes runtime、不 import Worker runtime、不
    import OpenClaw runtime、不 import connector runtime、不 import network client。
  - 不做 network call、不讀 secrets、不讀 connector data。
  - 不觸碰 real queue DB、不寫 audit trail、不寫 Blackboard。
  - 僅用標準庫（json / pathlib / typing）。

公開 API：
  load_result_feedback_preview_fixture() -> dict
  build_result_feedback_preview_view_model() -> dict
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "local_mock_data"
    / "hermes_result_feedback_preview_v0_9_6_d.json"
)

REQUIRED_FIXTURE_FIELDS = (
    "callback_id",
    "task_id",
    "command_id",
    "result_type",
    "result_status",
    "execution_mode",
    "started_at",
    "completed_at",
    "summary",
    "output_preview",
    "error_summary",
    "validation_status",
    "rollback_note",
    "audit_note",
)

# Safety flags that must be exactly True for the fixture to be treated as a
# trustworthy synthetic preview record.
REQUIRED_TRUE_SAFETY_FLAGS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "follow_up_requires_owner_confirmation",
)

# Safety flags that must be exactly False for the fixture to be treated as a
# trustworthy synthetic preview record.
REQUIRED_FALSE_SAFETY_FLAGS = (
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "follow_up_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
)

# Fields never trusted from the fixture record — this helper always forces them
# itself on both accepted and rejected view models.
FORCED_SAFE_FIELDS: Dict[str, bool] = {flag: True for flag in REQUIRED_TRUE_SAFETY_FLAGS}
FORCED_SAFE_FIELDS.update({flag: False for flag in REQUIRED_FALSE_SAFETY_FLAGS})

SAFETY_FLAG_ORDER = REQUIRED_TRUE_SAFETY_FLAGS + REQUIRED_FALSE_SAFETY_FLAGS


def load_result_feedback_preview_fixture() -> Dict[str, Any]:
    """讀取本地 synthetic fixture（純讀取，不寫入、不連外、不讀 secrets）。"""
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("fixture root must be a JSON object")
    return data


def _missing_required_fixture_fields(record: Mapping[str, Any]) -> List[str]:
    return [field for field in REQUIRED_FIXTURE_FIELDS if field not in record]


def _unsafe_fixture_flag_violations(record: Mapping[str, Any]) -> List[str]:
    violations: List[str] = []
    for flag in REQUIRED_TRUE_SAFETY_FLAGS:
        if record.get(flag) is not True:
            violations.append(f"{flag} must be true")
    for flag in REQUIRED_FALSE_SAFETY_FLAGS:
        if record.get(flag) is not False:
            violations.append(f"{flag} must be false")
    return violations


def _safety_flags_summary(record: Mapping[str, Any]) -> List[str]:
    return [f"{flag}={FORCED_SAFE_FIELDS[flag]}" for flag in SAFETY_FLAG_ORDER]


def _rejected_view(reason: str, details: List[str]) -> Dict[str, Any]:
    view: Dict[str, Any] = {field: None for field in REQUIRED_FIXTURE_FIELDS}
    view["accepted"] = False
    view["rejection_reason"] = reason
    view["rejection_details"] = list(details)
    view["preview_only"] = True
    view["safety_flags"] = [f"{flag}={value}" for flag, value in FORCED_SAFE_FIELDS.items()]
    view.update(FORCED_SAFE_FIELDS)
    return view


def build_result_feedback_preview_view_model() -> Dict[str, Any]:
    """從本地 synthetic fixture 推導 Dashboard 唯讀 Result Feedback Preview（純函式，fail-closed）。

    不 mutate 任何狀態、不寫入任何檔案、不連外、不派工、不呼叫 Worker / OpenClaw、不
    啟動 Hermes runtime、不寫 Blackboard / queue / audit trail。若 fixture 讀取失敗、
    缺少必要欄位、或安全旗標不符合強制安全值，回傳 `accepted=False` 的 rejection view
    model，不顯示任何欄位資料。

    十六個安全欄位（synthetic_local_only / mock_only / dry_run /
    external_side_effects_allowed / external_side_effects_occurred /
    owner_review_required / follow_up_allowed /
    follow_up_requires_owner_confirmation / worker_dispatch_allowed /
    openclaw_call_allowed / hermes_runtime_allowed / connector_call_allowed /
    google_sheets_write_allowed / blackboard_write_allowed / queue_write_allowed /
    audit_trail_write_allowed）恆由本模組強制設定為安全值，不論 fixture 是否嘗試覆寫。
    """
    try:
        record = load_result_feedback_preview_fixture()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _rejected_view(f"failed to load fixture: {exc}", [])

    missing = _missing_required_fixture_fields(record)
    if missing:
        return _rejected_view(
            "missing required fixture fields",
            [f"missing field: {field}" for field in missing],
        )

    violations = _unsafe_fixture_flag_violations(record)
    if violations:
        return _rejected_view("unsafe fixture safety flags", violations)

    view: Dict[str, Any] = {field: record.get(field) for field in REQUIRED_FIXTURE_FIELDS}
    view["accepted"] = True
    view["rejection_reason"] = None
    view["rejection_details"] = []
    view["preview_only"] = True
    view["safety_flags"] = _safety_flags_summary(record)
    view.update(FORCED_SAFE_FIELDS)
    return view
