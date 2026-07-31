"""Leak-marker baseline for the four read-only command-line tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import pytest

from scripts import check_mirror_drift_readonly as mirror
from scripts import check_three_source_readonly as three_source
from scripts import inspect_blackboard_readonly as inspector
from scripts import render_schema_docs_readonly as renderer


pytestmark = pytest.mark.contract

MARKER = "FAKE-SECRET-NB16-SCRIPT-SURFACE"
EXPECTED_ECHOING_TOOLS = frozenset(
    {"three_source", "mirror_drift", "board_inspector", "schema_renderer"}
)


def _three_source_output(_tmp_path: Path) -> str:
    report = three_source.ThreeSourceReport(
        three_source.SourceState("local", "UNREACHABLE", MARKER),
        three_source.SourceState("github", "UNREACHABLE", "offline"),
        three_source.SourceState("replit", "UNREACHABLE", "offline"),
        "INCOMPLETE",
    )
    return three_source.render_report(report)


def _mirror_output(tmp_path: Path) -> str:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()
    (repo / f"{MARKER}.md").write_text("authority", encoding="utf-8")
    return mirror.render_report(mirror.compare_mirror(repo, downstream))


def _inspector_output(_tmp_path: Path) -> str:
    summary = inspector.summarize_board_result(
        {
            "board_name": "synthetic",
            "valid": False,
            "entry_count": 0,
            "entries": [],
            "errors": [
                {
                    "filename": f"{MARKER}.json",
                    "code": "invalid_filename",
                    "message": "payload-free",
                }
            ],
        }
    )
    return json.dumps(summary, ensure_ascii=False, sort_keys=True)


def _renderer_output(_tmp_path: Path) -> str:
    return renderer.render_schema_markdown(
        {
            "title": MARKER,
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
        "synthetic.schema.json",
    )


SURFACES: dict[str, Callable[[Path], str]] = {
    "three_source": _three_source_output,
    "mirror_drift": _mirror_output,
    "board_inspector": _inspector_output,
    "schema_renderer": _renderer_output,
}


@pytest.mark.parametrize("tool_name", sorted(SURFACES))
def test_readonly_tool_leak_marker_baseline(tool_name: str, tmp_path: Path) -> None:
    rendered = SURFACES[tool_name](tmp_path)
    if MARKER in rendered:
        pytest.xfail(f"known local read-only output leak: {tool_name}")
    assert MARKER not in rendered


def test_readonly_tool_leak_inventory_is_exact(tmp_path: Path) -> None:
    echoing: set[str] = set()
    for tool_name, render in SURFACES.items():
        workspace = tmp_path / tool_name
        workspace.mkdir()
        if MARKER in render(workspace):
            echoing.add(tool_name)

    assert set(SURFACES) == EXPECTED_ECHOING_TOOLS
    assert echoing == EXPECTED_ECHOING_TOOLS
