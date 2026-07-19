# Governance Audit — Round 2 (2026-07-21)

Status: **REVIEW ONLY — FINDINGS NOT FIXED**

Scope: `10_MODEL_ORCHESTRATION.md`, `20_JUDGMENT_RUBRICS.md`,
`30_DELEGATION_PROMPTS.md`, `90_LESSONS_LEARNED.md`,
`99_LETTER_TO_FUTURE_SESSIONS.md`, `CLAUDE.md`, and
`NIGHT_BATCH_BACKLOG.md`, cross-checked against the authority and current-state
rules in `01_SAFETY_BOUNDARIES.md` and `05_VERIFIED_LONG_TERM_PLAN.md`.

This report only records defects and ambiguity. It changes none of the reviewed
rules, decisions, routes, code, or runtime behavior.

## 1. Method

The review checked five failure classes requested by NIGHT-BATCH-8:

1. repository or external paths that no longer resolve;
2. rules that give incompatible instructions for the same operation;
3. status claims that are older than the Phase 5 table or landed artifacts;
4. time-sensitive model/tool claims presented as current fact;
5. wording that a weak model could turn into excess authority or an incorrect HOLD.

All seven files were read with line numbers. Referenced landed artifacts were checked
on disk, and the NIGHT-BATCH commit history was inspected read-only. The external
model-routing path named by 10 C8 currently exists at
`C:\Users\Lnovo\Desktop\Dream-system\03_MODEL_ROUTING_RULES.md`; that fact does
not resolve its versioning risk described below.

## 2. Severity summary

| Severity | Count | Summary |
|---|---:|---|
| P0 | 0 | No active execution, dispatch, token, writer, or remote-connection authorization was found. |
| P1 | 0 | No currently reachable unsafe code path was in scope. |
| P2 | 6 | One authority conflict, four stale handoff/backlog failures, and one source-of-truth ambiguity. |
| P3 | 3 | Two stale historical/model statements and one obsolete future-tense lesson. |

## 3. Findings

### G2-01 — P2 — Night-batch standing instruction is absent from other top-priority authorization rules

Evidence:

- `CLAUDE.md:76-106` requires every executable instruction to use one exact
  Owner-instruction wrapper; `CLAUDE.md:147-158` and `CLAUDE.md:182` require a
  hard stop and prohibit advancing without the next Owner instruction.
- `CLAUDE.md:205` says this file and 01 outrank all other documents, and repeats
  that authorization exists only in an Owner instruction.
- `20_JUDGMENT_RUBRICS.md:54-62` similarly says an action must HOLD when its
  authority comes from a previous instruction or plan.
- `99_LETTER_TO_FUTURE_SESSIONS.md:12`, `:21`, and `:60` repeat the per-phase
  hard-stop rule without a night-batch exception.
- The newer rule is `05_VERIFIED_LONG_TERM_PLAN.md:464-468`: after Fable 5 batch
  review, merge/push and opening the next night batch do not wait for another Owner
  response. Its exception is mirrored in `01_SAFETY_BOUNDARIES.md:71`, so one of
  the two documents that CLAUDE declares co-highest now disagrees with CLAUDE.

Weak-model failure mode: one model follows CLAUDE/20 and incorrectly HOLDs the
approved batch merge; another follows 05 too broadly and treats the night-batch
standing instruction as authority for an ordinary phase. The exception needs one
bounded cross-reference in every authorization summary, not a relaxation of any
Phase 7/9/v1.1/v1.2 hard gate.

### G2-02 — P2 — Backlog says consumed work is marked, but multiple completed items remain advertised as stock

Evidence:

- `NIGHT_BATCH_BACKLOG.md:5` promises that each consumed item is marked with its
  NIGHT-BATCH number.
- `NIGHT_BATCH_BACKLOG.md:20-24` still lists the v1.1 design, v1.2 design, O1
  proposal, O2 proposal, and role prompts as available even though the files exist
  as `11_V1_1_FIRST_REAL_WRITE_DESIGN.md`,
  `14_V1_2_FIRST_CODE_TASK_DESIGN.md`,
  `research/O1_PLAN_LEVEL_AUTH_PROPOSAL.md`, and
  `research/O2_ROLE_WORKER_PROPOSAL.md`.
- `NIGHT_BATCH_BACKLOG.md:30-32` still advertises the Blackboard layout/reader,
  Hermes wiring design, and Phase 10 research after
  `12_BLACKBOARD_DATA_LAYOUT.md`, `app/blackboard_board_reader.py`,
  `13_HERMES_WIRING_DESIGN.md`, and
  `research/PHASE10_CONNECTOR_SCOPE_RESEARCH.md` landed.
- `NIGHT_BATCH_BACKLOG.md:40-41` still advertises the trust scan and Phase 0
  checker after `tests/test_trust_violation_scan.py` and
  `scripts/check_three_source_readonly.py` landed.
- The consumed list at `NIGHT_BATCH_BACKLOG.md:54-57` records only a subset of
  NB-6/NB-7 work and therefore cannot disambiguate these rows.

Weak-model failure mode: a future batch generator selects an already-completed
item and spends a package recreating or conflicting with an existing artifact.

### G2-03 — P2 — Backlog retains two findings that NIGHT-BATCH-7 already fixed

Evidence:

- `NIGHT_BATCH_BACKLOG.md:49` still labels the Phase 7 design corrections as
  pending, but commit `b660a24` changed `07_AUDIT_WRITE_DESIGN.md` for those
  findings.
- `NIGHT_BATCH_BACKLOG.md:50` still labels the production-endpoint guard as a
  pending P2 bug, but commit `87c4112` connected the guard and added regression
  tests.

Weak-model failure mode: a later package repeats the fix, changes frozen wording,
or reports a resolved P2 as an active release blocker.

### G2-04 — P2 — The future-session handoff tells the next model to reopen completed Phase 2

Evidence:

- `99_LETTER_TO_FUTURE_SESSIONS.md:43-51` says its incomplete list is synchronized
  through 2026-07-19 and explicitly records Phase 2-6 complete.
- `99_LETTER_TO_FUTURE_SESSIONS.md:59` then tells the next session to ask whether
  to commit the governance system and whether to begin Phase 2.
- The current authority table also records Phase 2 complete at
  `05_VERIFIED_LONG_TERM_PLAN.md:286`.

Weak-model failure mode: a fresh session reopens a frozen definition or asks the
Owner to repeat an already-recorded decision instead of reading the current table.

### G2-05 — P2 — The handoff simultaneously says Phase 0 is complete and must run every session

Evidence:

- `99_LETTER_TO_FUTURE_SESSIONS.md:41` puts the three-source verification under
  “completed (do not redo)” and pins the historical hash `7a93127e`.
- `99_LETTER_TO_FUTURE_SESSIONS.md:58` correctly tells the next session to run
  Phase 0 again.
- `20_JUDGMENT_RUBRICS.md:101-107` makes the check mandatory at session start and
  before push/deploy decisions.

Weak-model failure mode: the phrase “do not redo” wins over the later checklist,
so the model reuses the historical hash and misses local/GitHub drift. The history
can remain, but it cannot be worded as a permanent completion of a recurring gate.

### G2-06 — P2 — Model-routing authority is delegated to an unversioned path outside the repo source of truth

Evidence:

- `10_MODEL_ORCHESTRATION.md:96` declares
  `Desktop\Dream-system\03_MODEL_ROUTING_RULES.md` authoritative on construction
  routing and says this repo contains only a summary.
- `05_VERIFIED_LONG_TERM_PLAN.md:374` declares GitHub master the system source of
  truth. `90_LESSONS_LEARNED.md:62-69` records a prior incident caused by newer
  governance living outside the repo.
- The external file exists in this workstation check, but none of the reviewed
  files specifies a revision/hash, a one-way synchronization rule for Dream-system,
  or fail-closed behavior when another environment cannot read that path.

Weak-model failure mode: two workstations use different routing rules while both
claim compliance, or an environment without the Desktop path silently treats the
repo summary as authoritative. This is a source-of-truth ambiguity, not permission
to copy or edit the external file in this package.

### G2-07 — P3 — The handoff's author-date statement is contradicted by later verified use

Evidence:

- `99_LETTER_TO_FUTURE_SESSIONS.md:3` calls 2026-07-07 Fable 5's “last available
  day.”
- `10_MODEL_ORCHESTRATION.md:14` records that Fable 5 returned on 2026-07-14 and
  was the active model on 2026-07-18; `:102` still assigns it a current role.

Weak-model failure mode: a model concludes the named reviewer is unavailable and
unnecessarily downgrades or changes the review route. This is stale history rather
than a present safety-boundary defect.

### G2-08 — P3 — Phase 6 lesson remains written as an unperformed future action

Evidence:

- `90_LESSONS_LEARNED.md:59-60` says Phase 6 “will have to” add the review POST
  allowlist and tests, and describes its validation as future work.
- `05_VERIFIED_LONG_TERM_PLAN.md:290` records Phase 6 complete, including the
  dynamic route inventory, POST allowlist, and approve-without-dispatch tests.

Weak-model failure mode: a reader treats the lesson as an open implementation item
and duplicates the completed work. The historical incident is still useful; only
its resolution tense is stale.

### G2-09 — P3 — The handoff current-state block stopped being current after later batches

Evidence:

- `99_LETTER_TO_FUTURE_SESSIONS.md:43` explicitly limits synchronization to
  2026-07-19.
- `:46-50` omits the subsequent preflight guard, full-chain/hash-chain rehearsal,
  contract fuzz, coverage, model-checking, readonly board reader, and later design
  documents that are now visible in the repository.
- The same file calls section 5 the place from which a successor should start at
  `:39`, increasing the chance that the dated snapshot is read as exhaustive.

Weak-model failure mode: a successor repeats completed preparation or reports the
repository as less mature than the authoritative 05 table and current files show.

## 4. No-finding checks

- All repo-relative paths in the reviewed files that are presented as current
  artifacts resolved during this review. Placeholder paths inside delegation
  templates were not treated as artifacts.
- The Dream-system routing file and the old Drive mirror directory both existed on
  this workstation; the finding above is about authority/versioning, not a missing
  path claim.
- No reviewed sentence grants Phase 7 audit persistence, Phase 9 execution, a
  non-null token, new POST behavior, Worker dispatch, OpenClaw execution, or remote
  wiring.
- 20 R-13 and 10 C8 agree that high-risk acceptance needs at least two independent
  different-model reviewers; no conflict was found there.
- 30's T-06/T-07 templates retain read-back/adversarial separation and explicitly
  prohibit the reviewer from fixing files during review.

## 5. Recommended repair order (not executed)

1. Bound the 05 §6.13 exception in CLAUDE, 20, and 99 without relaxing Phase
   7/9/v1.1/v1.2 gates (G2-01).
2. Synchronize the backlog and remove only the already-consumed stock/findings
   (G2-02/G2-03).
3. Replace the obsolete handoff steps and recurring-Phase-0 contradiction
   (G2-04/G2-05), then refresh its dated snapshot.
4. Decide how an external Dream-system authority is version-pinned or mirrored
   before changing the routing text (G2-06).
5. Correct the two historical tenses without rewriting their lessons
   (G2-07/G2-08/G2-09).
