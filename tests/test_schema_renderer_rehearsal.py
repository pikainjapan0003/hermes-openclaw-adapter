"""In-memory renderer rehearsal for all ten Blackboard schemas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.blackboard_validators import SCHEMA_FILES, load_blackboard_schema
from scripts.render_schema_docs_readonly import render_schema_markdown


SCHEMA_DIR = (
    Path(__file__).resolve().parent.parent / "docs" / "schemas" / "blackboard"
)
SAFETY_FLAG_KEYS = {
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
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
    "follow_up_allowed",
    "follow_up_requires_owner_confirmation",
}


@pytest.mark.parametrize("message_type", sorted(SCHEMA_FILES))
def test_renderer_rehearses_required_const_and_safety_contract(
    message_type: str,
) -> None:
    filename = SCHEMA_FILES[message_type]
    schema = load_blackboard_schema(message_type)

    rendered = render_schema_markdown(schema, f"blackboard/{filename}")

    assert f"Source: `blackboard/{filename}`" in rendered
    required = schema["required"]
    properties = schema["properties"]
    for field in required:
        row = next(
            line
            for line in rendered.splitlines()
            if line.startswith(f"| `{field}` |")
        )
        assert " | yes | " in row

    for field, field_schema in properties.items():
        if "const" not in field_schema:
            continue
        encoded = json.dumps(
            field_schema["const"],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        row = next(
            line
            for line in rendered.splitlines()
            if line.startswith(f"| `{field}` |")
        )
        assert f"const={encoded}" in row

    safety_schema = properties["safety_flags"]
    assert set(safety_schema["required"]) == SAFETY_FLAG_KEYS
    assert set(safety_schema["properties"]) == SAFETY_FLAG_KEYS
    assert safety_schema["additionalProperties"] is False
    assert "| `safety_flags` | object | yes |" in rendered


def test_renderer_rehearsal_inventory_is_exactly_ten_schemas() -> None:
    expected_paths = {
        SCHEMA_DIR / filename
        for filename in SCHEMA_FILES.values()
    }

    assert len(SCHEMA_FILES) == 10
    assert all(path.is_file() for path in expected_paths)

