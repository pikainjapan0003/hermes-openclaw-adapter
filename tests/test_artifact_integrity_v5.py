"""Closed normalized-byte inventory extended to scripts and all schema docs."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tests.test_artifact_integrity_v4 import EXPECTED_ARTIFACT_SHA256, ROOT


pytestmark = pytest.mark.contract

EXPECTED_V5_PATH_COUNT = 278
EXPECTED_V5_MANIFEST_SHA256 = (
    "921137df7d0295044b3f0d4ceadd4c0436e3f6f9699b6d2e66ba914fee421186"
)


def _normalized_bytes(path: Path) -> bytes:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    assert b"\r" not in normalized, f"bare CR is not portable: {path}"
    return normalized


def _v5_paths() -> set[str]:
    paths = set(EXPECTED_ARTIFACT_SHA256)
    for base in (ROOT / "scripts", ROOT / "docs" / "schemas"):
        paths.update(
            path.relative_to(ROOT).as_posix()
            for path in base.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )
    return paths


def _manifest_digest(paths: set[str]) -> str:
    manifest = hashlib.sha256()
    for relative_path in sorted(paths):
        content_digest = hashlib.sha256(
            _normalized_bytes(ROOT / relative_path)
        ).hexdigest()
        manifest.update(relative_path.encode("utf-8"))
        manifest.update(b"\0")
        manifest.update(content_digest.encode("ascii"))
        manifest.update(b"\n")
    return manifest.hexdigest()


@pytest.mark.slow
def test_v5_inventory_is_closed_and_extends_all_v4_artifacts() -> None:
    paths = _v5_paths()

    assert set(EXPECTED_ARTIFACT_SHA256) <= paths
    assert len(paths) == EXPECTED_V5_PATH_COUNT
    assert sum(path.startswith("scripts/") for path in paths) == 212
    assert sum(path.startswith("docs/schemas/") for path in paths) == 16
    assert "docs/schemas/blackboard/INDEX.md" in paths


@pytest.mark.slow
def test_v5_normalized_manifest_digest_is_unchanged() -> None:
    paths = _v5_paths()

    assert _manifest_digest(paths) == EXPECTED_V5_MANIFEST_SHA256


def test_v5_crlf_and_lf_have_the_same_normalized_digest(tmp_path: Path) -> None:
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"one\ntwo\n")
    crlf.write_bytes(b"one\r\ntwo\r\n")

    assert hashlib.sha256(_normalized_bytes(lf)).digest() == hashlib.sha256(
        _normalized_bytes(crlf)
    ).digest()
