# Phase 11 Repository Health — 2026-07-23

Status: NIGHT-BATCH-11 package 15 measurement; report only.

## Acceptance snapshot

```text
python -m pytest -p no:cacheprovider -q --durations=10
845 passed in 64.92s

python -m mypy
Success: no issues found in 6 source files
```

Coverage with `main.py`, `worker.py`, and
`google_sheets_oauth_writer.py` excluded per the established closeout scope:
99% total branch coverage; the lowest included module is
`app/contracts_v0_7.py` at 95%. Separately measured,
`app/main.py` is 65% after package 4 and `app/worker.py` is 17% from
import/structure-only tests. The latter number is intentionally not raised by
running the worker.

## F4 governance sizes

| File | Lines | F4 maximum | Headroom | State |
|---|---:|---:|---:|---|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 | healthy |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 440 | 500 | 60 | watch |
| root `README.md` | 436 | 500 | 64 | watch |

Package 3 reduced 05 from 482 to 440 lines and left a rule-by-rule crosswalk.
No threshold is exceeded. Future 05 edits should prefer updating the compaction
archive/index rather than re-expanding completed-phase history.

Non-executed compaction proposal for root README: move the long historical
version-by-version rollout narrative to a dated archive while retaining the
current setup, current-state, and safety links. This is a proposal only; F4/F2
review is required before removing or relocating any rule-like text.

## Test growth and runtime profile

| Metric | NB-10 reviewed baseline | NB-11 | Growth |
|---|---:|---:|---:|
| collected tests | 805 | 845 | +40 (+4.97%) |
| uninstrumented full-suite runtime | 39.82 s | 64.92 s | +25.10 s (+63.03%) |
| tests exceeding 5 seconds | 0 | 0 | unchanged |

The runtime comparison is host/load sensitive and should be treated as a trend,
not a benchmark. The slowest NB-11 test was the rollback builder fuzz case at
3.14 s. The next material costs were approval/evidence fuzz and GET/dashboard
TestClient setup. No slow marker is currently justified by the 5-second rule.

Package 9 layer measurements at its 838-test boundary:

| Marker | Cases | Runtime |
|---|---:|---:|
| contract | 287 | 32.52 s |
| governance | 47 | 22.49 s |
| legacy | 233 | 13.61 s |
| fuzz | 271 | 23.90 s |

Each test receives exactly one layer; the marker is organizational, not a
safety or acceptance downgrade.

## New tests versus product code

From `99dde93..night-batch-11`:

- test count: +40;
- test-support/test source lines: +1,010;
- `app/` product lines: +0;
- read-only schema renderer tool: +111 lines under `scripts/`.

Thus the requested test-count-to-product-code ratio is `40:0`: this batch added
no runtime product code. For the one authorized read-only tool, test-source
lines to tool lines are `1,010:111` (about 9.1:1). This high ratio reflects
GET-only, AST, golden-vector, fuzz, and governance safety locking rather than
feature expansion.

## Repository single-file Top 10

| Lines | Path |
|---:|---|
| 1,984 | `app/main.py` |
| 1,067 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_final_authorization_plan_v0_8_1_k.py` |
| 1,042 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_authorization_review_v0_8_1_j.py` |
| 1,008 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_FINAL_AUTHORIZATION_PLAN_V0_8_1_K.md` |
| 977 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_creation_plan_v0_8_1_i.py` |
| 920 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_AUTHORIZATION_REVIEW_V0_8_1_J.md` |
| 911 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_CREATION_AUTHORIZATION_PLAN_V0_8_1_H.md` |
| 908 | `scripts/check_hermes_openclaw_local_mock_data_fixture_json_candidate_artifact_plan_v0_8_1_f.py` |
| 907 | `docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_CREATION_PLAN_V0_8_1_I.md` |
| 891 | `scripts/check_hermes_openclaw_worker_dry_run_result_audit_trail_dashboard_display_validation_hardening_v0_8_4_f.py` |

The legacy check-script/document cluster dominates repository file size. A
future docs-only inventory may propose archive boundaries, but this package
does not move or delete any of it.

## Health conclusion

All mechanical gates are green. The main maintenance concerns are volatile
onboarding facts, two raw-jsonschema error-message surfaces, dependency
authority drift, and the 60/64-line headroom in 05/root README. Phase 7 and
Phase 9 remain correctly blocked and are not health-cleanup work.
