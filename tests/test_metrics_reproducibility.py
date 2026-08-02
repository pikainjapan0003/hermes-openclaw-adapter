"""Deterministic, read-only metrics snapshot checks for health reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

import pytest


pytestmark = pytest.mark.governance

ROOT = Path(__file__).resolve().parents[1]
HEALTH_REPORT = ROOT / "docs" / "agent_operating_system" / "research" / "PHASE11_HEALTH_20260729.md"


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _snapshot() -> dict[str, Any]:
    test_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").glob("test_*.py")
    )
    schema_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs" / "schemas").rglob("*.json")
    )
    governed = {
        relative: _line_count(ROOT / relative)
        for relative in (
            "README.md",
            "docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md",
            "docs/agent_operating_system/07_AUDIT_WRITE_DESIGN.md",
            "docs/agent_operating_system/90_LESSONS_LEARNED.md",
        )
    }
    return {
        "test_files": test_files,
        "test_file_count": len(test_files),
        "test_source_lines": sum(_line_count(ROOT / path) for path in test_files),
        "schema_files": schema_files,
        "schema_file_count": len(schema_files),
        "governed_line_counts": governed,
    }


def _digest(snapshot: dict[str, Any]) -> str:
    canonical = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _collect_count(marker: str | None = None) -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-o",
        "addopts=",
        "--collect-only",
        "-q",
    ]
    if marker is not None:
        command.extend(["-m", marker])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0
    matches = re.findall(r"(?m)^(\d+)(?:/\d+)? tests? collected", completed.stdout)
    assert len(matches) == 1
    return int(matches[0])


def _runtime_metrics_report() -> dict[str, Any]:
    research_files = sorted(
        (ROOT / "docs" / "agent_operating_system" / "research").glob("*.md")
    )
    command = [
        "git",
        "-c",
        "core.whitespace=cr-at-eol",
        "diff",
        "--check",
        "9d26477",
        "HEAD",
    ]
    baseline_started = time.monotonic()
    baseline = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    baseline_elapsed = time.monotonic() - baseline_started
    assert baseline.returncode == 0
    adaptive_timeout = max(30.0, baseline_elapsed * 3.0)
    diff_check = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=adaptive_timeout,
        check=False,
    )
    assert diff_check.returncode == 0
    layer_counts = {
        layer: _collect_count(layer)
        for layer in ("contract", "governance", "legacy", "fuzz")
    }
    return {
        "git_diff_check": diff_check.stdout,
        "research_file_count": len(research_files),
        "research_line_count": sum(_line_count(path) for path in research_files),
        "test_outcome_count": _collect_count(),
        "layer_counts": layer_counts,
    }


def test_metrics_snapshot_is_reproducible_and_order_independent() -> None:
    first = _snapshot()
    second = _snapshot()

    assert first == second
    assert _digest(first) == _digest(second)
    assert first["test_file_count"] == len(first["test_files"])
    assert first["schema_file_count"] == len(first["schema_files"])
    assert first["test_files"] == sorted(first["test_files"])
    assert first["schema_files"] == sorted(first["schema_files"])


def test_health_report_is_explicitly_point_in_time_measurement() -> None:
    text = HEALTH_REPORT.read_text(encoding="utf-8")
    assert "MEASUREMENT ONLY" in text
    assert "NO ARCHIVE, PRODUCT, TEST, OR RUNTIME CHANGE" in text
    assert "NIGHT-BATCH-17" in text
    assert "No F4 threshold is exceeded" in text


@pytest.mark.slow
def test_runtime_metrics_report_round_trips_only_recomputed_values() -> None:
    report = _runtime_metrics_report()
    serialized = json.dumps(report, sort_keys=True, separators=(",", ":"))
    parsed = json.loads(serialized)

    assert parsed == report
    assert report["git_diff_check"] == ""
    assert sum(report["layer_counts"].values()) == report["test_outcome_count"]
    assert report["research_file_count"] == len(
        list((ROOT / "docs" / "agent_operating_system" / "research").glob("*.md"))
    )
