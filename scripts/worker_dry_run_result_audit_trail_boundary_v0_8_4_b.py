"""Standalone, read-only builder for the v0.8.4-B Worker dry-run result / audit trail model.

This module is a synthetic local-only boundary artifact. It reads a fixed JSON fixture,
validates that all permission and runtime-state flags remain false, and returns a plain
read-only dict describing a dry-run result, an audit trail record, an owner review event,
and a readback summary. It starts nothing, runs nothing, and reaches no network or external
system.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "local_mock_data"
    / "hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json"
)

REQUIRED_VERSION = "v0.8.4-B"
REQUIRED_SOURCE = "synthetic_local_only"
REQUIRED_RESULT_STATUS = "preview_result_not_executed"
REQUIRED_AUDIT_STATUS = "preview_audit_not_persisted"
REQUIRED_REVIEW_STATUS = "owner_review_required"
REQUIRED_SUMMARY_STATUS = "preview_readback_only"

PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
    "result_persistence_permission",
    "audit_trail_write_permission",
)

RUNTIME_STATE_KEYS = (
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
)

FORBIDDEN_CONTROL_URL_KEYS = (
    "action_url",
    "post_url",
    "webhook_url",
    "endpoint_url",
    "execute_url",
    "dispatch_url",
    "send_url",
)

BOUNDARY_SUMMARY = (
    "Synthetic local-only Worker dry-run result / audit trail / owner review event / "
    "readback summary preview. No Worker, Worker loop, OpenClaw, Hermes, Google Sheets, "
    "real queue DB, POST, execution, dispatch, secrets, webhook, endpoint, connector, or "
    "production/shared DB is used. All permission and runtime-state flags are false."
)


def _load_fixture(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("version") != REQUIRED_VERSION:
        raise ValueError(f"fixture 'version' must be {REQUIRED_VERSION!r}")
    if fixture.get("source") != REQUIRED_SOURCE:
        raise ValueError(f"fixture 'source' must be {REQUIRED_SOURCE!r}")
    if fixture.get("preview_only") is not True:
        raise ValueError("fixture 'preview_only' must be true")

    dry_run_result = fixture.get("dry_run_result")
    if not isinstance(dry_run_result, dict):
        raise ValueError("fixture 'dry_run_result' must be an object")
    if dry_run_result.get("result_status") != REQUIRED_RESULT_STATUS:
        raise ValueError(f"fixture 'dry_run_result.result_status' must be {REQUIRED_RESULT_STATUS!r}")
    if dry_run_result.get("execution_result") is not None:
        raise ValueError("fixture 'dry_run_result.execution_result' must be null")
    if dry_run_result.get("external_side_effects") != []:
        raise ValueError("fixture 'dry_run_result.external_side_effects' must be an empty list")
    if dry_run_result.get("owner_review_required") is not True:
        raise ValueError("fixture 'dry_run_result.owner_review_required' must be true")

    audit_trail_record = fixture.get("audit_trail_record")
    if not isinstance(audit_trail_record, dict):
        raise ValueError("fixture 'audit_trail_record' must be an object")
    if audit_trail_record.get("audit_status") != REQUIRED_AUDIT_STATUS:
        raise ValueError(f"fixture 'audit_trail_record.audit_status' must be {REQUIRED_AUDIT_STATUS!r}")
    if audit_trail_record.get("persistence_target") != "none":
        raise ValueError("fixture 'audit_trail_record.persistence_target' must be 'none'")
    if audit_trail_record.get("owner_review_required") is not True:
        raise ValueError("fixture 'audit_trail_record.owner_review_required' must be true")

    owner_review_event = fixture.get("owner_review_event")
    if not isinstance(owner_review_event, dict):
        raise ValueError("fixture 'owner_review_event' must be an object")
    if owner_review_event.get("review_status") != REQUIRED_REVIEW_STATUS:
        raise ValueError(f"fixture 'owner_review_event.review_status' must be {REQUIRED_REVIEW_STATUS!r}")
    if owner_review_event.get("review_action_available") is not False:
        raise ValueError("fixture 'owner_review_event.review_action_available' must be false")

    readback_summary = fixture.get("readback_summary")
    if not isinstance(readback_summary, dict):
        raise ValueError("fixture 'readback_summary' must be an object")
    if readback_summary.get("summary_status") != REQUIRED_SUMMARY_STATUS:
        raise ValueError(f"fixture 'readback_summary.summary_status' must be {REQUIRED_SUMMARY_STATUS!r}")

    permissions = fixture.get("permissions")
    if not isinstance(permissions, dict):
        raise ValueError("fixture 'permissions' must be an object")
    for key in PERMISSION_KEYS:
        if permissions.get(key) is not False:
            raise ValueError(f"fixture permission flag {key!r} must be false")

    runtime_state = fixture.get("runtime_state")
    if not isinstance(runtime_state, dict):
        raise ValueError("fixture 'runtime_state' must be an object")
    for key in RUNTIME_STATE_KEYS:
        if runtime_state.get(key) is not False:
            raise ValueError(f"fixture runtime-state flag {key!r} must be false")

    flat_text_scan = json.dumps(fixture)
    for key in FORBIDDEN_CONTROL_URL_KEYS:
        if key in flat_text_scan:
            raise ValueError(f"fixture must not contain forbidden control key {key!r}")


def build_worker_dry_run_result_audit_trail_model(input_path: Path | None = None) -> dict[str, Any]:
    path = input_path or DEFAULT_FIXTURE_PATH
    fixture = _load_fixture(path)
    _validate_fixture(fixture)

    permissions = {key: fixture["permissions"][key] for key in PERMISSION_KEYS}
    runtime_state = {key: fixture["runtime_state"][key] for key in RUNTIME_STATE_KEYS}

    model: dict[str, Any] = {
        "version": fixture["version"],
        "source": fixture["source"],
        "preview_only": fixture["preview_only"],
        "dry_run_result": dict(fixture["dry_run_result"]),
        "audit_trail_record": dict(fixture["audit_trail_record"]),
        "owner_review_event": dict(fixture["owner_review_event"]),
        "readback_summary": dict(fixture["readback_summary"]),
        "permissions": permissions,
        "runtime_state": runtime_state,
        "boundary_summary": BOUNDARY_SUMMARY,
    }
    return model


def validate_worker_dry_run_result_audit_trail_model(model: dict[str, Any]) -> None:
    if model.get("source") != REQUIRED_SOURCE:
        raise ValueError(f"model 'source' must be {REQUIRED_SOURCE!r}")
    if model.get("preview_only") is not True:
        raise ValueError("model 'preview_only' must be true")
    if model.get("dry_run_result", {}).get("result_status") != REQUIRED_RESULT_STATUS:
        raise ValueError(f"model 'dry_run_result.result_status' must be {REQUIRED_RESULT_STATUS!r}")
    if model.get("audit_trail_record", {}).get("audit_status") != REQUIRED_AUDIT_STATUS:
        raise ValueError(f"model 'audit_trail_record.audit_status' must be {REQUIRED_AUDIT_STATUS!r}")
    if model.get("owner_review_event", {}).get("review_status") != REQUIRED_REVIEW_STATUS:
        raise ValueError(f"model 'owner_review_event.review_status' must be {REQUIRED_REVIEW_STATUS!r}")
    if model.get("readback_summary", {}).get("summary_status") != REQUIRED_SUMMARY_STATUS:
        raise ValueError(f"model 'readback_summary.summary_status' must be {REQUIRED_SUMMARY_STATUS!r}")

    permissions = model.get("permissions", {})
    if not isinstance(permissions, dict) or any(permissions.get(key) is not False for key in PERMISSION_KEYS):
        raise ValueError("all model permission flags must be false")

    runtime_state = model.get("runtime_state", {})
    if not isinstance(runtime_state, dict) or any(runtime_state.get(key) is not False for key in RUNTIME_STATE_KEYS):
        raise ValueError("all model runtime-state flags must be false")


if __name__ == "__main__":
    result_audit_model = build_worker_dry_run_result_audit_trail_model()
    validate_worker_dry_run_result_audit_trail_model(result_audit_model)
    print(json.dumps(result_audit_model, indent=2, ensure_ascii=False))
