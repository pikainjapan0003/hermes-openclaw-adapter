"""Fourth-round scale, localization, and key-order tests for hash chains."""

from __future__ import annotations

import copy
import time
from typing import Any

import pytest

from app.hash_chain import canonical_json, entry_hash, verify_chain


pytestmark = pytest.mark.contract
CHAIN_LENGTH = 100_000


def _chain(length: int) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for index in range(length):
        entry = {
            "payload": None,
            "prev_entry_hash": None if previous is None else entry_hash(previous),
            "sequence": index,
        }
        entries.append(entry)
        previous = entry
    return entries


def _first_broken_link(entries: list[dict[str, Any]]) -> int | None:
    """Locate the first broken link with prefix verification and binary search."""
    if verify_chain(entries):
        return None
    low = 2
    high = len(entries)
    while low < high:
        middle = (low + high) // 2
        if verify_chain(entries[:middle]):
            low = middle + 1
        else:
            high = middle
    return low - 1


@pytest.mark.slow
def test_verify_one_hundred_thousand_entry_chain_records_runtime_without_gate() -> None:
    build_started = time.perf_counter()
    entries = _chain(CHAIN_LENGTH)
    build_seconds = time.perf_counter() - build_started

    verify_started = time.perf_counter()
    valid = verify_chain(entries)
    verify_seconds = time.perf_counter() - verify_started

    assert valid is True
    assert len(entries) == CHAIN_LENGTH
    print(
        "hash_chain_round4 "
        f"entries={CHAIN_LENGTH} build_seconds={build_seconds:.6f} "
        f"verify_seconds={verify_seconds:.6f} threshold=none"
    )


@pytest.mark.parametrize("tamper_index", (0, 1, 127, 2048, 4094))
def test_binary_prefix_search_locates_arbitrary_nonterminal_tamper(
    tamper_index: int,
) -> None:
    entries = _chain(4096)
    tampered = copy.deepcopy(entries)
    tampered[tamper_index]["payload"] = "changed"

    assert verify_chain(tampered) is False
    assert _first_broken_link(tampered) == tamper_index + 1


def test_null_values_and_extreme_unicode_keys_have_stable_order() -> None:
    lowest = ""
    nul = "\x00"
    ascii_key = "a"
    highest = "\U0010ffff"
    forward = {
        highest: None,
        ascii_key: {highest: None, lowest: None, nul: None},
        nul: None,
        lowest: None,
    }
    reverse = dict(reversed(list(forward.items())))

    encoded = canonical_json(forward)
    assert encoded == canonical_json(reverse)
    assert entry_hash(forward) == entry_hash(reverse)
    assert encoded == (
        b'{"":null,"\\u0000":null,"a":{"":null,"\\u0000":null,'
        b'"\xf4\x8f\xbf\xbf":null},"\xf4\x8f\xbf\xbf":null}'
    )

