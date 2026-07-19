"""Golden vectors locking the Phase 7 canonical JSON and chain rules."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

import pytest

from app.hash_chain import HashChainError, canonical_json, entry_hash, verify_chain


ROOT = Path(__file__).resolve().parent.parent
VECTOR_DIR = ROOT / "fixtures" / "hash_chain_vectors"
VECTOR_FILES = tuple(sorted(VECTOR_DIR.glob("*.json")))


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_golden_vector_inventory_is_exact_and_named() -> None:
    assert len(VECTOR_FILES) == 8
    assert {path.stem for path in VECTOR_FILES} == {
        "minimal",
        "types_and_order",
        "unicode_nfc",
        "nested_sorting",
        "escaped_text",
        "chain_genesis",
        "chain_second",
        "chain_third",
    }


@pytest.mark.parametrize("path", VECTOR_FILES, ids=lambda path: path.stem)
def test_canonical_bytes_and_sha256_match_golden_vector(path: Path) -> None:
    vector = _load(path)
    value = vector["input"]

    assert canonical_json(value).hex() == vector["canonical_hex"]
    assert entry_hash(value) == vector["sha256"]


def test_golden_genesis_and_linked_entries_form_a_valid_chain() -> None:
    genesis = _load(VECTOR_DIR / "chain_genesis.json")["input"]
    second = _load(VECTOR_DIR / "chain_second.json")["input"]
    third = _load(VECTOR_DIR / "chain_third.json")["input"]

    assert genesis["prev_entry_hash"] is None
    assert second["prev_entry_hash"] == entry_hash(genesis)
    assert third["prev_entry_hash"] == entry_hash(second)
    assert verify_chain([genesis, second, third]) is True


def test_unicode_boundary_accepts_nfc_vector_and_rejects_nfd_equivalent() -> None:
    value = _load(VECTOR_DIR / "unicode_nfc.json")["input"]
    assert unicodedata.normalize("NFC", value["text"]) == value["text"]

    nfd_value = dict(value)
    nfd_value["text"] = unicodedata.normalize("NFD", value["text"])
    with pytest.raises(HashChainError, match="not Unicode NFC"):
        canonical_json(nfd_value)
