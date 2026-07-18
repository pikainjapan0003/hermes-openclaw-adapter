"""Pure Phase 8-A offline display-projection builder and validator.

This module has no file, network, queue, dashboard, runtime, execution, or dispatch IO.
The projection is a lossy display object, not a Blackboard message or transport envelope.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any, Mapping

from jsonschema import Draft202012Validator, FormatChecker


PROJECTION_SCHEMA_VERSION = "1.0"

CANONICAL_SAFETY_FLAG_KEYS = frozenset(
    {
        "synthetic_local_only",
        "mock_only",
        "dry_run",
        "owner_review_required",
        "external_side_effects_allowed",
        "external_side_effects_occurred",
        "blackboard_write_allowed",
        "queue_write_allowed",
        "audit_trail_write_allowed",
        "worker_dispatch_allowed",
        "openclaw_call_allowed",
        "hermes_runtime_allowed",
        "connector_call_allowed",
        "google_sheets_write_allowed",
        "follow_up_allowed",
        "follow_up_requires_owner_confirmation",
    }
)

SAFETY_SUMMARY_KEYS = (
    "synthetic_local_only",
    "mock_only",
    "dry_run",
    "owner_review_required",
    "external_side_effects_allowed",
    "external_side_effects_occurred",
    "worker_dispatch_allowed",
    "openclaw_call_allowed",
    "hermes_runtime_allowed",
    "connector_call_allowed",
)

SAFE_POSTURE = {
    "synthetic_local_only": True,
    "mock_only": True,
    "dry_run": True,
    "owner_review_required": True,
    "external_side_effects_allowed": False,
    "external_side_effects_occurred": False,
    "worker_dispatch_allowed": False,
    "openclaw_call_allowed": False,
    "hermes_runtime_allowed": False,
    "connector_call_allowed": False,
}

SOURCE_FIELDS = frozenset(
    {
        "task_id",
        "parent_task_id",
        "phase",
        "status",
        "execution_class",
        "safety_flags",
        "approval_readiness",
        "decision",
        "decision_timestamp",
        "evidence_bundle_hash",
    }
)

PHASES = frozenset(
    {"task_draft", "dry_run", "evidence_ready", "approval_ready", "owner_decided", "failed"}
)
STATUSES = frozenset({"pending", "ready", "decided", "failed"})
EXECUTION_CLASSES = frozenset({"AUTO", "OWNER_APPROVAL", "OWNER_MANUAL"})
APPROVAL_READINESS_VALUES = frozenset({"not_ready", "ready_for_owner", "blocked"})
DECISIONS = frozenset({"approve", "edit", "reject", "respond"})

_COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_PROHIBITED_KEY_RE = re.compile(
    r"(?:token|secret|password|credential|authorization|cookie|environment|env|path|"
    r"payload|prompt|command|argument|callback|webhook|result_body|task_text|stack_trace)",
    re.IGNORECASE,
)
_PROHIBITED_VALUE_RES = (
    re.compile(
        r"(?:^|[^A-Za-z0-9])(?:sk|ghp|github_pat|xox[baprs])[-_][A-Za-z0-9_-]{12,}"
    ),
    re.compile(r"[A-Za-z]:[\\/]"),
    re.compile(r"(?:^|\s)/(?:home|users|mnt|etc|var|tmp)/", re.IGNORECASE),
    re.compile(r"https?://", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
)


class RemoteReadonlyProjectionError(ValueError):
    """Raised when an offline source cannot be safely projected."""


def _require_exact_fields(value: Mapping[str, Any], expected: frozenset[str], name: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise RemoteReadonlyProjectionError(
            f"{name} fields must be exact; missing={missing}, extra={extra}"
        )


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RemoteReadonlyProjectionError(f"{name} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: Any, name: str) -> datetime:
    text = _require_string(value, name)
    if not text.endswith("Z"):
        raise RemoteReadonlyProjectionError(f"{name} must be an explicit UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise RemoteReadonlyProjectionError(f"{name} must be an ISO-8601 timestamp") from exc
    return parsed


def _display_id(prefix: str, raw_id: Any) -> str:
    text = _require_string(raw_id, f"{prefix}_source_id")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _project_safety_summary(value: Any) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        raise RemoteReadonlyProjectionError("safety_flags must be an object")
    _require_exact_fields(value, CANONICAL_SAFETY_FLAG_KEYS, "safety_flags")
    if any(type(value[key]) is not bool for key in CANONICAL_SAFETY_FLAG_KEYS):
        raise RemoteReadonlyProjectionError("all safety_flags values must be booleans")
    for key, expected in SAFE_POSTURE.items():
        if value[key] is not expected:
            raise RemoteReadonlyProjectionError(
                f"unsafe projection source: safety_flags.{key} must be {expected}"
            )
    return {key: value[key] for key in SAFETY_SUMMARY_KEYS}


def _projection_leaks(value: Any, path: str = "$") -> list[dict[str, str]]:
    leaks: list[dict[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if _PROHIBITED_KEY_RE.search(str(key)):
                leaks.append(
                    {
                        "path": child_path,
                        "validator": "projectionLeak",
                        "message": "prohibited field name in display projection",
                    }
                )
            leaks.extend(_projection_leaks(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            leaks.extend(_projection_leaks(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if any(pattern.search(value) for pattern in _PROHIBITED_VALUE_RES):
            leaks.append(
                {
                    "path": path,
                    "validator": "projectionLeak",
                    "message": "prohibited secret, URL, or filesystem-path pattern",
                }
            )
    return leaks


def build_remote_readonly_projection(
    source: Mapping[str, Any],
    *,
    data_generated_at: str,
    source_commit_sha: str,
    stale_after: str,
) -> dict[str, Any]:
    """Build one closed, offline N=1 display projection without mutating ``source``."""

    if not isinstance(source, Mapping):
        raise RemoteReadonlyProjectionError("source must be an object")
    _require_exact_fields(source, SOURCE_FIELDS, "source")

    generated = _parse_timestamp(data_generated_at, "data_generated_at")
    stale = _parse_timestamp(stale_after, "stale_after")
    if stale <= generated:
        raise RemoteReadonlyProjectionError("stale_after must be later than data_generated_at")

    commit_sha = _require_string(source_commit_sha, "source_commit_sha")
    if not _COMMIT_RE.fullmatch(commit_sha):
        raise RemoteReadonlyProjectionError("source_commit_sha must be 40 or 64 lowercase hex chars")

    phase = _require_string(source["phase"], "phase")
    status = _require_string(source["status"], "status")
    execution_class = _require_string(source["execution_class"], "execution_class")
    readiness = _require_string(source["approval_readiness"], "approval_readiness")
    evidence_hash = _require_string(source["evidence_bundle_hash"], "evidence_bundle_hash")
    if phase not in PHASES:
        raise RemoteReadonlyProjectionError("phase is outside the N=1 display enum")
    if status not in STATUSES:
        raise RemoteReadonlyProjectionError("status is outside the N=1 display enum")
    if execution_class not in EXECUTION_CLASSES:
        raise RemoteReadonlyProjectionError("execution_class is invalid")
    if readiness not in APPROVAL_READINESS_VALUES:
        raise RemoteReadonlyProjectionError("approval_readiness is invalid")
    if not _HASH_RE.fullmatch(evidence_hash):
        raise RemoteReadonlyProjectionError("evidence_bundle_hash must be 64 lowercase hex chars")

    decision = source["decision"]
    decision_timestamp = source["decision_timestamp"]
    if status == "decided":
        if phase != "owner_decided":
            raise RemoteReadonlyProjectionError("decided status requires owner_decided phase")
        if decision not in DECISIONS:
            raise RemoteReadonlyProjectionError("decided status requires a valid decision")
        _parse_timestamp(decision_timestamp, "decision_timestamp")
    elif decision is not None or decision_timestamp is not None or phase == "owner_decided":
        raise RemoteReadonlyProjectionError(
            "non-decided projection requires null decision fields and a non-decision phase"
        )

    projection = {
        "projection_schema_version": PROJECTION_SCHEMA_VERSION,
        "data_generated_at": data_generated_at,
        "source_commit_sha": commit_sha,
        "pulled_at": None,
        "task_display_id": _display_id("task", source["task_id"]),
        "parent_task_display_id": _display_id("parent", source["parent_task_id"]),
        "phase": phase,
        "status": status,
        "execution_class": execution_class,
        "safety_summary": _project_safety_summary(source["safety_flags"]),
        "approval_readiness": readiness,
        "decision_summary": {
            "decision": decision,
            "decision_timestamp": decision_timestamp,
        },
        "evidence_bundle_hash": evidence_hash,
        "stale_after": stale_after,
    }
    leaks = _projection_leaks(projection)
    if leaks:
        raise RemoteReadonlyProjectionError(f"projection leak guard rejected output: {leaks}")
    return projection


def validate_remote_readonly_projection(
    projection: Any, schema: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate a projection against an injected schema and return structured errors."""

    if not isinstance(projection, Mapping):
        return {
            "valid": False,
            "schema": "remote_readonly_projection",
            "errors": [
                {
                    "path": "$",
                    "validator": "type",
                    "message": "projection must be an object",
                }
            ],
        }
    if not isinstance(schema, Mapping):
        return {
            "valid": False,
            "schema": "remote_readonly_projection",
            "errors": [
                {
                    "path": "$",
                    "validator": "schema",
                    "message": "schema must be an object",
                }
            ],
        }

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[dict[str, str]] = []
    for error in validator.iter_errors(projection):
        suffix = "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
        )
        errors.append(
            {
                "path": f"${suffix}",
                "validator": str(error.validator),
                "message": error.message,
            }
        )
    errors.extend(_projection_leaks(projection))
    errors.sort(key=lambda item: (item["path"], item["validator"], item["message"]))
    return {
        "valid": not errors,
        "schema": "remote_readonly_projection",
        "errors": errors,
    }
