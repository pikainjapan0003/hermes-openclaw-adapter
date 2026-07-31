"""Tests for the stdout-only human-readable schema renderer."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from scripts.render_schema_docs_readonly import (
    main,
    render_schema_markdown,
    render_schema_tree,
)


def _fake_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Synthetic Packet",
        "type": "object",
        "additionalProperties": False,
        "required": ["message_type", "count"],
        "properties": {
            "message_type": {
                "type": "string",
                "const": "synthetic_packet",
                "description": "closed discriminator",
            },
            "count": {"type": "integer", "minimum": 1},
            "mode": {"type": "string", "enum": ["preview", "closed"]},
        },
    }


def test_render_includes_every_field_required_flag_and_const() -> None:
    rendered = render_schema_markdown(_fake_schema(), "synthetic.schema.json")

    assert "`message_type` | string | yes | const=\"synthetic_packet\"" in rendered
    assert "`count` | integer | yes | minimum=1" in rendered
    assert "`mode` | string | no | enum=[\"preview\",\"closed\"]" in rendered
    assert "Closed object: yes" in rendered


def test_tree_reads_nested_schemas_in_stable_order(tmp_path: Path) -> None:
    first = tmp_path / "a.schema.json"
    nested = tmp_path / "nested"
    nested.mkdir()
    second = nested / "b.schema.json"
    first.write_text(json.dumps(_fake_schema()), encoding="utf-8")
    second.write_text(
        json.dumps(
            {
                "title": "Empty",
                "type": "object",
                "properties": {},
            }
        ),
        encoding="utf-8",
    )

    rendered = render_schema_tree(tmp_path)

    assert rendered.index("a.schema.json") < rendered.index("nested/b.schema.json")
    assert "No object properties declared." in rendered


def test_cli_prints_to_stdout_only(tmp_path: Path, monkeypatch, capsys) -> None:
    schema_path = tmp_path / "one.json"
    schema_path.write_text(json.dumps(_fake_schema()), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["render-schema-docs", str(tmp_path)])

    assert main() == 0
    captured = capsys.readouterr()
    assert "# Generated JSON Schema Reference" in captured.out
    assert captured.err == ""
    assert sorted(path.name for path in tmp_path.iterdir()) == ["one.json"]


def test_renderer_source_has_no_write_calls() -> None:
    source_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "render_schema_docs_readonly.py"
    )
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    forbidden = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = (
            node.func.attr
            if isinstance(node.func, ast.Attribute)
            else node.func.id
            if isinstance(node.func, ast.Name)
            else ""
        )
        if name in {"open", "write", "write_text", "write_bytes", "mkdir", "touch"}:
            forbidden.append((node.lineno, name))
    assert forbidden == []
