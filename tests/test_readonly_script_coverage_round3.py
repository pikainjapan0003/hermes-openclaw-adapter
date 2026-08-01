"""Round-three edge coverage for the four stdout-only helper scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import check_mirror_drift_readonly as mirror
from scripts import check_three_source_readonly as three_source
from scripts import inspect_blackboard_readonly as inspector


pytestmark = pytest.mark.contract


def test_mirror_rejects_a_missing_root_without_creating_anything(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a directory"):
        mirror.compare_mirror(tmp_path / "missing", tmp_path)


def test_three_source_rejects_missing_or_malformed_remote_ref(monkeypatch) -> None:
    def malformed_git(
        _command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            ["git"], 0, "not-a-hash\trefs/heads/master\n", ""
        )

    monkeypatch.setattr(three_source.subprocess, "run", malformed_git)
    state = three_source.read_origin_head(Path("repo"))
    assert state.value == "UNREACHABLE"
    assert state.detail == "branch hash not returned"


def test_three_source_maps_non_success_replit_http_to_unreachable() -> None:
    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def getcode(self) -> int:
            return 503

    original = three_source.urlopen
    try:
        three_source.urlopen = lambda *_args, **_kwargs: Response()  # type: ignore[assignment]
        state = three_source.read_replit_status("https://example.invalid")
    finally:
        three_source.urlopen = original
    assert state.value == "UNREACHABLE"
    assert state.detail == "HTTP 503: https://example.invalid"


def test_identifier_walker_stops_at_non_mapping_children() -> None:
    assert inspector._identifier_overview({"nested": [], "id": None}) == {"id": None}
    assert inspector._identifier_overview([]) == {}  # type: ignore[arg-type]
