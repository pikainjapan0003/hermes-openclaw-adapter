"""Phase 7 canonicalization and hash-chain tests; all data stays in memory."""

from __future__ import annotations

import ast
import copy
import json
import unicodedata
from pathlib import Path
from typing import Any

import pytest

import app.hash_chain as hash_chain_module
from app.hash_chain import HashChainError, canonical_json, entry_hash, verify_chain


ROOT = Path(__file__).resolve().parent.parent
AUDIT_FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "audit_event.valid.json"


def _audit_event() -> dict[str, Any]:
    event = json.loads(AUDIT_FIXTURE.read_text(encoding="utf-8"))
    event["prev_entry_hash"] = None
    return event


def _next_event(previous: dict[str, Any], sequence: int) -> dict[str, Any]:
    event = copy.deepcopy(previous)
    event["audit_id"] = f"audit-chain-{sequence}"
    event["event_id"] = f"audit-chain-event-{sequence}"
    event["event_notes"] = f"Synthetic preview chain event {sequence}."
    event["prev_entry_hash"] = entry_hash(previous)
    return event


def test_canonical_json_and_hash_are_deterministic_across_key_order() -> None:
    event = _audit_event()
    reordered = dict(reversed(list(event.items())))

    assert canonical_json(event) == canonical_json(reordered)
    assert entry_hash(event) == entry_hash(reordered)
    assert canonical_json(event).endswith(b"\n") is False
    assert len(entry_hash(event)) == 64


def test_genesis_and_linked_chain_are_valid() -> None:
    genesis = _audit_event()
    second = _next_event(genesis, 2)
    third = _next_event(second, 3)

    assert verify_chain([]) is True
    assert verify_chain([genesis]) is True
    assert verify_chain([genesis, second, third]) is True


def test_broken_link_and_later_null_are_rejected() -> None:
    genesis = _audit_event()
    second = _next_event(genesis, 2)

    broken = copy.deepcopy(second)
    broken["prev_entry_hash"] = "0" * 64
    assert verify_chain([genesis, broken]) is False

    later_null = copy.deepcopy(second)
    later_null["prev_entry_hash"] = None
    assert verify_chain([genesis, later_null]) is False


def test_tampering_with_a_middle_entry_breaks_the_following_link() -> None:
    genesis = _audit_event()
    second = _next_event(genesis, 2)
    third = _next_event(second, 3)
    tampered_second = copy.deepcopy(second)
    tampered_second["event_notes"] = "Tampered preview note."

    assert verify_chain([genesis, tampered_second, third]) is False


@pytest.mark.parametrize(
    "mutation",
    (
        lambda event: event.update({"forbidden_float": 1.5}),
        lambda event: event.update({"forbidden_bytes": b"bytes"}),
        lambda event: event.update({1: "non-string key"}),
        lambda event: event.update(
            {"event_notes": unicodedata.normalize("NFD", "café")}
        ),
    ),
    ids=("float", "bytes", "non-string-key", "non-nfc"),
)
def test_canonical_json_rejects_values_outside_the_domain(mutation: Any) -> None:
    event = _audit_event()
    mutation(event)

    with pytest.raises(HashChainError):
        canonical_json(event)


def test_hash_chain_module_has_only_in_memory_calculation_imports() -> None:
    source = Path(hash_chain_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {
        "__future__",
        "collections",
        "hashlib",
        "json",
        "typing",
        "unicodedata",
    }
    assert imported_roots.isdisjoint(
        {"app", "httpx", "os", "pathlib", "requests", "socket", "subprocess"}
    )
    assert "data/" not in source
