"""v0.8.1-V read-only Dashboard preview adapter implementation.

v0.8.1-V is read-only Dashboard preview adapter implementation.
v0.8.1-V only converts the v0.8.1-P loader returned in-memory preview object into read-only Dashboard display rows.
v0.8.1-V does not modify Dashboard.
v0.8.1-V does not create Dashboard route.
v0.8.1-V does not create Dashboard endpoint.
v0.8.1-V does not create Dashboard template.
v0.8.1-V does not create Dashboard static asset.
v0.8.1-V does not modify loader.
v0.8.1-V does not read fixture JSON directly.
v0.8.1-V does not read real queue DB.
v0.8.1-V does not write queue data.
v0.8.1-V does not send POST.
v0.8.1-V does not make network calls.
v0.8.1-V does not start Worker.
v0.8.1-V does not call OpenClaw.
v0.8.1-V does not activate Hermes.
v0.8.1-V does not read Google Sheets.
v0.8.1-V does not write Google Sheets.
v0.8.1-V does not read secrets.
v0.8.1-V does not create .env.
v0.8.1-V does not create webhook.
v0.8.1-V does not create connector.
v0.8.1-V does not create production DB.
v0.8.1-V does not create shared DB.
v0.8.1-V does not create Remote Blackboard API runtime.
v0.8.1-V does not commit.
v0.8.1-V does not push.
v0.8.1-V does not tag.

This adapter reads no file itself. It calls load_local_mock_fixture_preview(), which internally reads
and validates the synthetic local-only fixture JSON, and treats the returned in-memory preview object
as immutable input display data. The adapter never mutates, persists, or dispatches any record, never
calls an external tool, and never exposes an execution or dispatch control. Every row and the overall
model always carry local_only = True, read_only = True, and all permission flags False, together with
the disabled runtime badges (DISPATCH OFF, WORKER OFF, OPENCLAW NOT CONNECTED, HERMES NOT CONNECTED,
GOOGLE SHEETS DISABLED).
"""
from __future__ import annotations

import copy
from typing import Any

from load_local_mock_fixture_preview_v0_8_1 import (
    load_local_mock_fixture_preview,
    validate_local_mock_fixture_preview_object,
)

SOURCE = "local_mock_fixture_dashboard_preview_adapter"
SCHEMA_VERSION = "v0.8.1-dashboard-preview-adapter-1"
ADAPTER_VERSION = "v0.8.1-V"
EXPECTED_ROW_COUNT = 6

RUNTIME_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]


def _row_fallback(display_index: int) -> dict[str, str]:
    """Safe fallback values for a display row when a record field is missing."""
    return {
        "row_id": f"mock-row-{display_index:03d}",
        "display_title": f"Local mock preview row {display_index}",
        "display_summary": "Synthetic local-only read-only preview row.",
        "source_role": "Hermes",
        "target_role": "OpenClaw",
        "status": "preview_only",
        "created_at": "",
    }


def _build_row(record: dict[str, Any], zero_based_index: int) -> dict[str, Any]:
    """Convert one loader-returned record into a read-only display row.

    The record is treated as immutable input display data: it is deep-copied before any field is
    read, and only display-safe scalar fields are copied out into the new row dict. Missing fields
    fall back to safe synthetic placeholder values; no field name mismatch is treated as an error.
    """
    safe_record = copy.deepcopy(record) if isinstance(record, dict) else {}
    display_index = zero_based_index + 1
    fallback = _row_fallback(display_index)

    row_id = safe_record.get("message_id") or safe_record.get("preview_id") or fallback["row_id"]
    display_title = safe_record.get("display_title") or fallback["display_title"]
    display_summary = safe_record.get("display_summary") or fallback["display_summary"]
    source_role = safe_record.get("source_role") or fallback["source_role"]
    target_role = safe_record.get("target_role") or fallback["target_role"]
    status = safe_record.get("status") or fallback["status"]
    created_at = safe_record.get("created_at") or fallback["created_at"]

    return {
        "row_id": str(row_id),
        "display_index": display_index,
        "display_title": str(display_title),
        "display_summary": str(display_summary),
        "source_role": str(source_role),
        "target_role": str(target_role),
        "status": str(status),
        "created_at": str(created_at),
        "local_only": True,
        "read_only": True,
        "execution_permission": False,
        "dispatch_permission": False,
        "external_side_effects_permission": False,
        "runtime_badges": list(RUNTIME_BADGES),
    }


def build_dashboard_preview_rows() -> list[dict[str, Any]]:
    """Return a new list of read-only display rows built from the loader's in-memory preview object.

    Calls load_local_mock_fixture_preview() and validate_local_mock_fixture_preview_object() from the
    v0.8.1-P loader. The returned list and every row dict are newly constructed objects; the original
    records list returned by the loader is never returned or aliased.
    """
    preview = load_local_mock_fixture_preview()
    validate_local_mock_fixture_preview_object(preview)

    records = preview["records"]
    rows: list[dict[str, Any]] = []
    for zero_based_index, record in enumerate(records):
        rows.append(_build_row(record, zero_based_index))
    return rows


def build_dashboard_preview_model() -> dict[str, Any]:
    """Return the full read-only Dashboard preview model, including rows and safety metadata."""
    rows = build_dashboard_preview_rows()
    return {
        "source": SOURCE,
        "schema_version": SCHEMA_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "is_mock": True,
        "local_only": True,
        "read_only": True,
        "execution_permission": False,
        "dispatch_permission": False,
        "external_side_effects_permission": False,
        "runtime_badges": list(RUNTIME_BADGES),
        "rows": rows,
        "row_count": len(rows),
        "controls": {
            "execution_controls_visible": False,
            "dispatch_controls_visible": False,
            "external_actions_visible": False,
        },
    }


def validate_dashboard_preview_model(model: dict[str, Any]) -> None:
    """Validate the shape and safety flags of a preview model; raise ValueError on any mismatch.

    This is an in-memory check only. It performs no I/O, no network access, and no fixture read.
    """
    if not isinstance(model, dict):
        raise ValueError("model must be a dict")

    if model.get("source") != SOURCE:
        raise ValueError(f"model.source must be {SOURCE!r}")
    if model.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"model.schema_version must be {SCHEMA_VERSION!r}")
    if model.get("adapter_version") != ADAPTER_VERSION:
        raise ValueError(f"model.adapter_version must be {ADAPTER_VERSION!r}")
    if model.get("is_mock") is not True:
        raise ValueError("model.is_mock must be True")
    if model.get("local_only") is not True:
        raise ValueError("model.local_only must be True")
    if model.get("read_only") is not True:
        raise ValueError("model.read_only must be True")
    if model.get("execution_permission") is not False:
        raise ValueError("model.execution_permission must be False")
    if model.get("dispatch_permission") is not False:
        raise ValueError("model.dispatch_permission must be False")
    if model.get("external_side_effects_permission") is not False:
        raise ValueError("model.external_side_effects_permission must be False")
    if model.get("runtime_badges") != list(RUNTIME_BADGES):
        raise ValueError("model.runtime_badges must match the disabled-runtime badge list")

    rows = model.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"model.rows must be a list of {EXPECTED_ROW_COUNT} items")
    if model.get("row_count") != EXPECTED_ROW_COUNT:
        raise ValueError(f"model.row_count must be {EXPECTED_ROW_COUNT}")

    controls = model.get("controls")
    if not isinstance(controls, dict):
        raise ValueError("model.controls must be a dict")
    if controls.get("execution_controls_visible") is not False:
        raise ValueError("model.controls.execution_controls_visible must be False")
    if controls.get("dispatch_controls_visible") is not False:
        raise ValueError("model.controls.dispatch_controls_visible must be False")
    if controls.get("external_actions_visible") is not False:
        raise ValueError("model.controls.external_actions_visible must be False")

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each row must be a dict")
        if row.get("local_only") is not True:
            raise ValueError("row.local_only must be True")
        if row.get("read_only") is not True:
            raise ValueError("row.read_only must be True")
        if row.get("execution_permission") is not False:
            raise ValueError("row.execution_permission must be False")
        if row.get("dispatch_permission") is not False:
            raise ValueError("row.dispatch_permission must be False")
        if row.get("external_side_effects_permission") is not False:
            raise ValueError("row.external_side_effects_permission must be False")
        if row.get("runtime_badges") != list(RUNTIME_BADGES):
            raise ValueError("row.runtime_badges must match the disabled-runtime badge list")
