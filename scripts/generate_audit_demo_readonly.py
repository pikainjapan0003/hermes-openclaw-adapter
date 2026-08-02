"""Generate three harmless local Phase 7 audit preview records.

This script is intentionally append-only.  Its only runtime write is the
authorized ``data/audit_dev.jsonl`` target through ``append_audit_event``.
It never removes, truncates, rewrites, or recreates a ledger.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.audit_writer_local import AUDIT_PATH, append_audit_event, read_audit_events
from app.hash_chain import entry_hash, verify_chain


SAFETY_FLAGS = {
    "synthetic_local_only": True,
    "mock_only": True,
    "dry_run": True,
    "owner_review_required": True,
    "external_side_effects_allowed": False,
    "external_side_effects_occurred": False,
    "blackboard_write_allowed": False,
    "queue_write_allowed": False,
    "audit_trail_write_allowed": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "hermes_runtime_allowed": False,
    "connector_call_allowed": False,
    "google_sheets_write_allowed": False,
    "follow_up_allowed": False,
    "follow_up_requires_owner_confirmation": True,
}


def _timestamp(index: int) -> str:
    value = datetime(2026, 8, 3, tzinfo=timezone.utc) + timedelta(seconds=index)
    return value.isoformat().replace("+00:00", "Z")


def _demo_event(index: int, previous: str | None) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "message_type": "audit_event",
        "created_at": _timestamp(index),
        "safety_flags": dict(SAFETY_FLAGS),
        "prev_entry_hash": previous,
        "execution_class": "AUTO",
        "produced_by": "phase7-owner-demo",
        "parent_task_id": None,
        "role": "audit_recorder_preview",
        "audit_id": f"audit-phase7-demo-{index:03d}",
        "event_id": f"audit-phase7-demo-event-{index:03d}",
        "task_id": "task-phase7-demo-n1",
        "related_result_id": "result-phase7-demo-n1",
        "event_type": "n1_preview_record",
        "event_notes": "Synthetic local preview; no task executed and no side effect occurred.",
        "audit_status": "preview_audit_not_persisted",
        "persistence_target": "none",
        "preview_only": True,
    }


def main() -> None:
    existing = read_audit_events()
    previous = None if not existing else entry_hash(existing[-1])
    start = len(existing) + 1
    for offset in range(3):
        event = _demo_event(start + offset, previous)
        result = append_audit_event(event)
        previous = str(result["entry_hash"])

    entries = read_audit_events()
    raw = AUDIT_PATH.read_bytes()
    print(f"AUDIT_PATH={AUDIT_PATH}")
    for index, entry in enumerate(entries, start=1):
        print(f"RECORD_{index}={json.dumps(entry, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}")
    print(f"VERIFY_CHAIN={verify_chain(entries)}")
    print(f"FILE_SHA256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
