# Phase 11 Repository Health — 2026-07-24

Status: NIGHT-BATCH-12 package 14 measurement; report only.

## Environment note

The original package report did not preserve OS, Python, pytest, or checkout
details. **Environment unknown; timing values below are historical,
non-reproducible context and are not acceptance evidence.**

## Acceptance snapshot

```text
python -m pytest -p no:cacheprovider -q --durations=10
880 passed, 10 xfailed in 135.04s (0:02:15)

python -m mypy
Success: no issues found in 6 source files
```

The ten expected failures are the explicit schema-error leak baseline introduced
by package 2. They remain fail-visible until the Owner chooses a redaction
contract; they are not skipped acceptance checks.

Coverage with `main.py`, `worker.py`, and
`google_sheets_oauth_writer.py` excluded per the established closeout scope is
99% total branch coverage. The lowest included modules are
`dashboard_intake_view_v0_7.py`, `blackboard_board_reader.py`, and
`queue_task_annotation_v0_7.py` at 97%.

Package 6 moved `contracts_v0_7.py` from 95% to 100% and
`worker_mock_gateway_dry_run.py` from 97% to 100%. Package 5 made no accepted
coverage change: its GET/display-only scope reached 67% in an experimental
targeted measurement but could not meet 75% without entering prohibited POST,
dispatch, command, or write paths. It was therefore reverted and marked HOLD.
The last accepted full-suite measurements for excluded `main.py` and
`worker.py` remain 65% and 17%, respectively.

## F4 governance sizes

| File | Lines | F4 maximum | Headroom | State |
|---|---:|---:|---:|---|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 | healthy |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | 55 | watch |
| root `README.md` | 436 | 500 | 64 | watch |

No F4 threshold is exceeded. The five-line increase in 05 since the NB-11
health report is the NB-12 package-3 onboarding clarification. Measurement:
`wc -l docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` at
NIGHT-BATCH-13 package-3 start (`9da4f78`) returned `445`. It remains covered by
the compaction crosswalk guard, which locks the archived C01–C18 and M01–M11
rule inventory.

## Test growth and runtime

| Metric | NB-11 baseline | NB-12 | Growth |
|---|---:|---:|---:|
| collected outcomes | 845 | 890 | +45 (+5.33%) |
| passed | 845 | 880 | +35 |
| expected-failure baseline | 0 | 10 | +10 |
| uninstrumented full-suite runtime | 64.92 s | 135.04 s | +70.12 s (+108.01%) |
| tests exceeding 5 seconds | 0 | 1 | +1 |

The runtime comparison is host/load sensitive and is a trend, not a benchmark.
The new 500-message board-reader capacity probe was the only test over five
seconds at 6.72 s. The next slowest test was the twelve-step rehearsal at
4.16 s. A future test-profile package may mark the capacity probe as slow, but
this report changes no marker or test selection.

## `research/` growth

The baseline is the NIGHT-BATCH-12 branch point, commit `391705c`.

| Metric | Branch-point baseline | Before this report | Change before this report |
|---|---:|---:|---:|
| Markdown files | 19 | 23 | +4 (+21.05%) |
| total lines | 2,550 | 2,942 | +392 (+15.37%) |

Including this 98-line report, the final state is 24 Markdown files and 3,040
lines: +5 files (+26.32%) and +490 lines (+19.22%) from the branch-point
baseline.

F4 currently defines per-file thresholds for 90, 05, and the root README, but
does not define a file-count or total-line threshold for `research/`.
Therefore no research archive threshold can truthfully be declared exceeded.
No file is moved, deleted, or archived in this package.

Non-binding proposal for a future Owner-reviewed maintenance rule:

- measure research file count and total lines at every Phase 11 health pass;
- trigger an archive review only after an Owner ratifies numeric thresholds;
- if triggered, move superseded dated reports into a dated research archive
  while preserving their paths through an index and retaining all resolution
  metadata;
- require the docs drift and cross-reference guards to remain green before and
  after any move.

This is a proposal, not authorization to archive or rewrite history.

## Health conclusion

All executable gates are green. The material maintenance signals are the
intentional ten-case schema-error xfail baseline, one capacity test above five
seconds, 55/64-line headroom in 05/root README, and research growth that now
needs an Owner-defined threshold before automation can classify it as excess.
Phase 7 and Phase 9 remain correctly blocked.
