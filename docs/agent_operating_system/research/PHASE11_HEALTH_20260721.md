# Phase 11 Repository Health Snapshot (2026-07-21)

Status: measurement and recommendations only. No governance file was compacted and no
product/runtime behavior was changed.

## Resolution metadata

- 狀態：**已作廢（僅指 current-metric 用途）**。
- 歷史量測保留；current snapshot 由後續 `PHASE11_HEALTH_20260722.md` 取代。

## 1. Environment and scope

- Worktree: NIGHT-BATCH-9 package 10 candidate after package 9 commit `58b7d9a`.
- Runtime: WSL, Python 3.12.3, pytest 9.1.1.
- Full-suite cache was disabled with `-p no:cacheprovider`.
- Coverage data was written only to `/tmp/hermes-night-batch-9-coverage`.
- Branch coverage excluded exactly `app/main.py`, `app/worker.py`, and
  `app/google_sheets_oauth_writer.py`, matching the established closeout scope.

## 2. F4 size thresholds

Maintenance Protocol F4 requires action after 300 lines for 90, after 500 lines for 05,
and after 500 lines for any single governance document. For this package, README is
also checked against the 500-line ceiling specified by the batch.

| File | Current lines | F4 ceiling | Headroom | Result |
|---|---:|---:|---:|---|
| `docs/agent_operating_system/90_LESSONS_LEARNED.md` | 77 | 300 | 223 | pass |
| `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` | 482 | 500 | 18 | pass, near threshold |
| `README.md` | 435 | 500 | 65 | pass |

The new `tests/test_f4_size_thresholds.py` checks these three exact limits. The 05 plan
has the smallest margin; the next material addition should refresh its existing section
0 summary/index rather than crossing the threshold silently. This report does not
authorize moving or deleting a rule.

Targeted raw result:

```text
collected 3 items
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[90-lessons] PASSED
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[05-plan] PASSED
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[readme] PASSED
============================== 3 passed in 2.16s ===============================
```

## 3. Test inventory and full-suite result

An initial collection before adding the three F4 parameter cases reported 790 tests.
The complete package-10 candidate contains 793 tests.

```text
........................................................................ [ 90%]
........................................................................ [ 99%]
.                                                                        [100%]
793 passed in 81.01s (0:01:21)
```

The same 793 tests also passed under branch coverage:

```text
793 passed in 120.92s (0:02:00)
```

## 4. Duration profile

No individual setup/call/teardown duration exceeded 5 seconds. Therefore the requested
`>5s` list is empty and no new pytest marker is justified in the current suite.

The five slowest calls were:

| Seconds | Test |
|---:|---|
| 3.04 | `test_builder_input_fuzz.py::test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output` |
| 2.90 | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 2.76 | `test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` |
| 2.35 | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 2.26 | `test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |

Recommendation: keep all of these in the default gate because they enforce safety
contracts and remain under the threshold. If a future case exceeds 5 seconds, descriptive
markers such as `fuzz`, `security_scan`, or `dashboard_integration` may support profiling,
but the default CI command must continue to run them unless Owner explicitly changes the
acceptance policy.

## 5. Branch-coverage summary

Fresh measurement at this package candidate:

```text
TOTAL  2583 statements  27 missed  1056 branches  38 partial  98%
```

All 32 in-scope app modules remain at or above 80% branch coverage. The low-water module
is `app/blackboard_store.py` at exactly 80%. The next-lowest group is:

- `app/contracts_v0_7.py` — 95%;
- `app/blackboard_board_reader.py` — 97%;
- `app/dashboard_intake_view_v0_7.py` — 97%;
- `app/queue_task_annotation_v0_7.py` — 97%;
- `app/worker_mock_gateway_dry_run.py` — 97%.

The frozen `app/mock_e2e_v0_7.py` remains at 99% with behavior-locking tests only.
No product branch was removed or weakened for coverage. The three named exclusions are
scope exclusions, not below-threshold exemptions; the real-write-capable Google Sheets
writer was not selected as a coverage source or modified.

## 6. Health risks and next check

1. `05_VERIFIED_LONG_TERM_PLAN.md` has only 18 lines of F4 headroom.
2. `blackboard_store.py` is exactly at the 80% floor, so any new uncovered branch will
   make the next closeout fail the established target.
3. The full suite is still comfortably below three minutes in this Windows-mounted WSL
   run, but fuzz and safety scans are the leading duration contributors and should be
   compared on the same environment rather than against a faster native filesystem run.

Suggested next Phase 11 check: rerun the three mechanical F4 assertions, full-suite
durations, and the exact exclusion coverage command after the next product-code batch.
