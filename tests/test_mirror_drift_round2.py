"""Second-round scale and failure boundaries for the read-only mirror tool."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts import check_mirror_drift_readonly as mirror


pytestmark = pytest.mark.governance


def _put(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()

    for index in range(125):
        _put(repo, f"same/{index:03}.md", f"same-{index}")
        _put(downstream, f"same/{index:03}.md", f"same-{index}")
        _put(repo, f"behind/{index:03}.md", f"repo-{index}")
        _put(downstream, f"ahead/{index:03}.md", f"mirror-{index}")
        _put(repo, f"differs/{index:03}.md", f"repo-new-{index}")
        _put(downstream, f"differs/{index:03}.md", f"mirror-new-{index}")

    before = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*.md")
    }
    entries = mirror.compare_mirror(repo, downstream)
    after = {
        path.relative_to(tmp_path).as_posix(): path.read_bytes()
        for path in tmp_path.rglob("*.md")
    }

    assert len(entries) == 500
    assert {
        state: sum(entry.status == state for entry in entries)
        for state in (mirror.SAME, mirror.BEHIND, mirror.AHEAD, mirror.DIFFERS)
    } == {
        mirror.SAME: 125,
        mirror.BEHIND: 125,
        mirror.AHEAD: 125,
        mirror.DIFFERS: 125,
    }
    assert before == after
    report = mirror.render_report(entries)
    assert "DIFFERS: human decision required; do not overwrite either copy" in report
    assert "L-007 scenario" in report


def test_missing_mirror_directory_fails_closed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(ValueError, match="not a directory"):
        mirror.compare_mirror(repo, tmp_path / "missing-mirror")


def test_permission_failure_is_not_reclassified_as_a_drift_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()
    _put(repo, "restricted.md", "repo")
    _put(downstream, "restricted.md", "mirror")

    original_digest = mirror._digest

    def permission_limited(path: Path) -> str:
        if path.parent == downstream:
            raise PermissionError("simulated unreadable mirror")
        return original_digest(path)

    monkeypatch.setattr(mirror, "_digest", permission_limited)
    with pytest.raises(PermissionError, match="simulated unreadable mirror"):
        mirror.compare_mirror(repo, downstream)


def test_differs_means_ancestry_unknown_in_both_content_directions(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()

    _put(repo, "repo-may-be-newer.md", "version two")
    _put(downstream, "repo-may-be-newer.md", "version one")
    _put(repo, "mirror-may-be-newer.md", "version one")
    _put(downstream, "mirror-may-be-newer.md", "version two")

    entries = mirror.compare_mirror(repo, downstream)

    assert [entry.status for entry in entries] == [mirror.DIFFERS, mirror.DIFFERS]
    assert all("ancestry unknown" in entry.detail for entry in entries)


def test_same_name_file_and_directory_is_classified_by_available_side(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()

    (repo / "repo-file.md").write_text("repo", encoding="utf-8")
    (downstream / "repo-file.md").mkdir()
    (repo / "mirror-dir.md").mkdir()
    (downstream / "mirror-dir.md").write_text("mirror", encoding="utf-8")

    entries = {entry.path: entry.status for entry in mirror.compare_mirror(repo, downstream)}

    assert entries == {
        "mirror-dir.md": mirror.AHEAD,
        "repo-file.md": mirror.BEHIND,
    }


def test_symlink_mirror_item_is_read_only_and_has_deterministic_digest(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()
    (repo / "linked.md").write_text("same", encoding="utf-8")
    target = tmp_path / "mirror-target.md"
    target.write_text("same", encoding="utf-8")
    link = downstream / "linked.md"
    try:
        link.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {type(exc).__name__}")

    before = target.read_bytes()
    entries = mirror.compare_mirror(repo, downstream)

    assert entries == (mirror.DriftEntry("linked.md", mirror.SAME, "sha256 equal"),)
    assert target.read_bytes() == before


def test_mode_zero_item_access_failure_is_not_reclassified_as_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()
    restricted = downstream / "restricted.md"
    (repo / "restricted.md").write_text("repo", encoding="utf-8")
    restricted.write_text("mirror", encoding="utf-8")
    try:
        restricted.chmod(0)
    except OSError as exc:
        pytest.skip(f"permission mode unavailable: {type(exc).__name__}")

    original_digest = mirror._digest

    def permission_limited(path: Path) -> str:
        if path == restricted:
            raise PermissionError("simulated mode-000 access failure")
        return original_digest(path)

    monkeypatch.setattr(mirror, "_digest", permission_limited)
    try:
        with pytest.raises(PermissionError, match="mode-000"):
            mirror.compare_mirror(repo, downstream)
    finally:
        os.chmod(restricted, 0o600)
