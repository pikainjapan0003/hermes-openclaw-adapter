# Test Suite Layer Profile — 2026-07-26

Status: measurement only. No test marker, assertion, or product code changed.

Environment: WSL Python 3.12.3, pytest 9.1.1, isolated existing venv
`/tmp/hermes-nb12-venv`, Windows worktree mounted at `/mnt/c`.

Commands:

```text
python -m pytest -p no:cacheprovider -m <layer> -q --durations=15
```

## Layer results

| Layer | Snapshot outcomes (measured 2026-07-26) | Runtime | 2026-07-23 outcomes | Outcome growth | Runtime change |
|---|---:|---:|---:|---:|---:|
| contract | 334 (`324 passed, 10 xfailed`) | 70.18 s | 333 | +1 (+0.30%) | +15.10 s (+27.41%) |
| governance | 52 passed | 33.59 s | 52 | 0 (0.00%) | +5.39 s (+19.11%) |
| legacy | 274 passed | 23.52 s | 269 | +5 (+1.86%) | +2.30 s (+10.84%) |
| fuzz | 271 passed | 35.49 s | 271 | 0 (0.00%) | +6.95 s (+24.35%) |
| **Total** | **931 outcomes** | — | **925 outcomes** | **+6 (+0.65%)** | — |

The four outcome counts sum exactly to the 931-test collection measured for
this 2026-07-26 snapshot; they are not the current repository test count.
Per-layer runtimes are not additive substitutes for one full-suite timing:
collection is repeated four times and mounted-filesystem/cache variance is
material. Outcome growth is stable; runtime percentage changes are diagnostic
observations, not regression thresholds.

## Slowest 15 calls across the four runs

| Rank | Duration | Test |
|---:|---:|---|
| 1 | 8.22 s | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 2 | 4.42 s | `test_fixture_conventions.py::test_each_fixture_family_has_an_executable_loader_reference` |
| 3 | 4.19 s | `test_builder_input_fuzz.py::test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output` |
| 4 | 3.93 s | `test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` |
| 5 | 3.68 s | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 6 | 3.10 s | `test_builder_input_fuzz.py::test_evidence_bundle_builder_rejects_systematic_bad_inputs_without_output` |
| 7 | 2.28 s | `test_main_get_routes_coverage.py::test_dashboard_get_routes_render_without_controls` |
| 8 | 1.94 s | `test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |
| 9 | 1.94 s | `test_trust_violation_scan.py::test_post_route_inventory_is_exact_and_rejects_new_surface` |
| 10 | 1.93 s | `test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 11 | 1.79 s | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 12 | 1.75 s | `test_blackboard_board_reader.py::test_reader_validates_one_entry_for_all_ten_contracts` |
| 13 | 1.21 s | `test_dashboard_readonly.py::test_non_control_dashboard_get_routes_are_readonly` |
| 14 | 1.09 s | `test_cross_reference_integrity.py::test_unreferenced_definitions_are_reported_but_do_not_fail` |
| 15 | 1.04 s | `test_trust_violation_scan.py::test_approve_routes_have_no_reachable_dispatch_or_execution_call` |

The capacity probe remains the only call above five seconds. This report does
not add a slow marker, alter scheduling, or establish a CI threshold.

## Boundary

The four markers are organizational selection tools only. They do not change
execution class, authorization, warning policy, required full-suite
acceptance, or any safety gate. Selecting a marker never authorizes a skipped
layer to remain untested before merge.
