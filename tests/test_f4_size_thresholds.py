"""Mechanical guards for Maintenance Protocol F4 document-size thresholds."""

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
THRESHOLDS = (
    (ROOT / "docs" / "agent_operating_system" / "90_LESSONS_LEARNED.md", 300),
    (ROOT / "docs" / "agent_operating_system" / "05_VERIFIED_LONG_TERM_PLAN.md", 500),
    (ROOT / "README.md", 500),
)


@pytest.mark.parametrize(
    ("path", "maximum"),
    THRESHOLDS,
    ids=("90-lessons", "05-plan", "readme"),
)
def test_f4_governance_file_stays_within_size_threshold(
    path: Path, maximum: int
) -> None:
    line_count = len(path.read_text(encoding="utf-8").splitlines())

    assert line_count <= maximum, (
        f"{path.relative_to(ROOT)} has {line_count} lines; F4 threshold is {maximum}. "
        "Create or refresh the required summary/index before adding more text."
    )
