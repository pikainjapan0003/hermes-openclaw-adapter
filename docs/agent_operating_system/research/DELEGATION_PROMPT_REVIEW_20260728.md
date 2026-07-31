# Delegation Prompt Template Review — 2026-07-28

Status: **REVIEW ONLY — TEMPLATES MARKED, NOT CHANGED**

## Scope

Fresh-context review of every T-01 through T-12 template in
`30_DELEGATION_PROMPTS.md` against the current operating model:

- NIGHT-BATCH packages are immutable, committed one package at a time, and
  reviewed by Fable 5 under `05_VERIFIED_LONG_TERM_PLAN.md` §6.13;
- construction routes through the five Codex GPT-5.6 levels recorded in
  `10_MODEL_ORCHESTRATION.md` C8; and
- high-risk work requires independent multi-model review under
  `20_JUDGMENT_RUBRICS.md` R-13.

This package only records status and revision suggestions. It does not edit
`30_DELEGATION_PROMPTS.md`, change routing, create a new template, dispatch an
agent, or authorize any work.

## Findings

| ID | Severity | Location | Finding and misread risk |
|---|---|---|---|
| TREV-01 | P2 | `30_DELEGATION_PROMPTS.md:3-18,34-44,174-178`; `05_VERIFIED_LONG_TERM_PLAN.md:431-436` | The common envelope predates the nightly-batch protocol. It has no fields for immutable package number, current branch, per-package commit message, `git diff --check`, skipped/HOLD continuation, or the Fable 5 batch-review boundary. A commander can wrap a nightly package in T-02 and receive a plausible implementation while silently losing the audit rules that make §6.13 safe. |
| TREV-02 | P2 | `30_DELEGATION_PROMPTS.md:95-109`; `20_JUDGMENT_RUBRICS.md:119-125`; `10_MODEL_ORCHESTRATION.md:121` | T-07 calls itself mandatory for high-risk output but addresses one reviewer and says nothing about the R-13 requirement for at least two different fresh-context models. A weak commander can treat one T-07 result as high-risk sign-off even though current governance explicitly forbids that. |
| TREV-03 | P3 | `30_DELEGATION_PROMPTS.md:34-44,46-56,174-178`; `10_MODEL_ORCHESTRATION.md:98-116` | T-02/T-03 contain no Codex five-level routing or escalation field. They cannot record why work was assigned to Luna+high, Luna+max, Sol+high, Sol+xhigh, or Sol+max, and they omit the failure-trajectory escalation rule. The prompt can still describe work, but it no longer captures the current construction route. |
| TREV-04 | P3 | `30_DELEGATION_PROMPTS.md:58-67,111-120,122-145`; current connector/tool surfaces | T-04, T-08, T-09, and T-10 hard-code `WebSearch/WebFetch`, “MCP Google Drive,” and `gh CLI` as if tool names were stable capabilities. Current environments expose capability-specific connectors/plugins and may not use those names. A weak model may report a false HOLD or take an unapproved fallback instead of using the available read-only capability named by its task. |
| TREV-05 | P3 | `30_DELEGATION_PROMPTS.md:122-134`; `00_QUICK_DIAGNOSIS.md:151-161`; `research/THREE_SOURCE_REPORT_SEMANTICS_20260727.md` | T-09 checks Replit reachability but does not force the current distinction “HTTP reachable ≠ deployed hash known ≠ three revisions aligned.” A successful smoke page can therefore be overreported as deployment-version verification. |

No template itself grants persistence, execution, dispatch, a new route, or an
Owner-gated phase. The defects are missing current process guards, not hidden
authorization.

## Template-by-template marks

| Template | Mark | Current parts worth preserving | Proposed revision (not applied) |
|---|---|---|---|
| T-01 repo scan | **CURRENT WITH MINOR UPDATE** | Explicit scope, evidence lines, coverage disclosure, no edits | Add branch/package boundary and require reporting excluded paths/pattern limitations; keep it read-only. |
| T-02 implementation | **OUTDATED FOR NIGHT BATCH** | Whitelist, negative scope, tests, HOLD on conflict | Add routing level/reason, branch/base, immutable package number, forbidden redlines, per-package commit, `git diff --check`, exact pytest/mypy commands, and “HOLD then continue only when the issued batch says so.” |
| T-03 refactor | **CURRENT WITH PROCESS GAP** | Behavior invariant and pre/post tests | Add current routing/escalation and batch commit fields; explicitly forbid using a refactor package to fix a discovered behavior bug. |
| T-04 research/web | **CURRENT CONCEPT, TOOL WORDING STALE** | Source/date requirement and `UNVERIFIED` section | Replace named tool products with “available approved read-only web capability”; require primary/authoritative sources and record which capability was actually used. |
| T-05 general review | **CURRENT** | Findings-only, file:line evidence, no silent side choice | Add severity and explicit later-resolution metadata expectation; no functional rewrite needed. |
| T-06 read-back | **CURRENT WITH FRESHNESS CLARIFICATION** | Existence, headings, path checks, all failures | State that the reviewer must not inherit or rely on the author’s reasoning; existence-only review cannot sign off semantic correctness. |
| T-07 adversarial review | **OUTDATED / UNSAFE AS HIGH-RISK SIGN-OFF** | Misread, path, authorization, HOLD, and evidence checks | Add an R-13 banner: run independently with at least two different models; list both reports and surface disagreements to Owner. One result must be labelled insufficient for high-risk acceptance. |
| T-08 Drive/doc reading | **CURRENT INTENT, CAPABILITY WORDING STALE** | Read-only boundary, citations, permission HOLD | Name the exact connector in the issued work order, forbid silent fallback/export, and distinguish connector unavailability from document permission denial. |
| T-09 Dashboard/Replit smoke | **OUTDATED SEMANTICS** | No form submission/token probing and no secret echo | Add `deployed_hash=UNKNOWN` unless actually measured by an authorized source; distinguish HTTP reachability, local/GitHub alignment, and deployed revision; prohibit calling these “three-source aligned.” |
| T-10 GitHub review | **CURRENT INTENT, CAPABILITY WORDING STALE** | Read-only, exact hash, no push/PR/fork | Name the available GitHub connector/CLI per environment and prohibit authentication workarounds; use the three-source semantics for local/origin claims. |
| T-11 open-source evaluation | **CURRENT** | Fresh activity evidence, licensing/copy risk, no dependency import | Add primary-source preference and package/version capture; otherwise remains usable. |
| T-12 plan validation | **CURRENT WITH NIGHT-BATCH ADDENDUM NEEDED** | Phase-by-phase evidence, D-12, safety conflict HOLD | Add §6.13 status checks, distinguish Replit reachability from revision verification, and require current 05 §5 rather than a remembered HEAD. |

## Proposed structural revision

The next authorized edit to `30_DELEGATION_PROMPTS.md` should keep T-01 through
T-12 but add two common overlays rather than duplicate every template:

1. **Routing overlay:** task class → one of the five Codex levels, with the C8
   failure-trajectory escalation record.
2. **Night-batch overlay:** issued package text, immutable scope, branch/base,
   redlines, per-package tests/diff/commit, HOLD/skipped handling, and Fable 5
   batch review before merge/push.

T-07 additionally needs its own R-13 multi-model block; a common overlay cannot
turn a single review invocation into two independent reviews.

## Boundary

All marks and proposed words above are advisory. `30_DELEGATION_PROMPTS.md`
remains unchanged, and its current templates remain subordinate to CLAUDE.md,
01, 05 §6.13, 10 C8, 20 R-13, and the exact Owner-issued work order.
