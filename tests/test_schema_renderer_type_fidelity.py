"""Lock the renderer to the actual JSON Schema type semantics."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from scripts.render_schema_docs_readonly import (
    render_schema_markdown,
    render_schema_tree,
)


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_ROOT = ROOT / "docs" / "schemas"
pytestmark = pytest.mark.contract


def _json_type(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, Mapping):
        return "object"
    raise AssertionError(f"unsupported JSON value in test oracle: {type(value)!r}")


def _semantic_type(schema: Mapping[str, Any]) -> str:
    declared = schema.get("type")
    if isinstance(declared, str):
        return declared
    if isinstance(declared, list):
        return " | ".join(str(value) for value in declared)
    if "const" in schema:
        return _json_type(schema["const"])
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return " | ".join(dict.fromkeys(_json_type(value) for value in enum))
    for keyword, separator in (("oneOf", " | "), ("anyOf", " | "), ("allOf", " & ")):
        branches = schema.get(keyword)
        if isinstance(branches, list) and branches:
            types = [
                _semantic_type(branch)
                for branch in branches
                if isinstance(branch, Mapping)
            ]
            types = list(dict.fromkeys(types))
            if types:
                return separator.join(types)
    return "unspecified"


def test_every_repository_schema_field_has_a_faithful_rendered_type() -> None:
    paths = tuple(sorted(SCHEMA_ROOT.rglob("*.json")))
    assert len(paths) == 15

    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(schema, dict)
        properties = schema.get("properties", {})
        assert isinstance(properties, Mapping)
        rendered = render_schema_markdown(
            schema,
            path.relative_to(SCHEMA_ROOT).as_posix(),
        )
        for field, definition in properties.items():
            assert isinstance(definition, Mapping)
            expected = _semantic_type(definition)
            assert expected != "unspecified", f"{path}:{field} has no known type"
            assert f"| `{field}` | {expected} |" in rendered


def test_repository_render_has_no_unspecified_field_type() -> None:
    rendered = render_schema_tree(SCHEMA_ROOT)
    assert "| unspecified |" not in rendered


def test_composite_const_and_enum_type_semantics_are_explicit() -> None:
    schema = {
        "type": "object",
        "properties": {
            "one": {"oneOf": [{"type": "string"}, {"type": "null"}]},
            "any": {"anyOf": [{"type": "integer"}, {"type": "number"}]},
            "all": {"allOf": [{"type": "object"}, {"type": "object"}]},
            "constant": {"const": True},
            "choice": {"enum": ["safe", None]},
        },
    }

    rendered = render_schema_markdown(schema, "synthetic.json")

    assert "| `one` | string | null |" in rendered
    assert "| `any` | integer | number |" in rendered
    assert "| `all` | object |" in rendered
    assert "| `constant` | boolean |" in rendered
    assert "| `choice` | string | null |" in rendered
