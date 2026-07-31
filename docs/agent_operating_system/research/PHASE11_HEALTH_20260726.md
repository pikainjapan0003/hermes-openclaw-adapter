# Phase 11 Repository Health — 2026-07-26

Status: NIGHT-BATCH-14 package 18 measurement; report only.

## Acceptance snapshot

Accepted measurement environment: WSL, Python 3.12 isolated venv
`/home/lnovo/.venvs/hoa-test`, repository mounted at
`/mnt/c/Users/Lnovo/Desktop/hermes-adapter-work`.

```text
python -m coverage run --branch -m pytest -p no:cacheprovider -q --durations=10
929 passed, 10 xfailed in 155.43s (0:02:35)

python -m mypy
Success: no issues found in 6 source files
```

The ten expected failures remain the exact ten-schema E-01 redaction baseline.
No other failure is hidden by xfail. The slowest test was the read-only
500-message capacity probe at 18.80 s; fixture-convention source scanning was
10.96 s. Runtime is a host/load observation, not an acceptance benchmark.

The Windows system Python was not used for the accepted numbers: it lacked
coverage and FastAPI, so its two setup/collection attempts were rejected before
any result was claimed. No dependency or coverage artifact was written into the
repository.

## Coverage

Command used after the full instrumented run:

```text
coverage report --include="app/*" \
  --omit=app/main.py,app/worker.py,app/google_sheets_oauth_writer.py \
  --sort=cover

TOTAL  2591 statements, 1 missed, 1060 branches, 4 partial, 99%
```

The lowest included module remains
`app/rollback_preview_builder.py` at 98%. Its only missed defensive branch
compares two flag profiles after each profile has already been required to
equal the same exact 16-key safe object; it must not be deleted merely to raise
coverage. `health_store.py`, `mock_e2e_v0_7.py`, and
`full_loop_preview_adapter.py` are 99%; every other included app module is
100%.

`app/main.py` was measured separately at 69%. Package 7 correctly held instead
of touching POST/execution/callback paths: all still-eligible GET/display units
would provide a theoretical maximum of 70.40%, below the assigned 72% target.

## F4 governance sizes

Measurement command:

```text
wc -l docs/agent_operating_system/90_LESSONS_LEARNED.md \
      docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md \
      README.md docs/agent_operating_system/NIGHT_BATCH_BACKLOG.md
```

| File | Lines | F4 maximum | Headroom | State |
|---|---:|---:|---:|---|
| `90_LESSONS_LEARNED.md` | 78 | 300 | 222 | healthy |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | 55 | watch |
| root `README.md` | 436 | 500 | 64 | watch |
| `NIGHT_BATCH_BACKLOG.md` | 196 | 500 | 304 | healthy |

No F4 threshold is exceeded.

## Test growth

| Metric | NB-13 baseline | NB-14 package-18 point | Growth |
|---|---:|---:|---:|
| collected outcomes | 925 | 939 | +14 (+1.51%) |
| passed | 915 | 929 | +14 |
| expected-failure baseline | 10 | 10 | unchanged |
| recorded full-suite runtime | 103.18 s | 155.43 s | +52.25 s (+50.64%) |
| tests exceeding 5 seconds | 1 | 2 | +1 |

The runtime increase is not treated as a regression claim. The accepted run
used the Windows-mounted worktree and the read-only capacity test itself varied
materially between same-batch runs.

## `research/` growth

Measurement command before this report:

```text
find docs/agent_operating_system/research -maxdepth 1 -type f \
  -name '*.md' -print0 | sort -z | xargs -0 wc -l
```

| Metric | NB-13 final baseline | Before this report | Change |
|---|---:|---:|---:|
| Markdown files | 28 | 36 | +8 (+28.57%) |
| total lines (`wc -l`) | 3,420 | 3,932 | +512 (+14.97%) |

Including this report, the final state is **37 files and 4,054 lines**. The
previously stated 3,500-line value was explicitly
non-authoritative; the directory now exceeds it. This is a review signal only,
not a failure, deletion trigger, movement instruction, or CI threshold.

### Non-executed archive proposal

1. First create a docs-only manifest that classifies each dated report as
   active, superseded-with-resolution, historical evidence, or unresolved.
2. Keep Owner proposals, readiness evidence, the latest audit/health report,
   unresolved findings, and compaction crosswalks at their current paths.
3. For superseded resolved snapshots only, propose an old-path → candidate-path
   map and run all path/cross-reference guards against that map.
4. Require fresh-context verification that every Owner sentence, HOLD
   condition, incident lesson, and evidence citation remains directly
   discoverable.
5. Only after a separate explicit package approves the manifest may a later
   package consider creating an archive directory or moving files.

This batch does not create an archive directory, move a file, delete history,
or ratify a research-size threshold.

## Health conclusion

Executable gates are green, mypy is green, and included-app coverage remains
99%. The active maintenance signals are research-report growth, the package-7
GET/display coverage ceiling, and the documentation/contract findings recorded
by the quarterly and Round 6 reviews. v1.0 remains blocked only by the Phase 7
writer gate and the Owner-present Phase 9 N=1 gate.
