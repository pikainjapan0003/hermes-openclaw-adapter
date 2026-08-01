# Core Document Review — 20 Judgment Rubrics

Status: **REVIEW ONLY — NO RUBRIC CHANGED.** This review does not revise a
decision rule, authorize a package, select an Owner option, or relax any gate.

## Scope

R-01 through R-13 in `20_JUDGMENT_RUBRICS.md` were checked against the current
night-batch process (05 §6.13), Fable 5 batch review, the fast/full pytest
profiles, and F7. The check asks whether a weak model can follow 20 alone
without making a stale environment or completion claim.

## Per-rubric result

| Rubric | Result | Review note |
|---|---|---|
| R-01 | Aligned | Delegates current model names/order to 10 C8 and retains bounded retry/HOLD. |
| R-02 | Needs update | The generic completion rule has objective evidence, but its example and PASS rule do not name Fable 5 batch review or distinguish package completion from merge/push acceptance. |
| R-03 | Aligned | Stops only the blocked item and continues separately authorized work, matching nightly HOLD/skipped continuation. |
| R-04 | Needs environment refresh | The UNC/WSL example assumes the old fixed topology now corrected in 00 D-16. The change-of-route principle remains sound. |
| R-05 | Needs update | The quality floor omits `git diff --check` and the distinction between default fast tests and the required F7 full-suite command. |
| R-06 | Aligned | Authorization remains a quoted Owner instruction; plans/dashboard/prior rounds are excluded. |
| R-07 | Aligned | Safe alternatives do not silently become authorization. |
| R-08 | Partially aligned | Sample-first and stop-after-two-anomalies remain useful, but nightly immutable package/independent-commit rules are not cross-referenced. |
| R-09 | Partially aligned | Fresh-context review remains required, but the rubric predates the Fable 5 batch-review route in §6.13. |
| R-10 | Aligned | Requires current-session evidence and fail-closed uncertainty. |
| R-11 | Contradictory | D-12 correctly says Replit exposes reachability but no deployed hash; R-11 still says “three hashes/status agree” and its positive example claims three hashes. |
| R-12 | Aligned | Explicitly records the narrow §6.13 exception and preserves Phase 7/9/v1.1/v1.2 gates. |
| R-13 | Aligned with dated examples | The ≥2-model rule and Fable/Codex route remain explicit; model examples are non-authoritative because 10 C8 owns current names. |

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| C20-01 | P2 | R-11 | “Three hashes agree” is impossible under the current read-only Replit evidence contract. A weak model can invent a deployed hash to make the rubric pass. |
| C20-02 | P2 | R-05 | “Tests green” can be satisfied by the new default fast path while slow tests remain unrun; batch acceptance requires `python -m pytest -o addopts=""`. `git diff --check` is also absent. |
| C20-03 | P3 | R-02, R-09 | Completion/fresh-review wording does not route nightly work through Fable 5 review and the §6.13 merge boundary. |
| C20-04 | P3 | R-04 | The WSL-only workaround example conflicts with host-neutral checkout discovery now stated in 00 D-16. |
| C20-05 | P3 | R-08 | The batch rubric omits immutable package definitions, per-package commits, and explicit HOLD/skipped continuation. |
| C20-06 | P3 | R-05, R-08 | F7 filesystem portability and path-trust checks are not part of the applicable quality/batch checklist. |

No P0/P1 finding was identified. These findings are proposals for a later
20-file repair; this review deliberately changes none of R-01 through R-13.

## Later repair boundary

A repair package should preserve all existing authorization semantics, add
cross-references rather than duplicate 05/40, and never turn Fable 5 review
into permission for Phase 7 or Phase 9. R-11 must say local/GitHub hashes can
align while Replit remains reachability-only with deployed hash unknown.
