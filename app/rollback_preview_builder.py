"""Pure Phase 7 rollback-preview builder for one harmless N=1 rehearsal."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.evidence_bundle_builder import verify_bundle_hash


_SAFE_N1_FLAGS: dict[str, bool] = {
    "synthetic_local_only": True,
    "mock_only": True,
    "dry_run": True,
    "owner_review_required": True,
    "external_side_effects_allowed": False,
    "external_side_effects_occurred": False,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "hermes_runtime_allowed": False,
    "connector_call_allowed": False,
    "google_sheets_write_allowed": False,
    "follow_up_allowed": False,
    "follow_up_requires_owner_confirmation": True,
}
_FALSE_MOCK_RESULT_FLAGS = (
    "external_side_effects_performed",
    "worker_dispatched",
    "real_openclaw_called",
    "queue_written",
    "audit_trail_written",
)
_ROLLBACK_NOTE = "No rollback is needed because no execution or side effect occurred."


class RollbackPreviewBuildError(ValueError):
    """Raised when the three source contracts cannot form a safe preview."""


def _mapping(record: Mapping[str, Any], field: str, owner: str) -> Mapping[str, Any]:
    value = record.get(field)
    if not isinstance(value, Mapping):
        raise RollbackPreviewBuildError(f"{owner}.{field} must be an object")
    return value


def _text(record: Mapping[str, Any], field: str, owner: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise RollbackPreviewBuildError(f"{owner}.{field} must be non-empty text")
    return value


def _parent_task_id(record: Mapping[str, Any], owner: str) -> str | None:
    value = record.get("parent_task_id")
    if value is not None and (not isinstance(value, str) or not value):
        raise RollbackPreviewBuildError(
            f"{owner}.parent_task_id must be non-empty text or null"
        )
    return value


def build_rollback_preview(
    audit_event: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    result_message: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic descriptive rollback data without any side effect."""

    if not isinstance(audit_event, Mapping):
        raise RollbackPreviewBuildError("audit_event must be an object")
    if not isinstance(evidence_bundle, Mapping):
        raise RollbackPreviewBuildError("evidence_bundle must be an object")
    if not isinstance(result_message, Mapping):
        raise RollbackPreviewBuildError("result_message must be an object")

    if audit_event.get("message_type") != "audit_event":
        raise RollbackPreviewBuildError("audit_event message_type is required")
    if evidence_bundle.get("bundle_type") != "n1_dry_run_evidence":
        raise RollbackPreviewBuildError("evidence_bundle bundle_type is required")
    if result_message.get("message_type") != "result_message":
        raise RollbackPreviewBuildError("result_message message_type is required")

    if audit_event.get("preview_only") is not True:
        raise RollbackPreviewBuildError("audit_event must be preview_only")
    if audit_event.get("audit_status") != "preview_audit_not_persisted":
        raise RollbackPreviewBuildError("audit_event audit_status must be preview")
    if audit_event.get("persistence_target") != "none":
        raise RollbackPreviewBuildError("audit_event persistence_target must be none")
    if not verify_bundle_hash(evidence_bundle):
        raise RollbackPreviewBuildError("evidence_bundle hash verification failed")

    bundle_task = _mapping(evidence_bundle, "task", "evidence_bundle")
    mock_result = _mapping(evidence_bundle, "mock_result", "evidence_bundle")
    if evidence_bundle.get("expected_side_effects") != []:
        raise RollbackPreviewBuildError(
            "evidence_bundle.expected_side_effects must be empty"
        )
    for field in _FALSE_MOCK_RESULT_FLAGS:
        if mock_result.get(field) is not False:
            raise RollbackPreviewBuildError(
                f"evidence_bundle.mock_result.{field} must be false"
            )

    if result_message.get("result_status") != "preview_result_not_executed":
        raise RollbackPreviewBuildError("result_message result_status must be preview")
    if result_message.get("execution_mode") != "mock_only":
        raise RollbackPreviewBuildError("result_message execution_mode must be mock_only")
    if result_message.get("external_side_effects") != []:
        raise RollbackPreviewBuildError(
            "result_message.external_side_effects must be empty"
        )

    audit_flags = dict(_mapping(audit_event, "safety_flags", "audit_event"))
    result_flags = dict(_mapping(result_message, "safety_flags", "result_message"))
    if audit_flags != _SAFE_N1_FLAGS or result_flags != _SAFE_N1_FLAGS:
        raise RollbackPreviewBuildError(
            "source safety_flags must match the canonical 16-key safe profile"
        )
    if audit_flags != result_flags:
        raise RollbackPreviewBuildError("source safety_flags must match")

    schema_version = _text(audit_event, "schema_version", "audit_event")
    if result_message.get("schema_version") != schema_version:
        raise RollbackPreviewBuildError("source schema_version values must match")

    if (
        audit_event.get("execution_class") != "AUTO"
        or result_message.get("execution_class") != "AUTO"
        or bundle_task.get("execution_class") != "AUTO"
    ):
        raise RollbackPreviewBuildError("all source execution_class values must be AUTO")

    parent_task_id = _parent_task_id(audit_event, "audit_event")
    if _parent_task_id(result_message, "result_message") != parent_task_id:
        raise RollbackPreviewBuildError("source parent_task_id values must match")

    task_id = _text(audit_event, "task_id", "audit_event")
    if result_message.get("task_id") != task_id or bundle_task.get("task_id") != task_id:
        raise RollbackPreviewBuildError("source task_id values must match")

    related_result_id = _text(audit_event, "related_result_id", "audit_event")
    if result_message.get("result_id") != related_result_id:
        raise RollbackPreviewBuildError("source result_id values must match")

    source_audit_id = _text(audit_event, "audit_id", "audit_event")
    created_at = _text(audit_event, "created_at", "audit_event")

    return {
        "schema_version": schema_version,
        "message_type": "rollback_event",
        "created_at": created_at,
        "safety_flags": dict(audit_flags),
        "prev_entry_hash": None,
        "execution_class": "AUTO",
        "produced_by": "rollback-preview-builder",
        "parent_task_id": parent_task_id,
        "role": "rollback_reviewer",
        "rollback_id": f"rollback-{source_audit_id}-{related_result_id}",
        "task_id": task_id,
        "related_result_id": related_result_id,
        "source_audit_id": source_audit_id,
        "rollback_status": "NOT_REQUIRED",
        "rollback_required": False,
        "preview_only": True,
        "rollback_note": _ROLLBACK_NOTE,
        "rollback_path": None,
        "reason": (
            f"Audit {source_audit_id} recorded a preview-only result "
            "with no external side effects."
        ),
    }
