"""Pure Owner approval-packet builder for one harmless N=1 query.

The output is data for offline Owner review.  This module has no filesystem,
queue, network, Worker, OpenClaw, or runtime dependency, and an ``approve``
value never causes an action.
"""

from __future__ import annotations

from typing import Any, Mapping


DECISION_VERBS = ("approve", "edit", "reject", "respond")
N1_QUERY_TIMEOUT_SECONDS = 30

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
_PERMISSION_FLAGS = {
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "result_persistence_permission",
    "audit_trail_write_permission",
}
_RUNTIME_FLAGS = {
    "worker_started",
    "worker_loop_started",
    "task_executed",
    "openclaw_called",
    "hermes_called",
    "google_sheets_enabled",
    "real_queue_db_read",
    "queue_written",
    "post_enabled",
    "secrets_read",
    "webhook_created",
    "endpoint_created",
    "connector_created",
    "production_db_created",
    "remote_blackboard_api_runtime_created",
}


class ApprovalPacketBuildError(ValueError):
    """Raised when source evidence cannot safely form an approval packet."""


def _mapping(message: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = message.get(field)
    if not isinstance(value, Mapping):
        raise ApprovalPacketBuildError(f"{field} must be an object")
    return value


def _text(message: Mapping[str, Any], field: str) -> str:
    value = message.get(field)
    if not isinstance(value, str) or not value:
        raise ApprovalPacketBuildError(f"{field} must be a non-empty string")
    return value


def _require_false_flags(
    message: Mapping[str, Any], field: str, expected_keys: set[str]
) -> None:
    flags = _mapping(message, field)
    if set(flags) != expected_keys or any(
        value is not False for value in flags.values()
    ):
        raise ApprovalPacketBuildError(f"all {field} values must be false")


def build_approval_packet(
    worker_dry_run: Mapping[str, Any],
    result_message: Mapping[str, Any],
    *,
    decision: str = "respond",
    approval_timestamp: str | None = None,
    prev_entry_hash: str | None = None,
) -> dict[str, Any]:
    """Build a closed, deterministic packet from dry-run and result evidence.

    Only the N=1 synthetic, harmless, mock-only query shape is accepted.  The
    returned decision is inert data.  No execution token can be supplied: the
    builder always emits ``None`` for Phase 4.
    """

    if not isinstance(worker_dry_run, Mapping):
        raise ApprovalPacketBuildError("worker_dry_run must be an object")
    if not isinstance(result_message, Mapping):
        raise ApprovalPacketBuildError("result_message must be an object")
    if worker_dry_run.get("message_type") != "worker_dry_run":
        raise ApprovalPacketBuildError("worker_dry_run message_type is required")
    if result_message.get("message_type") != "result_message":
        raise ApprovalPacketBuildError("result_message message_type is required")
    if decision not in DECISION_VERBS:
        raise ApprovalPacketBuildError("decision must be an allowed Phase 4 verb")
    if approval_timestamp is not None and (
        not isinstance(approval_timestamp, str) or not approval_timestamp
    ):
        raise ApprovalPacketBuildError("approval_timestamp must be text or null")
    if prev_entry_hash is not None and (
        not isinstance(prev_entry_hash, str)
        or len(prev_entry_hash) != 64
        or any(character not in "0123456789abcdef" for character in prev_entry_hash)
    ):
        raise ApprovalPacketBuildError(
            "prev_entry_hash must be a lowercase SHA-256 value or null"
        )

    worker_flags = dict(_mapping(worker_dry_run, "safety_flags"))
    result_flags = dict(_mapping(result_message, "safety_flags"))
    if worker_flags != _SAFE_N1_FLAGS or result_flags != _SAFE_N1_FLAGS:
        raise ApprovalPacketBuildError(
            "source safety_flags must match the synthetic N=1 safe profile"
        )

    schema_version = _text(worker_dry_run, "schema_version")
    if result_message.get("schema_version") != schema_version:
        raise ApprovalPacketBuildError("source schema_version values must match")
    if (
        worker_dry_run.get("execution_class") != "AUTO"
        or result_message.get("execution_class") != "AUTO"
    ):
        raise ApprovalPacketBuildError("N=1 harmless query must use AUTO")

    task_id = _text(worker_dry_run, "task_id")
    if result_message.get("task_id") != task_id:
        raise ApprovalPacketBuildError("source task_id values must match")
    dry_run_id = _text(worker_dry_run, "dry_run_id")
    if result_message.get("related_dry_run_id") != dry_run_id:
        raise ApprovalPacketBuildError("result must reference the source dry_run_id")
    if worker_dry_run.get("parent_task_id") != result_message.get("parent_task_id"):
        raise ApprovalPacketBuildError("source parent_task_id values must match")

    if worker_dry_run.get("preview_only") is not True:
        raise ApprovalPacketBuildError("worker dry-run must be preview_only")
    if worker_dry_run.get("dry_run_status") != "preview_only_not_executed":
        raise ApprovalPacketBuildError("worker dry-run must not be executed")
    _require_false_flags(worker_dry_run, "permissions", _PERMISSION_FLAGS)
    _require_false_flags(worker_dry_run, "runtime_state", _RUNTIME_FLAGS)

    if result_message.get("result_status") != "preview_result_not_executed":
        raise ApprovalPacketBuildError("result must be an unexecuted preview")
    if result_message.get("execution_mode") != "mock_only":
        raise ApprovalPacketBuildError("result must be mock_only")
    if result_message.get("external_side_effects") != []:
        raise ApprovalPacketBuildError("N=1 preview must have no external side effects")

    result_id = _text(result_message, "result_id")
    command_id = _text(result_message, "command_id")
    query_action = _text(worker_dry_run, "proposed_worker_action")

    return {
        "schema_version": schema_version,
        "message_type": "approval_packet",
        "created_at": _text(result_message, "created_at"),
        "safety_flags": dict(worker_flags),
        "prev_entry_hash": prev_entry_hash,
        "execution_class": "AUTO",
        "produced_by": "approval-packet-builder",
        "parent_task_id": worker_dry_run.get("parent_task_id"),
        "role": "owner_approval_packet_producer",
        "approval_packet_id": f"approval-{dry_run_id}-{result_id}",
        "task_id": task_id,
        "action_summary": query_action,
        "risk_level": "low",
        "exact_target": {
            "action_type": "n1_harmless_query",
            "task_id": task_id,
            "command_id": command_id,
            "query_action": query_action,
        },
        "expected_side_effects": [],
        "rollback_path": _text(result_message, "rollback_note"),
        "timeout": N1_QUERY_TIMEOUT_SECONDS,
        "dry_run_evidence": {
            "dry_run_id": dry_run_id,
            "result_id": result_id,
            "result_status": "preview_result_not_executed",
            "preview_only": True,
        },
        "audit_trail_preview": {
            "summary": _text(result_message, "audit_note"),
            "persisted": False,
        },
        "approval_timestamp": approval_timestamp,
        "single_use_execution_token": None,
        "decision": decision,
    }


def build_dashboard_approval_packet_preview() -> dict[str, Any]:
    """Return deterministic synthetic packet data for GET-only display."""

    worker_dry_run = {
        "schema_version": "1.0",
        "message_type": "worker_dry_run",
        "created_at": "2026-07-18T10:04:00Z",
        "safety_flags": dict(_SAFE_N1_FLAGS),
        "prev_entry_hash": None,
        "execution_class": "AUTO",
        "produced_by": "worker-dry-run-preview",
        "parent_task_id": None,
        "role": "single_worker_preview",
        "dry_run_id": "dryrun-phase4-dashboard-001",
        "task_id": "task-phase4-dashboard-001",
        "proposed_worker_action": "Query one synthetic adapter status value.",
        "dry_run_status": "preview_only_not_executed",
        "preview_only": True,
        "permissions": {
            "execution_permission": False,
            "dispatch_permission": False,
            "external_side_effects_permission": False,
            "result_persistence_permission": False,
            "audit_trail_write_permission": False,
        },
        "runtime_state": {
            "worker_started": False,
            "worker_loop_started": False,
            "task_executed": False,
            "openclaw_called": False,
            "hermes_called": False,
            "google_sheets_enabled": False,
            "real_queue_db_read": False,
            "queue_written": False,
            "post_enabled": False,
            "secrets_read": False,
            "webhook_created": False,
            "endpoint_created": False,
            "connector_created": False,
            "production_db_created": False,
            "remote_blackboard_api_runtime_created": False,
        },
    }
    result_message = {
        "schema_version": "1.0",
        "message_type": "result_message",
        "created_at": "2026-07-18T10:06:00Z",
        "safety_flags": dict(_SAFE_N1_FLAGS),
        "prev_entry_hash": None,
        "execution_class": "AUTO",
        "produced_by": "adapter-worker-mock",
        "parent_task_id": None,
        "role": "result_reporter",
        "result_id": "result-phase4-dashboard-001",
        "task_id": "task-phase4-dashboard-001",
        "command_id": "cmd-phase4-dashboard-001",
        "related_dry_run_id": "dryrun-phase4-dashboard-001",
        "result_status": "preview_result_not_executed",
        "execution_mode": "mock_only",
        "external_side_effects": [],
        "rollback_note": "No rollback is required because nothing was executed.",
        "audit_note": "Preview only; no audit trail was persisted.",
    }
    return build_approval_packet(worker_dry_run, result_message)
