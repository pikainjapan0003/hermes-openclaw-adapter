"""Independent golden-vector integrity checks with no product hash imports."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parent.parent
HASH_VECTOR_DIR = ROOT / "fixtures" / "hash_chain_vectors"
BUILDER_VECTOR_DIR = ROOT / "fixtures" / "builder_golden_vectors"
HASH_VECTOR_FILES = tuple(sorted(HASH_VECTOR_DIR.glob("*.json")))
BUILDER_VECTOR_FILES = tuple(sorted(BUILDER_VECTOR_DIR.glob("*.json")))


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _independent_canonical_bytes(value: dict[str, Any]) -> bytes:
    """Reproduce the documented canonical encoding without app imports."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _independent_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(_independent_canonical_bytes(value)).hexdigest()


def _independent_evidence_hash(value: dict[str, Any]) -> str:
    payload = {
        str(key): item
        for key, item in value.items()
        if key != "bundle_hash"
    }
    return _independent_sha256(payload)


def test_independent_vector_inventory_is_exact() -> None:
    assert {path.name for path in HASH_VECTOR_FILES} == {
        "chain_genesis.json",
        "chain_second.json",
        "chain_third.json",
        "escaped_text.json",
        "minimal.json",
        "nested_sorting.json",
        "types_and_order.json",
        "unicode_nfc.json",
    }
    assert {path.name for path in BUILDER_VECTOR_FILES} == {
        "approval_packet_vectors.json",
        "evidence_bundle_vectors.json",
    }


@pytest.mark.parametrize(
    "path",
    HASH_VECTOR_FILES,
    ids=lambda path: path.stem,
)
def test_each_hash_vector_matches_independent_bytes_and_sha256(
    path: Path,
) -> None:
    vector = _load(path)
    value = vector["input"]
    assert isinstance(value, dict)

    canonical = _independent_canonical_bytes(value)
    assert canonical.hex() == vector["canonical_hex"]
    assert hashlib.sha256(canonical).hexdigest() == vector["sha256"]


def test_three_chain_files_link_to_independently_recomputed_predecessors() -> None:
    genesis = _load(HASH_VECTOR_DIR / "chain_genesis.json")
    second = _load(HASH_VECTOR_DIR / "chain_second.json")
    third = _load(HASH_VECTOR_DIR / "chain_third.json")

    assert genesis["input"]["prev_entry_hash"] is None
    assert second["input"]["prev_entry_hash"] == _independent_sha256(
        genesis["input"]
    )
    assert third["input"]["prev_entry_hash"] == _independent_sha256(
        second["input"]
    )


def test_approval_manifest_hashes_match_independently_built_expected_outputs() -> None:
    manifest = _load(BUILDER_VECTOR_DIR / "approval_packet_vectors.json")
    template = _load(ROOT / manifest["expected_output_template"])

    assert len(manifest["vectors"]) == 6
    for vector in manifest["vectors"]:
        expected = copy.deepcopy(template)
        expected.update(vector["expected_overrides"])
        assert _independent_sha256(expected) == vector["bundle_hash"], vector["name"]


def test_evidence_manifest_hashes_match_independent_payload_hashes() -> None:
    manifest = _load(BUILDER_VECTOR_DIR / "evidence_bundle_vectors.json")
    template = _load(ROOT / manifest["expected_output_template"])

    assert len(manifest["vectors"]) == 6
    for vector in manifest["vectors"]:
        expected = copy.deepcopy(template)
        expected["created_at"] = vector["created_at"]
        expected["bundle_hash"] = vector["bundle_hash"]
        assert _independent_evidence_hash(expected) == vector["bundle_hash"], (
            vector["name"]
        )
