"""Tests for the read-only repo-to-mirror drift reporter."""

from pathlib import Path

from scripts.check_mirror_drift_readonly import (
    AHEAD,
    BEHIND,
    SAME,
    compare_mirror,
    main,
    render_report,
)


def _trees(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo-docs"
    mirror = tmp_path / "mirror-docs"
    repo.mkdir()
    mirror.mkdir()
    return repo, mirror


def test_equal_file_is_reported_same(tmp_path: Path, capsys) -> None:
    repo, mirror = _trees(tmp_path)
    (repo / "same.md").write_text("authoritative", encoding="utf-8")
    (mirror / "same.md").write_text("authoritative", encoding="utf-8")

    assert compare_mirror(repo, mirror)[0].status == SAME
    assert main([str(repo), str(mirror)]) == 0
    assert "SUMMARY: SAME=1 BEHIND=0 AHEAD=0" in capsys.readouterr().out


def test_missing_or_different_mirror_file_is_behind(tmp_path: Path) -> None:
    repo, mirror = _trees(tmp_path)
    (repo / "missing.md").write_text("repo", encoding="utf-8")
    (repo / "different.md").write_text("new repo version", encoding="utf-8")
    (mirror / "different.md").write_text("old mirror version", encoding="utf-8")

    entries = compare_mirror(repo, mirror)

    assert {(entry.path, entry.status) for entry in entries} == {
        ("different.md", BEHIND),
        ("missing.md", BEHIND),
    }
    assert main([str(repo), str(mirror)]) == 1


def test_mirror_only_file_is_ahead_incident(tmp_path: Path, capsys) -> None:
    repo, mirror = _trees(tmp_path)
    (mirror / "unreviewed.md").write_text("mirror-only", encoding="utf-8")

    entries = compare_mirror(repo, mirror)
    report = render_report(entries)

    assert entries[0].status == AHEAD
    assert "INCIDENT" in report
    assert "40_MAINTENANCE_PROTOCOL.md F6" in report
    assert main([str(repo), str(mirror)]) == 2
    assert "AHEAD | unreviewed.md" in capsys.readouterr().out


def test_comparison_is_read_only(tmp_path: Path) -> None:
    repo, mirror = _trees(tmp_path)
    repo_file = repo / "nested" / "document.md"
    mirror_file = mirror / "nested" / "document.md"
    repo_file.parent.mkdir()
    mirror_file.parent.mkdir()
    repo_file.write_bytes(b"repo")
    mirror_file.write_bytes(b"mirror")
    before = (repo_file.read_bytes(), mirror_file.read_bytes())

    compare_mirror(repo, mirror)

    assert (repo_file.read_bytes(), mirror_file.read_bytes()) == before
