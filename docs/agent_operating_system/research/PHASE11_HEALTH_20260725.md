# Phase 11 Repository Health — 2026-07-25

Status: NIGHT-BATCH-13 package 14 measurement; report only.

## Acceptance snapshot

```text
python -m pytest -p no:cacheprovider -q --durations=10
915 passed, 10 xfailed in 103.18s (0:01:43)

python -m mypy
Success: no issues found in 6 source files
```

The ten expected failures remain the exact ten-schema E-01 leak baseline.
Package 5 now guards both their count and schema inventory; no other failure is
hidden by xfail.

The only test above five seconds was the read-only capacity probe at 5.28 s.
Fixture-convention source scanning was 3.77 s; the remaining slowest entries
were existing deterministic builder fuzz tests. Runtime is host/load sensitive
and is not an acceptance benchmark.

## Coverage

The full 925-outcome suite was instrumented. The established closeout report
omits only `main.py`, `worker.py`, and `google_sheets_oauth_writer.py`:

```text
TOTAL  2591 statements, 7 missed, 1060 branches, 12 partial, 99%
```

The lowest included modules are now 98%. Package 6 raised
`dashboard_intake_view_v0_7.py`, `blackboard_board_reader.py`, and
`queue_task_annotation_v0_7.py` from 97% to 100%.

`main.py` was measured separately at 69% branch coverage, up from the accepted
65% baseline. Package 1 covered only the five authorized pure/read-only helpers;
command, dispatch, callback, execution, and POST paths remain untested by that
package and unauthorized.

## F4 governance sizes

Measurement command and working point:

```text
wc -l docs/agent_operating_system/90_LESSONS_LEARNED.md \
      docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md \
      README.md

78   docs/agent_operating_system/90_LESSONS_LEARNED.md
445  docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md
436  README.md
```

| File | Lines | F4 maximum | Headroom | State |
|---|---:|---:|---:|---|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 | healthy |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | 55 | watch |
| root `README.md` | 436 | 500 | 64 | watch |

No F4 threshold is exceeded. The 05 crosswalk now explicitly treats ≤440 as
the NIGHT-BATCH-11 compaction snapshot rather than a permanent invariant.

## Test growth

| Metric | NB-12 reviewed baseline | NB-13 package-14 point | Growth |
|---|---:|---:|---:|
| collected outcomes | 890 | 925 | +35 (+3.93%) |
| passed | 880 | 915 | +35 |
| expected-failure baseline | 10 | 10 | unchanged |
| recorded full-suite runtime | 135.04 s | 103.18 s | -31.86 s (-23.59%) |
| tests exceeding 5 seconds | 1 | 1 | unchanged |

The runtime change is not treated as a speedup claim. Fable's independent
NB-12 run was materially faster than the recorded NIGHT-BATCH-12 environment,
which confirms that host/load dominates this metric.

The package-11 layer snapshot is:

| Layer | Outcomes | Runtime |
|---|---:|---:|
| contract | 333 (`323 passed, 10 xfailed`) | 55.08 s |
| governance | 52 | 28.20 s |
| legacy | 269 | 21.22 s |
| fuzz | 271 | 28.54 s |

The counts sum to 925, and the meta guard verifies exactly one layer per
collected test.

## `research/` growth

Branch-point baseline is master `50eb292`:

| Metric | NB-12 baseline | Before this report | Change |
|---|---:|---:|---:|
| Markdown files | 24 | 27 | +3 (+12.50%) |
| total lines (`wc -l`) | 3,040 | 3,289 | +249 (+8.19%) |

Including this 131-line report, the final state is 28 files and 3,420 lines: +4 files (+16.67%) and +380 lines (+12.50%) from `50eb292`.

There is still no ratified governance threshold for aggregate research size.
For this health report only, **3,500 lines is a non-authoritative observation
value**, not a deletion, movement, failure, or CI threshold. The directory is
approaching that observation value, so an archive review proposal is warranted
without performing it.

### Non-executed archive proposal

1. Keep current authority-adjacent artifacts in place: unresolved Owner
   proposals, the compaction crosswalk, the latest governance audit, the latest
   health report, and active design/readiness documents.
2. Consider moving only superseded dated health/audit snapshots whose findings
   all carry resolution metadata into `research/archive/2026-07/`.
3. Before any move, create an index mapping every old path to its archived path
   and update path/cross-reference guards in the same separately authorized
   package.
4. Require a fresh-context check that no Owner sentence, HOLD condition,
   evidence link, or unresolved finding becomes harder to locate.
5. Do not archive by file age or line count alone.

This proposal grants no authority to create the archive directory, move a
file, delete history, or change a governance rule.

## Health conclusion

Executable gates are green and included-module coverage remains 99%. Current
maintenance signals are research-report growth, three Round-5 documentation
findings still awaiting docs-only cleanup, and the intentionally unresolved
redaction decision. v1.0 remains blocked only by the Phase 7 writer gate and
the Owner-present Phase 9 N=1 gate.
