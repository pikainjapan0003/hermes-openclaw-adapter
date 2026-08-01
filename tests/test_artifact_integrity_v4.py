"""Unified normalized-byte inventory for schemas, fixtures, and golden data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.test_fixture_sha256_inventory import EXPECTED_SHA256


pytestmark = pytest.mark.contract

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "docs" / "schemas"
FIXTURE_ROOT = ROOT / "fixtures"

# This is the single round-four inventory consumed by both the closed path guard
# and the digest check.  The reviewed 50-fixture table is included verbatim and
# extended with every schema; research reports are intentionally out of scope.
EXPECTED_ARTIFACT_SHA256 = {
    **EXPECTED_SHA256,
    "docs/schemas/blackboard/annotation.schema.json": "2476d889a6a075d1b1e5bcd61d4ca5d7b61d1e1af9b6a5994626bc86672cfebd",
    "docs/schemas/blackboard/approval_packet.schema.json": "03a1edb77e308b6a08c2436fd73b5aad6eba63b7c3f304225b25efc442646b23",
    "docs/schemas/blackboard/approval_readiness.schema.json": "1dbdf7e248da5bb803387c220789b08184e6568a747719a6f34f7922ff1fa3b6",
    "docs/schemas/blackboard/audit_event.schema.json": "f62147e2e93265aaae0c14dcec6aac8aae38a0741eac777f6264cd2b8e926df7",
    "docs/schemas/blackboard/openclaw_command_envelope.schema.json": "2d3b629d99a1edf67fa03ed10bad2b91917453e2a395fbe4079b3cc8478c0f4e",
    "docs/schemas/blackboard/owner_decision.schema.json": "b7a127143c7384ac4112d447a1f044384d54c6c563f14a093af0f23f7e1f2f3f",
    "docs/schemas/blackboard/result_message.schema.json": "32ae59130813ef80a54519af849767c1773723949f10f9e6b775a4ad80876b95",
    "docs/schemas/blackboard/rollback_event.schema.json": "fe03bf333a11e5bfb7ac2739418dc3d43e68d2e0fe4f6d698cf947055d042098",
    "docs/schemas/blackboard/task_draft.schema.json": "17b8179216a493d05e1d50d9abedbd14df2d374253d4e3504c507f40657bfa63",
    "docs/schemas/blackboard/worker_dry_run.schema.json": "d4186db27eed91c62539b6b18089718774567784445daee3deff6d7f3b264156",
    "docs/schemas/callback_event_v0_7.schema.json": "9d179c664c8119e9ed32980fd180238edc51bc1218de10a76b57d72e384f01a6",
    "docs/schemas/evidence_bundle.json": "4f9f6afaaa6cfafe33d197fc2c6602292d4c0ccc6df013280c48ed0fa1544f2f",
    "docs/schemas/remote_readonly_projection.schema.json": "3e38136785999adfdd89491ab2abe8c7b061568405a75cd72938ca478ed38ece",
    "docs/schemas/task_envelope_v0_7.schema.json": "3678f13627eb2aeee354c987914fd86b5d4de4a205165bfbc517e0d867153304",
    "docs/schemas/three_source_report.schema.json": "9f0b9d2d4542a9929a54b45dba627221882842baed6037436df8763ac89ca035",
}


def _verifiable_paths() -> set[str]:
    paths = {
        path.relative_to(ROOT).as_posix()
        for path in FIXTURE_ROOT.rglob("*")
        if path.is_file()
    }
    paths.update(
        path.relative_to(ROOT).as_posix()
        for path in SCHEMA_ROOT.rglob("*.json")
        if path.is_file()
    )
    return paths


def _normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    assert b"\r" not in normalized, f"bare CR is not a portable artifact: {path}"
    return normalized


def test_v4_inventory_is_the_exact_nonresearch_verifiable_artifact_set() -> None:
    actual = _verifiable_paths()
    expected = set(EXPECTED_ARTIFACT_SHA256)

    assert len(expected) == 65
    assert actual == expected, {
        "unregistered": sorted(actual - expected),
        "missing": sorted(expected - actual),
    }


@pytest.mark.parametrize("relative_path", sorted(EXPECTED_ARTIFACT_SHA256))
def test_v4_normalized_artifact_digest_matches_single_inventory(
    relative_path: str,
) -> None:
    path = ROOT / relative_path
    normalized = _normalized_bytes(path)

    assert hashlib.sha256(normalized).hexdigest() == EXPECTED_ARTIFACT_SHA256[
        relative_path
    ]
    decoded = json.loads(normalized.decode("utf-8"))
    assert isinstance(decoded, dict), relative_path


def test_v4_inventory_covers_each_required_family() -> None:
    paths = set(EXPECTED_ARTIFACT_SHA256)
    assert any(path.startswith("docs/schemas/blackboard/") for path in paths)
    assert any(path.startswith("fixtures/blackboard_contract/") for path in paths)
    assert any(path.startswith("fixtures/builder_golden_vectors/") for path in paths)
    assert any(path.startswith("fixtures/hash_chain_vectors/") for path in paths)
    assert any(path.startswith("fixtures/local_mock_data/") for path in paths)
    assert all("/research/" not in path for path in paths)
