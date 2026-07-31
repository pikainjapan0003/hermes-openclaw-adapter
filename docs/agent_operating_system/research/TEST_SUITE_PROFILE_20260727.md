# Test Suite Layer Profile — 2026-07-27

Status: NIGHT-BATCH-15 package 17 checkpoint. Layer markers organize tests; they
do not change authorization, execution class, or the requirement to run the
complete suite before acceptance.

Environment: WSL Python virtual environment
`/home/lnovo/.venvs/hoa-test`, Windows worktree mounted under `/mnt/c`.

Command for each layer:

```text
python -m pytest -p no:cacheprovider -m <layer> -q --durations=5
```

## Layer results

| Layer | Outcomes | Deselected | Runtime |
|---|---:|---:|---:|
| contract | 364 (`354 passed, 10 xfailed`) | 842 | 94.91 s |
| governance | 55 passed | 1,151 | 26.20 s |
| legacy | 276 passed | 930 | 17.17 s |
| fuzz | 511 passed | 695 | 38.56 s |
| **Total outcomes** | **1,206** | — | — |

The four outcome counts sum exactly to the 1,206-item collection:
364 + 55 + 276 + 511 = 1,206. Selection runtimes are not additive substitutes
for a full-suite timing because collection and startup repeat four times.

The previous `TEST_SUITE_PROFILE_20260726.md` checkpoint measured 931 outcomes;
the later NIGHT-BATCH-14 final health report measured 939 outcomes after
additional same-batch tests. This report supersedes neither historical
measurement. Its 1,206 count is the package-17 point after the current batch's
new mutation, stress, preflight, dependency, renderer, and guard tests.

## Slowest observed calls

| Layer | Test | Duration |
|---|---|---:|
| contract | `test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` | 26.92 s |
| contract | `test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` | 7.14 s |
| contract | `test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` | 7.01 s |
| contract | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` | 5.29 s |
| fuzz | `test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` | 3.25 s |
| fuzz | `test_builder_input_fuzz.py::test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output` | 3.19 s |
| governance | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` | 2.40 s |

These are host/load observations, not CI thresholds.

## Layer inventory guard

`tests/conftest.py` now has an exact reviewed inventory for all 59 current
`test_*.py` files. An unknown new test file:

- passes when it declares exactly one explicit layer marker; or
- fails collection when it has no explicit marker and is absent from the
  reviewed inventory.

`tests/test_test_layer_markers.py` separately proves:

1. every collected outcome has exactly one layer;
2. the 59-file disk inventory equals the four reviewed default inventories;
3. a simulated unknown unmarked file raises instead of silently defaulting to
   `contract`; and
4. all four layer outcome counts sum to the complete collection.

The guard is classification governance only. A marker never authorizes a test
layer to be skipped from final acceptance.
