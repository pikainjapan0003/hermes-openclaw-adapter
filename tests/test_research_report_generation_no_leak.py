"""Research-report flows must not persist caller-controlled sensitive markers."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import check_mirror_drift_readonly as mirror
from scripts import check_three_source_readonly as three_source
from scripts import inspect_blackboard_readonly as inspector
from scripts import render_schema_docs_readonly as renderer


pytestmark = pytest.mark.governance

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "docs" / "agent_operating_system" / "research"
MARKERS = (
    "FAKE-SECRET-NB19-REPORT-WRITE",
    r"C:\Users\Owner\private\research-source.txt",
)
WRITE_CALLS = {"open", "write", "write_text", "write_bytes", "touch"}


def test_committed_research_reports_do_not_contain_synthetic_sensitive_markers() -> None:
    reports = sorted(RESEARCH.glob("*.md"))
    assert reports
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in reports)
    assert all(marker not in corpus for marker in MARKERS)


def test_product_and_script_sources_have_no_research_report_write_target() -> None:
    findings: list[tuple[str, int, str]] = []
    for source_root in (ROOT / "app", ROOT / "scripts"):
        for path in sorted(source_root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            if "research" not in text.lower():
                continue
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
                if name in WRITE_CALLS:
                    findings.append(
                        (path.relative_to(ROOT).as_posix(), node.lineno, name)
                    )
    assert findings == []


def test_readonly_report_renderers_leave_designated_research_directory_empty(
    tmp_path: Path,
) -> None:
    generated_research = tmp_path / "research"
    generated_research.mkdir()
    inputs = tmp_path / "inputs"
    inputs.mkdir()

    report = three_source.ThreeSourceReport(
        three_source.SourceState("local", "UNREACHABLE", MARKERS[0]),
        three_source.SourceState("github", "UNREACHABLE", "offline"),
        three_source.SourceState("replit", "UNREACHABLE", "offline"),
        "INCOMPLETE",
    )
    three_source.render_report(report)

    repo = inputs / "repo"
    downstream = inputs / "mirror"
    repo.mkdir()
    downstream.mkdir()
    (repo / f"{MARKERS[0]}.md").write_text("authority", encoding="utf-8")
    mirror.render_report(mirror.compare_mirror(repo, downstream))

    json.dumps(
        inspector.summarize_board_result(
            {
                "board_name": "synthetic",
                "valid": False,
                "entry_count": 0,
                "entries": [],
                "errors": [
                    {
                        "filename": f"{MARKERS[0]}.json",
                        "code": "invalid_filename",
                        "message": "payload-free",
                    }
                ],
            }
        )
    )
    renderer.render_schema_markdown(
        {"title": MARKERS[0], "type": "object", "properties": {}},
        "synthetic.schema.json",
    )

    assert list(generated_research.iterdir()) == []

