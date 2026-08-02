"""Guard provenance for timing claims in performance and health reports."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


pytestmark = pytest.mark.governance

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "agent_operating_system" / "research"
TIMING_RE = re.compile(
    r"(?i)(?:\b\d+(?:\.\d+)?\s*(?:s|sec|secs|seconds|min|mins|minutes)\b|"
    r"\bin\s+\d+(?:\.\d+)?\s*\(?\d*:?\d*\)?\s*s\b)"
)
ENVIRONMENT_RE = re.compile(
    r"(?im)^(?:##\s+.*environment|##\s+reproducibility\b|environment\s*:|"
    r"accepted measurement environment|measurements used|measurements were run|"
    r"runtime is|\*\*environment unknown;)")


def _reports() -> list[Path]:
    return sorted(
        set(RESEARCH.glob("TEST_PERFORMANCE_*.md"))
        | set(RESEARCH.glob("PHASE11_HEALTH_*.md"))
    )


def test_timing_report_inventory_is_nonempty() -> None:
    reports = _reports()
    assert reports
    assert all(path.is_file() for path in reports)


@pytest.mark.parametrize("path", _reports(), ids=lambda value: value.name)
def test_every_timing_report_has_environment_and_commands(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    timing_lines = [line for line in text.splitlines() if TIMING_RE.search(line)]

    if not timing_lines:
        pytest.skip("report has no timing claim")

    environment_match = ENVIRONMENT_RE.search(text)
    assert environment_match is not None, (
        f"{path.relative_to(ROOT)} has timing claims but no environment note"
    )
    assert "pytest" in text.lower(), (
        f"{path.relative_to(ROOT)} has timing claims but no test command"
    )
