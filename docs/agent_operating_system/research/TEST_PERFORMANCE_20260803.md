# Test Performance — 2026-08-03

Status: **MEASUREMENT AND MARKER MAINTENANCE ONLY — TEST LOGIC UNCHANGED**

## Environment and commands

The NIGHT-BATCH-20 package-19 measurement used Python 3.12.3 in the disposable
WSL venv `/tmp/hermes-nb20-venv`, reading the authorized Windows worktree via
`/mnt/c`. This is materially slower than an ext4-native WSL checkout, so its
times must not overwrite the accepted native-WSL trend line.

```text
python -m pytest -p no:cacheprovider -q --durations=15
python -m pytest -p no:cacheprovider -o addopts="" -q --durations=15
```

## Profile results and growth

| Profile | Previous accepted native-WSL result | Current mounted-worktree result | Outcome growth |
|---|---|---|---|
| Default fast | 1942 passed, 18 deselected, 14 xfailed in 94.62s | 1960 passed, 1 skipped, 21 deselected, 14 xfailed in 335.91s | +18 passed; +3 deliberately deselected slow tests; environment not time-comparable |
| Full | 1960 passed, 14 xfailed in 403.54s | 1980 passed, 1 skipped, 14 xfailed, 1 failed in 805.63s | +22 total collected outcomes; mounted-worktree run not green |

The sole full-profile failure was
`test_runtime_metrics_report_round_trips_only_recomputed_values`: its internal
`git diff --check 9d26477` subprocess exceeded its fixed 30-second timeout on
the `/mnt/c` worktree. The same worktree's direct diff check succeeds. This is
recorded as environment-specific evidence, not converted to an xfail and not
repaired under this marker/report-only package. A native-WSL clone rerun is the
required disposition before batch acceptance.

### Native-WSL disposition

The committed package was then cloned to the ext4-native checkout
`/tmp/hermes-nb20-native.IPftxs/repo` and rerun with the same disposable venv:

| Profile | Native result |
|---|---|
| Default fast | `1960 passed, 1 skipped, 21 deselected, 14 xfailed in 133.83s (0:02:13)` |
| Full | `1981 passed, 1 skipped, 14 xfailed in 616.98s (0:10:16)` |

The arithmetic is exact: 1,960 fast-path passes plus 21 explicitly deselected
slow tests equals the 1,981 full-path passes. The mounted-worktree timeout did
not recur; the native full profile is green.

## Default fast path — slowest 15 calls

| Seconds | Node |
|---:|---|
| 6.97 | `test_full_chain_contract_rehearsal_v6.py::test_v6_repeated_full_chain_is_byte_identical_and_independently_hashed` |
| 6.82 | `test_fixture_conventions.py::test_each_fixture_family_has_an_executable_loader_reference` |
| 6.58 | `test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 5.62 | `test_builder_input_fuzz.py::test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output` |
| 5.42 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 4.28 | `test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` |
| 3.88 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[2048]` |
| 3.17 | `test_builder_input_fuzz.py::test_evidence_bundle_builder_rejects_systematic_bad_inputs_without_output` |
| 3.02 | `test_metrics_reproducibility.py::test_metrics_snapshot_is_reproducible_and_order_independent` |
| 2.68 | `test_slow_marker_integrity.py::test_slow_assignments_remain_compatible_with_exactly_one_layer` |
| 2.59 | `test_contract_mutation_resistance_round5.py::test_round_five_inventory_is_exact_disjoint_and_combination_only` |
| 2.52 | `test_research_report_generation_no_leak.py::test_committed_research_reports_do_not_contain_synthetic_sensitive_markers` |
| 2.48 | `test_mirror_drift_round2.py::test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs` |
| 2.15 | `test_hash_chain_long_chain.py::test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper` |
| 2.09 | `test_slow_marker_integrity.py::test_every_measured_over_two_second_test_is_marked_slow` |

These are existing fast-path tests. Package 19 does not retroactively move
them to `slow`, because the work order only authorizes markers for newly added
tests and this `/mnt/c` measurement is not comparable to the native baseline.

## Full path — slowest 15 calls

| Seconds | Node |
|---:|---|
| 327.03 | `test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress` |
| 30.12 | `test_metrics_reproducibility.py::test_runtime_metrics_report_round_trips_only_recomputed_values` |
| 27.05 | `test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` |
| 13.31 | `test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 11.75 | `test_board_reader_concurrency_round2.py::test_eight_concurrent_readers_return_the_same_500_file_result` |
| 11.69 | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 11.62 | `test_hash_chain_round4.py::test_verify_one_hundred_thousand_entry_chain_records_runtime_without_gate` |
| 11.28 | `test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` |
| 9.95 | `test_artifact_integrity_v5.py::test_v5_normalized_manifest_digest_is_unchanged` |
| 8.08 | `test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` |
| 5.34 | `test_slow_marker_integrity.py::test_slow_assignments_remain_compatible_with_exactly_one_layer` |
| 5.14 | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 4.54 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 4.50 | `test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 4.25 | `test_fixture_conventions.py::test_each_fixture_family_has_an_executable_loader_reference` |

## Marker changes

Three new NIGHT-BATCH-20 tests have explicit optional `slow` markers:

- `tests/test_artifact_integrity_v5.py::test_v5_inventory_is_closed_and_extends_all_v4_artifacts`;
- `tests/test_artifact_integrity_v5.py::test_v5_normalized_manifest_digest_is_unchanged`; and
- `tests/test_board_reader_concurrency_round2.py::test_eight_concurrent_readers_return_the_same_500_file_result`.

The concurrency file's former list-valued module marker was split into one
explicit contract-layer marker plus a function-level slow marker so the
existing AST inventory can recognize exactly one layer. No assertion or
product behavior changed.

## Native full path — slowest 15 calls

| Seconds | Node |
|---:|---|
| 260.14 | `test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress` |
| 83.36 | `test_metrics_reproducibility.py::test_runtime_metrics_report_round_trips_only_recomputed_values` |
| 45.18 | `test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` |
| 31.28 | `test_hash_chain_round4.py::test_verify_one_hundred_thousand_entry_chain_records_runtime_without_gate` |
| 17.45 | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 9.19 | `test_research_report_generation_no_leak.py::test_product_and_script_sources_have_no_research_report_write_target` |
| 7.65 | `test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` |
| 6.63 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[4094]` |
| 6.15 | `test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` |
| 5.38 | `test_board_reader_concurrency_round2.py::test_eight_concurrent_readers_return_the_same_500_file_result` |
| 4.69 | `test_hash_chain_round4.py::test_binary_prefix_search_locates_arbitrary_nonterminal_tamper[2048]` |
| 3.68 | `test_mirror_drift_round2.py::test_five_hundred_files_keep_all_four_states_and_do_not_mutate_inputs` |
| 3.58 | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 3.50 | `test_error_surface_no_leak.py::test_fixture_loader_pytest_report_redacts_sensitive_markers[missing_path]` |
| 3.48 | `test_slow_marker_integrity.py::test_slow_assignments_remain_compatible_with_exactly_one_layer` |

## Conclusion

The default profile remains mathematically complete relative to the full
profile: the 21 deselected outcomes are the 21 explicit slow items. Mounted
and native timings show why environment labels matter. The required native-WSL
rerun is green; final-HEAD acceptance still requires the separately mandated
last full-suite run after package 22.
