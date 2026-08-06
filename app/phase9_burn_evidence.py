"""Pure builder for the Phase 9 pre-call burn evidence event.

The builder deliberately has no ledger knowledge.  Its caller supplies the
current audit-chain predecessor, while the injected audit writer owns append,
durability, and post-append chain verification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from app.phase9_gate import BurnRecord


class BurnEvidenceBuildError(ValueError):
    """Payload-free rejection at the burn-evidence construction boundary."""


_EVENT_FIELDS = frozenset(
    {
        "schema_version",
        "message_type",
        "created_at",
        "safety_flags",
        "prev_entry_hash",
        "execution_class",
        "produced_by",
        "parent_task_id",
        "role",
        "audit_id",
        "event_id",
        "task_id",
        "related_result_id",
        "event_type",
        "event_notes",
        "audit_status",
        "persistence_target",
        "preview_only",
    }
)


def _identifier(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BurnEvidenceBuildError(f"{name} must be a non-empty identifier")
    if len(value) > 256 or any(character in value for character in "\x00\r\n"):
        raise BurnEvidenceBuildError(f"{name} is not a safe identifier")
    return value


def _previous_hash(value: str | None) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise BurnEvidenceBuildError("prev_entry_hash must be null or lowercase SHA-256")
    return value


def _created_at(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise BurnEvidenceBuildError("burned_at must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _safety_flags() -> dict[str, bool]:
    """Describe this audit append only, not the later executor capability."""

    return {
        "synthetic_local_only": False,
        "mock_only": False,
        "dry_run": False,
        "owner_review_required": True,
        "external_side_effects_allowed": False,
        "external_side_effects_occurred": False,
        "blackboard_write_allowed": False,
        "queue_write_allowed": False,
        "audit_trail_write_allowed": True,
        "worker_dispatch_allowed": False,
        "openclaw_call_allowed": False,
        "hermes_runtime_allowed": False,
        "connector_call_allowed": False,
        "google_sheets_write_allowed": False,
        "follow_up_allowed": False,
        "follow_up_requires_owner_confirmation": True,
    }


def validate_phase9_burn_evidence(event: Mapping[str, object]) -> None:
    """Reject any shape or posture outside this one persisted event type."""

    if not isinstance(event, Mapping) or set(event) != _EVENT_FIELDS:
        raise BurnEvidenceBuildError("burn evidence fields are not closed")
    if (
        event.get("schema_version") != "1.0"
        or event.get("message_type") != "audit_event"
        or event.get("execution_class") != "OWNER_MANUAL"
        or event.get("produced_by") != "phase9-gate"
        or event.get("parent_task_id") is not None
        or event.get("role") != "phase9_burn_evidence_recorder"
        or event.get("event_type") != "phase9_single_use_authorization_burned"
        or event.get("audit_status") != "persisted"
        or event.get("persistence_target") != "data/audit_dev.jsonl"
        or event.get("preview_only") is not False
    ):
        raise BurnEvidenceBuildError("burn evidence posture is invalid")
    if event.get("safety_flags") != _safety_flags():
        raise BurnEvidenceBuildError("burn evidence safety flags are invalid")
    predecessor = event.get("prev_entry_hash")
    if predecessor is not None and not isinstance(predecessor, str):
        raise BurnEvidenceBuildError("prev_entry_hash has an invalid type")
    _previous_hash(predecessor)
    for field_name in ("audit_id", "event_id", "task_id", "related_result_id"):
        identifier = event.get(field_name)
        if not isinstance(identifier, str):
            raise BurnEvidenceBuildError(f"{field_name} has an invalid type")
        _identifier(field_name, identifier)
    if not isinstance(event.get("created_at"), str):
        raise BurnEvidenceBuildError("burn evidence created_at is invalid")
    if not isinstance(event.get("event_notes"), str) or not event["event_notes"]:
        raise BurnEvidenceBuildError("burn evidence notes are invalid")


def build_phase9_burn_evidence(
    burn_record: BurnRecord,
    *,
    audit_id: str,
    event_id: str,
    task_id: str,
    related_result_id: str,
    prev_entry_hash: str | None,
) -> dict[str, object]:
    """Return one closed-schema audit event without performing any I/O.

    ``prev_entry_hash`` is an explicit input because only the writer/caller can
    observe the physical audit tail.  Guessing or repairing it here would make
    this pure builder an unsafe second source of chain state.
    """

    if not isinstance(burn_record, BurnRecord):
        raise BurnEvidenceBuildError("burn_record must be a BurnRecord")
    if not burn_record.rehearsal_id.strip():
        raise BurnEvidenceBuildError("burn record rehearsal identifier is invalid")
    if burn_record.attempt_number < 1:
        raise BurnEvidenceBuildError("burn record attempt number is invalid")

    event: dict[str, object] = {
        "schema_version": "1.0",
        "message_type": "audit_event",
        "created_at": _created_at(burn_record.burned_at),
        "safety_flags": _safety_flags(),
        "prev_entry_hash": _previous_hash(prev_entry_hash),
        "execution_class": "OWNER_MANUAL",
        "produced_by": "phase9-gate",
        "parent_task_id": None,
        "role": "phase9_burn_evidence_recorder",
        "audit_id": _identifier("audit_id", audit_id),
        "event_id": _identifier("event_id", event_id),
        "task_id": _identifier("task_id", task_id),
        "related_result_id": _identifier(
            "related_result_id",
            related_result_id,
        ),
        "event_type": "phase9_single_use_authorization_burned",
        "event_notes": (
            "The Phase 9 one-shot authorization was consumed before any "
            "OpenClaw call."
        ),
        "audit_status": "persisted",
        "persistence_target": "data/audit_dev.jsonl",
        "preview_only": False,
    }
    validate_phase9_burn_evidence(event)
    return event


__all__ = [
    "BurnEvidenceBuildError",
    "build_phase9_burn_evidence",
    "validate_phase9_burn_evidence",
]
