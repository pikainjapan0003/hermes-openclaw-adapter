"""Pre-authorize the F7 hardlink rejection rule without creating a writer.

This module contains only a test-local predicate.  It is not imported by
``app/`` and performs no write, persistence, queue, dispatch, or runtime work.
"""

from __future__ import annotations

from pathlib import Path

import pytest


pytestmark = pytest.mark.governance


def would_writer_reject(path: Path) -> bool:
    """Return the fail-closed F7 precondition for a hypothetical writer."""

    try:
        return path.stat().st_nlink > 1
    except OSError:
        return True


def test_hypothetical_writer_rejects_a_hardlinked_target(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    target = tmp_path / "target.json"
    source.write_text("synthetic-local-only", encoding="utf-8")
    try:
        target.hardlink_to(source)
    except OSError as exc:
        pytest.skip(f"platform cannot create hardlink: {type(exc).__name__}")

    assert source.stat().st_nlink > 1
    assert target.stat().st_nlink > 1
    assert would_writer_reject(target) is True


def test_hypothetical_writer_allows_single_link_for_this_one_rule(
    tmp_path: Path,
) -> None:
    target = tmp_path / "single-link.json"
    target.write_text("synthetic-local-only", encoding="utf-8")

    assert target.stat().st_nlink == 1
    assert would_writer_reject(target) is False


def test_hypothetical_writer_fails_closed_when_stat_is_unavailable(
    tmp_path: Path,
) -> None:
    assert would_writer_reject(tmp_path / "missing.json") is True
