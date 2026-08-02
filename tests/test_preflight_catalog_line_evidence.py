"""Mechanically verify all twelve preflight catalog file:line citations."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


pytestmark = pytest.mark.governance
ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "agent_operating_system" / "research" / "PREFLIGHT_CONDITION_CATALOG.md"
ROW = re.compile(
    r"^\|\s*(?P<number>\d+)\s*\|\s*`(?P<condition>[^`]+)`.*?"
    r"`(?P<path>[^`]+\.py):(?P<line>\d+)`",
)


def test_all_twelve_catalog_citations_resolve_to_the_named_check() -> None:
    citations: list[tuple[int, str, Path, int]] = []
    for text in CATALOG.read_text(encoding="utf-8").splitlines():
        match = ROW.match(text)
        if match:
            citations.append(
                (
                    int(match.group("number")),
                    match.group("condition"),
                    ROOT / match.group("path"),
                    int(match.group("line")),
                )
            )

    assert [number for number, _, _, _ in citations] == list(range(1, 13))
    for _, condition, path, line_number in citations:
        assert path.is_file(), path
        lines = path.read_text(encoding="utf-8").splitlines()
        assert 1 <= line_number <= len(lines)
        assert condition in lines[line_number - 1], (
            f"stale citation for {condition}: {path.relative_to(ROOT)}:{line_number}"
        )
