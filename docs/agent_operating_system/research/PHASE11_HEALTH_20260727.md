# Phase 11 Repository Health — 2026-07-27

Status: NIGHT-BATCH-15 package 20 measurement and proposal only. This report
does not authorize cleanup, archive movement, product changes, runtime,
persistence, execution, dispatch, or either v1.0 gate.

## Acceptance snapshot

Environment: WSL, repository at
`/mnt/c/Users/Lnovo/Desktop/hermes-adapter-work`, Python virtual environment
`/home/lnovo/.venvs/hoa-test`.

Command:

```text
COVERAGE_FILE=/tmp/nb15.coverage python -m coverage run --branch \
  -m pytest -p no:cacheprovider -q --durations=10
```

Observed result:

```text
1208 passed, 10 xfailed in 291.88s (0:04:51)
```

The ten expected failures remain the exact E-01 schema-redaction baseline. No
new expected failure was added. The repository contains no `.coverage` output;
instrumentation data was written only to `/tmp/nb15.coverage`.

Type check:

```text
python -m mypy
Success: no issues found in 6 source files
```

## Coverage

Command:

```text
COVERAGE_FILE=/tmp/nb15.coverage python -m coverage report \
  --include="app/*" \
  --omit="app/main.py,app/worker.py,app/google_sheets_oauth_writer.py" \
  --sort=cover
```

Result:

```text
TOTAL  2591 statements, 1 missed, 1060 branches, 2 partial, 99%
```

All included modules are 100% except:

- `app/rollback_preview_builder.py`: 98%, retaining the already classified
  impossible-after-exact-profile comparison as defense in depth;
- `app/full_loop_preview_adapter.py`: 99%, retaining the already classified
  mathematically unreachable inner branch.

No product branch was deleted for coverage. `app/` has zero diff in this batch.

`app/main.py` was measured separately:

```text
app/main.py  774 statements, 206 missed, 172 branches, 9 partial, 71%
```

This is up from the accepted 69% baseline using only GET-route and pure-helper
tests. POST and forbidden execution/callback helpers remain untouched.

## Slowest calls

| Test | Instrumented duration |
|---|---:|
| 2,000-file board-reader stress probe | 79.13 s |
| 500-message board-reader capacity probe | 20.72 s |
| dependency declared-without-import scan | 17.20 s |
| dependency literal-import scan | 14.30 s |
| queue-claim dashboard guard | 3.75 s |

The same 2,000-file stress test took 26.96 seconds for its reader phase without
coverage instrumentation earlier in this batch. The 79.13-second call is
therefore treated as an instrumented host/load observation, not evidence of a
product performance regression and not a CI threshold.

## Test growth

| Metric | NIGHT-BATCH-14 final | NIGHT-BATCH-15 final | Change |
|---|---:|---:|---:|
| collected outcomes | 939 | 1,218 | +279 (+29.71%) |
| passed | 929 | 1,208 | +279 |
| expected failures | 10 | 10 | unchanged |
| `test_*.py` files | not recorded in final health | 60 | informational |
| test diff vs `441a5c3` | — | +1,118 / -8 lines | tests only |
| product `app/` diff | — | 0 | no product change |

Most growth is intentional: package 7 contributes 240 deterministic mutation
cases, and packages 8–18 add stress, long-chain, dependency, schema, preflight,
layer, and independent-golden checks. The increase is a maintenance signal,
not permission to drop layers from final acceptance.

## F4 governance sizes

Command:

```text
wc -l docs/agent_operating_system/90_LESSONS_LEARNED.md \
      docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md \
      README.md docs/agent_operating_system/NIGHT_BATCH_BACKLOG.md \
      CLAUDE.md docs/agent_operating_system/README.md
```

| File | Lines | F4 maximum | Headroom |
|---|---:|---:|---:|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | 55 |
| root `README.md` | 436 | 500 | 64 |
| `NIGHT_BATCH_BACKLOG.md` | 237 | 500 | 263 |
| root `CLAUDE.md` | 228 | 500 | 272 |
| AOS `README.md` | 52 | 500 | 448 |

No F4 threshold is exceeded. The plan and root README remain watch items but
were not compacted or rewritten in this package.

## `research/` growth

Before this report, a correctly quoted WSL command measured:

```text
find docs/agent_operating_system/research -maxdepth 1 -type f \
  -name '*.md' -print0 | sort -z | xargs -0 wc -l
```

| Metric | NIGHT-BATCH-14 final | Before this report | Change |
|---|---:|---:|---:|
| Markdown files | 37 | 44 | +7 (+18.92%) |
| total lines | 4,054 | 4,560 | +506 (+12.48%) |

Including this report, the package-20 final state is **45 Markdown files and
4,732 lines**.

The first attempt omitted safe wildcard quoting and returned an invalid zero
count; that result was rejected and is not used above.

The historical 3,500-line research observation was explicitly non-authoritative
and is already exceeded. Growth justifies a proposal, not automatic movement.

### Non-executed archive proposal

1. Create a read-only manifest classifying every research file as active
   authority-support, unresolved proposal/finding, resolved historical
   evidence, or measurement snapshot.
2. Keep all Owner-choice sources, current readiness, latest governance/health
   reports, unresolved findings, and compaction crosswalks at stable paths.
3. For resolved dated reports, first add resolution metadata; do not move a
   report whose finding status cannot be reconstructed from the manifest.
4. Prepare an old-path to proposed-path map and run every path, cross-reference,
   onboarding, and docs-drift guard against that map before asking for movement
   authority.
5. Require a separate Owner-reviewed docs package before creating an archive
   directory, moving a file, changing an index, or deleting history.

No archive directory is created and no file is moved or deleted here.

## Health conclusion

The complete suite, mypy, contract layers, and coverage remain green. The
maintenance signals are test/runtime growth, research growth, two stale
onboarding facts, three new error-surface findings, and the Round 7 RED/ROOT
proposal inconsistencies. v1.0 remains blocked only by the Phase 7 authorized
local audit writer and the Owner-present Phase 9 N=1 gate.
