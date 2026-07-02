"""Standalone, read-only builder for the v0.8.3-B Worker dry-run preview model.

This module is a synthetic local-only boundary artifact. It reads a fixed JSON fixture,
validates that all permission and runtime-state flags remain false, and returns a plain
read-only dict. It starts nothing, runs nothing, and reaches no network or external system.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "local_mock_data"
    / "hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json"
)

REQUIRED_SOURCE = "synthetic_local_only"
REQUIRED_DRY_RUN_STATUS = "preview_only_not_executed"

PERMISSION_KEYS = (
    "execution_permission",
    "dispatch_permission",
    "external_side_effects_permission",
)

RUNTIME_STATE_KEYS = (
    "worker_started",
    "worker_loop_started",
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

REVIEW_NOTICE = (
    "This is a synthetic local-only preview only. Owner Review is required before any future "
    "round may change any permission or runtime-state flag away from false."
)


def _load_fixture(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("source") != REQUIRED_SOURCE:
        raise ValueError(f"fixture 'source' must be {REQUIRED_SOURCE!r}")
    if fixture.get("dry_run_status") != REQUIRED_DRY_RUN_STATUS:
        raise ValueError(f"fixture 'dry_run_status' must be {REQUIRED_DRY_RUN_STATUS!r}")
    if fixture.get("owner_review_required") is not True:
        raise ValueError("fixture 'owner_review_required' must be true")
    for key in PERMISSION_KEYS:
        if fixture.get(key) is not False:
            raise ValueError(f"fixture permission flag {key!r} must be false")
    for key in RUNTIME_STATE_KEYS:
        if fixture.get(key) is not False:
            raise ValueError(f"fixture runtime-state flag {key!r} must be false")
    for key in FORBIDDEN_CONTROL_URL_KEYS:
        if key in fixture:
            raise ValueError(f"fixture must not contain forbidden control key {key!r}")


def build_worker_dry_run_preview_model(input_path: Path | None = None) -> dict[str, Any]:
    path = input_path or DEFAULT_FIXTURE_PATH
    fixture = _load_fixture(path)
    _validate_fixture(fixture)

    permissions = {key: fixture[key] for key in PERMISSION_KEYS}
    runtime_state = {key: fixture[key] for key in RUNTIME_STATE_KEYS}

    model: dict[str, Any] = {
        "schema_version": fixture["schema_version"],
        "dry_run_id": fixture["dry_run_id"],
        "source": fixture["source"],
        "task_title": fixture["task_title"],
        "task_summary": fixture["task_summary"],
        "source_role": fixture["source_role"],
        "target_role": fixture["target_role"],
        "proposed_worker_action": fixture["proposed_worker_action"],
        "dry_run_status": fixture["dry_run_status"],
        "owner_review_required": fixture["owner_review_required"],
        "permissions": permissions,
        "runtime_state": runtime_state,
        "boundary_summary": (
            "Synthetic local-only preview. No Worker, OpenClaw, Hermes, Google Sheets, or real "
            "queue involvement. All permission and runtime-state flags are false."
        ),
        "review_notice": REVIEW_NOTICE,
    }
    return model


if __name__ == "__main__":
    preview_model = build_worker_dry_run_preview_model()
    print(json.dumps(preview_model, indent=2, ensure_ascii=False))
