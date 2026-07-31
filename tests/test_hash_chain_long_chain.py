"""Long in-memory hash-chain integrity and tamper-localization probe."""

from __future__ import annotations

import copy
import json
import random
import time
from pathlib import Path
from typing import Any

from app.hash_chain import entry_hash, verify_chain


ROOT = Path(__file__).resolve().parent.parent
AUDIT_FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "audit_event.valid.json"
SEED = 20260727
CHAIN_LENGTH = 1_000


def _long_chain() -> list[dict[str, Any]]:
    template = json.loads(AUDIT_FIXTURE.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for index in range(CHAIN_LENGTH):
        event = copy.deepcopy(template)
        event["audit_id"] = f"audit-long-chain-{index:04d}"
        event["event_id"] = f"audit-long-chain-event-{index:04d}"
        event["event_notes"] = f"Synthetic long-chain preview {index}."
        event["prev_entry_hash"] = None if previous is None else entry_hash(previous)
        entries.append(event)
        previous = event
    return entries


def test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper() -> None:
    entries = _long_chain()

    started = time.perf_counter()
    assert verify_chain(entries) is True
    valid_runtime_seconds = time.perf_counter() - started

    rng = random.Random(SEED)
    tamper_index = rng.randint(1, CHAIN_LENGTH - 2)
    tampered = copy.deepcopy(entries)
    tampered[tamper_index]["event_notes"] = "Tampered synthetic preview."

    started = time.perf_counter()
    assert verify_chain(tampered) is False
    tamper_runtime_seconds = time.perf_counter() - started

    first_broken_link = tamper_index + 1
    assert tampered[first_broken_link]["prev_entry_hash"] == entry_hash(
        entries[tamper_index]
    )
    assert tampered[first_broken_link]["prev_entry_hash"] != entry_hash(
        tampered[tamper_index]
    )

    untrusted_suffix = tampered[first_broken_link:]
    assert len(untrusted_suffix) == CHAIN_LENGTH - first_broken_link
    assert first_broken_link > tamper_index

    print(
        "hash_chain_long "
        f"entries={CHAIN_LENGTH} seed={SEED} tamper_index={tamper_index} "
        f"first_broken_link={first_broken_link} "
        f"valid_runtime_seconds={valid_runtime_seconds:.6f} "
        f"tamper_runtime_seconds={tamper_runtime_seconds:.6f}"
    )
