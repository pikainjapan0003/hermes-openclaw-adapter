"""Round-five mutations for cross-flag safety semantics.

Earlier mutation rounds alter individual fields.  This round changes two or
more boolean safety flags together and proves that source agreement cannot
turn a semantically unsafe combination into an accepted builder input.
"""

from __future__ import annotations

import itertools
import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import (
    ApprovalPacketBuildError,
    build_approval_packet,
)
from app.rollback_preview_builder import (
    RollbackPreviewBuildError,
    build_rollback_preview,
)


pytestmark = pytest.mark.fuzz

SEED = 20260802
ROOT = Path(__file__).resolve().parent.parent
BLACKBOARD = ROOT / "fixtures" / "blackboard_contract"
EVIDENCE = ROOT / "fixtures" / "local_mock_data" / "n1_dry_run_evidence_bundle.json"

TRUE_GUARDS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "follow_up_requires_owner_confirmation",
)
CAPABILITY_FLAGS = (
    "external_side_effects_allowed",
    "blackboard_write_allowed",
    "queue_write_allowed",
    "audit_trail_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
)
OCCURRENCE_FLAGS = (
    "external_side_effects_occurred",
    "hermes_runtime_allowed",
    "connector_call_allowed",
    "google_sheets_write_allowed",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _safe_flags() -> dict[str, bool]:
    return _load(BLACKBOARD / "worker_dry_run.valid.json")["safety_flags"]


def _mutated_flags(*changes: tuple[str, bool]) -> dict[str, bool]:
    flags = deepcopy(_safe_flags())
    for key, value in changes:
        flags[key] = value
    return flags


def _isolation_cases() -> list[tuple[str, dict[str, bool]]]:
    """A disabled isolation guard combined with an enabled capability."""
    return [
        (
            f"isolation:{guard}=false+{capability}=true",
            _mutated_flags((guard, False), (capability, True)),
        )
        for guard in TRUE_GUARDS
        for capability in CAPABILITY_FLAGS
    ]


def _occurrence_cases() -> list[tuple[str, dict[str, bool]]]:
    """An occurrence/runtime flag enabled while a required guard is disabled."""
    return [
        (
            f"occurrence:{flag}=true+{guard}=false",
            _mutated_flags((flag, True), (guard, False)),
        )
        for flag in OCCURRENCE_FLAGS
        for guard in TRUE_GUARDS
    ]


def _follow_up_cases() -> list[tuple[str, dict[str, bool]]]:
    """Follow-up permission combined with two weakened review/isolation guards."""
    weakening_flags = TRUE_GUARDS + CAPABILITY_FLAGS
    pairs = list(itertools.combinations(weakening_flags, 2))[:30]
    return [
        (
            f"follow-up:allowed+{first}=unsafe+{second}=unsafe",
            _mutated_flags(
                ("follow_up_allowed", True),
                (first, not _safe_flags()[first]),
                (second, not _safe_flags()[second]),
            ),
        )
        for first, second in pairs
    ]


def _approval_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        _load(BLACKBOARD / "worker_dry_run.valid.json"),
        _load(BLACKBOARD / "result_message.valid.json"),
    )


def _rollback_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _load(BLACKBOARD / "audit_event.valid.json"),
        _load(EVIDENCE),
        _load(BLACKBOARD / "result_message.valid.json"),
    )


def test_round_five_inventory_is_exact_disjoint_and_combination_only() -> None:
    classes = (_isolation_cases(), _occurrence_cases(), _follow_up_cases())
    assert SEED == 20260802
    assert [len(cases) for cases in classes] == [30, 30, 30]

    labels = [label for cases in classes for label, _ in cases]
    assert len(labels) == len(set(labels)) == 90
    safe = _safe_flags()
    assert len(safe) == 16
    for cases in classes:
        for _, flags in cases:
            assert flags.keys() == safe.keys()
            assert all(type(value) is bool for value in flags.values())
            assert sum(flags[key] != safe[key] for key in safe) >= 2


@pytest.mark.parametrize(
    "case_class,cases",
    (
        ("isolation", _isolation_cases()),
        ("occurrence", _occurrence_cases()),
        ("follow_up", _follow_up_cases()),
    ),
)
def test_semantically_unsafe_flag_combinations_fail_closed(
    case_class: str, cases: list[tuple[str, dict[str, bool]]]
) -> None:
    shuffled = list(cases)
    random.Random(f"{SEED}:{case_class}").shuffle(shuffled)

    for index, (label, flags) in enumerate(shuffled):
        output = None
        if index % 2 == 0:
            worker, result = _approval_sources()
            worker["safety_flags"] = deepcopy(flags)
            result["safety_flags"] = deepcopy(flags)
            with pytest.raises(ApprovalPacketBuildError, match="safe profile"):
                output = build_approval_packet(
                    worker,
                    result,
                    decision="respond",
                    approval_timestamp=None,
                    prev_entry_hash=None,
                )
        else:
            audit, bundle, result = _rollback_sources()
            audit["safety_flags"] = deepcopy(flags)
            result["safety_flags"] = deepcopy(flags)
            with pytest.raises(RollbackPreviewBuildError, match="safe profile"):
                output = build_rollback_preview(audit, bundle, result)
        assert output is None, label
