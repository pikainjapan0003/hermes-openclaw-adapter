"""v0.8.1-P local filesystem read-only loader for the synthetic local-only mock fixture JSON.

Authorized by the exact v0.8.1-O Owner authorization phrase. This loader only reads the already
validated synthetic local-only fixture JSON and returns an in-memory read-only preview data object.

Strict boundaries (per v0.8.1-N contract and v0.8.1-O authorization conditions):
- standard library only; imports no app runtime, no QueueStore, no Dashboard, no Worker/OpenClaw/
  Hermes/Google Sheets integration
- reads only fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json
- runs the v0.8.1-M validation script before reading fixture data
- reads no secrets, no .env, no real queue DB
- sends no POST, makes no network call
- writes no repo file, modifies no fixture, creates no runtime / route / endpoint / template /
  static asset
- returns a new dict (records deep-copied); output permission flags are all False
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json"
M_VALIDATION_SCRIPT = REPO_ROOT / "scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py"

EXPECTED_SCHEMA_VERSION = "v0.8.1-local-mock-1"
EXPECTED_RECORD_COUNT = 6

RUNTIME_BADGES = [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED",
]


def _run_m_validation() -> None:
    """Run the v0.8.1-M validation script; raise RuntimeError if it does not pass.

    Uses the current Python interpreter to execute the tracked validation script as a subprocess.
    This performs no network access and does not modify the git index or any file.
    """
    result = subprocess.run(
        [sys.executable, str(M_VALIDATION_SCRIPT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "v0.8.1-M validation failed; refusing to load fixture preview.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def load_local_mock_fixture_preview() -> dict[str, Any]:
    """Return an in-memory read-only preview data object built from the validated fixture JSON.

    The v0.8.1-M validation script is run first; if it fails a RuntimeError is raised and no fixture
    data is loaded. The returned object is a new dict (records are deep-copied) with all permission
    flags set to False.
    """
    _run_m_validation()

    raw = FIXTURE_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)

    if not isinstance(data, dict):
        raise ValueError("fixture JSON top-level value must be an object")

    if data.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise ValueError(
            f"unexpected schema_version: {data.get('schema_version')!r} "
            f"(expected {EXPECTED_SCHEMA_VERSION!r})"
        )

    if data.get("is_mock") is not True:
        raise ValueError("fixture is_mock must be True")

    records = data.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_RECORD_COUNT:
        raise ValueError(
            f"fixture records must be a list of {EXPECTED_RECORD_COUNT} items"
        )

    invariants = data.get("safety_invariants", {})
    if not isinstance(invariants, dict):
        raise ValueError("fixture safety_invariants must be an object")
    if invariants.get("execution_permission") is not False:
        raise ValueError("fixture safety_invariants.execution_permission must be False")
    if invariants.get("dispatch_permission") is not False:
        raise ValueError("fixture safety_invariants.dispatch_permission must be False")
    if invariants.get("external_side_effects_permission") is not False:
        raise ValueError(
            "fixture safety_invariants.external_side_effects_permission must be False"
        )

    return {
        "source": "local_mock_fixture",
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "is_mock": True,
        "local_only": True,
        "read_only": True,
        "records": copy.deepcopy(records),
        "runtime_badges": list(RUNTIME_BADGES),
        "execution_permission": False,
        "dispatch_permission": False,
        "external_side_effects_permission": False,
    }


def validate_local_mock_fixture_preview_object(preview: dict[str, Any]) -> None:
    """Validate the shape and safety flags of a preview object; raise ValueError on any mismatch.

    This is an in-memory check only. It performs no I/O, no network access, and no fixture read.
    """
    if not isinstance(preview, dict):
        raise ValueError("preview must be a dict")

    if preview.get("source") != "local_mock_fixture":
        raise ValueError("preview.source must be 'local_mock_fixture'")
    if preview.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise ValueError("preview.schema_version must be v0.8.1-local-mock-1")
    if preview.get("is_mock") is not True:
        raise ValueError("preview.is_mock must be True")
    if preview.get("local_only") is not True:
        raise ValueError("preview.local_only must be True")
    if preview.get("read_only") is not True:
        raise ValueError("preview.read_only must be True")

    records = preview.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_RECORD_COUNT:
        raise ValueError(f"preview.records must be a list of {EXPECTED_RECORD_COUNT} items")

    if preview.get("runtime_badges") != list(RUNTIME_BADGES):
        raise ValueError("preview.runtime_badges must match the disabled-runtime badge list")

    if preview.get("execution_permission") is not False:
        raise ValueError("preview.execution_permission must be False")
    if preview.get("dispatch_permission") is not False:
        raise ValueError("preview.dispatch_permission must be False")
    if preview.get("external_side_effects_permission") is not False:
        raise ValueError("preview.external_side_effects_permission must be False")
