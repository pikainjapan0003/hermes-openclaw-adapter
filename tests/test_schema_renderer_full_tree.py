"""Full repository rehearsal for the read-only JSON Schema renderer."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scripts.render_schema_docs_readonly import (
    render_schema_markdown,
    render_schema_tree,
)


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_ROOT = ROOT / "docs" / "schemas"
SCHEMA_PATHS = tuple(sorted(SCHEMA_ROOT.rglob("*.json")))


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _row(rendered: str, field: str) -> str:
    prefix = f"| `{field}` |"
    rows = [line for line in rendered.splitlines() if line.startswith(prefix)]
    assert len(rows) == 1
    return rows[0]


def test_renderer_covers_the_complete_15_schema_inventory_in_memory() -> None:
    assert len(SCHEMA_PATHS) == 15
    relative_paths = {
        path.relative_to(SCHEMA_ROOT).as_posix() for path in SCHEMA_PATHS
    }
    assert "evidence_bundle.json" in relative_paths
    assert "three_source_report.schema.json" in relative_paths
    assert len(
        [path for path in relative_paths if path.startswith("blackboard/")]
    ) == 10

    rendered = render_schema_tree(SCHEMA_ROOT)
    for relative_path in relative_paths:
        assert f"Source: `{relative_path}`" in rendered


def test_each_schema_renders_required_const_enum_and_object_closure() -> None:
    for path in SCHEMA_PATHS:
        schema = _load(path)
        relative_path = path.relative_to(SCHEMA_ROOT).as_posix()
        rendered = render_schema_markdown(schema, relative_path)
        properties = schema.get("properties", {})
        assert isinstance(properties, Mapping)
        required = set(schema.get("required", []))

        for field, definition in properties.items():
            assert isinstance(definition, Mapping)
            row = _row(rendered, str(field))
            expected_required = "yes" if field in required else "no"
            assert f"| {expected_required} |" in row
            if "const" in definition:
                const_text = json.dumps(
                    definition["const"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                assert f"const={const_text}" in row
            if "enum" in definition:
                enum_text = json.dumps(
                    definition["enum"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                assert f"enum={enum_text}" in row

        expected_closed = (
            "Closed object: yes"
            if schema.get("additionalProperties") is False
            else "Closed object: no/unspecified"
        )
        assert expected_closed in rendered
