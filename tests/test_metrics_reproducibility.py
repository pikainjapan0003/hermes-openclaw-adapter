"""Deterministic, read-only metrics snapshot checks for health reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
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
