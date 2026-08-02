# Phase 11 Health - 2026-08-05 (NIGHT-BATCH-22 Round 14)

Status: **MEASUREMENT ONLY - NO PRODUCT, TEST, RUNTIME, ARCHIVE, OR OWNER-GATE AUTHORIZATION**

This report records recomputable repository health at the NIGHT-BATCH-22
package-22 starting point (`9f4e8a3`). It does not authorize persistence,
execution, dispatch, remote wiring, an archive move, Phase 7, or Phase 9.

## Reproducibility and environment

The accepted baseline is master `fa1ffb8`; this branch is not an accepted phase
state until its independent review and merge. Test timing was measured with
Python 3.12.3 in WSL2. The complete run used the current worktree with full
Git history so the reproducibility test could resolve `9d26477`.

```text
# PowerShell, repository root
[IO.File]::ReadAllLines((Resolve-Path $path), [Text.Encoding]::UTF8).Length
Get-ChildItem tests -File -Filter *.py
Get-ChildItem docs/agent_operating_system/research -File -Filter *.md
git rev-list --count fa1ffb8..HEAD
git diff --shortstat fa1ffb8..HEAD

# WSL2, disposable venv
python -m pytest -q --durations=15
python -m pytest -o addopts="" -q --durations=15
python -m mypy
```

The Windows system Python was not used for suite timing because its
environment lacks FastAPI and collection stops with `ModuleNotFoundError`.

## Test state and growth

| Measure | Accepted NIGHT-BATCH-21 result | NIGHT-BATCH-22 result | Change |
|---|---:|---:|---:|
| Test files | 95 (prior report) | 99 | +4 files |
| Test source lines (UTF-8 `splitlines`) | not measured with this command | 15,486 | Baseline not recomputed; do not infer a percentage |
| Collected outcomes | 2,121 (prior report) | 2,304 collected / 2,283 active after 21 deselections | +183 full outcomes |
| Default fast | `2085 passed, 1 skipped, 21 deselected, 14 xfailed in 304.26s` | `2268 passed, 1 skipped, 21 deselected, 14 xfailed in 135.89s` | Green; +183 passes |
| Complete | `2106 passed, 1 skipped, 14 xfailed in 759.87s` | `2289 passed, 1 skipped, 14 xfailed in 716.78s` | Green; +183 passes |

The arithmetic is exact: 2,268 fast-path passes plus 21 deliberately
deselected slow tests equals 2,289 complete-path passes. The skip and 14
expected failures are unchanged. The fast and complete runs both finished
green; the complete run is the authoritative Git-dependent measurement.

## Managed coverage

No `app/` source changed after the package-15 coverage rotation. The latest
recomputed managed coverage therefore remains valid for this docs/tests-only
tail of the batch:

| Scope | Statements | Branches | Result |
|---|---:|---:|---:|
| All `app/` except `main.py`, `worker.py`, `google_sheets_oauth_writer.py` | 2,593 / 0 misses | 1,062 / 1 partial | 99% |
| `contracts_v0_7.py` | 122 / 0 misses | 92 / 0 partial | 100% |
| `full_loop_preview_adapter.py` | 132 / 0 misses | 70 / 1 retained partial | 99% |

The retained defensive branch is not removed for a coverage number. The three
excluded modules remain excluded exactly as specified by the managed scope.

## Governance file sizes and F4

Counts use UTF-8 `ReadAllLines`/`splitlines`, not a pipeline count that can
discard line boundaries:

| File | Lines | F4 disposition |
|---|---:|---|
| `README.md` | 447 | below 500 |
| `docs/agent_operating_system/00_QUICK_DIAGNOSIS.md` | 221 | below 500 |
| `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` | 446 | below 500 |
| `docs/agent_operating_system/07_AUDIT_WRITE_DESIGN.md` | 357 | below 500 |
| `docs/agent_operating_system/10_MODEL_ORCHESTRATION.md` | 139 | below 500 |
| `docs/agent_operating_system/20_JUDGMENT_RUBRICS.md` | 127 | below 500 |
| `docs/agent_operating_system/30_DELEGATION_PROMPTS.md` | 216 | below 500 |
| `docs/agent_operating_system/40_MAINTENANCE_PROTOCOL.md` | 147 | below 500 |
| `docs/agent_operating_system/90_LESSONS_LEARNED.md` | 126 | below its 300 trigger |
| `docs/agent_operating_system/NIGHT_BATCH_BACKLOG.md` | 507 | **above the 500-line F4 review trigger** |

The current mechanical F4 test covers `90`, `05`, and `README`; it does not
cover the backlog. The backlog crossing is therefore a documented maintenance
finding, not a reason to delete or silently compress text. A future, separately
scoped docs package should produce a rule-by-rule compaction proposal; this
batch does not execute that compaction.

## Research trend

Immediately before this report, the first-level `research/*.md` inventory was
**97 files and 9,606 lines**, measured with the UTF-8 command above. Adding
this report makes the next snapshot 98 files; the exact post-report count must
be recomputed rather than guessed. The v5 research-governance proposal records
the same pre-report count and keeps all movement in `MOVEMENT HOLD`.

The 60-file/6,000-line review-request triggers are exceeded. This makes a
governance review eligible; it does not authorize an archive directory, move,
rename, compression, or deletion. Owner choice of research-governance option
remains blank.

## Change shape and test-to-code ratio

For `fa1ffb8..9f4e8a3`, the measured diff is:

```text
29 files changed, 1416 insertions(+), 8 deletions(-)
```

The additions break down as 711 test lines, 68 read-only script lines, and
zero `app/` product-code lines. Thus the test-to-read-only-tooling addition
ratio is **711:68 (10.46:1)**; a test-to-`app/` ratio is undefined because the
denominator is zero. This is evidence of a test/docs-heavy batch, not a
permission to add runtime code.

## Findings and blockers

1. **Healthy:** fast and complete profiles are green and exactly reconciled;
   mypy and managed coverage remain green from the latest product-code check.
2. **Maintenance finding:** `NIGHT_BATCH_BACKLOG.md` is at 507 lines and
   exceeds the F4 review trigger. Propose compaction in a future docs-only
   package; do not delete a rule or Owner sentence.
3. **Design gap:** detached-HEAD and shallow-clone semantics are not exposed by
   the current three-source tool/schema, so tests do not invent fail-closed
   claims for them.
4. **Owner gates unchanged:** AUD/RB/PB/ROOT remain blank. Phase 7 still needs
   the exact active Owner instruction, and Phase 9 still needs Phase 7 closeout
   plus synchronous Owner presence.

NIGHT-BATCH-22 adds evidence, tests, read-only tooling, and planning documents;
it creates no audit writer, persistent data path, execution/dispatch path,
token, route, runtime/remote wiring, archive, or schema change.
