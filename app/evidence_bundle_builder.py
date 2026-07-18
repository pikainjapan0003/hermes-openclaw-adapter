"""Pure Phase 5 evidence-bundle builder for one harmless N=1 query.

The builder accepts in-memory task, command-envelope, and mock-result records,
then copies only explicitly allowlisted fields into a deterministic bundle.  It
does not read or write files, inspect environment variables, dispatch work, or
call any runtime.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Mapping, Sequence


_FORBIDDEN_FIELD_MARKERS = (
    "token",
    "secret",
    "password",
    "authorization",
    "credential",
    "api_key",
    "apikey",
    "private_key",
    "environment",
    "env",
    "path",
)
_SECRET_VALUE_PATTERN = re.compile(
    r"(?:\bsk-[A-Za-z0-9_-]{16,}\b|\bghp_[A-Za-z0-9]{20,}\b|"
    r"\bgithub_pat_[A-Za-z0-9_]{20,}\b|\bxox[baprs]-[A-Za-z0-9-]{16,}\b|"
    r"\bAIza[A-Za-z0-9_-]{20,}\b|-----BEGIN [A-Z ]*PRIVATE KEY-----)",
    re.IGNORECASE,
)
_REAL_PATH_PATTERN = re.compile(
    r"^(?:[A-Za-z]:[\\/]|/(?:home|users|etc|var|tmp|opt|srv|root)(?:/|$))",
    re.IGNORECASE,
)
_REMOTE_URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)

_MOCK_FALSE_FIELDS = (
    "worker_loop_started",
    "worker_dispatched",
    "real_openclaw_called",
    "external_side_effects_performed",
    "queue_written",
    "audit_trail_written",
)
_GATEWAY_FALSE_FIELDS = (
    "production_gateway",
    "real_openclaw_called",
    "worker_dispatched",
    "external_side_effects_performed",
    "queue_written",
    "audit_trail_written",
)


class EvidenceBundleError(ValueError):
    """Raised when the supplied rehearsal evidence is incomplete or unsafe."""


class SensitiveEvidenceError(EvidenceBundleError):
    """Raised when input contains a secret-, environment-, or path-like value."""


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceBundleError(f"{name} must be an object")
    return value


def _text(record: Mapping[str, Any], field: str, owner: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise EvidenceBundleError(f"{owner}.{field} must be non-empty text")
    return value


def _scan_sensitive(value: Any, location: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(marker in lowered for marker in _FORBIDDEN_FIELD_MARKERS):
                raise SensitiveEvidenceError(
                    f"forbidden sensitive field at {location}.{key_text}"
                )
            _scan_sensitive(child, f"{location}.{key_text}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _scan_sensitive(child, f"{location}[{index}]")
        return
    if isinstance(value, str) and (
        _SECRET_VALUE_PATTERN.search(value)
        or _REAL_PATH_PATTERN.search(value)
        or _REMOTE_URL_PATTERN.search(value)
    ):
        raise SensitiveEvidenceError(f"forbidden sensitive value at {location}")


def _require_false(record: Mapping[str, Any], fields: Sequence[str], owner: str) -> None:
    for field in fields:
        if record.get(field) is not False:
            raise EvidenceBundleError(f"{owner}.{field} must be false")


def compute_bundle_hash(bundle: Mapping[str, Any]) -> str:
    """Compute SHA-256 over canonical JSON, excluding ``bundle_hash`` itself."""

    if not isinstance(bundle, Mapping):
        raise EvidenceBundleError("bundle must be an object")
    canonical_payload = {
        str(key): value for key, value in bundle.items() if key != "bundle_hash"
    }
    canonical_json = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def verify_bundle_hash(bundle: Mapping[str, Any]) -> bool:
    """Return whether the stored bundle hash matches a fresh recomputation."""

    if not isinstance(bundle, Mapping):
        return False
    stored_hash = bundle.get("bundle_hash")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        return False
    return hmac.compare_digest(stored_hash, compute_bundle_hash(bundle))


def build_evidence_bundle(
    task: Mapping[str, Any],
    command_envelope: Mapping[str, Any],
    mock_result: Mapping[str, Any],
    expected_side_effects: Sequence[str],
    *,
    created_at: str,
) -> dict[str, Any]:
    """Build deterministic evidence for a synthetic, harmless N=1 query.

    The returned data is evidence only.  It is not approval, execution
    permission, dispatch permission, or an execution token.
    """

    task = _mapping(task, "task")
    command_envelope = _mapping(command_envelope, "command_envelope")
    mock_result = _mapping(mock_result, "mock_result")
    gateway_response = _mapping(mock_result.get("gateway_response"), "gateway_response")

    _scan_sensitive(task, "task")
    _scan_sensitive(command_envelope, "command_envelope")
    _scan_sensitive(mock_result, "mock_result")

    if not isinstance(created_at, str) or not created_at:
        raise EvidenceBundleError("created_at must be non-empty text")
    if not isinstance(expected_side_effects, Sequence) or isinstance(
        expected_side_effects, (str, bytes)
    ):
        raise EvidenceBundleError("expected_side_effects must be an array")
    if list(expected_side_effects) != []:
        raise EvidenceBundleError("N=1 query expected_side_effects must be empty")

    task_id = _text(task, "task_id", "task")
    if task.get("task_type") != "query":
        raise EvidenceBundleError("task.task_type must be query")
    if task.get("target_runtime") != "openclaw_mock":
        raise EvidenceBundleError("task.target_runtime must be openclaw_mock")
    if task.get("execution_class") != "AUTO":
        raise EvidenceBundleError("task.execution_class must be AUTO")

    command_id = _text(command_envelope, "command_id", "command_envelope")
    if command_envelope.get("task_id") != task_id:
        raise EvidenceBundleError("command_envelope.task_id must match task.task_id")
    if command_envelope.get("risk_level") != "low":
        raise EvidenceBundleError("command_envelope.risk_level must be low")
    if command_envelope.get("execution_mode") != "mock_only":
        raise EvidenceBundleError("command_envelope.execution_mode must be mock_only")
    if command_envelope.get("dry_run") is not True:
        raise EvidenceBundleError("command_envelope.dry_run must be true")
    if command_envelope.get("mock_only") is not True:
        raise EvidenceBundleError("command_envelope.mock_only must be true")
    if command_envelope.get("external_touchpoints") != []:
        raise EvidenceBundleError("command_envelope.external_touchpoints must be empty")
    if command_envelope.get("external_side_effects_allowed") is not False:
        raise EvidenceBundleError(
            "command_envelope.external_side_effects_allowed must be false"
        )

    if mock_result.get("source") != "synthetic_local_only":
        raise EvidenceBundleError("mock_result.source must be synthetic_local_only")
    if mock_result.get("accepted") is not True:
        raise EvidenceBundleError("mock_result.accepted must be true")
    if mock_result.get("worker_dry_run") is not True:
        raise EvidenceBundleError("mock_result.worker_dry_run must be true")
    if mock_result.get("mock_gateway_called") is not True:
        raise EvidenceBundleError("mock_result.mock_gateway_called must be true")
    _require_false(mock_result, _MOCK_FALSE_FIELDS, "mock_result")

    if gateway_response.get("response_source") != "synthetic_local_only":
        raise EvidenceBundleError(
            "gateway_response.response_source must be synthetic_local_only"
        )
    if gateway_response.get("accepted") is not True:
        raise EvidenceBundleError("gateway_response.accepted must be true")
    if gateway_response.get("mock_gateway") is not True:
        raise EvidenceBundleError("gateway_response.mock_gateway must be true")
    _require_false(gateway_response, _GATEWAY_FALSE_FIELDS, "gateway_response")
    if gateway_response.get("task_id") != task_id:
        raise EvidenceBundleError("gateway_response.task_id must match task.task_id")
    if gateway_response.get("command_id") != command_id:
        raise EvidenceBundleError(
            "gateway_response.command_id must match command_envelope.command_id"
        )
    if gateway_response.get("tool_target") != command_envelope.get("tool_target"):
        raise EvidenceBundleError(
            "gateway_response.tool_target must match command_envelope.tool_target"
        )

    bundle: dict[str, Any] = {
        "schema_version": "1.0",
        "bundle_type": "n1_dry_run_evidence",
        "bundle_id": f"evidence-{task_id}-{command_id}",
        "created_at": created_at,
        "task": {
            "task_id": task_id,
            "title": _text(task, "title", "task"),
            "summary": _text(task, "summary", "task"),
            "task_type": "query",
            "target_runtime": "openclaw_mock",
            "execution_class": "AUTO",
        },
        "command_envelope": {
            "command_id": command_id,
            "task_id": task_id,
            "tool_target": _text(command_envelope, "tool_target", "command_envelope"),
            "requested_action": _text(
                command_envelope, "requested_action", "command_envelope"
            ),
            "risk_level": "low",
            "owner_review_required": _mapping(
                command_envelope.get("approval_snapshot"), "approval_snapshot"
            ).get("owner_review_required"),
            "execution_mode": "mock_only",
            "dry_run": True,
            "mock_only": True,
            "external_touchpoints": [],
            "rollback_plan": _text(
                command_envelope, "rollback_plan", "command_envelope"
            ),
            "external_side_effects_allowed": False,
        },
        "mock_result": {
            "source": "synthetic_local_only",
            "accepted": True,
            "worker_dry_run": True,
            "worker_loop_started": False,
            "worker_dispatched": False,
            "real_openclaw_called": False,
            "external_side_effects_performed": False,
            "queue_written": False,
            "audit_trail_written": False,
            "mock_gateway_called": True,
            "gateway_response": {
                "response_source": "synthetic_local_only",
                "accepted": True,
                "mock_gateway": True,
                "production_gateway": False,
                "real_openclaw_called": False,
                "worker_dispatched": False,
                "external_side_effects_performed": False,
                "queue_written": False,
                "audit_trail_written": False,
                "command_id": command_id,
                "task_id": task_id,
                "tool_target": _text(
                    gateway_response, "tool_target", "gateway_response"
                ),
                "mock_response_summary": _text(
                    gateway_response,
                    "mock_response_summary",
                    "gateway_response",
                ),
            },
        },
        "expected_side_effects": [],
        "diff_preview": {
            "applicable": False,
            "summary": "No diff is applicable to a read-only mock query.",
        },
        "hash_algorithm": "sha256",
    }
    if bundle["command_envelope"]["owner_review_required"] is not True:
        raise EvidenceBundleError(
            "command_envelope.approval_snapshot.owner_review_required must be true"
        )
    bundle["bundle_hash"] = compute_bundle_hash(bundle)
    return bundle
