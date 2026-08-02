# Governance Audit Round 12 — NIGHT-BATCH-19

**REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Scope and method

This fresh-context review compared the NIGHT-BATCH-19 documentation and
reports with the current authority in `05_VERIFIED_LONG_TERM_PLAN.md`, lesson
L-010, maintenance rule F7 item 5, and the repository's configured fast/full
pytest profiles. It also checked whether the NIGHT-BATCH-19 backlog and health
snapshot identify their own point-in-time limits.

The review was performed after NIGHT-BATCH-20 packages 1–12. Those packages
may supply later disposition evidence, but this report does not repair any
finding, select an Owner option, authorize Phase 7 or Phase 9, or change a
runtime contract.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R12-01 | P2 | `NIGHT_BATCH_BACKLOG.md:418-440` | The heading says NIGHT-BATCH-19 is consumed only through package 19 and the table ends there, although packages 20–22 are present in the accepted base. This makes the current-status inventory incomplete and hides the backlog refill, L-010/F7 maintenance update, and Phase-11 health closeout from a reader who relies on the table. |
| R12-02 | P3 | `90_LESSONS_LEARNED.md:94`; `research/PHASE11_HEALTH_20260802.md:39`; `40_MAINTENANCE_PROTOCOL.md:8-16` | Two files cite `F7.5`, but F7 has no addressable subsection named F7.5; the intended authority is numbered-list item 5 at line 16. The prose is semantically aligned, but a weak model searching for a heading or anchor can fail to find the rule. |
| R12-03 | P3 | `research/PHASE11_HEALTH_20260802.md:25-43` | The dated health snapshot records the package-time results (`1936` fast and `1954` full) but has no later-status metadata for the independently accepted final HEAD results (`1942` fast and `1960` full). The original numbers are valid point-in-time evidence and must not be overwritten; an explicit later-status note is needed to prevent them being mistaken for the accepted closeout. |

No P0 or P1 finding was identified.

## Fast/full profile consistency

The authoritative commands are consistent:

- `pyproject.toml` excludes `slow` by default;
- `40_MAINTENANCE_PROTOCOL.md:22-23` defines the default and explicit fast
  paths; and
- `40_MAINTENANCE_PROTOCOL.md:24` defines the acceptance path as
  `python -m pytest -o addopts=""`.

`research/PHASE11_HEALTH_20260802.md:16-17` uses the same two profiles, adding
only reporting options. `research/PHASE7_IMPL_PACKAGE_SPEC.md:145` and
`research/V1_0_READINESS_20260802.md:62` use the same full-suite override.
No contradictory command or claim that a fast pass proves full acceptance was
found in the reviewed NIGHT-BATCH-19 artifacts.

## L-010 and F7 item 5 alignment

The rule itself is aligned at its two authoritative points: L-010 requires raw
per-package `git diff --check` evidence, and F7 item 5 requires it after edits
and before commit in the active authorized checkout. R12-02 concerns the
address syntax only; it does not dispute the rule's content.

## Required later disposition

R12-01 requires a docs-only backlog closeout update. R12-02 requires replacing
the pseudo-address with an unambiguous `F7 item 5` reference. R12-03 requires a
later-status note that preserves, rather than rewrites, the original
measurement. Until separately authorized, these remain findings only.
