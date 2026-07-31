# Phase 11 Repository Health — 2026-07-28

Status: NIGHT-BATCH-16 package 20 measurement only. This report does not
authorize cleanup, archive movement, product changes, persistence, execution,
dispatch, runtime/remote wiring, or either v1.0 gate.

## Acceptance snapshot

Environment: Windows PowerShell, isolated CPython virtual environment at
`C:\Users\Lnovo\AppData\Local\Temp\hoa-nb16-venv`; coverage data at
`C:\Users\Lnovo\AppData\Local\Temp\nb16-final.coverage` outside the repository.

Command:

```text
$env:COVERAGE_FILE='C:\Users\Lnovo\AppData\Local\Temp\nb16-final.coverage'
python -m coverage run --branch -m pytest -p no:cacheprovider -q --durations=10
```

Observed result:

```text
1356 passed, 1 skipped, 14 xfailed in 267.59s (0:04:27)
```

- The single skip is the Windows host's inability to create the malicious-path
  symlink used by `test_board_reader_malicious_paths.py`. It must be rerun on a
  symlink-capable WSL checkout; it is not reported as passed.
- Ten expected failures retain the E-01/E-02 schema-redaction baseline.
- Four expected failures are the new exact ES3-01 through ES3-04 read-only
  script error-surface baseline. No xfail is counted as a fix.
- No `.coverage` file was created in the repository.

Type check:

```text
python -m mypy
Success: no issues found in 6 source files
```

## Coverage

Managed application command:

```text
python -m coverage report --include='app/*' \
  --omit='app/main.py,app/worker.py,app/google_sheets_oauth_writer.py' \
  --sort=cover
```

Result:

```text
TOTAL  2591 statements, 1 missed, 1060 branches, 2 partial, 99%
```

All managed modules are 100% except the two previously classified defensive
residuals:

- `app/rollback_preview_builder.py`: 98%, with the exact-profile comparison
  unreachable after both profiles independently pass the same closed check;
- `app/full_loop_preview_adapter.py`: 99%, with a redundant nested false arc
  mathematically unreachable after the containing condition.

Those branches remain defense in depth. This batch did not delete or weaken
either for coverage.

Package 4 measured `app/main.py` over the complete suite as:

```text
774 statements, 206 missed, 172 branches, 99 covered branch arcs
raw covered opportunities 667 / 946 = 70.507% (coverage display: 71%)
```

The remaining safe GET/display candidates could add at most five opportunities
(`672/946 = 71.036%`), still below the displayed 72% target. Package 4 correctly
HOLDed with zero edit/commit rather than enter POST, control, execution, or
callback surfaces.

## Slowest instrumented calls

| Test | Duration |
|---|---:|
| 2,000-file board-reader stress probe | 99.46 s |
| 500-message board-reader capacity probe | 31.01 s |
| dependency literal-import declaration scan | 10.90 s |
| dependency declared-without-import baseline | 10.87 s |
| 1,000-entry hash-chain tamper test | 3.74 s |

The two board-reader probes dominate the instrumented suite. These are local
coverage observations, not product latency promises or CI thresholds.

## Test growth

| Metric | NIGHT-BATCH-15 final | NIGHT-BATCH-16 package-20 checkpoint | Change |
|---|---:|---:|---:|
| collected outcomes | 1,218 | 1,371 | +153 (+12.56%) |
| passed | 1,208 | 1,356 | +148 (+12.25%) |
| expected failures | 10 | 14 | +4 (ES3 exact baseline) |
| skipped | 0 | 1 | +1 (Windows symlink capability) |
| `test_*.py` files | 60 | 66 | +6 (+10.00%) |
| test Python lines | not recorded | 11,068 | informational |

The largest intentional growth is the 120-case cross-message mutation suite.
The remainder covers malicious board paths, extreme canonical JSON/hash inputs,
version evolution, corrected one-pager consistency, script leak baselines,
independent chain/golden checks, and the 12-condition preflight truth table.
Marker subsets remain organizational only; final acceptance still uses the
complete suite.

## F4 governance sizes

Byte-newline count command (equivalent to `wc -l` for these tracked files):

```text
python -c "from pathlib import Path; print(Path('<file>').read_bytes().count(b'\\n'))"
```

| File | Lines | F4 maximum | Headroom |
|---|---:|---:|---:|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | 55 |
| root `README.md` | 436 | 500 | 64 |
| `NIGHT_BATCH_BACKLOG.md` | 284 | 500 | 216 |
| root `CLAUDE.md` | 228 | 500 | 272 |
| AOS `README.md` | 52 | 500 | 448 |
| `30_DELEGATION_PROMPTS.md` | 178 | 500 | 322 |

No F4 threshold is exceeded. The plan and root README remain the closest
authority files to their thresholds; neither was compacted in this package.

## `research/` trend

Count command:

```text
python - <<'PY'
from pathlib import Path
files = list(Path('docs/agent_operating_system/research').glob('*.md'))
print(len(files), sum(p.read_bytes().count(b'\n') for p in files))
PY
```

| Metric | NIGHT-BATCH-15 final | Before this report | Including this report | Change from NB-15 |
|---|---:|---:|---:|---:|
| Markdown files | 45 | 52 | 53 | +8 (+17.78%) |
| total lines | 4,732 | 5,461 | 5,636 | +904 (+19.10%) |

The historical 45-file/4,732-line values and the current values use the same
first-level `research/*.md` byte-newline method. Growth comes from seven
NIGHT-BATCH-16 review/design/measurement files before this report.

`RESEARCH_DIR_GOVERNANCE.md` proposes—without authority—a review request at
more than 60 files or more than 6,000 lines. The directory is approaching those
observations, so that proposal is the appropriate place for an Owner choice.
This report does **not** activate the proposed threshold, create an archive,
move a file, compact a report, or delete history.

## Health conclusion

The complete suite, mypy, managed app coverage, package boundaries, and
governance thresholds remain green. Current maintenance signals are:

1. research-directory growth approaching the non-authoritative proposal values;
2. two slow board-reader measurement tests;
3. four newly explicit read-only script error-surface xfails;
4. one malicious-symlink case requiring WSL confirmation;
5. Round 7 disposition metadata and three onboarding text findings still open;
6. delegation templates needing current §6.13/C8/R-13 overlays; and
7. mixed Blackboard schema versions being preserved per entry rather than
   governed by a board-wide uniformity rule.

v1.0 remains blocked only by the separately Owner-gated Phase 7 local audit
writer and the Owner-present Phase 9 N=1 session. The Phase 7 package document
is a planning draft, not permission to implement it.
