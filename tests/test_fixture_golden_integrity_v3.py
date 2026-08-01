"""Third-round integrity checks for frozen fixtures and golden manifests."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from tests.test_fixture_sha256_inventory import EXPECTED_SHA256


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures"
GOLDEN_ROOT = FIXTURE_ROOT / "builder_golden_vectors"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def test_v3_fixture_inventory_has_exact_reviewed_paths_and_valid_json() -> None:
    paths = {
        path.relative_to(ROOT).as_posix()
        for path in FIXTURE_ROOT.rglob("*")
        if path.is_file()
    }
    assert paths == set(EXPECTED_SHA256)
    for relative_path in sorted(paths):
        value = _json(ROOT / relative_path)
        assert isinstance(value, dict), relative_path


@pytest.mark.parametrize("relative_path", sorted(EXPECTED_SHA256))
def test_v3_normalized_fixture_sha256_is_line_ending_portable(
    relative_path: str,
) -> None:
    raw = (ROOT / relative_path).read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == EXPECTED_SHA256[relative_path]
    portable = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == hashlib.sha256(portable).hexdigest()


def test_v3_golden_manifests_are_closed_and_reference_existing_files() -> None:
    approval = _json(GOLDEN_ROOT / "approval_packet_vectors.json")
    evidence = _json(GOLDEN_ROOT / "evidence_bundle_vectors.json")
    for manifest in (approval, evidence):
        vectors = manifest.get("vectors")
        assert isinstance(vectors, list) and len(vectors) == 6
        template = manifest.get("expected_output_template")
        assert isinstance(template, str)
        assert (ROOT / template).is_file()
        sources = manifest.get("source_files")
        assert isinstance(sources, dict)
        for source in sources.values():
            if isinstance(source, str) and source.endswith(".json"):
                assert (ROOT / source).is_file(), source
        for vector in vectors:
            assert isinstance(vector, dict)
            digest = vector.get("bundle_hash")
            assert isinstance(digest, str) and SHA256.fullmatch(digest)


def test_v3_hash_vectors_have_independent_canonical_bytes_and_digests() -> None:
    vector_root = FIXTURE_ROOT / "hash_chain_vectors"
    files = sorted(vector_root.glob("*.json"))
    assert len(files) == 8
    for path in files:
        vector = _json(path)
        value = vector["input"]
        canonical = _canonical(value)
        assert canonical.hex() == vector["canonical_hex"]
        assert hashlib.sha256(canonical).hexdigest() == vector["sha256"]


def test_v3_golden_json_canonicalization_is_repeatable() -> None:
    for path in sorted(GOLDEN_ROOT.glob("*.json")):
        value = _json(path)
        first = _canonical(value)
        second = _canonical(json.loads(first.decode("utf-8")))
        assert first == second
