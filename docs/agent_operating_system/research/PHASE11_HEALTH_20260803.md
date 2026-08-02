# Phase 11 Health — 2026-08-03 (NIGHT-BATCH-20 Round 12)

Status: **MEASUREMENT ONLY — NO PRODUCT, TEST, RUNTIME, ARCHIVE, OR OWNER-GATE AUTHORIZATION**

## Reproducibility and environment

Counts use the same path sets and `splitlines()` rule as
`tests/test_metrics_reproducibility.py`. Tests and coverage used Python 3.12.3
in `/tmp/hermes-nb20-venv` against the ext4-native clone
`/tmp/hermes-nb20-native.IPftxs/repo`. Coverage data stayed at
`/tmp/hermes-nb20.coverage`; neither checkout contains `.coverage`.

```text
python -m pytest -p no:cacheprovider -q
python -m pytest -p no:cacheprovider -o addopts="" -q --durations=15
python -m pytest -p no:cacheprovider -o addopts="" --collect-only -q
python -m mypy
COVERAGE_FILE=/tmp/hermes-nb20.coverage python -m pytest -p no:cacheprovider -q --ignore tests/test_main_coverage_floor.py --cov=app --cov-branch --cov-report=term-missing
COVERAGE_FILE=/tmp/hermes-nb20.coverage python -m coverage report --omit=app/main.py,app/worker.py,app/google_sheets_oauth_writer.py --sort=cover
python -c "from pathlib import Path; ... read_text(encoding='utf-8').splitlines()"
git diff --shortstat 97080e1..HEAD
```

## Test state and growth

| Measure | NIGHT-BATCH-19 accepted base | NIGHT-BATCH-20 measurement | Change |
|---|---:|---:|---:|
| Test files | 83 | 89 | +6 / +7.23% |
| Test source lines | 13,502 | 14,073 | +571 / +4.23% |
| Collected outcomes | 1,974 | 1,997 | +23 / +1.17% |
| Default fast | 1,942 passed; 18 deselected; 14 xfailed in 94.62s | 1,961 passed; 1 skipped; 21 deselected; 14 xfailed in 70.78s | Environment/run-order sensitive; outcome growth is authoritative, speed ratio is not |

The ext4-native full profile immediately before the package-7 coverage
correction was green: `1981 passed, 1 skipped, 14 xfailed in 616.98s
(0:10:16)`. The correction added one tests-only case, which passed separately;
the batch instruction still requires a new full run at the final package-22
HEAD. This report does not substitute the earlier full run or arithmetic for
that final acceptance command.

The default profile remains structurally honest: 1,961 fast passes plus 21
explicitly deselected slow tests accounts for the 1,982 eventual passing test
functions in the 1,997-outcome collection; the other 15 outcomes are one skip
and the unchanged 14 expected xfails.

## Coverage

The instrumented default profile completed with `1960 passed, 1 skipped,
20 deselected, 14 xfailed in 347.73s`. Package 7 then appended its one targeted
defense-in-depth test to the same `/tmp` coverage dataset.

| Managed scope | Statements | Branches | Result |
|---|---:|---:|---:|
| All `app/` except `main.py`, `worker.py`, and `google_sheets_oauth_writer.py` | 2,593 / 0 misses | 1,062 / 1 partial | 99% |
| `rollback_preview_builder.py` | 80 / 0 misses | 52 / 0 partial | 100% (was 98%) |
| `full_loop_preview_adapter.py` | 132 / 0 misses | 70 / 1 retained partial | 99% |

The remaining `full_loop_preview_adapter.py:268->271` arc is the previously
classified logically unreachable redundant guard. It was not deleted or
weakened for coverage. Managed coverage has no missing statement; rounded
branch coverage remains 99%.

## Governance line counts and F4

| File | Lines | F4 disposition |
|---|---:|---|
| `README.md` | 447 | 53-line headroom to 500 |
| `00_QUICK_DIAGNOSIS.md` | 221 | below 500 |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 55-line headroom to 500 |
| `07_AUDIT_WRITE_DESIGN.md` | 357 | below 500 |
| `10_MODEL_ORCHESTRATION.md` | 139 | below 500 |
| `20_JUDGMENT_RUBRICS.md` | 127 | below 500 |
| `30_DELEGATION_PROMPTS.md` | 216 | below 500 |
| `40_MAINTENANCE_PROTOCOL.md` | 109 | below 500 |
| `90_LESSONS_LEARNED.md` | 106 | 194-line headroom to its 300 trigger |
| `NIGHT_BATCH_BACKLOG.md` | 504 | **crossed the general 500-line F4 threshold** |

The backlog now needs a separately scoped summary/index or split proposal. This
report does not compact, move, delete, or rewrite it. README and 05 remain near
500 and should continue to point to indexed research rather than absorb long
batch history.

## Research trend

The accepted base contained **75 first-level research Markdown files / 7,748
lines**. The pre-report NIGHT-BATCH-20 snapshot contains **80 files / 8,187
lines**: **+5 files / +439 lines** (+6.67% files, +5.67% lines). This health
report is intentionally excluded from the pre-report snapshot and must be
counted by the next recomputation.

`RESEARCH_DIR_GOVERNANCE.md` v3 observes that its proposed 60-file and
6,000-line review-request triggers are crossed. Its Owner field remains blank,
so the only valid state is review-request eligible with movement HOLD. No
archive directory, move, rename, compression, or deletion occurred.

## Change shape

Before this report, `97080e1..HEAD` contains 22 commits and reports `25 files
changed, 1226 insertions(+), 45 deletions(-)`. `app/` product code and every
schema JSON have zero diff. Product changes are limited to the stdout-only
schema renderer; the rest is tests, scripts documentation, governance and
research evidence.

## Findings and blockers

1. **Healthy:** native fast and pre-correction full profiles are green; mypy is
   `Success: no issues found in 6 source files`; managed coverage remains 99%.
2. **Healthy:** package 7 reaches its ≥99% targets without deleting defensive
   code: rollback is 100%, full-loop is 99% with one explained false arc.
3. **Portability debt:** the mounted `/mnt/c` full run failed only because an
   internal `git diff --check 9d26477` exceeded 30 seconds. The native clone did
   not reproduce it. Do not xfail or weaken the guard; design timeout semantics
   separately.
4. **HOLD:** package 8 proved current schemas accept unknown/downgraded/mixed
   `schema_version` strings; tests-only scope cannot create evolution policy.
5. **HOLD:** package 10 proved the requested approval/evidence four-field join
   does not exist in the actual contract shape; tests-only scope cannot invent
   it.
6. **Governance maintenance:** the backlog crossed 500 lines and Round-12 has
   one P2 plus two P3 documentation findings. These are future docs work, not
   authority to repair them in this report.
7. **Owner gates unchanged:** AUD/RB/PB/ROOT remain blank. Phase 7 still needs
   the exact active Owner instruction, and Phase 9 still needs Phase 7 closeout
   plus synchronous Owner presence.

NIGHT-BATCH-20 improves read-only contracts, evidence and governance. It
creates no audit writer, persistent data path, execution/dispatch path, token,
route, runtime/remote wiring, archive, or schema change.
