"""Guard the renderer's explicit root conditional-rule presentation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.render_schema_docs_readonly import render_schema_markdown


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "docs" / "schemas"
pytestmark = pytest.mark.contract


def _schemas_with_root_conditionals() -> list[Path]:
    return sorted(
        path
        for path in SCHEMA_ROOT.rglob("*.json")
        if isinstance(json.loads(path.read_text(encoding="utf-8")), dict)
        and (
            isinstance(json.loads(path.read_text(encoding="utf-8")).get("allOf"), list)
            or isinstance(json.loads(path.read_text(encoding="utf-8")).get("if"), dict)
        )
    )


def _render(path: Path) -> str:
    schema = json.loads(path.read_text(encoding="utf-8"))
    return render_schema_markdown(schema, path.relative_to(SCHEMA_ROOT).as_posix())


def test_every_root_conditional_schema_is_rendered() -> None:
    paths = _schemas_with_root_conditionals()

    assert paths == [SCHEMA_ROOT / "remote_readonly_projection.schema.json"]
    rendered = _render(paths[0])
    assert "### Conditional rules" in rendered
    assert 'if status == "decided" then phase == "owner_decided"' in rendered
    assert 'otherwise phase != "owner_decided"' in rendered


def test_schemas_without_root_conditionals_do_not_invent_a_section() -> None:
    conditional_paths = set(_schemas_with_root_conditionals())
    ordinary_paths = sorted(
        path for path in SCHEMA_ROOT.rglob("*.json") if path not in conditional_paths
    )

    assert ordinary_paths
    for path in ordinary_paths:
        assert "### Conditional rules" not in _render(path), path
