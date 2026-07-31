"""Collection-time test-layer markers; assertions and test logic stay untouched."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


FUZZ_FILES = {
    "test_board_reader_file_fuzz.py",
    "test_builder_input_fuzz.py",
    "test_schema_fuzz.py",
}
GOVERNANCE_FILES = {
    "test_check_mirror_drift_readonly.py",
    "test_contract_index.py",
    "test_cross_reference_integrity.py",
    "test_dashboard_readonly.py",
    "test_docs_drift_guard.py",
    "test_f4_size_thresholds.py",
    "test_n1_preflight_gate.py",
    "test_queue_claim_guard.py",
    "test_three_source_readonly.py",
    "test_trust_violation_scan.py",
    "test_worker_structure_contract.py",
}
LEGACY_PREFIXES = (
    "test_coverage_closeout_",
    "test_legacy_",
)


def _layer_for(path: Path) -> str:
    name = path.name
    if name in FUZZ_FILES:
        return "fuzz"
    if name in GOVERNANCE_FILES:
        return "governance"
    if name.startswith(LEGACY_PREFIXES):
        return "legacy"
    return "contract"


def pytest_collection_modifyitems(items: list[pytest.Item], config: Any) -> None:
    """Assign exactly one declared layer marker using the source test filename."""

    del config
    for item in items:
        item.add_marker(getattr(pytest.mark, _layer_for(Path(str(item.path)))))
