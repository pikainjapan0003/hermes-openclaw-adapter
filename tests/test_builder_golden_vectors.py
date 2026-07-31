"""Golden vectors freezing both deterministic N=1 contract builders."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from app.approval_packet_builder import build_approval_packet
from app.evidence_bundle_builder import build_evidence_bundle, compute_bundle_hash
from app.worker_mock_gateway_dry_run import run_worker_to_mock_gateway_dry_run


ROOT = Path(__file__).resolve().parent.parent
VECTOR_DIR = ROOT / "fixtures" / "builder_golden_vectors"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


APPROVAL_VECTORS = _load(VECTOR_DIR / "approval_packet_vectors.json")
EVIDENCE_VECTORS = _load(VECTOR_DIR / "evidence_bundle_vectors.json")


@pytest.mark.parametrize(
    "vector",
    APPROVAL_VECTORS["vectors"],
    ids=lambda vector: vector["name"],
)
def test_approval_packet_golden_vectors(vector: dict[str, Any]) -> None:
    sources = APPROVAL_VECTORS["source_files"]
    worker_dry_run = _load(ROOT / sources["worker_dry_run"])
    result_message = _load(ROOT / sources["result_message"])
    expected = _load(ROOT / APPROVAL_VECTORS["expected_output_template"])
    expected.update(vector["expected_overrides"])

    actual = build_approval_packet(worker_dry_run, result_message, **vector["kwargs"])

    assert actual == expected
    assert _canonical_hash(expected) == vector["bundle_hash"]
    assert _canonical_hash(actual) == vector["bundle_hash"]
    assert actual["single_use_execution_token"] is None


@pytest.mark.parametrize(
    "vector",
    EVIDENCE_VECTORS["vectors"],
    ids=lambda vector: vector["name"],
)
def test_evidence_bundle_golden_vectors(vector: dict[str, Any]) -> None:
    task = _load(ROOT / EVIDENCE_VECTORS["source_files"]["task"])
    command = dict(EVIDENCE_VECTORS["command_envelope"])
    assert command.pop("task_id_from_source") is True
    command["task_id"] = task["task_id"]
    mock_result = run_worker_to_mock_gateway_dry_run(command)

    expected = _load(ROOT / EVIDENCE_VECTORS["expected_output_template"])
    expected["created_at"] = vector["created_at"]
    expected["bundle_hash"] = vector["bundle_hash"]
    actual = build_evidence_bundle(
        task,
        command,
        mock_result,
        [],
        created_at=vector["created_at"],
    )

    assert actual == expected
    assert actual["bundle_hash"] == vector["bundle_hash"]
    assert compute_bundle_hash(actual) == vector["bundle_hash"]


def test_vector_inventory_is_exact_and_inputs_are_real() -> None:
    assert len(APPROVAL_VECTORS["vectors"]) == 6
    assert len(EVIDENCE_VECTORS["vectors"]) == 6
    assert len({item["name"] for item in APPROVAL_VECTORS["vectors"]}) == 6
    assert len({item["name"] for item in EVIDENCE_VECTORS["vectors"]}) == 6
    for manifest in (APPROVAL_VECTORS, EVIDENCE_VECTORS):
        for source_path in manifest["source_files"].values():
            assert (ROOT / source_path).is_file()
        assert (ROOT / manifest["expected_output_template"]).is_file()
