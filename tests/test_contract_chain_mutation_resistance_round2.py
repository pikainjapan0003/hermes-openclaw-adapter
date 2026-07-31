"""Deterministic cross-message mutation resistance for one N=1 chain."""

from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from app.blackboard_validators import validate_blackboard_message


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "blackboard_contract"
SEED = 20260728
CASES_PER_KIND = 40
MESSAGE_TYPES = (
    "task_draft",
    "annotation",
    "approval_readiness",
    "owner_decision",
    "worker_dry_run",
    "openclaw_command_envelope",
    "result_message",
    "approval_packet",
    "audit_event",
    "rollback_event",
)


class ChainInvariantError(ValueError):
    """A schema or cross-message invariant failed closed."""


@dataclass(frozen=True)
class Mutation:
    kind: str
    target: str
    field: str
    ordinal: int


def _fixture(message_type: str) -> dict[str, Any]:
    value = json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )
    assert isinstance(value, dict)
    return value


def _chain() -> dict[str, dict[str, Any]]:
    return {message_type: _fixture(message_type) for message_type in MESSAGE_TYPES}


def _same(label: str, *values: object) -> None:
    if len(set(map(repr, values))) != 1:
        raise ChainInvariantError(f"cross-message {label} mismatch")


def _validate_chain(messages: dict[str, dict[str, Any]]) -> None:
    for message_type, message in messages.items():
        result = validate_blackboard_message(message, message_type)
        if not result["valid"]:
            raise ChainInvariantError(f"{message_type} schema rejected")

    ordered = [messages[name] for name in MESSAGE_TYPES]
    _same("schema_version", *(item["schema_version"] for item in ordered))
    _same("parent_task_id", *(item["parent_task_id"] for item in ordered))
    _same("safety_flags", *(item["safety_flags"] for item in ordered))

    task = messages["task_draft"]
    annotation = messages["annotation"]
    readiness = messages["approval_readiness"]
    decision = messages["owner_decision"]
    dry_run = messages["worker_dry_run"]
    command = messages["openclaw_command_envelope"]
    result = messages["result_message"]
    packet = messages["approval_packet"]
    audit = messages["audit_event"]
    rollback = messages["rollback_event"]

    _same(
        "task_id",
        task["task_id"],
        annotation["task_id"],
        readiness["task_id"],
        decision["task_id"],
        dry_run["task_id"],
        command["task_id"],
        result["task_id"],
        packet["task_id"],
        packet["exact_target"]["task_id"],
        audit["task_id"],
        rollback["task_id"],
    )
    _same("annotation_id", annotation["annotation_id"], readiness["annotation_id"])
    _same("readiness_id", readiness["readiness_id"], decision["readiness_id"])
    _same("decision_id", decision["decision_id"], dry_run["decision_id"])
    _same(
        "dry_run_id",
        dry_run["dry_run_id"],
        command["dry_run_id"],
        result["related_dry_run_id"],
        packet["dry_run_evidence"]["dry_run_id"],
    )
    _same(
        "command_id",
        command["command_id"],
        result["command_id"],
        packet["exact_target"]["command_id"],
    )
    _same(
        "result_id",
        result["result_id"],
        packet["dry_run_evidence"]["result_id"],
        audit["related_result_id"],
        rollback["related_result_id"],
    )
    _same("audit_id", audit["audit_id"], rollback["source_audit_id"])


ID_TARGETS = (
    ("annotation", "task_id"),
    ("approval_readiness", "annotation_id"),
    ("owner_decision", "readiness_id"),
    ("worker_dry_run", "decision_id"),
    ("openclaw_command_envelope", "dry_run_id"),
    ("result_message", "command_id"),
    ("result_message", "related_dry_run_id"),
    ("approval_packet", "task_id"),
    ("audit_event", "related_result_id"),
    ("rollback_event", "source_audit_id"),
)
FLAG_TARGETS = tuple(MESSAGE_TYPES[1:])
FLAG_NAMES = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "follow_up_requires_owner_confirmation",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "external_side_effects_allowed",
)


def _cases() -> tuple[Mutation, ...]:
    rng = random.Random(SEED)
    cases: list[Mutation] = []
    for ordinal in range(CASES_PER_KIND):
        target, field = rng.choice(ID_TARGETS)
        cases.append(Mutation("id", target, field, ordinal))
    for ordinal in range(CASES_PER_KIND):
        cases.append(
            Mutation(
                "flag",
                rng.choice(FLAG_TARGETS),
                rng.choice(FLAG_NAMES),
                ordinal,
            )
        )
    for ordinal in range(CASES_PER_KIND):
        cases.append(Mutation("version", rng.choice(MESSAGE_TYPES), "schema_version", ordinal))
    rng.shuffle(cases)
    return tuple(cases)


CASES = _cases()


def _mutate(messages: dict[str, dict[str, Any]], mutation: Mutation) -> None:
    message = messages[mutation.target]
    if mutation.kind == "id":
        message[mutation.field] = f"mismatch-{SEED}-{mutation.ordinal}"
    elif mutation.kind == "flag":
        flags = message["safety_flags"]
        assert isinstance(flags, dict)
        flags[mutation.field] = not flags[mutation.field]
    else:
        message[mutation.field] = f"9.{mutation.ordinal}"


def test_valid_chain_satisfies_cross_message_invariants() -> None:
    assert len(CASES) == 120
    assert {kind: sum(case.kind == kind for case in CASES) for kind in ("id", "flag", "version")} == {
        "id": 40,
        "flag": 40,
        "version": 40,
    }
    _validate_chain(_chain())


@pytest.mark.parametrize(
    "mutation",
    CASES,
    ids=lambda case: f"{case.kind}-{case.target}-{case.field}-{case.ordinal}",
)
def test_cross_message_mutations_fail_closed(mutation: Mutation) -> None:
    messages = copy.deepcopy(_chain())
    _mutate(messages, mutation)

    with pytest.raises(ChainInvariantError):
        _validate_chain(messages)
