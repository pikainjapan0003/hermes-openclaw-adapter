# Phase 11 Health — 2026-08-02 (NIGHT-BATCH-19 Round 11)

Status: **MEASUREMENT ONLY.** This report does not authorize product changes,
persistence, an audit writer, execution/dispatch, token changes, runtime or
remote wiring, schema changes, or an Owner option selection.

## Reproducibility and environment

Measurements used the authorized Windows checkout on branch
`night-batch-19` with Python 3.12 in
`hoa-nb18-win-venv`. Coverage data was directed to
`C:\Users\Lnovo\AppData\Local\Temp\hoa-nb19.coverage`; repo `.coverage`
remained absent.

```text
python -m pytest -p no:cacheprovider -q
python -m pytest -p no:cacheprovider -o "addopts=" -q
python -m mypy
git diff --check 9d26477
python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py --cov=app --cov-branch --cov-report=term-missing
python -m coverage report --omit=app/main.py,app/worker.py,app/google_sheets_oauth_writer.py --sort=cover
python -c "from pathlib import Path; ... read_text(encoding='utf-8').splitlines()"
```

## Fast path versus full path

| Profile | Exact result | Meaning |
|---|---|---|
| Default fast | `1936 passed, 6 skipped, 18 deselected, 14 xfailed in 97.00s (0:01:37)` | Daily feedback; slow tests deliberately deselected |
| Full after correction | `1954 passed, 6 skipped, 14 xfailed in 366.77s (0:06:06)` | Batch acceptance; all slow tests included |
| Mypy | `Success: no issues found in 6 source files` | Existing typed-module scope |

The first full run was **not** green: `1 failed, 1953 passed, 6 skipped,
14 xfailed in 300.36s`. The slow metrics guard independently ran
`git diff --check 9d26477` and found nine new EOF blank lines that ordinary
working-tree `git diff --check` had missed while the files were untracked or
already committed. Commit `26ded83` removed exactly those nine blank lines;
the metrics/slow guard then passed 6/6 and the full suite was rerun to the green
result above. This is direct evidence for L-010/F7 item 5, not a hidden retry.

Total full outcomes are 1,974 (`1954 + 6 + 14`), up from the NIGHT-BATCH-18
baseline of 1,882: **+92 outcomes / +4.89%**. The established 14-xfail
redaction baseline did not grow.

### Later accepted closeout (metadata only)

The original package-time measurements above remain unchanged. Fable 5 later
accepted final NIGHT-BATCH-19 HEAD `97080e1` after independently running the
same two profiles in native WSL: default fast was `1942 passed, 18 deselected,
14 xfailed in 94.62s`; full was `1960 passed, 14 xfailed in 403.54s`. This note
is later-status metadata, not a rewrite of the point-in-time rows and not an
authorization for any runtime or safety-gated work.

## Coverage

The coverage measurement used the fast profile and omitted only the separate
coverage-floor test from pytest collection to avoid recursive instrumentation.
It completed as:

```text
1936 passed, 6 skipped, 17 deselected, 14 xfailed in 326.50s (0:05:26)
```

Raw all-app coverage was 90%; the explicitly unmanaged modules remained
visible as `main.py` 70%, `worker.py` 17%, and
`google_sheets_oauth_writer.py` 0%. With exactly those three omitted, managed
coverage was:

| Managed scope | Statements | Branches | Result |
|---|---:|---:|---:|
| All other `app/` modules | 2,593 / 1 miss | 1,062 / 2 partial-or-missed | 99% |

The lowest managed modules remain `rollback_preview_builder.py` at 98% and
`full_loop_preview_adapter.py` at 99%. Their defensive branches were not
deleted for coverage.

## Line counts and F4 headroom

| File/inventory | Current measurement | F4 threshold/status |
|---|---:|---|
| `00_QUICK_DIAGNOSIS.md` | 221 lines | below 500 single-file threshold |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 lines | 55-line headroom to 500 |
| `20_JUDGMENT_RUBRICS.md` | 127 lines | below 500 |
| `40_MAINTENANCE_PROTOCOL.md` | 109 lines | below 500 |
| `90_LESSONS_LEARNED.md` | 96 lines | 204-line headroom to its 300 trigger |
| `NIGHT_BATCH_BACKLOG.md` | 445 lines | 55-line headroom to 500 |
| root `README.md` | 447 lines | 53-line headroom to 500 |
| test files | 83 | NIGHT-BATCH-18 baseline 76; +7 |
| test source | 13,502 lines | baseline 12,642; +860 / +6.80% |

No governed file crossed F4. README, 05, and backlog are all within 55 lines
of 500, so the next docs-heavy batch should prefer indexed reports over adding
long current-state prose to those three files.

## Research trend

The pre-report snapshot contained **74 research Markdown files / 7,620 lines**.
The requested comparison baseline was **69 files / 7,287 lines**, so the trend
before adding this report was **+5 files / +333 lines** (+7.25% files,
+4.57% lines). The five additions are scoped review/evidence reports; no
archive, move, rename, compression, or deletion occurred.

This file itself is intentionally excluded from that pre-report snapshot, as
in prior Phase-11 point-in-time reports. A future recomputation must count it
rather than copy these numbers.

## Change-growth signal

NIGHT-BATCH-19 through package 21 had 20 commits because packages 6, 9, and 11
were HOLD with no commit, while packages 2 and 21 each needed a transparent
correction commit. The base-to-head stat before this report was 27 files,
1,332 insertions, and 24 deletions. `app/` product code had zero diff.

Test source grew by 860 lines while product source grew by zero. A finite
test-to-product line ratio is therefore not meaningful; report it as
`860 test lines : 0 product lines`, not as division by zero or “infinite
quality.” The growth is dominated by explicit boundary, integrity, and scale
tests rather than product behavior.

## Health findings and remaining blockers

1. **Healthy:** default feedback dropped from multi-minute full runs to 97
   seconds in this measurement, while the documented full path remains green.
2. **Healthy:** managed coverage remains 99%, mypy remains green, and the 14
   expected redaction xfails are unchanged.
3. **HOLD:** package 6 proved a board-root symlink is accepted; F7 requires
   rejection, but that package forbade a reader change.
4. **HOLD:** package 9's truncated/oversized Replit-body requirement conflicts
   with the current HTTP-reachability-only tool.
5. **HOLD:** package 11 proved `$ref`, unions, and deep schema semantics are not
   fully rendered; tests-only scope could not repair the renderer.
6. **Owner gates unchanged:** Phase 7 still needs the exact active instruction,
   and Phase 9 still needs completed Phase 7 plus synchronous Owner presence.

The batch improves evidence and maintenance speed only. It creates no audit
writer, persistent data path, execution/dispatch path, token, route, runtime,
remote connection, or schema change.
