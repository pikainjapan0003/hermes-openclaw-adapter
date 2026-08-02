# Governance Audit Round 14 — 2026-08-05

Status: review-type report only. Findings are not fixes and do not authorize
schema, runtime, persistence, route, or remote changes.

## Scope and method

This round cross-checked the NIGHT-BATCH-22 package 1–12 outputs and the
authoritative maintenance/lessons documents. The review searched for:

- F8's broadened three evidence classes and the L-013 lesson;
- L-010 and the F7 item-5 `git diff --check` rule (older `F7.5` citations were
  checked as a weak-model lookup risk, not silently rewritten);
- the default fast path versus the explicit full path;
- references to the new renderer conditional-rule, inventory digest,
  three-source state, mirror-edge, and error-surface boundaries.

The review did not treat a historical dated report's measured command as a
current default. Current command authority is `40_MAINTENANCE_PROTOCOL.md` and
`pyproject.toml`.

## Findings

| ID | Severity | Location | Finding | Disposition |
|---|---|---|---|---|
| R14-01 | P3 | `docs/agent_operating_system/NIGHT_BATCH_BACKLOG.md:397-433`; new package reports | The backlog still describes NIGHT-BATCH-20 as the latest consumed stock and does not yet index the new package 1–12 artifacts. This is expected to be handled by NIGHT-BATCH-22 package 20, but a reader using the backlog before that package lands cannot discover the new reports from the stock table. | List only; no package-13 repair |
| R14-02 | P3 | `docs/agent_operating_system/research/GOVERNANCE_AUDIT_ROUND12.md:22`, `GOVERNANCE_AUDIT_ROUND13.md:17`, `PHASE7_IMPL_PACKAGE_SPEC.md:74` | Historical reports and the Phase-7 draft still contain decimal-looking `F7.5`/`F7.2`/`F7.4` references while the authority exposes numbered F7 items. The current `40_MAINTENANCE_PROTOCOL.md:16` wording is addressable as F7 item 5, but a weak model searching for a subsection anchor can still miss the older references. | Existing documentation debt; list only |
| R14-03 | P3 | `40_MAINTENANCE_PROTOCOL.md:22-25`; `pyproject.toml:18-23`; dated Phase-11 reports | Current authority is consistent: default `python -m pytest` excludes `slow`, while full acceptance uses `python -m pytest -o addopts=""`. Dated reports use equivalent historical variants (`-p no:cacheprovider` or explicit `-q`) and label their environment; those are not treated as current-command contradictions. | Pass |
| R14-04 | P3 | `40_MAINTENANCE_PROTOCOL.md:27-48`; `90_LESSONS_LEARNED.md:118-126` | F8 now requires field existence, schema-keyword presence/absence, and behavior-precondition evidence. L-013 records the previous field-only gap and the same three-class remedy. The new package-5 allOf and package-6 detached/shallow boundaries are therefore represented as renderer evidence or explicit HOLD rather than invented facts. | Pass |
| R14-05 | P3 | `research/THREE_SOURCE_STATE_FIELD_PROPOSAL.md:1-135`; `research/ERROR_SURFACE_AUDIT_ROUND8.md:1-40` | Both proposals preserve read-only/planning boundaries and leave Owner decision blanks. The conditional renderer report exposes only public schema names/literals and records its local-only output boundary. No new authorization or runtime path is implied. | Pass |

No P0 or P1 finding was found. R14-01 and R14-02 are documentation-index and
addressability debt, not evidence of a product safety bypass; they are listed
so the later backlog/docs packages cannot silently forget them.

## Cross-reference disposition

- L-010 is present at the lesson and maintenance-rule points; package reports
  use the required per-package `git diff --check` discipline.
- The F7 item-5 addressability issue remains visible in R14-02; this report does
  not rewrite historical findings.
- L-013 is recorded in 90 and its broadened F8 rule is present in 40.
- The current fast/full command pair is one authoritative pair; historical
  measurements retain their original environment and command for auditability.

## Boundary statement

This report only records consistency findings. It does not authorize audit
writing, persistence, execution/dispatch, new routes, token changes, remote
runtime, archive/move/delete operations, or schema edits.
