"""Deterministic in-memory mutation tests for all Blackboard contracts."""

from __future__ import annotations

import copy
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from app.blackboard_validators import SCHEMA_FILES, validate_blackboard_message


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "blackboard_contract"
FUZZ_SEED = 20260719
COMMON_FIELDS = (
    "schema_version",
    "message_type",
    "created_at",
    "safety_flags",
    "prev_entry_hash",
    "execution_class",
    "produced_by",
    "parent_task_id",
    "role",
)


class MutationCase(NamedTuple):
    message_type: str
    mutation_id: str
    message: dict[str, Any]


def _fixture(message_type: str) -> dict[str, Any]:
    path = FIXTURE_DIR / f"{message_type}.valid.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _mutation_cases() -> tuple[MutationCase, ...]:
    rng = random.Random(FUZZ_SEED)
    cases: list[MutationCase] = []
    for message_type in sorted(SCHEMA_FILES):
        valid = _fixture(message_type)

        for field in COMMON_FIELDS:
            mutated = copy.deepcopy(valid)
            del mutated[field]
            cases.append(MutationCase(message_type, f"missing-{field}", mutated))

        extra_flag = copy.deepcopy(valid)
        extra_flag["safety_flags"]["fuzz_unregistered_flag"] = False
        cases.append(MutationCase(message_type, "extra-safety-flag", extra_flag))

        wrong_type = copy.deepcopy(valid)
        wrong_type["message_type"] = "fuzz_wrong_message_type"
        cases.append(MutationCase(message_type, "wrong-message-type", wrong_type))

        extra_root = copy.deepcopy(valid)
        extra_root["fuzz_unregistered_root_field"] = "rejected"
        cases.append(MutationCase(message_type, "extra-root-field", extra_root))

        flag_names = sorted(valid["safety_flags"])
        for flag in rng.sample(flag_names, 8):
            wrong_flag_type = copy.deepcopy(valid)
            wrong_flag_type["safety_flags"][flag] = "not-a-boolean"
            cases.append(
                MutationCase(message_type, f"wrong-flag-type-{flag}", wrong_flag_type)
            )

    return tuple(cases)


MUTATION_CASES = _mutation_cases()


def test_fuzz_inventory_is_exact_and_seed_is_fixed() -> None:
    counts = Counter(case.message_type for case in MUTATION_CASES)

    assert FUZZ_SEED == 20260719
    assert set(counts) == set(SCHEMA_FILES)
    assert counts == {message_type: 20 for message_type in SCHEMA_FILES}
    assert len(MUTATION_CASES) == 200


@pytest.mark.parametrize(
    "case",
    MUTATION_CASES,
    ids=lambda case: f"{case.message_type}-{case.mutation_id}",
)
def test_seeded_schema_mutations_fail_closed_with_structured_errors(
    case: MutationCase,
) -> None:
    result = validate_blackboard_message(case.message, case.message_type)

    assert result["valid"] is False
    assert result["message_type"] == case.message_type
    assert result["schema_file"] == SCHEMA_FILES[case.message_type]
    assert isinstance(result["errors"], list) and result["errors"]
    for error in result["errors"]:
        assert set(error) == {"path", "schema_path", "validator", "message"}
        assert isinstance(error["path"], str) and error["path"].startswith("$")
        assert isinstance(error["schema_path"], str) and error["schema_path"].startswith("$")
        assert isinstance(error["validator"], str) and error["validator"]
        assert isinstance(error["message"], str) and error["message"]
