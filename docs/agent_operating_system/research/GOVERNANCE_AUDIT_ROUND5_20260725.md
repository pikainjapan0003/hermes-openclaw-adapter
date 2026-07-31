# Governance Audit Round 5 — 2026-07-25

Status: **REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

Scope: all research reports introduced by NIGHT-BATCH-12, their
NIGHT-BATCH-13 resolution metadata through package 9, the compacted 05 plan,
the pytest layer hook, fixture loaders, and the AOS README governance quick
route.

## Method

The review used current file/line locations, searched executable Python
references separately from documentation references, compared each report's
claims with the implementation/test it names, and checked every quick-route ID
against its authority file. A historical finding may remain in place, but its
resolution state must be distinguishable from current work.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R5-01 | P2 | `tests/test_main_pure_helpers_coverage.py:17`; `tests/conftest.py:29-51` | The new main-helper file declares `legacy`, but the collection hook does not recognize its name and adds the default `contract` marker. It therefore belongs to two layer categories despite the documented exactly-one-layer invariant. NIGHT-BATCH-13 package 11 is the authorized place to repair and mechanically guard this; this review does not alter the hook. |
| R5-02 | P2 | `research/FIXTURE_INVENTORY_20260724.md:88-99,117-123`; repository search for the three basenames at lines 91-93 | The inventory says the three legacy local-mock fixtures are exercised by main/dashboard GET tests through preview loaders. Their basenames are absent from `app/**/*.py` and `tests/**/*.py`; executable references are in historical `scripts/` loaders/checkers. The files are not unreferenced, but “primary test coverage” and “loader exercised by the named tests” are unsupported. The no-orphan conclusion needs a distinction between test-covered fixtures and script-referenced legacy artifacts. |
| R5-03 | P3 | `research/GOVERNANCE_AUDIT_ROUND4_20260724.md:28-29,68-70`; `research/ONBOARDING_REVIEW_20260723.md:5-19`; `research/ERROR_SURFACE_AUDIT_20260723.md:9-18` | Round 4 still says R4-01/R4-02 lack resolution metadata and that none of its findings were fixed. NIGHT-BATCH-13 package 4 has now added that metadata. The historical finding text is valid evidence, but Round 4 needs resolution annotations so a weak reader does not reopen completed metadata work. |
| R5-04 | P3 | `research/SCHEMA_ERROR_REDACTION_CONTRACT_DESIGN.md:85-139,181-189` | The E-02 section now requires a mechanically tested remote-projection export gate, but the recommendation's implementation checklist names only ten Blackboard leak-marker cases and selection errors. A later authorized implementation package also needs a projection-validator leak-marker case; otherwise E-02 could be declared complete using only E-01 tests. |

No P0 or P1 finding was identified.

## Checks with no finding

### Compaction and current metrics

The crosswalk now labels ≤440 as the NIGHT-BATCH-11 package-3 snapshot.
`PHASE11_HEALTH_20260724.md` records the corrected `wc -l` result of 445 and
55-line F4 headroom. C01–C18 and M01–M11 remain mechanically guarded.

### Resolution metadata

O-01–O-05 are individually marked resolved with the NB-12 package-3 commit.
E-01/E-02 are correctly marked “design prepared; unresolved,” the Owner
decision remains blank, and both validator modules remain unchanged. R5-03 is
about the older Round 4 summary, not a missing status in those two source
reports.

### README governance quick route

The C, D, L, R, F, and §6 identifiers named by the quick route still exist in
their authority files. The route calls itself a second entry point and does
not restate or supersede their text. Existing cross-reference integrity tests
remain the mechanical guard.

### NIGHT-BATCH-12 report boundaries

The board-reader capacity report preserves 50 independent N=1 boards rather
than one 500-entry board. The redaction design remains planning-only, the
Owner field remains blank, and the health report does not turn its proposed
research-size observation into a rule.

## Boundary

This report fixes none of R5-01–R5-04. It does not edit a validator, fixture,
schema, loader, test marker, runtime path, Owner decision, or Phase 7/9 gate.
