# Weak-Model Onboarding Review — 2026-07-23

Status: review only; findings are not fixes or authorization.

## Simulation

Reader profile: a fresh, weak model with no prior conversation. Allowed reading
path, in order:

1. repository `CLAUDE.md`;
2. `docs/agent_operating_system/README.md`;
3. `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` §5 only.

Question at each hop: can the reader state (a) where the system is, (b) what it
may do now, and (c) what remains forbidden, without importing assumptions?

## Step-by-step result

### Hop 1 — `CLAUDE.md`

The first eleven sections define an old ChatGPT/Claude handoff envelope before
the Agent Operating System entry point appears in §12. A fresh reader learns
formatting and stop phrases before learning repository state. It cannot answer
“where is the system now?” from this file alone.

It can recover the core authority boundary from §6 and §12: ordinary work needs
an Owner instruction; the §6.13 night-batch exception is bounded; Phase 7,
Phase 9, v1.1, and v1.2 retain their own gates. This is safe, but the high-value
statement arrives late.

Jump count so far: one long-file scan; no authoritative state answer.

### Hop 2 — Agent Operating System `README.md`

The “現在系統在哪” block immediately gives the intended answer: Phase 2–6
complete, Phase 7 design ready but implementation locked, Phase 8 planning
complete, and Phase 9 requires the Owner. It points to 05 §5 for current status.

However, the same line still cites `master 7d2123f`, queue guard `0d3be1f`, and
“106 tests”, all historical values. A weak model has no way to distinguish the
stable phase statement from the stale metrics and may treat the whole sentence
as the current checkout.

Jump count: one cross-file jump from CLAUDE §12 to README, then one planned jump
to 05 §5.

### Hop 3 — 05 §5

The status table is the strongest state authority in the path. It confirms:
Phase 2–6 complete; Phase 7 is “design ready” and requires the exact Owner
authorization sentence; Phase 8 planning is complete; Phase 9–11 have not
started; Phase 9 and Phase 7 are the final v1.0 gates.

The reader can now answer all three onboarding questions. Minimum useful path:
two cross-file jumps and three inspected regions. It must trust §5 over stale
README metrics.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| O-01 | P2 | `docs/agent_operating_system/README.md:9` | The onboarding “current state” sentence embeds obsolete master/test baselines. This directly conflicts with its role as the fast current-state answer and can make a weak model mistrust correct phase claims. |
| O-02 | P2 | `CLAUDE.md:1-181` | Repository orientation is delayed until §12. A fresh weak model cannot identify the active authority or state after the first screenful and may overfit to the legacy loop-format contract. |
| O-03 | P3 | `CLAUDE.md:71-116` | The night-batch exception and its exclusions are safe but dense. “merge/push” appears near the exception; a weak reader must retain the later Phase 7/9/v1.1/v1.2 exclusions to avoid overgeneralizing permission. |
| O-04 | P3 | `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md:284-293` | The table lists Phase 8 before Phase 7 and groups 9–11 in one row. The facts are correct, but the non-numeric order increases the chance that “next phase” is inferred from row order rather than explicit blockers. |
| O-05 | P3 | onboarding path | It takes two file jumps and a long initial scan to get an authoritative “can/cannot do now” answer. The target from Phase 1 (“CLAUDE + README alone”) is only partially met because README carries stale volatile facts. |

## Safe answer a weak model should produce today

- Current: Phase 2–6 complete; Phase 7 design exists but its writer is not
  authorized; Phase 8 planning/offline projection work is complete; Phase 9 is
  not unlocked.
- Allowed now: only the explicitly assigned package scope, including bounded
  night-batch work under 05 §6.13 after Fable 5 review.
- Forbidden: Phase 7 persistent audit writing without the exact Owner sentence;
  Phase 9 without synchronous Owner presence and a separately designed token
  gate; v1.1/v1.2 without their new Owner instructions; any extrapolation of the
  night-batch exception.

No wording was changed in this package. O-01 through O-05 are backlog inputs,
not authority to edit governance files.
