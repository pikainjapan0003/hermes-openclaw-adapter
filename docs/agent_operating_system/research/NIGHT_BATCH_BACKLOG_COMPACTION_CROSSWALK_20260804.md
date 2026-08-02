# NIGHT_BATCH_BACKLOG compaction crosswalk

Date: 2026-08-04

Purpose: preserve every consumed-package entry removed from the active backlog during NIGHT-BATCH-21 package 4. This file is historical bookkeeping only. It grants no authorization and does not reopen any consumed package. The active stock and every Owner gate remain in `NIGHT_BATCH_BACKLOG.md`.

## Before/after rule

| Before location | Entry count | After location | Semantic change |
|---|---:|---|---|
| Backlog NB-18 completed table | 22 package rows | NB-18 table below + one-line backlog index | None |
| Backlog NB-19 consumed table | 22 package rows after R12-01 closeout | NB-19 table below + one-line backlog index | None; HOLD and correction evidence retained |
| Backlog NB-20 consumed table | 19 package rows | NB-20 table below + one-line backlog index | None; HOLD/correction evidence retained |

The mapping is one-to-one: the 60 rows moved by package 4 remain present, and R12-01 adds the three previously omitted NB-19 closeout rows. No active-stock row, Owner-gate row, boundary, finding, or authorization sentence was moved or removed.

## NB-18 table

| Package | Result | Commit |
|---:|---|---|
| 1 | Fixture SHA-256 inventory is line-ending portable | `977375fe` |
| 2 | Board-reader hardlink boundary and shared-inode report | `494e47a3` |
| 3 | Malicious board-path boundary tests | `65cca7de` |
| 4 | Coverage-floor assertion decoupled from child return code | `1cfe0128` |
| 5 | Round-9 documentation findings resolved | `59364fb7` |
| 6 | Core-document boundary updates and Owner-only proposal | `3f4a5f1b` |
| 7 | Error-surface redaction hardening | `0220923f` |
| 8 | Slow-test markers and performance selection | `738a2daf` |
| 9 | Test-layer guard compatibility | `b8141495` |
| 10 | Contract mutation resistance round 4 | `8fb700f9` |
| 11 | Builder extreme-input round 2 | `46b42b86` |
| 12 | Read-only script coverage round 3 | `1ad4d042` |
| 13 | Full-chain rehearsal v6 determinism | `5d5e70cf` |
| 14 | Phase-9 preflight condition catalog v2 | `d14e0ff5` |
| 15 | v1.1/PB impact analysis v2 | `9bff23b8` |
| 16 | Governance audit round 10 | `255cceaa` |
| 17 | Metrics reproducibility test | `4ceaea4a` |
| 18 | Fixture/golden integrity v3 | `d0091cf8` |
| 19 | Backlog refill round 8 | `22bca79` / `f0602af` |
| 20 | Lesson L-009 | `a9aa42c` |
| 21 | Maintenance F7 | `f7a3496` |
| 22 | Phase-11 health report 2026-08-01 | `1b6da89` |

## NB-19 table

| Package | Result | Commit/evidence |
|---:|---|---|
| 1 | Trailing blank removed | `357566c` |
| 2 | Default fast/full test profiles and measured slow marker | `6cfda35`, `d551c3c` |
| 3 | Slow-marker integrity meta-test | `e1be0ff` |
| 4 | Round-10 documentation findings repaired | `32b3216` |
| 5 | Recomputable report metrics extended | `8078fae` |
| 6 | **HOLD**: root symlink accepted by current reader | Direct WSL evidence; no commit |
| 7 | Test-local future-writer hardlink precondition guard | `fe236f2` |
| 8 | 90 safety-flag combination mutations | `26e8a49` |
| 9 | **HOLD**: truncated HTTP-200 body remains `REACHABLE` | Direct injected-response evidence; no commit |
| 10 | Mirror scale/missing/permission/DIFFERS boundaries | `cef0d02` |
| 11 | **HOLD**: renderer omits ref/union/deep semantics | Direct rendered-output evidence; no commit |
| 12 | 100,000-entry hash-chain measurement and tamper localization | `04da304` |
| 13 | Research-report persistence leak audit | `219e6bb` |
| 14 | Governance audit Round 11 | `a3964c6` |
| 15 | 00 Round-2 environment corrections and proposals | `da712ab` |
| 16 | 20 R-01 through R-13 review | `3120ea9` |
| 17 | v1.0 readiness fifth pass | `85fd7e2` |
| 18 | Phase-7 implementation package spec v2 | `3f4d1f4` |
| 19 | Unified 65-artifact integrity inventory | `b9375c1` |
| 20 | Backlog refill Round 9 | `3b82cc3` |
| 21 | Lesson L-010 and diff-check evidence rule | `c62ff6b`; correction `26ded83` |
| 22 | Phase-11 health report 2026-08-02 | `97080e1` |

## NB-20 table

| Package | Result | Commit/evidence |
|---:|---|---|
| 1 | Renderer supports `oneOf`/`anyOf`/`allOf` and const-only types; current unspecified count is zero | `a3206f8` |
| 2 | Exhaustive renderer type-fidelity guard | `3e4e949` |
| 3 | F7 resolved-root invariant and filesystem-boundary tests | `53f52be` |
| 4 | HTTP reachability-only semantics documented | `bd16530` |
| 5 | Three NIGHT-BATCH-19 HOLD decisions recorded | `ad145eb` |
| 6 | L-011 records path-indirection specification debt | `c1f94ee` |
| 7 | Lowest managed legacy modules receive tests without deleting defensive branches | `3b3c587`, correction `aba025b`; independent coverage: rollback 100%, full-loop 99% |
| 8 | **HOLD**: current schemas permit non-`1.0` `schema_version`; tests-only scope cannot create version-evolution semantics | Direct 90-case evidence; no commit |
| 9 | Eight concurrent readers over one 500-file board return identical results without mutation | `64fe49b` |
| 10 | **HOLD**: approval packet and evidence bundle do not expose four fields at a common shape and no cross-builder gate exists | Direct builder evidence; no commit |
| 11 | Twelve preflight catalog citations are line-verified | `e90e5ce` |
| 12 | Renderer and mirror stdout redaction Round 6 | `ae1b47d` |
| 13 | Governance audit Round 12 | `5869b25` |
| 14 | Non-safety delegation-template workflow refresh | `cbd6270` |
| 15 | Environment snapshots, five-level routing and nightly workflow rechecked | `439b8e1` |
| 16 | v1.0 readiness sixth pass with estimates and sole gatekeepers | `8b64962` |
| 17 | Phase-7 implementation package draft v3; still twice marked unauthorized | `3744a61` |
| 18 | Closed 278-item normalized artifact inventory | `50ae4f7` |
| 19 | Fast/full performance Round 2 and markers for new expensive tests | `8cd34c1`, native-measurement correction `98fbcf5` |
