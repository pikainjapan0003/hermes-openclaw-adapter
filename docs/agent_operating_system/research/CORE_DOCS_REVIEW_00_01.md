# Core Documents Review: 00 / 01 — 2026-07-29

Status: **REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Scope and authority boundary

This fresh-context review read `00_QUICK_DIAGNOSIS.md` and
`01_SAFETY_BOUNDARIES.md` in full. It checked every D-01 through D-18 card and
all six sections of 01 for:

- dated environment or repository facts presented as current;
- conflict with the nightly/Fable 5 process in 05 §6.13;
- conflict with the current five-level Codex routing in 10 C8;
- weak-model wording that can be mistaken for authority; and
- any weakening of the canonical safety boundary.

01 is F2-governed. This report does not edit 00 or 01 and cannot authorize a
later edit.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| C01-01 | P2 | `00_QUICK_DIAGNOSIS.md:3-6,95-109,213-219`; `CLAUDE.md:8-9,125,178-179,205,228`; `05_VERIFIED_LONG_TERM_PLAN.md:282,431-436` | 00 labels a 2026-07-07 ChatGPT → Claude Code → Owner harness as “current” and says the routing paragraph was added “this session,” but it has no later-status note for the Codex five-level construction route or the §6.13 nightly/Fable 5 batch boundary. The original diagnosis remains useful history; a weak model can nevertheless treat its old current-state sentences as the active workflow and omit immutable packages, per-package commits, HOLD continuation, or Fable review. |
| C01-02 | P2 | `00_QUICK_DIAGNOSIS.md:127-133`; `01_SAFETY_BOUNDARIES.md:33-59,83-98`; `research/PREFLIGHT_CONDITION_CATALOG.md:17-22` | D-09 prescribes an environment-variable execution token as a mandatory future real-component mechanism. The current Phase 9 contract still locks the token to `null`, has no live-token design, and remains an Owner gate. Although D-09 says “future,” its imperative wording can be mistaken for a settled token transport design. It must be labelled as superseded planning, not implemented or inferred from. |
| C01-03 | P2 | `00_QUICK_DIAGNOSIS.md:151-161,187-193`; active NIGHT-BATCH-17 checkout at `C:\\Users\\Lnovo\\Desktop\\hermes-adapter-work` | D-12/D-16 hard-code `/home/lnovo/projects/hermes-openclaw-adapter`, state that the repository is in WSL, and instruct Git to run there. This batch's governed checkout is a native Windows working copy. Copying the old command from 00 can inspect the wrong clone and recreate the multi-copy mistake already seen historically. The rule should be “resolve the active authorized checkout first,” with commands as dated examples. |
| C01-04 | P3 | `00_QUICK_DIAGNOSIS.md:143-149,179-185`; `10_MODEL_ORCHESTRATION.md:100-116`; `20_JUDGMENT_RUBRICS.md:9-12` | D-11 names `WebSearch/WebFetch` as fixed tools and D-15's examples route Haiku → Sonnet. Current governance treats tools as available approved capabilities and routes Codex through Luna/Sol levels before Fable 5. The cards link to current orchestration for the rule, but stale examples are highly copyable by a weak model and can cause false HOLD or a nonexistent model request. |
| C01-05 | P3 | `01_SAFETY_BOUNDARIES.md:52,63-71`; `CLAUDE.md:125,178-179,228` | 01 §2 says the only valid authorization form is the active Owner instruction. The later §4.5 correctly records the narrow, previously Owner-approved §6.13 nightly merge/push exception, but §2 has no forward cross-reference. A reader that stops at the canonical prohibition can incorrectly claim every nightly commit/merge/push lacks authority. This is fail-closed friction, not an unsafe permission expansion; any future F2-approved wording should point to the exact narrow exception without broadening it. |

No P0 or P1 finding was identified.

## D-card review result

| Cards | Result |
|---|---|
| D-01–D-05 | Core diagnosis remains valid. D-05's historical “this session” wording is included in C01-01. |
| D-06–D-08 | Safety intent remains valid. Lack of subagent capability has an explicit fallback, and dashboard display remains non-authorizing. |
| D-09 | C01-02: future token mechanism is presented too concretely before Phase 9 design. |
| D-10 | Explicit connector scope and L0 fail-closed default remain aligned with 01. |
| D-11 | C01-04: capability names are stale; the verification principle remains valid. |
| D-12 | C01-03: semantic three-source check is valid, fixed path/host command is not portable. |
| D-13–D-14 | Emergency handoff and lesson capture remain aligned with 40/90/99. |
| D-15 | C01-04: routing examples are stale; retry/escalation intent remains valid. |
| D-16 | C01-03: dated topology is wrongly copyable as a universal current fact. |
| D-17–D-18 | Phase identity and truncation guards remain conservative and compatible. |

## 01 boundary review result

The permanent “X is not Y” rules, default prohibitions, HOLD behavior,
execution-class restrictions, and AUTO fail-closed qualification remain intact.
No sentence was found that turns display, advice, approval, result, or closeout
into execution permission. C01-05 concerns the discoverability of an already
documented narrow exception; it does not challenge or expand that exception.

## Disposition

All five findings remain open and require a separately authorized docs package;
any change to 01 requires Owner handling under F2. This review grants no token,
writer, route, runtime, connector, archive, execution, dispatch, merge, or push
authority.
