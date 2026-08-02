# Phase 11 Health — 2026-08-04 (NIGHT-BATCH-21 Round 13)

Status: **MEASUREMENT ONLY — NO PRODUCT, TEST, RUNTIME, ARCHIVE, OR OWNER-GATE AUTHORIZATION**

## Reproducibility and environment

Line, file and diff counts were recomputed at package-21 HEAD `08160ad` from
the authorized Windows checkout. Test timing used the package-18 HEAD
`30e2504` in an ext4-native disposable WSL clone with Python 3.12.3; packages
19–21 changed reports/governance only, so they do not change collection or test
behavior. Coverage is the package-7 recomputed closeout; no product source
changed afterward. The final package-22 HEAD still requires a separate full
suite run.

```text
# PowerShell, repository root
[IO.File]::ReadAllLines((Resolve-Path $path), [Text.Encoding]::UTF8).Length
Get-ChildItem tests -File -Filter *.py
Get-ChildItem docs/agent_operating_system/research -File -Filter *.md
git rev-list --count 7cd2d98..HEAD
git diff --shortstat 7cd2d98..HEAD

# ext4-native WSL clone
python -m pytest -q --durations=20
python -m pytest -o addopts="" -q --durations=20
python -m mypy
```

## Test state and growth

| Measure | Accepted NIGHT-BATCH-20 base | NIGHT-BATCH-21 package-21 snapshot | Change |
|---|---:|---:|---:|
| Test files | 89 | 95 | +6 / +6.74% |
| Test source lines | 14,073 | 14,776 | +703 / +5.00% |
| Collected outcomes | 1,997 | 2,121 | +124 / +6.21% |
| Default fast | Baseline `1960 passed, 1 skipped, 21 deselected, 14 xfailed in 133.83s` | `2085 passed, 1 skipped, 21 deselected, 14 xfailed in 304.26s`; wall `328.57s` | Green; `<150s` objective not met |
| Full | Baseline `1981 passed, 1 skipped, 14 xfailed in 616.98s` | `2106 passed, 1 skipped, 14 xfailed in 759.87s`; wall `803.64s` | Green; +125 passing tests at this checkpoint |

The profile remains structurally honest: 2,085 fast passes plus 21 explicitly
deselected slow tests equals 2,106 full passes; the remaining outcomes are one
skip and the unchanged 14 expected xfails. The six new test files contribute
124 outcomes. Their focused run was `124 passed in 6.69s`, with a 0.59-second
slowest call, so package 19 found no newly added >2-second item eligible for a
marker-only repair. The run-level fast regression requires a separately scoped
aggregate-cost review; it was not hidden by bulk marking.

Mypy result at the same product-code state:

```text
Success: no issues found in 6 source files
```

## Coverage

Package 7 recomputed and documented the only managed residual. No later
package changed `app/` product code.

| Managed scope | Statements | Branches | Result |
|---|---:|---:|---:|
| All `app/` except `main.py`, `worker.py`, and `google_sheets_oauth_writer.py` | 2,593 / 0 misses | 1,062 / 1 partial | 99% |
| `rollback_preview_builder.py` | 80 / 0 misses | 52 / 0 partial | 100% |
| `full_loop_preview_adapter.py` | 132 / 0 misses | 70 / 1 retained partial | 99% |

The remaining `full_loop_preview_adapter.py:268->271` branch is logically
unreachable under the outer predicate and retained as defense in depth. It was
not removed or weakened to manufacture a coverage number.

## Governance line counts and F4

| File | Lines | F4 disposition |
|---|---:|---|
| `README.md` | 52 | below 500 after accepted compaction |
| `00_QUICK_DIAGNOSIS.md` | 221 | below 500 |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 55-line headroom to 500 |
| `07_AUDIT_WRITE_DESIGN.md` | 357 | below 500 |
| `10_MODEL_ORCHESTRATION.md` | 139 | below 500 |
| `20_JUDGMENT_RUBRICS.md` | 127 | below 500 |
| `30_DELEGATION_PROMPTS.md` | 216 | below 500 |
| `40_MAINTENANCE_PROTOCOL.md` | 113 | below 500 |
| `90_LESSONS_LEARNED.md` | 116 | 184-line headroom to its 300 trigger |
| `NIGHT_BATCH_BACKLOG.md` | 450 | 50-line headroom to 500; Round-11 stock compacted in place |

No listed governance file crosses its F4 threshold. `05` and the backlog are
the closest and should continue to index research evidence rather than absorb
long narrative histories.

## Research trend

Accepted NIGHT-BATCH-20 contains **81 first-level research Markdown files /
8,314 lines**. Before this report, NIGHT-BATCH-21 contains **90 files / 8,940
lines**: **+9 files / +626 lines** (+11.11% files, +7.53% lines). This report is
excluded from that pre-report snapshot and must be included by the next
recomputation.

`RESEARCH_DIR_GOVERNANCE.md` v4 now has an exact 18-path proposed candidate
list and a one-sentence Owner response format. Every candidate remains movement
HOLD because retention, path-map, link-ledger, separate move instruction and
Owner decision prerequisites are absent. No archive directory, move, rename,
compression or deletion occurred.

## Change shape

Before this report, `7cd2d98..08160ad` contains 20 commits and reports:

```text
22 files changed, 1252 insertions(+), 103 deletions(-)
```

`app/main.py`, `app/google_sheets_oauth_writer.py`, every schema JSON, formal
`data/`, runtime/remote wiring, execution/dispatch and execution-token behavior
have zero authorized change in this batch.

## Findings and blockers

1. **Healthy:** the fast and full profiles are green, collection arithmetic is
   exact, mypy is green, and managed coverage remains 99% with no missing
   statement.
2. **Performance debt:** the clean native fast profile is 304.26 seconds and
   misses the `<150s` objective. New files do not contain a >2-second test;
   aggregate profiling is the honest next step.
3. **HOLD:** package 5's brief falsely claimed no current schema uses `allOf`;
   the existing remote-readonly projection does. No renderer claim or test was
   fabricated.
4. **HOLD:** package 10 required detached/shallow fail-closed behavior that the
   present three-source tool does not expose. Tests-only scope could not invent
   an implementation gate.
5. **Governance debt:** Round 13 records two P2 and three P3 findings, including
   the fourth contract/spec precheck failure. L-012 and F8 now require actual
   field evidence, but a later proposal must broaden the rule to schema-keyword
   and behavior preconditions.
6. **Owner gates unchanged:** AUD/RB/PB/ROOT remain blank. Phase 7 still needs
   the exact active Owner instruction, and Phase 9 still needs Phase 7 closeout
   plus synchronous Owner presence.

NIGHT-BATCH-21 improves proposals, tests, evidence and maintenance controls.
It creates no audit writer, persistent data path, execution/dispatch path,
token, route, runtime/remote wiring, archive, or schema change.
