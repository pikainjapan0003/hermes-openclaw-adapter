"""Seeded mutation matrix for the projection schema's root if/then rule."""

from __future__ import annotations

import copy
import json
import random
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from app.remote_readonly_projection import (
    CANONICAL_SAFETY_FLAG_KEYS,
    RemoteReadonlyProjectionError,
    build_remote_readonly_projection,
)


pytestmark = pytest.mark.fuzz

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "docs" / "schemas" / "remote_readonly_projection.schema.json").read_text(
        encoding="utf-8"
    )
)
SEED = 20260805
STATUSES = ("pending", "ready", "decided", "failed")
PHASES = ("task_draft", "dry_run", "evidence_ready", "approval_ready", "owner_decided", "failed")
DECISIONS: tuple[Any, ...] = (
    None,
    "approve",
    "edit",
    "reject",
    "respond",
    "invalid-decision",
)


def _source() -> dict[str, Any]:
    flags = {key: False for key in CANONICAL_SAFETY_FLAG_KEYS}
    flags.update(
        {
            "synthetic_local_only": True,
            "mock_only": True,
            "dry_run": True,
            "owner_review_required": True,
            "follow_up_requires_owner_confirmation": True,
        }
    )
    return {
        "task_id": "task-conditional-mutation",
        "parent_task_id": "parent-conditional-mutation",
        "phase": "approval_ready",
        "status": "ready",
        "execution_class": "OWNER_APPROVAL",
        "safety_flags": flags,
        "approval_readiness": "ready_for_owner",
        "decision": None,
        "decision_timestamp": None,
        "evidence_bundle_hash": "a" * 64,
    }


def _cases() -> list[tuple[str, str, Any]]:
    cases = [(status, phase, decision) for status in STATUSES for phase in PHASES for decision in DECISIONS]
    random.Random(SEED).shuffle(cases)
    assert len(cases) == 144
    return cases


@pytest.mark.parametrize("status,phase,decision", _cases())
def test_status_phase_if_then_mutations_fail_closed(
    status: str, phase: str, decision: Any
) -> None:
    source = _source()
    source.update(
        {
            "status": status,
            "phase": phase,
            "decision": decision,
            "decision_timestamp": (
                "2026-08-05T00:05:00Z" if decision is not None else None
            ),
        }
    )

    should_pass = (
        status == "decided"
        and phase == "owner_decided"
        and decision in {"approve", "edit", "reject", "respond"}
    ) or (
        status != "decided"
        and phase != "owner_decided"
        and decision is None
    )

    if not should_pass:
        with pytest.raises(RemoteReadonlyProjectionError):
            build_remote_readonly_projection(
                source,
                data_generated_at="2026-08-05T00:00:00Z",
                source_commit_sha="b" * 40,
                stale_after="2026-08-05T00:15:00Z",
            )
        return

    projection = build_remote_readonly_projection(
        source,
        data_generated_at="2026-08-05T00:00:00Z",
        source_commit_sha="b" * 40,
        stale_after="2026-08-05T00:15:00Z",
    )
    errors = list(
        Draft202012Validator(SCHEMA, format_checker=FormatChecker()).iter_errors(projection)
    )
    assert errors == []
    assert projection["status"] == status
    assert projection["phase"] == phase


def test_mutation_matrix_is_seeded_and_does_not_mutate_template() -> None:
    template = _source()
    before = copy.deepcopy(template)
    assert len(_cases()) >= 90
    assert template == before
