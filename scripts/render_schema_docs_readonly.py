"""Render repository JSON Schemas as Markdown tables on stdout only.

Type composition labels are display conventions, not JSON Schema semantic
merges. Root-level ``allOf``/``if``/``then``/``else`` conditional rules are
not rendered by this version; package 4 owns that explicitly scoped addition.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


def _constraint(schema: Mapping[str, Any]) -> str:
    parts: list[str] = []
    if "const" in schema:
        parts.append(
            "const=" + json.dumps(schema["const"], ensure_ascii=False, separators=(",", ":"))
        )
    if isinstance(schema.get("enum"), list):
        parts.append(
            "enum=" + json.dumps(schema["enum"], ensure_ascii=False, separators=(",", ":"))
        )
    for key in ("format", "pattern", "minimum", "maximum", "minLength", "maxLength"):
        if key in schema:
            parts.append(f"{key}={schema[key]}")
    for keyword in ("oneOf", "anyOf", "allOf"):
        branches = schema.get(keyword)
        if not isinstance(branches, list):
            continue
        for branch in branches:
            if not isinstance(branch, Mapping):
                continue
            nested = _constraint(branch)
            if nested != "—":
                parts.extend(nested.split("; "))
    return "; ".join(dict.fromkeys(parts)) or "—"


def _json_type(value: Any) -> str:
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
    return "unspecified"


def _type_name(schema: Mapping[str, Any]) -> str:
    value = schema.get("type")
    if isinstance(value, list):
        return " | ".join(str(item) for item in value)
    if isinstance(value, str):
        return value
    if "const" in schema:
        return _json_type(schema["const"])
    enum = schema.get("enum")
    if isinstance(enum, list) and enum:
        return " | ".join(dict.fromkeys(_json_type(item) for item in enum))
    for keyword, separator in (("oneOf", " | "), ("anyOf", " | "), ("allOf", " & ")):
        branches = schema.get(keyword)
        if not isinstance(branches, list) or not branches:
            continue
        names = [
            _type_name(branch)
            for branch in branches
            if isinstance(branch, Mapping)
        ]
        names = [name for name in dict.fromkeys(names) if name != "unspecified"]
        if names:
            return separator.join(names)
    return "unspecified"


def _literal(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _condition_terms(schema: Mapping[str, Any], prefix: str = "") -> list[str]:
    terms: list[str] = []
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        return terms
    for field, detail in properties.items():
        if not isinstance(detail, Mapping):
            continue
        name = f"{prefix}.{field}" if prefix else str(field)
        if "const" in detail:
            terms.append(f"{name} == {_literal(detail['const'])}")
        elif isinstance(detail.get("enum"), list):
            terms.append(f"{name} in {_literal(detail['enum'])}")
        elif isinstance(detail.get("not"), Mapping):
            negated = detail["not"]
            if "const" in negated:
                terms.append(f"{name} != {_literal(negated['const'])}")
        terms.extend(_condition_terms(detail, name))
    return terms


def _conditional_rule_lines(schema: Mapping[str, Any]) -> list[str]:
    """Describe root conditional rules without claiming full schema semantics."""

    rules: list[Mapping[str, Any]] = []
    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        rules.extend(item for item in all_of if isinstance(item, Mapping))
    if isinstance(schema.get("if"), Mapping):
        rules.append(schema)

    lines: list[str] = []
    for rule in rules:
        condition = rule.get("if")
        then = rule.get("then")
        otherwise = rule.get("else")
        if not isinstance(condition, Mapping) or not isinstance(then, Mapping):
            continue
        condition_terms = _condition_terms(condition)
        then_terms = _condition_terms(then)
        if not condition_terms or not then_terms:
            continue
        lines.append(
            "- if "
            + " and ".join(condition_terms)
            + " then "
            + " and ".join(then_terms)
        )
        if isinstance(otherwise, Mapping):
            else_terms = _condition_terms(otherwise)
            if else_terms:
                lines.append("- otherwise " + " and ".join(else_terms))
    return lines


def render_schema_markdown(schema: Mapping[str, Any], source_name: str) -> str:
    """Return one deterministic Markdown section without writing a file."""

    title = str(schema.get("title") or source_name)
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        properties = {}
    required_value = schema.get("required")
    required = (
        {str(item) for item in required_value}
        if isinstance(required_value, Sequence)
        and not isinstance(required_value, (str, bytes))
        else set()
    )

    lines = [
        f"## {title}",
        "",
        f"Source: `{source_name}`",
        "",
        "| Field | Type | Required | Constraints | Description |",
        "|---|---|---|---|---|",
    ]
    for field, field_schema in properties.items():
        details = field_schema if isinstance(field_schema, Mapping) else {}
        description = str(details.get("description") or "—").replace("|", "\\|")
        lines.append(
            f"| `{field}` | {_type_name(details)} | "
            f"{'yes' if field in required else 'no'} | "
            f"{_constraint(details).replace('|', chr(92) + '|')} | {description} |"
        )
    if not properties:
        lines.append("| — | — | — | — | No object properties declared. |")
    lines.append("")
    lines.append(
        "Closed object: "
        + ("yes" if schema.get("additionalProperties") is False else "no/unspecified")
    )
    conditional_rules = _conditional_rule_lines(schema)
    if conditional_rules:
        lines.extend(["", "### Conditional rules", "", *conditional_rules])
    return "\n".join(lines)


def render_schema_tree(schema_root: Path) -> str:
    """Read every `*.json` below `schema_root` and return combined Markdown."""

    sections: list[str] = ["# Generated JSON Schema Reference", ""]
    for path in sorted(schema_root.rglob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, Mapping):
            raise ValueError(f"schema root must be an object: {path}")
        sections.append(
            render_schema_markdown(value, path.relative_to(schema_root).as_posix())
        )
        sections.append("")
    if len(sections) == 2:
        sections.append("_No JSON schema files found._")
    return "\n".join(sections).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "schema_root",
        nargs="?",
        type=Path,
        default=Path("docs/schemas"),
        help="schema directory to read recursively (default: docs/schemas)",
    )
    args = parser.parse_args()
    print(render_schema_tree(args.schema_root), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
