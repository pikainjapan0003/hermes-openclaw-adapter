# Test Performance - 2026-08-05

Status: **MEASUREMENT AND MARKER MAINTENANCE ONLY - TEST LOGIC UNCHANGED**

This report covers NIGHT-BATCH-22 packages 1-18 at commit
`2d64a33`. It records measurements; it does not change the fast/complete
policy or authorize any runtime behavior.

## Environment and commands

The fast profile was measured in an ext4-native WSL2 temporary checkout using
the existing disposable venv. The complete profile was measured in the
current WSL2 worktree so that the reproducibility test could resolve the
historical Git baseline `9d26477`.

```text
Python 3.12.3
Linux 6.18.33.2-microsoft-standard-WSL2 x86_64 GNU/Linux
python -m pytest -q --durations=15
python -m pytest -o addopts="" -q --durations=15
```

The Windows system Python was not used for timing: it lacks the repository's
FastAPI dependency and collection stops with `ModuleNotFoundError`.

## Results and count reconciliation

| Profile | Previous accepted NIGHT-BATCH-21 result | NIGHT-BATCH-22 result | Outcome |
|---|---|---|---|
| Default fast | `2085 passed, 1 skipped, 21 deselected, 14 xfailed in 304.26s` | `2268 passed, 1 skipped, 21 deselected, 14 xfailed in 135.89s` | Green; 183 additional passes; fast timing improved in this isolated environment |
| Complete | `2106 passed, 1 skipped, 14 xfailed in 759.87s` | `2289 passed, 1 skipped, 14 xfailed in 716.78s` | Green; 183 additional passes; no complete-profile time gate |

The arithmetic is exact: 2,268 fast-path passes plus the 21 explicitly
deselected slow tests equals the 2,289 complete-path passes. The 14 xfails and
the one skip are unchanged. The complete run was the authoritative run for
Git-dependent tests; it finished green in the worktree with full history.

## Raw fast-profile result

```text
2268 passed, 1 skipped, 21 deselected, 14 xfailed in 135.89s (0:02:15)
```

## Raw complete-profile result

```text
2289 passed, 1 skipped, 14 xfailed in 716.78s (0:11:56)
```

## Slowest 15 calls: fast profile

| Seconds | Test |
|---:|---|
| 4.84 | `tests/test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 4.37 | `tests/test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 3.40 | `tests/test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[2048]` |
| 3.09 | `tests/test_mirror_drift_round2.py::test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs` |
| 1.89 | `tests/test_main_get_routes_coverage.py::test_dashboard_get_routes_render_without_controls` |
| 1.83 | `tests/test_slow_marker_integrity.py::test_slow_assignments_remain_compatible_with_exactly_one_layer` |
| 1.52 | `tests/test_trust_violation_scan.py::test_post_route_inventory_is_exact_and_rejects_new_surface` |
| 1.28 | `tests/test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 1.26 | `tests/test_trust_violation_scan.py::test_approve_routes_have_no_reachable_dispatch_or_execution_call` |
| 1.23 | `tests/test_main_get_routes_coverage.py::test_package_does_not_issue_post_or_touch_worker_contract` (setup) |
| 1.19 | `tests/test_hash_chain_long_chain.py::test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper` |
| 1.16 | `tests/test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |
| 1.14 | `tests/test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 1.09 | `tests/test_queue_state_matrix.py::test_queue_control_transition_matrix_is_atomic_and_does_not_claim[retry_failed-running]` |
| 1.03 | `tests/test_blackboard_board_reader.py::test_reader_validates_one_entry_for_all_ten_contracts` |

## Slowest 15 calls: complete profile

| Seconds | Test |
|---:|---|
| 257.88 | `tests/test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress` |
| 104.71 | `tests/test_metrics_reproducibility.py::test_runtime_metrics_report_round_trips_only_recomputed_values` |
| 21.55 | `tests/test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` |
| 15.23 | `tests/test_hash_chain_round4.py::test_verify_one_hundred_thousand_entry_chain_records_runtime_without_gate` |
| 14.04 | `tests/test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` |
| 8.21 | `tests/test_board_reader_concurrency_round2.py::test_eight_concurrent_readers_return_the_same_500_file_result` |
| 7.92 | `tests/test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 7.58 | `tests/test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` |
| 5.36 | `tests/test_artifact_integrity_v6.py::test_v6_inventory_is_closed_and_extends_v5_with_governance_docs` |
| 5.11 | `tests/test_artifact_integrity_v5.py::test_v5_normalized_manifest_digest_is_unchanged` |
| 4.79 | `tests/test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 4.44 | `tests/test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 4.06 | `tests/test_fixture_conventions.py::test_each_fixture_family_has_an_executable_loader_reference` |
| 3.07 | `tests/test_full_chain_contract_rehearsal_v6.py::test_v6_repeated_full_chain_is_byte_identical_and_independently_hashed` |
| 2.81 | `tests/test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` |

## Marker disposition

No existing test was reclassified in this package. The package-14 guard still
requires every measured timing claim to identify its environment and command;
the current report satisfies that requirement. The complete-profile run has
no time gate, and no new test exceeded the policy threshold in the fast
profile, so no marker change is justified.

## Conclusion

The fast and complete profiles are both green and exactly reconciled. Timings
remain environment-specific evidence rather than a correctness claim; the
mandatory final complete-suite run at the end of NIGHT-BATCH-22 remains the
acceptance run for the final branch head.
