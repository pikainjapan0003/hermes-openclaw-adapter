"""Extreme but in-memory inputs for Phase 7 canonical JSON."""

from __future__ import annotations

import json
import unicodedata

import pytest

from app.hash_chain import HashChainError, canonical_json


pytestmark = pytest.mark.contract


def test_one_megabyte_key_and_value_are_canonical_and_deterministic() -> None:
    long_key = "k" * 1_048_576
    long_value = "v" * 1_048_576
    value = {"tail": 1, long_key: long_value}

    first = canonical_json(value)
    second = canonical_json(dict(reversed(tuple(value.items()))))

    assert first == second
    assert first.startswith(b'{"' + (b"k" * 128))
    assert first.endswith(b',"tail":1}')


def test_five_hundred_nested_objects_have_stable_bytes() -> None:
    nested: object = "leaf"
    for _ in range(500):
        nested = {"n": nested}
    value = {"root": nested}

    first = canonical_json(value)
    second = canonical_json(value)

    assert first == second
    assert first.count(b'{"n":') == 500
    assert json.loads(first) == value


def test_ten_thousand_keys_sort_identically() -> None:
    value = {f"key-{index:05d}": index for index in reversed(range(10_000))}
    reordered = dict(reversed(tuple(value.items())))

    first = canonical_json(value)
    second = canonical_json(reordered)

    assert first == second
    assert first.startswith(b'{"key-00000":0')
    assert first.endswith(b'"key-09999":9999}')


def test_nfc_astral_scalar_and_zero_width_character_are_stable() -> None:
    value = {
        "emoji": "\U0001f600",
        "nfc": unicodedata.normalize("NFC", "cafe\u0301"),
        "zero_width": "left\u200bright",
    }

    encoded = canonical_json(value)

    assert encoded == canonical_json(dict(reversed(tuple(value.items()))))
    assert json.loads(encoded) == value


@pytest.mark.parametrize(
    "value",
    (
        {"text": unicodedata.normalize("NFD", "café")},
        {"nested": [{"text": unicodedata.normalize("NFD", "résumé")}]},
        {unicodedata.normalize("NFD", "café"): "value"},
    ),
    ids=("nfd-value", "nested-nfd-value", "nfd-key"),
)
def test_nfd_is_always_rejected_fail_closed(value: dict[str, object]) -> None:
    with pytest.raises(HashChainError, match="Unicode NFC"):
        canonical_json(value)


@pytest.mark.parametrize("surrogate", ("\ud83d\ude00", "\ud800", "\udfff"))
def test_surrogate_code_units_fail_closed(surrogate: str) -> None:
    with pytest.raises(HashChainError, match="encoding failed"):
        canonical_json({"surrogate": surrogate})
