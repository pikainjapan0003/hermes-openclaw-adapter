# Test Performance — 2026-08-04

Status: **MEASUREMENT AND MARKER MAINTENANCE ONLY — TEST LOGIC UNCHANGED**

## Environment and commands

Measurements used a disposable ext4-native WSL clone at NIGHT-BATCH-21
package-18 HEAD `30e2504`, Python 3.12.3, Linux
`6.18.33.2-microsoft-standard-WSL2 x86_64`. No other pytest process was running
during the accepted measurements.

```text
python -m pytest -q --durations=20
python -m pytest -o addopts="" -q --durations=20
```

An earlier diagnostic launch was discarded because the Codex tool timeout
detached its WSL child and a later collection shared CPU with that orphan. The
orphan was identified by PID and stopped before the two results below; its
partial duration is not reported as a suite measurement.

## Profile results and growth

| Profile | NIGHT-BATCH-20 accepted native baseline | NIGHT-BATCH-21 result | Outcome |
|---|---|---|---|
| Default fast | `1960 passed, 1 skipped, 21 deselected, 14 xfailed in 133.83s` | `2085 passed, 1 skipped, 21 deselected, 14 xfailed in 304.26s`; wall `328.57s` | Green, but the `<150s` target is **not met** |
| Full | `1981 passed, 1 skipped, 14 xfailed in 616.98s` | `2106 passed, 1 skipped, 14 xfailed in 759.87s`; wall `803.64s` | Green; no full-profile time gate |

The collection arithmetic is exact: 2,085 fast-path passes plus the 21
explicitly deselected slow tests equals 2,106 full-path passes. No test is
hidden by the default profile.

The accepted timings show a real run-level regression relative to the prior
native baseline. This package cannot attribute the entire difference to one
test: the default profile's slowest calls are existing tests, while a focused
run of the five new NIGHT-BATCH-21 test files completed `124 passed in 6.69s`
and its slowest call was 0.59s. Because the work order permits marker changes
for newly added tests over two seconds, no marker change is justified here.
Moving existing tests or groups of individually sub-two-second tests would be
an out-of-scope policy change and could conceal contract coverage.

## Default fast path — slowest 20 calls

| Seconds | Node |
|---:|---|
| 13.04 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 9.93 | `test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 7.85 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[2048]` |
| 6.27 | `test_blackboard_board_reader.py::test_reader_validates_one_entry_for_all_ten_contracts` |
| 5.69 | `test_mirror_drift_round2.py::test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs` |
| 3.39 | `test_slow_marker_integrity.py::test_slow_assignments_remain_compatible_with_exactly_one_layer` |
| 3.02 | `test_builder_extreme_legal_inputs.py::test_evidence_bundle_hash_is_independently_recomputable_at_extremes` |
| 2.87 | `test_hash_chain_long_chain.py::test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper` |
| 2.73 | `test_full_chain_contract_rehearsal_v6.py::test_v6_repeated_full_chain_is_byte_identical_and_independently_hashed` |
| 2.50 | `test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |
| 2.28 | `test_dashboard_readonly.py::test_non_control_dashboard_get_routes_are_readonly` |
| 1.93 | `test_trust_violation_scan.py::test_post_route_inventory_is_exact_and_rejects_new_surface` |
| 1.89 | `test_coverage_closeout_storage.py::test_queue_store_lifecycle_queries_and_transitions` |
| 1.81 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[127]` |
| 1.75 | `test_slow_marker_integrity.py::test_every_measured_over_two_second_test_is_marked_slow` |
| 1.74 | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 1.74 | `test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 1.72 | `test_main_get_routes_coverage.py::test_dashboard_get_routes_render_without_controls` |
| 1.68 | `test_main_get_routes_coverage.py::test_get_result_and_dashboard_detail_read_existing_tmp_evidence` (setup) |
| 1.47 | `test_board_reader_concurrency.py::test_concurrent_readers_return_identical_valid_board_results` |

## Full path — slowest 20 calls

| Seconds | Node |
|---:|---|
| 326.37 | `test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress` |
| 77.54 | `test_metrics_reproducibility.py::test_runtime_metrics_report_round_trips_only_recomputed_values` |
| 55.03 | `test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` |
| 30.28 | `test_hash_chain_round4.py::test_verify_one_hundred_thousand_entry_chain_records_runtime_without_gate` |
| 18.35 | `test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` |
| 14.12 | `test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` |
| 12.94 | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 10.04 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 9.97 | `test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 5.84 | `test_board_reader_concurrency_round2.py::test_eight_concurrent_readers_return_the_same_500_file_result` |
| 5.44 | `test_mirror_drift_round2.py::test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs` |
| 5.21 | `test_error_surface_no_leak.py::test_fixture_loader_pytest_report_redacts_sensitive_markers[missing_path]` |
| 4.74 | `test_error_surface_no_leak.py::test_fixture_loader_pytest_report_redacts_sensitive_markers[malformed_payload]` |
| 4.27 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[2048]` |
| 3.68 | `test_hash_chain_long_chain.py::test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper` |
| 3.06 | `test_error_surface_no_leak.py::test_fixture_loader_helpers_have_no_direct_output_calls` |
| 2.89 | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 2.23 | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 2.17 | `test_dashboard_readonly.py::test_non_control_dashboard_get_routes_are_readonly` |
| 2.10 | `test_full_chain_contract_rehearsal_v6.py::test_v6_repeated_full_chain_is_byte_identical_and_independently_hashed` |

## Marker disposition and risk

No marker changed. The new-test focused profile was:

```text
124 passed in 6.69s
slowest new call: 0.59s
```

The default suite is correct but no longer fast enough for the stated
`<150s` objective on this clean native-WSL run. A future explicitly scoped
performance package should profile aggregate cost by file and decide whether
the fast-profile policy itself needs revision; this report does not make that
governance decision.
