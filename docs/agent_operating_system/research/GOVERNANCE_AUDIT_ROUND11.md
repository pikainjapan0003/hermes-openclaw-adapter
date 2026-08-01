# Governance Audit Round 11 — NIGHT-BATCH-18

**REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

## Scope and method

This fresh-context review compared every NIGHT-BATCH-18 commit and changed
artifact against `05_VERIFIED_LONG_TERM_PLAN.md`, the current no-writer/no-
execution boundary, lesson L-009, and maintenance rule F7. It separately
inspected the four post-package mechanical correction commits:

- `f0602af` — backlog placement repair;
- `092cc0d` — backlog closeout repair;
- `49b62ae` — Phase-11 health line-count repair;
- `10fd5a2` — backlog summary wording repair.

The review checked consistency and traceability only. It does not repair a
finding, choose AUD/RB/PB/ROOT, authorize a writer, or open Phase 7 or Phase 9.

## Package consistency

| Packages | Review result |
|---|---|
| 1–4 | Portable fixture hashing, shared-inode reporting, malicious-path boundaries, and the decoupled coverage floor agree with the tested cross-platform behavior. |
| 5–9 | Documentation repairs, the Owner-only proposal, error redaction, slow markers, and layer compatibility retain their stated non-authorizing boundaries. |
| 10–18 | Mutation, builder, script, rehearsal, preflight, impact, governance, metrics, and integrity artifacts remain test/review evidence; none creates a write or execution path. |
| 19–22 | Backlog, L-009, F7, and health records remain governance artifacts. The correction commits did not cross into product/runtime scope. |

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R11-01 | P2 | `NIGHT_BATCH_BACKLOG.md:368,371` | The package-19 row names only `22bca79 / f0602af`, omitting later package-19 correction commits `092cc0d` and `10fd5a2`; the package-22 row names only `1b6da89`, omitting correction `49b62ae`. The final files are correct, but the audit table cannot reconstruct all commits that produced them. |
| R11-02 | P2 | `07_AUDIT_WRITE_DESIGN.md:81-83`; `40_MAINTENANCE_PROTOCOL.md:8-17`; `90_LESSONS_LEARNED.md:8-12` | The Phase-7 design repeats the future-writer hardlink prohibition but does not cite F7 or L-009 at the point of use. Today the wording agrees. Without an explicit cross-reference, a later edit can silently drift on `st_nlink`, CRLF normalization, or capability skips. |
| R11-03 | P3 | `research/PHASE11_HEALTH_20260801.md:83-87`; `research/GOVERNANCE_AUDIT_ROUND10_20260801.md:52-61` | The dated health snapshot says Round-10 findings remain, while the Round-10 report now carries a later NIGHT-BATCH-19 resolution table. This is historically explainable but lacks point-of-use later-status metadata in the health file. |

No P0 or P1 finding was identified.

## L-009 / F7 alignment

- Fixture digest normalization is implemented as CRLF-to-LF before hashing and
  is covered by the fixed inventory; this matches L-009 and F7.4.
- The reader accepts a valid hardlink only as input and reports
  `shared_inode=true`; future writer rejection for `st_nlink > 1` is stated in
  both the Phase-7 design and F7.1.
- Symlink, non-regular-file, outside-root, and capability-dependent tests align
  with F7.2. No test grants a platform skip without a stated reason.
- Mirror `DIFFERS` remains a human-decision state under F7.3.

The alignment result does not close R11-02: duplicated prose is not a durable
cross-reference.

## Mechanical-correction disposition

All four correction commits are mechanically scoped and leave safety behavior
unchanged. R11-01 concerns their missing trace-table references, not their
content. No correction commit changes a route, schema, token, writer,
dispatch, runtime, remote connection, or Owner option field.

## Required later disposition

R11-01 and R11-02 need a separately scoped docs-only repair. R11-03 can be
resolved with historical/later-status metadata. Until then, this report is
evidence of known drift only and must not be treated as implementation
authority.

