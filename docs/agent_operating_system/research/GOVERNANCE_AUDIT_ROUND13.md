# Governance Audit Round 13 — contract/specification alignment

**REVIEW ONLY — FINDINGS RECORDED, NOTHING FIXED OR AUTHORIZED**

Date: 2026-08-04

## Scope and method

This fresh-context pass compared NIGHT-BATCH-20's reports and institutional edits with the accepted schemas, tools, F7/L-011 rules, and the NIGHT-BATCH-21 precheck. It specifically searched for a fourth instance of a dispatch brief making a contract claim without first inspecting the real artifact. Historical point-in-time measurements were not treated as drift merely because later commits exist.

## Findings

| ID | Severity | Location | Finding |
|---|---|---|---|
| R13-01 | P2 | `research/BATCH_SPEC_PRECHECK_NB21.md:24-29`; `docs/schemas/remote_readonly_projection.schema.json:124-145` | **Fourth contract/specification mismatch found.** Package 5's required factual sentence said the current 15 schemas do not use `allOf`, but the remote-readonly projection already has a root-level `allOf`. The precheck excluded package 5 as “not field-bearing,” so it never verified this schema-keyword claim. Package 5 correctly became HOLD with no commit. F8 must cover every factual contract assertion, not only named fields. |
| R13-02 | P2 | `research/BATCH_SPEC_PRECHECK_NB21.md:21-22`; `scripts/check_three_source_readonly.py:65-68`; `:117-120` | The precheck proved the three-source report's output fields, then allowed package 10 to proceed, but the package also required detached HEAD and shallow clones to fail closed. `read_local_head` checks only `git rev-parse HEAD`, so both contexts can still yield a valid hash and no context flag exists in the report. This is a behavior-precondition mismatch outside the current field-only precheck. Package 10 correctly became HOLD rather than using synthetic monkeypatch evidence. |
| R13-03 | P3 | `research/PHASE7_IMPL_PACKAGE_SPEC.md:74`; `:107-109`; `40_MAINTENANCE_PROTOCOL.md:8-16` | The Phase-7 draft cites `F7.2` and `F7.4`, but F7 exposes numbered list items rather than addressable decimal subsections. Round 12 already identified the same weak-model lookup risk for `F7.5`; point-of-use references should say `F7 item 2` and `F7 item 4`. The writer remains unauthorized, so this is documentation drift only. |
| R13-04 | P3 | `NIGHT_BATCH_BACKLOG.md:404-412` | The active backlog still describes NIGHT-BATCH-20 as an unmerged branch and indexes outcomes only through package 19, even though accepted master `7cd2d98` contains the package-22 closeout. Unlike the dated readiness/health reports, the backlog is a current stock document. It needs later-status bookkeeping, while preserving the original package/HOLD evidence. |
| R13-05 | P3 | `research/ERROR_SURFACE_AUDIT_ROUND7.md` ESR7-02; `tests/test_artifact_integrity_v5.py:21-23` | The artifact inventory is a local pytest surface, but a bare-CR assertion can include raw bytes after pytest assertion rewriting and path failures can expose absolute paths. No remote/runtime consumer exists, so this is non-blocking; documentation must not call this failure surface payload-free. |

No P0 or P1 finding was identified.

## Incident lineage

The recurring specification failure now has at least four concrete sites:

1. rollback-preview inputs named evidence-bundle fields that did not exist (L-008 origin);
2. the NB-17 hardlink brief equated inode sharing with path escape;
3. the NB-19 board-root symlink brief misdefined the caller-selected root boundary, followed by NB-20's invented four-field cross-builder shape; and
4. NB-21 package 5 asserted absence of `allOf` without grepping the schema tree.

R13-02 is a related fifth site: output-field presence was checked, but required Git-context behavior was not. The lesson is broader than “grep field names”: dispatch preflight must inspect every factual schema keyword, fixture shape, and behavior precondition on which mechanical acceptance depends.

## Required later disposition

- R13-01/R13-02: extend F8 language from field-only evidence to all factual contract and behavior preconditions; retain package 5 and package 10 as HOLD until separately corrected.
- R13-03: docs-only reference cleanup in a future explicitly scoped package.
- R13-04: current-status backlog bookkeeping only; do not rewrite dated reports.
- R13-05: keep the inventory error surface local; any redaction fix needs a separately scoped test-tool package and must not alter the 14-xfail product baseline by accident.

These findings authorize no schema, validator, writer, runtime, route, remote, or test-behavior change.
