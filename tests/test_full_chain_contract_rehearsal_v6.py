"""Round-six full-chain repeatability rehearsal (memory only)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from app.blackboard_validators import validate_blackboard_message
from app.evidence_bundle_builder import verify_bundle_hash

from tests.test_full_chain_contract_rehearsal import (
    BLACKBOARD_PREFIX_ORDER,
    FULL_CHAIN_ORDER,
    _build_full_chain,
    _validate_evidence_bundle,
)


pytestmark = pytest.mark.contract
REPETITIONS = 20


def _ordered_outputs(
    messages: dict[str, dict[str, Any]], evidence_bundle: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        *(messages[name] for name in BLACKBOARD_PREFIX_ORDER),
        evidence_bundle,
        messages["audit_event_genesis"],
        messages["audit_event_linked"],
        messages["rollback_preview"],
    ]


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _independent_digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def test_v6_repeated_full_chain_is_byte_identical_and_independently_hashed() -> None:
    baseline_bytes: list[bytes] | None = None
    baseline_hashes: list[str] | None = None

    for _ in range(REPETITIONS):
        messages, evidence_bundle = _build_full_chain()
        outputs = _ordered_outputs(messages, evidence_bundle)
        assert len(outputs) == len(FULL_CHAIN_ORDER) == 12

        for message_type in BLACKBOARD_PREFIX_ORDER:
            validation = validate_blackboard_message(messages[message_type])
            assert validation["valid"] is True, validation["errors"]
        for name in ("audit_event_genesis", "audit_event_linked", "rollback_preview"):
            validation = validate_blackboard_message(
                messages[name],
                "audit_event" if name.startswith("audit_event") else "rollback_event",
            )
            assert validation["valid"] is True, validation["errors"]
        assert _validate_evidence_bundle(evidence_bundle) == []
        assert verify_bundle_hash(evidence_bundle) is True

        current_bytes = [_canonical_bytes(value) for value in outputs]
        current_hashes = [_independent_digest(value) for value in outputs]
        if baseline_bytes is None:
            baseline_bytes = current_bytes
            baseline_hashes = current_hashes
        else:
            assert current_bytes == baseline_bytes
            assert current_hashes == baseline_hashes

    assert baseline_bytes is not None
    assert baseline_hashes is not None
    assert len(set(baseline_hashes)) == 12


def test_v6_single_byte_tamper_changes_independent_digest_without_execution() -> None:
    messages, evidence_bundle = _build_full_chain()
    original = messages["result_message"]
    original_hash = _independent_digest(original)
    tampered = dict(original)
    tampered["summary"] = str(tampered["summary"]) + "-tampered"

    assert _independent_digest(tampered) != original_hash
    assert validate_blackboard_message(tampered, "result_message")["valid"] is True
    assert verify_bundle_hash(evidence_bundle) is True
