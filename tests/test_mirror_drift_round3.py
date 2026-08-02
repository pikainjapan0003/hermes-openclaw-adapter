"""Third-round path-shape boundaries for the read-only mirror comparison."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_mirror_drift_readonly as mirror


pytestmark = pytest.mark.governance


def _trees(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    downstream = tmp_path / "mirror"
    repo.mkdir()
    downstream.mkdir()
    return repo, downstream


def _put(root: Path, relative: str, data: bytes = b"same") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def test_mirror_only_nested_subdirectory_is_ahead_not_same(tmp_path: Path) -> None:
    repo, downstream = _trees(tmp_path)
    _put(downstream, "mirror-only/deep/document.md", b"unreviewed")

    entries = mirror.compare_mirror(repo, downstream)

    assert [(entry.path, entry.status) for entry in entries] == [
        ("mirror-only/deep/document.md", mirror.AHEAD)
    ]
    assert mirror.main([str(repo), str(downstream)]) == 2


def test_filename_case_difference_is_two_directional_drift(tmp_path: Path) -> None:
    repo, downstream = _trees(tmp_path)
    _put(repo, "Policy.md")
    _put(downstream, "policy.md")

    entries = mirror.compare_mirror(repo, downstream)

    assert [(entry.path, entry.status) for entry in entries] == [
        ("Policy.md", mirror.BEHIND),
        ("policy.md", mirror.AHEAD),
    ]


def test_empty_file_is_content_while_missing_file_is_behind(tmp_path: Path) -> None:
    repo, downstream = _trees(tmp_path)
    _put(repo, "empty-both.md", b"")
    _put(downstream, "empty-both.md", b"")
    _put(repo, "empty-missing.md", b"")

    entries = mirror.compare_mirror(repo, downstream)

    assert [(entry.path, entry.status) for entry in entries] == [
        ("empty-both.md", mirror.SAME),
        ("empty-missing.md", mirror.BEHIND),
    ]


def test_long_nested_relative_path_is_compared_without_truncation(
    tmp_path: Path,
) -> None:
    repo, downstream = _trees(tmp_path)
    relative = "/".join(
        ["segment-" + str(index).zfill(2) + "-" + ("x" * 28) for index in range(2)]
        + ["document-" + ("y" * 48) + ".md"]
    )
    assert len(relative) > 120
    _put(repo, relative, b"repo")
    _put(downstream, relative, b"mirror")

    entries = mirror.compare_mirror(repo, downstream)

    assert len(entries) == 1
    assert entries[0].path == relative
    assert entries[0].status == mirror.DIFFERS
