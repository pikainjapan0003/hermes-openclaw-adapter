# Phase 11 Repository Health Snapshot — Round 2 (2026-07-22)

Status: measurement and recommendations only. No governance file was compacted, no
product behavior was changed, and no slow marker or persistence path was added.

## Resolution metadata

- 狀態：**已修（報告型 artifact，當輪無待修 finding）**。
- 本檔是 NIGHT-BATCH-10 closeout 基線；新一輪量測完成後只會被標為歷史快照。

## 1. Environment and measurement scope

- Candidate: NIGHT-BATCH-10 after package 9, commit `fe4fd6c`.
- Runtime: WSL, Python 3.12.3, pytest 9.1.1.
- Full suite used `-p no:cacheprovider`.
- Coverage data was written to `/tmp/nb10-health.coverage`, outside the repository.
- Branch coverage excluded exactly `app/main.py`, `app/worker.py`, and
  `app/google_sheets_oauth_writer.py`.
- Single-file line ranking used Git-tracked `.py`, `.md`, `.json`, `.toml`, and `.txt`
  files; generated, ignored, and runtime files were not counted.

## 2. F4 size thresholds

| File | 2026-07-21 | Current | Ceiling | Headroom | Result |
|---|---:|---:|---:|---:|---|
| `docs/agent_operating_system/90_LESSONS_LEARNED.md` | 77 | 78 | 300 | 222 | pass |
| `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` | 482 | 482 | 500 | 18 | pass, near threshold |
| `README.md` | 435 | 436 | 500 | 64 | pass |

The existing mechanical gate remains green:

```text
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[90-lessons] PASSED
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[05-plan] PASSED
tests/test_f4_size_thresholds.py::test_f4_governance_file_stays_within_size_threshold[readme] PASSED
============================== 3 passed in 1.33s ===============================
```

No F4 threshold was crossed, so this package is not HOLD.

### Proposed 05 compaction plan — not executed

1. Freeze new prose additions to 05 until a docs-only compaction package has an exact
   line-preserving inventory and Owner review.
2. Keep §5 status rows and §6 Owner decisions in 05 as the authority; do not move,
   paraphrase, or delete a safety rule.
3. Identify dated evidence narratives that duplicate existing closeout/research files.
   For each candidate, prepare an old-line → canonical-target manifest and leave a
   stable one-line cross-reference at the old section.
4. Run path, anchor, status-table, and authorization-language checks before and after
   the candidate compaction; fresh-context review must prove no exception or HOLD gate
   disappeared.
5. Merge only after Owner reviews the exact deletion/move diff. A line-count target
   must never justify weakening a rule.

This proposal does not authorize compaction. The immediate operational rule is simply:
do not spend the remaining 18 lines on duplicate status prose.

## 3. Test inventory and growth

| Metric | NIGHT-BATCH-9 closeout | Current | Change |
|---|---:|---:|---:|
| Collected/passed cases | 793 | 805 | +12 (+1.51%) |
| Full-suite elapsed, same Windows-mounted WSL class | 81.01s | 60.40s | -20.61s (-25.44%) |
| Coverage-run elapsed | 120.92s | 93.22s | -27.70s (-22.91%) |

The count increase is exact: packages 1–3 added four cases and package 7 added eight
Blackboard-store cases. Timing varies with host load and filesystem cache, so the
percentage decreases are observations, not a performance guarantee and not evidence
that any safety test may be removed.

Full-suite raw summary:

```text
........................................................................ [ 98%]
.............                                                            [100%]
805 passed in 60.40s (0:01:00)
```

## 4. Duration profile

No setup/call/teardown exceeded the existing five-second watch threshold. The ten
slowest measured items were:

| Seconds | Phase | Test |
|---:|---|---|
| 2.92 | call | `test_builder_input_fuzz.py::test_rollback_preview_builder_rejects_systematic_bad_inputs_without_output` |
| 2.77 | call | `test_builder_input_fuzz.py::test_approval_packet_builder_rejects_systematic_bad_inputs_without_output` |
| 2.20 | call | `test_builder_input_fuzz.py::test_evidence_bundle_builder_rejects_systematic_bad_inputs_without_output` |
| 1.92 | call | `test_queue_claim_guard.py::test_app_import_all_dashboard_gets_and_approve_never_claim` |
| 1.72 | call | `test_blackboard_board_reader.py::test_reader_validates_one_entry_for_all_ten_contracts` |
| 1.44 | call | `test_queue_claim_guard.py::test_ast_allows_only_the_exact_local_in_memory_claim_exception` |
| 1.41 | call | `test_full_chain_contract_rehearsal.py::test_complete_twelve_step_contract_chain_is_valid_linked_and_hashed` |
| 1.28 | setup | `test_dashboard_readonly.py::test_dashboard_route_inventory_is_exact_and_dynamic` |
| 1.08 | call | `test_trust_violation_scan.py::test_execution_token_remains_null_in_schema_ast_and_source_text` |
| 0.96 | call | `test_trust_violation_scan.py::test_post_route_inventory_is_exact_and_rejects_new_surface` |

The three builder fuzz tests remain the leading group but are under threshold and
enforce fail-closed behavior. No marker split is recommended now; the default test
command must continue to include them.

## 5. Branch-coverage summary

Exact in-scope total:

```text
TOTAL  2591 statements  14 missed  1060 branches  30 partial  99%
805 passed in 93.22s (0:01:33)
```

All 32 included app modules remain at or above 95%, exceeding the established 80%
floor. The low-water modules and recently changed modules are:

| Module | Branch coverage | Note |
|---|---:|---|
| `app/contracts_v0_7.py` | 95% | current low-water module |
| `app/blackboard_board_reader.py` | 97% | duplicate-key hook covered; defensive branches remain |
| `app/dashboard_intake_view_v0_7.py` | 97% | unchanged |
| `app/queue_task_annotation_v0_7.py` | 97% | unchanged |
| `app/worker_mock_gateway_dry_run.py` | 97% | unchanged |
| `app/blackboard_store.py` | 99% | raised from 80% by tests only |

The three exclusions remain scope exclusions, not claims of adequate coverage. In
particular, the real-write-capable Google Sheets writer was neither imported for
coverage work nor modified.

## 6. Git-tracked single-file line-count Top 10

| Rank | Lines | Path |
|---:|---:|---|
| 1 | 1984 | `app/main.py` |
| 2 | 1067 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_final_authorization_plan_v0_8_1_k.py` |
| 3 | 1042 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_authorization_review_v0_8_1_j.py` |
| 4 | 1008 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_FINAL_AUTHORIZATION_PLAN_V0_8_1_K.md` |
| 5 | 977 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_plan_v0_8_1_i.py` |
| 6 | 920 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_AUTHORIZATION_REVIEW_V0_8_1_J.md` |
| 7 | 911 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_CREATION_AUTHORIZATION_PLAN_V0_8_1_H.md` |
| 8 | 908 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_candidate_artifact_plan_v0_8_1_f.py` |
| 9 | 907 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_PLAN_V0_8_1_I.md` |
| 10 | 891 | `scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_display_validation_hardening_v0_8_4_f.py` |

This table is diagnostic only. File size does not authorize refactoring, deletion,
splitting, or behavior change. `app/main.py` remains explicitly excluded from this
night package's product changes.

## 7. Health findings and next check

1. 05 remains the nearest governance threshold with only 18 lines of headroom.
2. The test inventory grew 1.51% while all tests and coverage remained green.
3. No individual test needs a slow marker under the current five-second policy.
4. `blackboard_store.py` no longer sits on the 80% floor; its new minimum is 99%.
5. Repository size concentration remains in legacy authorization-plan scripts/docs and
   `app/main.py`; any cleanup requires a separate scope and behavior-preservation review.

Suggested next Phase 11 check: after the next product-code batch, rerun the same three
F4 assertions, exact exclusion coverage command, duration profile, and tracked-file
ranking before proposing any compaction.
