# Fixture Inventory Recheck — 2026-07-26

Status: **REVIEW ONLY**. No fixture was added, edited, moved, deduplicated, or
deleted.

## Method

Read-only commands enumerated tracked fixture paths, grouped first-level
directories, calculated SHA-256 for every tracked file, compared fixture paths
against the NIGHT-BATCH-14 base `9026fbe`, and searched exact basenames across
`app/`, `tests/`, and `scripts/`.

```text
git ls-files fixtures
Get-FileHash -Algorithm SHA256 <each tracked fixture>
git diff --name-status 9026fbe..HEAD -- fixtures
rg -l --fixed-strings <basename> app tests scripts
```

## Count comparison

| Directory | NB-12 baseline | 2026-07-26 | Change |
|---|---:|---:|---:|
| `fixtures/blackboard_contract/` | 30 | 30 | 0 |
| `fixtures/builder_golden_vectors/` | 2 | 2 | 0 |
| `fixtures/hash_chain_vectors/` | 8 | 8 | 0 |
| `fixtures/local_mock_data/` | 10 | 10 | 0 |
| **Total** | **50** | **50** | **0** |

`git diff --name-status 9026fbe..HEAD -- fixtures` produced no output.

## SHA-256 groups

- Files hashed: 50/50.
- Byte-identical hash groups containing more than one file: **0**.
- Added files versus the 50-file baseline: **0**.
- Deleted files versus the 50-file baseline: **0**.

The result does not imply semantic uniqueness. Blackboard negative fixtures
deliberately share structural patterns while retaining different message
contracts.

## Reference and orphan review

No confirmed orphan was found, with an important distinction:

- 47 fixtures have the test/inventory relationships documented in
  `FIXTURE_INVENTORY_20260724.md`;
- three legacy fixtures have **historical executable script references, not
  pytest coverage**.

| Legacy fixture | `app/` + `tests/` exact-basename hits | `scripts/` hits | Classification |
|---|---:|---:|---|
| `hermes_openclaw_local_mock_messages_v0_8_1.json` | 0 | 42 | Historical script-referenced |
| `hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json` | 0 | 16 | Historical script-referenced |
| `hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json` | 0 | 10 | Historical script-referenced |

“Script-referenced” prevents an unsupported orphan label; it does not claim
current runtime use, pytest validation, or migration readiness.

## Boundary

This recheck is not deletion authority. A future zero-reference result would
still require semantic review and a separately authorized removal proposal.
No duplicate, reference count, or stale-looking filename may trigger
mechanical deletion.
