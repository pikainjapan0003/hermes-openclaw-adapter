# Phase 11 Health — 2026-07-29 (Round 9)

Status: **MEASUREMENT ONLY — NO ARCHIVE, PRODUCT, TEST, OR RUNTIME CHANGE**

## Commands and environment

Measurements used the NIGHT-BATCH-17 Windows checkout and the isolated project
virtual environment. Coverage artifacts were written under the Windows system
Temp directory, never the repository.

```text
python -m pytest -p no:cacheprovider -q --durations=20
python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py --cov=app --cov-branch --cov-report=json:<TEMP>
python -m pytest -p no:cacheprovider --collect-only -q
python -c "from pathlib import Path; print(len(Path('<file>').read_text(encoding='utf-8').splitlines()))"
git diff --check
```

The coverage-floor test itself runs the non-floor suite in a child process and
writes coverage data only to pytest `tmp_path`.

## Test outcomes and runtime

| Checkpoint | Result | Runtime |
|---|---:|---:|
| Full suite during package 18, before the 51 fixture-inventory outcomes | 1,472 passed, 1 skipped, 14 xfailed | 402.91 s |
| Coverage run after package 19, excluding only the nested floor | 1,522 passed, 1 skipped, 14 xfailed | 383.37 s |
| Final collection before this report | 1,538 outcomes | 6.77 s collection |

The final collection consists of the coverage-run outcomes plus the one
coverage-floor test. The only skip is platform-dependent. The 14 expected
failures remain exactly ten E-01/E-02 schema-error cases plus four ES3
read-only-tool cases; Error Surface Round 4 added no new `xfail`.

The default full-suite time is now dominated by the 242.44-second nested
coverage floor. The non-floor slow families remain board stress/capacity,
repository-wide dependency AST scans, and two captured pytest report probes.
Exact top-20 and layer timings are recorded in
`TEST_PERFORMANCE_20260729.md`.

## Test growth

| Snapshot | Collected/outcome baseline | Change from prior |
|---|---:|---:|
| NIGHT-BATCH-16 WSL result | 1,371 outcomes (1,357 passed + 14 xfailed) | baseline |
| NIGHT-BATCH-17 final collection | 1,538 outcomes | +167 / +12.18% |

Passing cases increased by 166 if the final floor test is included (1,357 →
1,523), and one platform skip is present. Runtime growth is not expressed as a
percentage because the prior result was WSL, the current result is Windows,
and the coverage floor deliberately adds a second instrumented suite run.

Current test source inventory: 70 `tests/test_*.py` files and 11,803 lines
before this report (which adds no test file).

## Coverage

The branch-inclusive coverage JSON contains 3,562 statements and 1,268 branch
opportunities across all `app/` modules.

| Scope | Statements missed | Branches missed | Raw combined coverage |
|---|---:|---:|---:|
| All `app/` | 380 / 3,562 | 110 / 1,268 | 89.855% |
| Managed scope excluding `main.py`, `worker.py`, and `google_sheets_oauth_writer.py` | 1 / 2,591 | 2 / 1,060 | 99.918% |

Explicitly excluded modules remain visible rather than hidden:

| Module | Statement coverage | Branch coverage | Combined |
|---|---:|---:|---:|
| `app/main.py` | 568/774 = 73.385% | 99/172 = 57.558% | 70.507% |
| `app/worker.py` | 24/130 = 18.462% | 1/16 = 6.250% | 17.123% |
| `app/google_sheets_oauth_writer.py` | 0/67 | 0/20 | 0% |

The lowest managed module is `rollback_preview_builder.py` at 98.485%
combined, with one statement and one branch intentionally retained as a
defensive redundant check. `full_loop_preview_adapter.py` is 99.505% with one
defensive partial branch. No product branch was deleted for coverage.

## Core document line counts and F4 thresholds

| File | Lines | F4 threshold / headroom |
|---|---:|---:|
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 / 55 |
| root `README.md` | 436 | 500 / 64 |
| `07_AUDIT_WRITE_DESIGN.md` | 354 | 500 / 146 |
| `NIGHT_BATCH_BACKLOG.md` | 337 | 500 / 163 |
| `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` | 332 | 500 / 168 |
| `90_LESSONS_LEARNED.md` | 78 | 300 / 222 |
| `CLAUDE.md` | 228 | 500 / 272 |

No F4 threshold is exceeded. The plan remains the nearest governed file to its
threshold, but its §0 index exists as required. The backlog is growing and
should be considered by the research-governance policy rather than compressed
ad hoc.

## Research directory trend

| Snapshot | Markdown files | Lines | File growth | Line growth |
|---|---:|---:|---:|---:|
| NIGHT-BATCH-16 baseline | 53 | 5,636 | baseline | baseline |
| NIGHT-BATCH-17 after this report | 64 | 6,949 | +11 / +20.75% | +1,313 / +23.30% |

The largest current research files remain proposal/design artifacts:
`O2_ROLE_WORKER_PROPOSAL.md` (277), `RESEARCH_DIR_GOVERNANCE.md` (246),
`O1_PLAN_LEVEL_AUTH_PROPOSAL.md` (228), and
`GOVERNANCE_AUDIT_ROUND2_20260721.md` (226). Size alone is not permission to
move or compress them, especially while Owner choices/findings remain open.

NIGHT-BATCH-17 package 4 expanded `RESEARCH_DIR_GOVERNANCE.md` into an
executable planning SOP with classification, retention, manifest, and future
Option-B archive steps. The Owner decision is still blank. Therefore this
health round **does not create an archive directory, move, rename, compact, or
delete any research file**.

## Current maintenance signals

1. Package 7 is HOLD because the reader accepts a board-internal hardlink to a
   board-external valid fixture; a separately scoped product/test fix is in the
   backlog.
2. ES4-01/ES4-02 show that malformed fixture values and missing paths can reach
   local pytest reports; ordinary successful loading has no direct output.
3. Round 9 records two P3 metadata/wording findings: the old health snapshot's
   Round-7 status and the prior “five selections” wording for a ROOT gate with
   no formal choices. Later checkpoint metadata: R7-01 through R7-05 were
   dispositioned by NIGHT-BATCH-17 package 2; the corrected summaries describe
   four formal option groups (RED/AUD/RB/PB) plus one unlabelled ROOT direction
   gate. The original measurements and findings remain historical evidence.
4. The 00/01 review records three P2 and two P3 documentation findings. The
   canonical prohibitions remain intact; any 01 edit remains F2/Owner-gated.
5. The coverage floor protects `main.py` without entering 198 forbidden
   POST/control/execution/callback statements, but it now dominates Windows
   developer runtime. Its required/fast-path split is only a proposal.
6. All 50 fixtures are byte-locked by SHA-256; any later fixture change must be
   explicitly reviewed rather than automatically accepting a new digest.

## v1.0 and Owner gates

v1.0 remains blocked only by the separately Owner-gated Phase 7 append-only
local audit implementation/inspection and the Owner-present Phase 9 N=1
session. RED/AUD/RB/PB, ROOT direction, and research governance decisions also
remain blank. None is selected by this report.

## Conclusion

Contract/test evidence grew without product or runtime expansion. Managed
coverage remains 99.918%, all F4 thresholds remain green, and the fixture
inventory is now byte-locked. The main maintenance costs are the deliberately
expensive coverage floor and continued research growth. Package 4's governance
proposal is the correct future decision point; this round measures it and does
not execute it.
