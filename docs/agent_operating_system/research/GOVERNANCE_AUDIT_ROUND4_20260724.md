# Governance Audit Round 4 — 2026-07-24

Status: **REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Scope and method

Fresh-eyes review of the research artifacts created or materially updated in
NIGHT-BATCH-11 against the compacted current
`05_VERIFIED_LONG_TERM_PLAN.md`, the referenced implementation/tests, current
marker assignment, and both requirements files.

Checks:

1. the compaction crosswalk still locates every moved rule and agrees with the
   present compact plan;
2. dated reports that describe a finding clearly distinguish historical
   evidence from current reality;
3. pytest layer documentation matches the collection hook;
4. dependency-audit declarations match `requirements.txt`,
   `requirements-dev.txt`, and current `pyproject.toml`; and
5. no report wording can be mistaken for Phase 7/9, runtime, remote, or write
   authorization.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R4-01 | P2 | `research/ONBOARDING_REVIEW_20260723.md:3,19-31,39-45,58-66,80-81`; current `CLAUDE.md:3-18`; current `docs/agent_operating_system/README.md:9`; current `05_VERIFIED_LONG_TERM_PLAN.md:282-286` | The onboarding report has no resolution metadata and still presents all O-01–O-05 findings as current. NIGHT-BATCH-12 package 3 has now moved the can/cannot/next answer to the top of `CLAUDE.md`, removed volatile README metrics, and added an explicit §5 entry summary/order warning. The historical findings remain useful evidence, but a weak reader can reopen already-fixed work or conclude the current entry path is still unsafe. |
| R4-02 | P3 | `research/ERROR_SURFACE_AUDIT_20260723.md:24,26,36-39`; `research/SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md:1-7,101-137`; `tests/test_schema_error_redaction_baseline.py:1-12,34-52` | E-01/E-02 remain real unresolved exposure risks, but the audit still says a redaction contract is only a later need. A planning-only three-option contract and a ten-schema xfail baseline now exist. The missing distinction is: “design prepared, Owner choice blank, validator unchanged.” Without resolution metadata, readers may either redo the design or incorrectly assume the finding was fixed. |
| R4-03 | P3 | `research/05_COMPACTION_RULE_CROSSWALK_20260723.md:9-18`; current `05_VERIFIED_LONG_TERM_PLAN.md` (441 lines by repository measurement) | The crosswalk records an after-target of ≤440 lines and says the current compact wording remains in 05. The current plan is 441 lines after the authorized onboarding-entry clarification. No rule is missing and the F4 maximum of 500 is not breached, but the crosswalk's “current/mechanical” wording is now one line stale. It should later be labelled as the package-3 compaction snapshot rather than a permanent current-size invariant. |

No P0 or P1 finding was identified.

## Checks with no finding

### Compaction content and indexes

The archived §6.3, §6.9, and §6.12 text remains present in the crosswalk, the
rule-by-rule table still contains C01–C18 and M01–M11, and the current 05 file
retains explicit index pointers. Round 4 found no missing Owner sentence, HOLD
condition, Phase 7 gate, or Phase 9 Owner-presence gate.

### Test marker documentation versus collection

`TEST_SUITE_PROFILE_20260723.md:3-18` labels its counts as the NIGHT-BATCH-11
package-9 boundary. `tests/conftest.py:12-49` still assigns every test exactly
one declared marker, using the documented fuzz/governance allowlists, legacy
prefixes, and contract fallback. Newer test counts do not contradict the dated
838-case snapshot.

### Dependency report versus declarations

`DEPENDENCY_AUDIT_20260723.md:12-20` exactly matches the current ten production
and four development pins. Its `pyproject.toml` drift statement at lines 32–39
also remains true: the project metadata still omits `jsonschema` and the two
Google distributions while the requirements-based workflow declares them.
No new third-party import or undeclared direct requirement was found in the
NB-11/NB-12 files reviewed here.

### Authorization language

The NB-11 research files consistently label proposals/reviews as non-authority.
No audit, health report, test marker, crosswalk, or dependency note grants an
audit writer, execution/dispatch, runtime/remote wiring, or token capability.

## Boundary

This report does not fix R4-01–R4-03. It does not select a redaction option,
change a validator, edit requirements, recompact 05, or authorize any runtime
path.

