# Phase 11 Health — 2026-08-01 (NIGHT-BATCH-18 Round 8)

Status: **MEASUREMENT ONLY. This report does not authorize product, runtime,
persistence, audit-writer, execution, dispatch, remote, or schema changes.**

## Reproducibility

Measurements were run in the isolated Windows project environment
`hoa-nb18-win-venv` on the NIGHT-BATCH-17 checkout. Coverage data was written
to `C:\Users\Lnovo\AppData\Local\Temp\hoa-nb18-final.coverage`, outside the
repository. The commands were:

```text
python -m pytest -p no:cacheprovider --collect-only -q
python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py --cov=app --cov-branch --cov-report=term-missing
python -m coverage report --omit=app/main.py,app/worker.py,app/google_sheets_oauth_writer.py --sort=cover
python -c "from pathlib import Path; ... splitlines()"
git diff --check
```

The coverage-floor test is excluded from the coverage measurement because it
launches its own instrumented child suite. The normal full-suite run remains a
separate acceptance checkpoint.

## Test and runtime measurements

The complete collection contains **1,882 test outcomes** (the coverage run has
1,881 outcomes because it excludes the floor test). The package-22 coverage
run completed as:

```text
1861 passed, 6 skipped, 14 xfailed in 391.04s (0:06:31)
```

The 14 expected xfails remain the established ten schema-error cases and four
ES3 read-only-tool cases. The six skips are platform/capability-dependent
boundary cases; no new xfail or skip was introduced by this report.

## Coverage

The branch-inclusive run reported 3,564 statements and 1,270 branch
opportunities across `app/`. The explicitly excluded modules remain visible in
the raw report: `main.py` 71%, `worker.py` 17%, and
`google_sheets_oauth_writer.py` 0%.

The managed scope excludes exactly those three modules:

| Scope | Statements | Branches | Combined coverage |
|---|---:|---:|---:|
| Managed `app/` modules | 2,593 statements / 1 miss | 1,062 opportunities / 2 partial-or-missed | 99% reported |

The managed-module floor remains satisfied. The lowest managed module is
`rollback_preview_builder.py` at 98%; its one defensive branch is retained.
`full_loop_preview_adapter.py` is 99% with one defensive partial branch. No
product branch was removed to improve coverage.

## F4 line-count and growth snapshot

| File or inventory | Lines/items |
|---|---:|
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 |
| `README.md` | 436 |
| `07_AUDIT_WRITE_DESIGN.md` | 357 |
| `NIGHT_BATCH_BACKLOG.md` | 376 |
| `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` | 332 |
| `90_LESSONS_LEARNED.md` | 86 |
| `40_MAINTENANCE_PROTOCOL.md` | 101 |
| `tests/test_*.py` files | 76 |
| test-source lines | 12,642 |
| research Markdown files | 68 |
| research Markdown lines | 7,190 |

All governed F4 thresholds remain below their limits: 05 is 445/500, README
436/500, and 90 is 86/300. The backlog is 376 lines and should be managed as
governance inventory, not silently deleted or compressed.

## Maintenance signals

1. Fixture SHA-256 checks are now line-ending portable and covered by a fixed
   50-file inventory plus golden-vector tests.
2. The board reader rejects malformed, non-regular, outside-root, recursive,
   and duplicate-key inputs without echoing payloads. A valid hardlink is
   informationally marked `shared_inode`; a future writer remains prohibited
   from accepting it.
3. Mirror `DIFFERS` is a human-decision state. No read-only tool overwrites a
   repo or mirror copy.
4. The remaining Round-10 findings are review items only. They do not grant an
   implementation package or an Owner gate.

## Owner gates and conclusion

AUD, RB, PB, and ROOT decisions remain blank. Phase 7 still needs the exact
Owner instruction `允許寫入 data/audit_dev.jsonl（local dev append-only）`, and
Phase 9 still requires Owner presence. This measurement report selects none of
them. NB18 increased contract evidence and cross-platform reproducibility
without adding a persistence or execution path; the managed coverage floor and
all current F4 thresholds remain green.
