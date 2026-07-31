"""Round-three mutations for audit time, hash-chain order, and monotonic IDs."""

from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import json
import random
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import pytest

from app.blackboard_validators import validate_blackboard_message
from app.hash_chain import entry_hash


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "blackboard_contract" / "audit_event.valid.json"
SEED = 20260729
CASES_PER_KIND = 30
CHAIN_LENGTH = CASES_PER_KIND + 1
ID_PATTERN = re.compile(r"^(?P<prefix>.+)-(?P<ordinal>[0-9]{3})$")


class OrderedContractError(ValueError):
    """A cross-entry time, hash, or sequence invariant failed closed."""


@dataclass(frozen=True)
class Mutation:
    kind: str
    index: int


def _base_event() -> dict[str, Any]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _chain() -> list[dict[str, Any]]:
    start = datetime(2026, 7, 29, 0, 0, tzinfo=timezone.utc)
    chain: list[dict[str, Any]] = []
    for index in range(1, CHAIN_LENGTH + 1):
        event = copy.deepcopy(_base_event())
        event["audit_id"] = f"audit-sequence-{index:03d}"
        event["event_id"] = f"audit-event-sequence-{index:03d}"
        event["created_at"] = (start + timedelta(seconds=index)).isoformat().replace(
            "+00:00", "Z"
        )
        event["prev_entry_hash"] = None if not chain else entry_hash(chain[-1])
        chain.append(event)
    return chain


def _timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise OrderedContractError("created_at is not text")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OrderedContractError("created_at is invalid") from exc


def _ordinal(value: object, prefix: str) -> int:
    if not isinstance(value, str):
        raise OrderedContractError("sequence id is not text")
    match = ID_PATTERN.fullmatch(value)
    if match is None or match.group("prefix") != prefix:
        raise OrderedContractError("sequence id format mismatch")
    return int(match.group("ordinal"))


def _validate_ordered_chain(chain: list[dict[str, Any]]) -> None:
    if len(chain) != CHAIN_LENGTH:
        raise OrderedContractError("chain length mismatch")

    previous_time: datetime | None = None
    for expected, event in enumerate(chain, start=1):
        result = validate_blackboard_message(event, "audit_event")
        if not result["valid"]:
            raise OrderedContractError("audit_event schema rejected")

        current_time = _timestamp(event["created_at"])
        if previous_time is not None and current_time <= previous_time:
            raise OrderedContractError("created_at is not strictly increasing")
        previous_time = current_time

        expected_prev = None if expected == 1 else entry_hash(chain[expected - 2])
        if event["prev_entry_hash"] != expected_prev:
            raise OrderedContractError("prev_entry_hash sequence mismatch")

        audit_ordinal = _ordinal(event["audit_id"], "audit-sequence")
        event_ordinal = _ordinal(event["event_id"], "audit-event-sequence")
        if audit_ordinal != expected or event_ordinal != expected:
            raise OrderedContractError("id sequence is not monotonic by one")


def _rehash_from(chain: list[dict[str, Any]], start_index: int) -> None:
    for index in range(start_index, len(chain)):
        chain[index]["prev_entry_hash"] = (
            None if index == 0 else entry_hash(chain[index - 1])
        )


def _cases() -> tuple[Mutation, ...]:
    cases = [
        Mutation(kind, index)
        for kind in ("created_at", "prev_entry_hash", "id_sequence")
        for index in range(1, CASES_PER_KIND + 1)
    ]
    random.Random(SEED).shuffle(cases)
    return tuple(cases)


CASES = _cases()


def _mutate(chain: list[dict[str, Any]], mutation: Mutation) -> None:
    index = mutation.index
    if mutation.kind == "created_at":
        chain[index]["created_at"] = chain[index - 1]["created_at"]
        _rehash_from(chain, index)
    elif mutation.kind == "prev_entry_hash":
        chain[index]["prev_entry_hash"] = f"{mutation.index:064x}"
        assert chain[index]["prev_entry_hash"] != entry_hash(chain[index - 1])
    else:
        chain[index]["audit_id"] = chain[index - 1]["audit_id"]
        chain[index]["event_id"] = chain[index - 1]["event_id"]
        _rehash_from(chain, index)


def test_temporal_sequence_case_inventory_and_valid_baseline() -> None:
    assert len(CASES) == 90
    assert {
        kind: sum(case.kind == kind for case in CASES)
        for kind in ("created_at", "prev_entry_hash", "id_sequence")
    } == {"created_at": 30, "prev_entry_hash": 30, "id_sequence": 30}
    _validate_ordered_chain(_chain())


@pytest.mark.parametrize(
    "mutation",
    CASES,
    ids=lambda case: f"{case.kind}-{case.index:02d}",
)
def test_temporal_and_sequence_mutations_fail_closed(mutation: Mutation) -> None:
    chain = _chain()
    _mutate(chain, mutation)
    with pytest.raises(OrderedContractError):
        _validate_ordered_chain(chain)
