# Governance Quarterly Review — 2026-07-26

Status: **REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

Scope: F4 size thresholds, cross-rule consistency among
`01_SAFETY_BOUNDARIES.md`, `05_VERIFIED_LONG_TERM_PLAN.md`,
`10_MODEL_ORCHESTRATION.md`, `20_JUDGMENT_RUBRICS.md`,
`40_MAINTENANCE_PROTOCOL.md`, and `CLAUDE.md`, plus regression review of
`90_LESSONS_LEARNED.md` L-001 through L-008.

## F4 line-count measurement

Method: PowerShell `Get-Content -Encoding UTF8 <file> | Measure-Object -Line`
equivalent count over each top-level Agent Operating System Markdown file.
Root `CLAUDE.md` and `README.md` were measured separately.

| File | Lines | F4 action threshold | Result |
|---|---:|---:|---|
| `00_QUICK_DIAGNOSIS.md` | 219 | 500 | below |
| `01_SAFETY_BOUNDARIES.md` | 98 | 500 | below |
| `02_V1_0_DEFINITION.md` | 63 | 500 | below |
| `05_VERIFIED_LONG_TERM_PLAN.md` | 445 | 500 | below; summary already exists |
| `07_AUDIT_WRITE_DESIGN.md` | 354 | 500 | below |
| `08_REMOTE_READONLY_PLAN.md` | 254 | 500 | below |
| `09_N1_PREFLIGHT_RUNBOOK.md` | 166 | 500 | below |
| `10_MODEL_ORCHESTRATION.md` | 117 | 500 | below |
| `11_V1_1_FIRST_REAL_WRITE_DESIGN.md` | 332 | 500 | below |
| `12_BLACKBOARD_DATA_LAYOUT.md` | 137 | 500 | below |
| `13_HERMES_WIRING_DESIGN.md` | 296 | 500 | below |
| `14_V1_2_FIRST_CODE_TASK_DESIGN.md` | 211 | 500 | below |
| `20_JUDGMENT_RUBRICS.md` | 127 | 500 | below |
| `30_DELEGATION_PROMPTS.md` | 178 | 500 | below |
| `40_MAINTENANCE_PROTOCOL.md` | 90 | 500 | below |
| `90_LESSONS_LEARNED.md` | 78 | 300 | below |
| `99_LETTER_TO_FUTURE_SESSIONS.md` | 66 | 500 | below |
| `NIGHT_BATCH_BACKLOG.md` | 159 | 500 | below |
| AOS `README.md` | 52 | 500 | below |
| root `CLAUDE.md` | 228 | 500 | below |
| root `README.md` | 436 | 500 | below |

No F4 threshold is exceeded.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| GQ-01 | P2 | `05_VERIFIED_LONG_TERM_PLAN.md:358`; current authorized nightly workspace `C:\Users\Lnovo\Desktop\hermes-adapter-work` | The authority still says all development happens in the WSL repo, while the established Codex workflow now develops and commits in the complete Windows Desktop worktree before Fable 5 review. Both can point to the same GitHub authority, but a fresh model can enter the stale WSL copy or reject the authorized Desktop branch as invalid. The current workspace relationship and handoff direction are not recorded in the governance files reviewed here. |
| GQ-02 | P2 | `10_MODEL_ORCHESTRATION.md:68-77,106-115`; `20_JUDGMENT_RUBRICS.md:8-12` | C5 still gives the old `haiku → sonnet → strongest` escalation path, while C8 says the C5 path is revised to the Luna/Sol ladder and the prior cross-system route is abolished. R-01 directs weak models to “C5” without also pointing to C8. The later text can be treated as overriding, but the earlier executable recipe remains live and can select the wrong route before a reader reaches C8. |
| GQ-03 | P3 | `05_VERIFIED_LONG_TERM_PLAN.md:260`; `40_MAINTENANCE_PROTOCOL.md:42-57`; current `research/PHASE11_HEALTH_*.md` series | Phase 11 still says every health report is appended to 90, while the maintained practice stores health reports under `research/` and uses 90 for incident lessons in the F3 format. The safe behavior is visible from practice, but the normative output sentence can make a weak model bloat or rewrite 90 during a routine measurement. |
| GQ-04 | P3 | `90_LESSONS_LEARNED.md:7-15`; NIGHT-BATCH-14 package-10 measurement attempt | L-001 recurred: a PowerShell double-quoted `wsl.exe ... bash -lc` command expanded `$layer` before Bash, selected an empty marker, and collected zero tests. Re-running with the entire Bash script single-quoted succeeded. The lesson remains valid, but “ban `$`” is overbroad; the mechanically useful rule is to prevent host-shell expansion by quoting the Bash program correctly. |
| GQ-05 | P3 | `90_LESSONS_LEARNED.md:17-24`; NIGHT-BATCH-14 attachment read | The first PowerShell read of the UTF-8 Chinese dispatch rendered mojibake until both `Get-Content -Encoding UTF8` and UTF-8 console output were set. This is a non-destructive recurrence of L-002's encoding half. The lesson mentions the symptom but its prescribed Python JSON workaround does not cover ordinary UTF-8 text reads. |

No P0 or P1 finding was identified.

## L-001–L-008 regression status

| Lesson | Still valid? | Current evidence |
|---|---|---|
| L-001 host-shell expansion | Yes; recurrence observed | GQ-04 |
| L-002 PowerShell 5.1 parsing/encoding | Yes; encoding recurrence observed | GQ-05 |
| L-003 UNC Git latency | Yes | This review used the local Windows worktree and WSL `/mnt/c`, not UNC Git; no contrary evidence |
| L-004 subagent capability is environment-specific | Yes | No capability was inferred from the dated snapshot; current batch did not rely on a subagent |
| L-005 adversarial review catches governance defects | Yes | GQ-01–GQ-03 were found by cross-reading rather than by changing rules |
| L-006 dashboard review controls are a named exception | Yes | The route/test inventory still distinguishes decision recording from dispatch |
| L-007 mirror drift | Yes | No mirror file was edited in this branch; F6 still requires post-master synchronization |
| L-008 cross-contract field existence | Yes | No schema, fixture, or builder field was inferred or changed in this review |

The two observed recurrences caused failed/garbled diagnostic attempts only.
They did not modify product state, relax a gate, or produce an unverified
completion claim.

## Boundary

This report does not resolve GQ-01–GQ-05, edit an L0 rule, change model routing,
choose a workspace authority policy, append an incident to 90, or authorize
Phase 7, Phase 9, runtime, remote, execution, dispatch, or persistence.
