"""Deterministic file-level fuzz cases for the read-only board reader."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from app.blackboard_board_reader import read_blackboard_board


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "blackboard_contract"
SEED = 20260720
CASE_COUNT = 64


def _fixture(message_type: str) -> dict:
    return json.loads(
        (FIXTURES / f"{message_type}.valid.json").read_text(encoding="utf-8")
    )


def _write_good_task(board: Path) -> dict:
    message = _fixture("task_draft")
    (board / "0001_task_draft.json").write_text(
        json.dumps(message, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return message


def _case_bytes(category: str, index: int, marker: str) -> bytes:
    rng = random.Random(SEED + index)
    if category == "truncated":
        raw = json.dumps({"marker": marker, "value": rng.randrange(10_000)})
        return raw[: -rng.randint(1, min(8, len(raw)))].encode("utf-8")
    if category == "non_utf8":
        return b'{"marker":"' + bytes([0x80 + index % 0x7F]) + b'"}'
    if category == "deep_nested":
        depth = 128 + index * 3
        return (("[" * depth) + json.dumps(marker) + ("]" * depth)).encode("utf-8")
    if category == "long_key":
        key = f"{marker}-" + ("k" * (4096 + index * 17))
        return json.dumps([{key: 1}]).encode("utf-8")
    if category == "duplicate_key":
        return (
            '[{"duplicate":'
            + json.dumps(marker)
            + ',"duplicate":"second"}]'
        ).encode("utf-8")
    if category == "array_root":
        return json.dumps([marker, rng.randrange(10_000)]).encode("utf-8")
    if category == "empty":
        return (" \r\n\t" * index).encode("utf-8")
    if category == "one_megabyte":
        return json.dumps([marker + ("x" * 1_048_576)]).encode("utf-8")
    raise AssertionError(f"unknown fuzz category: {category}")


CATEGORIES = (
    "truncated",
    "non_utf8",
    "deep_nested",
    "long_key",
    "duplicate_key",
    "array_root",
    "empty",
)
CASES = tuple(
    (category, index)
    for category in CATEGORIES
    for index in range(1, 10)
) + (("one_megabyte", 1),)


def test_fuzz_inventory_is_fixed_and_covers_all_requested_classes() -> None:
    assert SEED == 20260720
    assert len(CASES) == CASE_COUNT == 64
    assert {category for category, _index in CASES} == set(CATEGORIES) | {
        "one_megabyte"
    }


@pytest.mark.parametrize(
    ("category", "index"),
    CASES,
    ids=(f"{category}-{index}" for category, index in CASES),
)
def test_bad_board_file_is_structurally_rejected_without_payload_leak_or_good_file_loss(
    tmp_path: Path,
    category: str,
    index: int,
) -> None:
    marker = f"RAW-PAYLOAD-{SEED}-{category}-{index}"
    good = _write_good_task(tmp_path)
    (tmp_path / "0002_annotation.json").write_bytes(
        _case_bytes(category, index, marker)
    )

    result = read_blackboard_board(tmp_path)

    assert result["valid"] is False
    assert result["errors"]
    assert marker not in json.dumps(result, ensure_ascii=False)
    good_entry = next(
        entry for entry in result["entries"] if entry["message_type"] == "task_draft"
    )
    assert good_entry["valid"] is True
    assert good_entry["message"] == good
    assert all("message" not in entry for entry in result["entries"] if not entry["valid"])
