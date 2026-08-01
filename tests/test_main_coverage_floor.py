"""Regression floor for ``app/main.py`` branch-inclusive coverage.

Fable 5 determined that the GET-only safe surface is exhausted: only eight
additional safe statements remain, while the other 198 uncovered statements
belong to POST/control or execution/callback areas.  This test therefore guards
the accepted 70.507% raw level with a one-percentage-point tolerance; it never
tries to execute the forbidden surface to make the number higher.
"""

from __future__ import annotations

import io
import importlib
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import pytest


pytestmark = pytest.mark.governance

ROOT = Path(__file__).resolve().parents[1]
CURRENT_RAW_PERCENT = 70.507
ALLOWED_REGRESSION_POINTS = 1.0
MINIMUM_RAW_PERCENT = CURRENT_RAW_PERCENT - ALLOWED_REGRESSION_POINTS


def test_main_branch_coverage_does_not_regress(tmp_path: Path) -> None:
    """Measure the whole suite without recursively running this floor test."""

    data_file = tmp_path / "main-floor.coverage"
    env = os.environ.copy()
    env["COVERAGE_FILE"] = str(data_file)
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--branch",
            "--include=app/main.py",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "-q",
            "tests",
            "--ignore=tests/test_main_coverage_floor.py",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        check=False,
    )
    # This floor measures only the executed ``app/main.py`` surface.  The
    # subprocess intentionally runs the suite, but unrelated test failures must
    # not turn into a second (cascade) failure here; the coverage report below
    # remains the single assertion for this test.
    del completed
    if not data_file.exists():
        raise AssertionError("coverage-floor subprocess produced no coverage data")

    coverage_module: Any = importlib.import_module("coverage")
    measured = coverage_module.Coverage(data_file=str(data_file))
    measured.load()
    measured.set_option("report:precision", 3)
    report_output = io.StringIO()
    percentage = measured.report(
        include=[str(ROOT / "app" / "main.py")],
        file=report_output,
    )
    assert percentage >= MINIMUM_RAW_PERCENT, (
        f"main.py branch-inclusive coverage regressed to {percentage:.3f}%; "
        f"floor is {MINIMUM_RAW_PERCENT:.3f}%\n{report_output.getvalue()}"
    )
