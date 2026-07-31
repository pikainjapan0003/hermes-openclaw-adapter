# Test Performance — 2026-07-29

Status: **MEASUREMENT AND SETTINGS PROPOSAL ONLY — TEST LOGIC UNCHANGED**

## Environment and commands

Measured on the NIGHT-BATCH-17 Windows checkout with the isolated project
virtual environment. These values are not directly comparable to WSL timing.
No cache provider was used.

```text
python -m pytest -p no:cacheprovider -q --durations=20
python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py --durations=20
python -m pytest -p no:cacheprovider -q -m <layer>
```

For the governance layer only, the layer timing excluded
`tests/test_main_coverage_floor.py`; that floor is reported separately.

## Whole-suite measurements

| Measurement | Outcomes | Pytest runtime |
|---|---:|---:|
| Default full suite, including nested coverage floor | 1,472 passed, 1 skipped, 14 xfailed | 402.91 s |
| Full suite excluding only coverage floor | 1,471 passed, 1 skipped, 14 xfailed | 207.40 s |
| Coverage-floor test's isolated child suite | same non-floor suite, output captured | 242.44 s call duration |

The first value is the actual current default command. It is intentionally
larger than “non-floor + floor” arithmetic may suggest because process startup,
filesystem cache state, coverage instrumentation, and Windows scheduling vary.
The floor writes its coverage data only to pytest `tmp_path`.

NIGHT-BATCH-16's WSL snapshot was 1,357 passed and 14 xfailed in 69.04 s. The
current branch adds 115 passing outcomes plus one platform skip. Runtime growth
must not be reported as a percentage across these snapshots because both the
host platform and the new nested coverage instrumentation differ.

## Layer timing

| Layer | Outcomes | Pytest runtime | Process wall time |
|---|---:|---:|---:|
| contract | 410 passed, 14 xfailed | 115.67 s | 118.931 s |
| governance, excluding coverage floor | 61 passed | 28.07 s | 32.691 s |
| legacy | 276 passed | 16.50 s | 20.101 s |
| fuzz | 724 passed, 1 skipped | 60.28 s | 65.154 s |

The four layer outcome counts plus the separately measured coverage floor equal
the default collection. Running layers independently repeats collection and
startup, so their times must not be summed as a prediction of one full run.

## Slowest 20 calls

| Rank | Seconds | Test |
|---:|---:|---|
| 1 | 242.44 | `test_main_coverage_floor.py::test_main_branch_coverage_does_not_regress` |
| 2 | 38.78 | `test_board_reader_stress.py::test_board_reader_stress_measures_200_complete_boards` |
| 3 | 11.33 | `test_board_reader_capacity.py::test_reader_capacity_probe_reports_runtime_and_peak_memory` |
| 4 | 5.32 | `test_error_surface_no_leak.py::test_fixture_loader_pytest_report_leak_baseline_is_explicit[malformed_payload]` |
| 5 | 5.08 | `test_error_surface_no_leak.py::test_fixture_loader_pytest_report_leak_baseline_is_explicit[missing_path]` |
| 6 | 4.93 | `test_dependency_declaration_sync.py::test_declared_without_literal_import_baseline_does_not_silently_grow` |
| 7 | 4.72 | `test_dependency_declaration_sync.py::test_literal_third_party_imports_have_a_declared_distribution` |
| 8 | 2.68 | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 9 | 1.72 | `test_error_surface_no_leak.py::test_fixture_loader_helpers_have_no_direct_output_calls` |
| 10 | 1.49 | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 11 | 1.47 | `test_hash_chain_long_chain.py::test_verify_chain_accepts_1000_entries_and_rejects_seeded_middle_tamper` |
| 12 | 1.43 | `test_docs_drift_guard.py::test_git_inventory_ignores_runtime_artifact_presence_in_fake_repo` |
| 13 | 1.38 | `test_main_get_routes_coverage.py::test_dashboard_get_routes_render_without_controls` |
| 14 | 1.36 | `test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 15 | 1.18 | `test_blackboard_board_reader.py::test_reader_validates_one_entry_for_all_ten_contracts` |
| 16 | 1.08 | `test_dashboard_readonly.py::test_non_control_dashboard_get_routes_are_readonly` |
| 17 | 0.97 | `test_builder_extreme_legal_inputs.py::test_evidence_bundle_hash_is_independently_recomputable_at_extremes` |
| 18 | 0.94 | `test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |
| 19 | 0.94 | `test_trust_violation_scan.py::test_post_route_inventory_is_exact_and_rejects_new_surface` |
| 20 | 0.89 | `test_n1_preflight_dryrun.py::test_every_non_green_condition_combination_is_blocked` |

The non-floor rerun showed the same dominant families, with ordinary timing
variation: stress 47.97 s, capacity 13.14 s, two dependency scans 8.40/7.78 s,
and the two captured pytest probes 7.39/7.09 s.

## Candidate settings and fixture changes — not applied

### P1: separate the coverage floor from the default developer loop

Keep the exact floor and fail-closed threshold, but in a later authorized test
governance package consider a dedicated command such as:

```text
python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py
python -m pytest -p no:cacheprovider -q tests/test_main_coverage_floor.py
```

CI/Fable review would still require both commands. This avoids an implicit
nested whole-suite run during every local default invocation; it does not lower
coverage or touch POST/execution code.

### P2: session-scope the literal-import inventory

`test_dependency_declaration_sync.py` calls `_literal_import_roots()` in two
tests, reparsing every Python file both times. A reviewed session-scoped fixture
could compute the immutable set once per pytest session and feed both
assertions. Keep all assertion baselines unchanged. Estimated opportunity is
one repository-wide AST scan per full process, not the entire 9–17 seconds.

### P3: parallelize only isolated, tmp-path-safe layers

Contract, legacy, and most fuzz tests are natural candidates for process-level
parallel CI jobs. Governance tests that inspect Git/global collection and the
coverage floor should remain isolated until a dedicated determinism review.
No parallel pytest dependency is currently declared; this report does not add
one or assume it exists.

### P4: keep stress/capacity tests explicit

The 200-board stress and 500-board capacity probes are intentionally expensive
behavior checks. Any future slow-marker proposal must keep them in required
Fable/CI acceptance and must not shrink their workloads merely to improve a
number.

## Decision boundary

No pytest marker, `pyproject.toml` option, fixture scope, workload, assertion,
dependency, or product file changed in this package. The command presets above
are proposals, not active settings. A later package must measure before/after
on the same platform and prove that all outcomes and safety guards remain.
