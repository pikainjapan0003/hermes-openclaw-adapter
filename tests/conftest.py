"""Collection-time test-layer markers; assertions and test logic stay untouched."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


LAYER_MARKERS = frozenset({"contract", "governance", "legacy", "fuzz"})
OPTIONAL_MARKERS = frozenset({"slow"})
COLLECTED_LAYER_ASSIGNMENTS: dict[str, tuple[str, ...]] = {}
COLLECTED_OPTIONAL_ASSIGNMENTS: dict[str, tuple[str, ...]] = {}
COLLECTED_ITEM_COUNT = 0

FUZZ_FILES = {
    "test_board_reader_file_fuzz.py",
    "test_builder_input_fuzz.py",
    "test_contract_mutation_resistance.py",
    "test_remote_projection_conditional_mutation.py",
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
    "test_performance_claim_guard.py",
    "test_three_source_readonly.py",
    "test_test_layer_markers.py",
    "test_trust_violation_scan.py",
    "test_worker_structure_contract.py",
}
LEGACY_PREFIXES = (
    "test_coverage_closeout_",
    "test_legacy_",
)
LEGACY_FILES = {
    "test_coverage_closeout_board_reader.py",
    "test_coverage_closeout_legacy_chain.py",
    "test_coverage_closeout_storage.py",
    "test_coverage_closeout_views.py",
    "test_legacy_adapter_readback_coverage.py",
    "test_legacy_contract_cleanup_coverage.py",
    "test_legacy_contract_coverage_round3.py",
    "test_legacy_policy_coverage_round2.py",
    "test_legacy_preview_coverage.py",
    "test_legacy_view_reader_coverage_round4.py",
}
CONTRACT_FILES = {
    "test_approval_packet.py",
    "test_blackboard_board_reader.py",
    "test_blackboard_schemas.py",
    "test_blackboard_store_coverage.py",
    "test_board_reader_capacity.py",
    "test_board_reader_concurrency.py",
    "test_board_reader_stress.py",
    "test_board_roundtrip_rehearsal.py",
    "test_builder_golden_vectors.py",
    "test_compaction_crosswalk_integrity.py",
    "test_contract_coverage_edges.py",
    "test_dependency_declaration_sync.py",
    "test_error_surface_no_leak.py",
    "test_evidence_bundle.py",
    "test_fixture_conventions.py",
    "test_full_chain_contract_rehearsal.py",
    "test_hash_chain.py",
    "test_hash_chain_long_chain.py",
    "test_hash_chain_vectors.py",
    "test_inspect_blackboard_readonly.py",
    "test_main_get_routes_coverage.py",
    "test_main_pure_helpers_coverage.py",
    "test_mock_gateway_real_chain.py",
    "test_n1_preflight_dryrun.py",
    "test_noncontract_error_surface_no_leak.py",
    "test_queue_state_matrix.py",
    "test_remote_readonly_projection.py",
    "test_render_schema_docs_readonly.py",
    "test_rollback_preview_builder.py",
    "test_schema_error_redaction_baseline.py",
    "test_schema_renderer_full_tree.py",
    "test_schema_renderer_rehearsal.py",
    "test_three_source_report_schema.py",
}


def _layer_for(path: Path) -> str:
    name = path.name
    if name in FUZZ_FILES:
        return "fuzz"
    if name in GOVERNANCE_FILES:
        return "governance"
    if name in LEGACY_FILES and name.startswith(LEGACY_PREFIXES):
        return "legacy"
    if name in CONTRACT_FILES:
        return "contract"
    raise ValueError(
        f"{name} has no explicit test-layer marker and is absent from the "
        "reviewed layer inventory"
    )


def pytest_collection_modifyitems(items: list[pytest.Item], config: Any) -> None:
    """Assign exactly one declared layer marker using the source test filename."""

    global COLLECTED_ITEM_COUNT
    del config
    COLLECTED_ITEM_COUNT = len(items)
    COLLECTED_LAYER_ASSIGNMENTS.clear()
    COLLECTED_OPTIONAL_ASSIGNMENTS.clear()
    for item in items:
        explicit_layers = {
            marker.name
            for marker in item.iter_markers()
            if marker.name in LAYER_MARKERS
        }
        if not explicit_layers:
            item.add_marker(getattr(pytest.mark, _layer_for(Path(str(item.path)))))
        assigned_layers = tuple(
            sorted(
                {
                    marker.name
                    for marker in item.iter_markers()
                    if marker.name in LAYER_MARKERS
                }
            )
        )
        COLLECTED_LAYER_ASSIGNMENTS[item.nodeid] = assigned_layers
        COLLECTED_OPTIONAL_ASSIGNMENTS[item.nodeid] = tuple(
            sorted(
                {
                    marker.name
                    for marker in item.iter_markers()
                    if marker.name in OPTIONAL_MARKERS
                }
            )
        )
