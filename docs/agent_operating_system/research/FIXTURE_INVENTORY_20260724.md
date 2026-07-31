# Fixture Inventory — 2026-07-24

Status: read-only inventory. No fixture was added, edited, moved, or deleted.

Method: enumerate every tracked file below `fixtures/`, search direct basename
and directory-pattern references, trace fixture-path constants through the
tests that exercise their loaders, and group SHA-256 hashes to identify
byte-identical content.

## Summary

| Directory | Files | Purpose | Primary test coverage |
|---|---:|---|---|
| `fixtures/blackboard_contract/` | 30 | Ten Blackboard message contracts × valid, missing-common, and extra-safety-flag cases | `tests/test_blackboard_schemas.py` exact inventory and parameterized load |
| `fixtures/builder_golden_vectors/` | 2 | Deterministic approval/evidence builder input-output vectors | `tests/test_builder_golden_vectors.py` |
| `fixtures/hash_chain_vectors/` | 8 | Canonical JSON bytes/hash and three-entry chain vectors | `tests/test_hash_chain_vectors.py` directory inventory |
| `fixtures/local_mock_data/` | 10 | Frozen preview/rehearsal evidence and remote-projection cases | Dedicated and transitive loader tests listed below |
| **Total** | **50** |  |  |

## Complete file-to-test map

### Blackboard contract fixtures

All 30 files are mechanically enumerated and loaded by
`tests/test_blackboard_schemas.py`; the exact 30-name assertion prevents an
unreviewed extra or missing case. Valid fixtures are additionally reused by
board-reader, full-chain, builder, hash-chain, and redaction-baseline tests.

| File | Purpose | Primary test |
|---|---|---|
| `blackboard_contract/annotation.valid.json` | Valid annotation message | `test_blackboard_schemas.py::test_positive_fixture_is_valid_and_has_canonical_common_fields` |
| `blackboard_contract/annotation.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py::test_missing_common_field_fixture_is_rejected` |
| `blackboard_contract/annotation.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py::test_extra_safety_flag_fixture_is_rejected` |
| `blackboard_contract/approval_packet.valid.json` | Valid Phase 4 approval packet | `test_blackboard_schemas.py`; dedicated equality/schema checks in `test_approval_packet.py` |
| `blackboard_contract/approval_packet.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py`; `test_approval_packet.py` |
| `blackboard_contract/approval_packet.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py`; `test_approval_packet.py` |
| `blackboard_contract/approval_readiness.valid.json` | Valid approval-readiness message | `test_blackboard_schemas.py` |
| `blackboard_contract/approval_readiness.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/approval_readiness.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/audit_event.valid.json` | Valid preview-only audit event | `test_blackboard_schemas.py`; reused by `test_hash_chain.py` and rollback tests |
| `blackboard_contract/audit_event.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/audit_event.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/openclaw_command_envelope.valid.json` | Valid dry-run command envelope | `test_blackboard_schemas.py` |
| `blackboard_contract/openclaw_command_envelope.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/openclaw_command_envelope.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/owner_decision.valid.json` | Valid Owner decision data message | `test_blackboard_schemas.py` |
| `blackboard_contract/owner_decision.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/owner_decision.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/result_message.valid.json` | Valid mock result message | `test_blackboard_schemas.py`; reused by approval/rollback builder tests |
| `blackboard_contract/result_message.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/result_message.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/rollback_event.valid.json` | Valid descriptive rollback event | `test_blackboard_schemas.py` |
| `blackboard_contract/rollback_event.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/rollback_event.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/task_draft.valid.json` | Valid root task draft | `test_blackboard_schemas.py`; reused by evidence and board tests |
| `blackboard_contract/task_draft.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/task_draft.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |
| `blackboard_contract/worker_dry_run.valid.json` | Valid inert worker dry-run | `test_blackboard_schemas.py`; reused by approval builder tests |
| `blackboard_contract/worker_dry_run.invalid_missing_common.json` | Missing required common field | `test_blackboard_schemas.py` |
| `blackboard_contract/worker_dry_run.invalid_extra_safety_flag.json` | 17th safety flag rejection | `test_blackboard_schemas.py` |

### Builder golden vectors

| File | Purpose | Primary test |
|---|---|---|
| `builder_golden_vectors/approval_packet_vectors.json` | Six deterministic approval-packet source/kwargs/expected-output cases | `tests/test_builder_golden_vectors.py` |
| `builder_golden_vectors/evidence_bundle_vectors.json` | Six deterministic evidence-bundle source/kwargs/expected-output/hash cases | `tests/test_builder_golden_vectors.py` |

### Hash-chain vectors

`tests/test_hash_chain_vectors.py` inventories every JSON file in this
directory, so files loaded through the directory glob are not orphans merely
because their basename is absent from source text.

| File | Purpose | Primary test |
|---|---|---|
| `hash_chain_vectors/chain_genesis.json` | Genesis entry and hash | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/chain_second.json` | Second entry linked to genesis | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/chain_third.json` | Third entry linked to second | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/escaped_text.json` | Escaped/control-text canonicalization | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/minimal.json` | Minimal JSON object vector | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/nested_sorting.json` | Recursive key-order canonicalization | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/types_and_order.json` | Mixed scalar/array/object ordering | `tests/test_hash_chain_vectors.py` |
| `hash_chain_vectors/unicode_nfc.json` | Unicode NFC boundary | `tests/test_hash_chain_vectors.py` |

### Local mock and projection data

| File | Purpose | Primary test or exercised loader |
|---|---|---|
| `local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json` | Frozen full-loop read-only rehearsal | `tests/test_legacy_preview_coverage.py` through `app/full_loop_preview_adapter.py` |
| `local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json` | Legacy local mock preview source | `tests/test_main_get_routes_coverage.py` and `test_dashboard_readonly.py` through the dashboard preview loader |
| `local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json` | Legacy worker dry-run preview | main/dashboard GET tests through `worker_dry_run_preview_boundary_v0_8_3_b.py` |
| `local_mock_data/hermes_openclaw_worker_dry_run_result_audit_trail_v0_8_4_b.json` | Legacy dry-run result/audit display fixture | main/dashboard GET tests through `worker_dry_run_result_audit_trail_boundary_v0_8_4_b.py` |
| `local_mock_data/hermes_result_feedback_preview_v0_9_6_d.json` | Frozen result-feedback preview | `tests/test_legacy_preview_coverage.py` through `app/result_feedback_preview.py` |
| `local_mock_data/n1_dry_run_evidence_bundle.json` | Phase 5 evidence-bundle golden record | `tests/test_evidence_bundle.py`; reused by rollback/full-chain/preflight tests |
| `local_mock_data/remote_readonly_projection.valid.json` | Valid offline remote projection | `tests/test_remote_readonly_projection.py` |
| `local_mock_data/remote_readonly_projection.invalid_extra_payload.json` | Projection extra-payload rejection | `tests/test_remote_readonly_projection.py` |
| `local_mock_data/remote_readonly_projection.invalid_pulled_at.json` | Projection timestamp/field rejection | `tests/test_remote_readonly_projection.py` |
| `local_mock_data/remote_readonly_projection.invalid_secret_value.json` | Projection leak-guard rejection | `tests/test_remote_readonly_projection.py` |

## Duplicate-content result

SHA-256 grouping across all 50 files found **no byte-identical duplicate
files**.

There is intentional structural repetition:

- every Blackboard case repeats the nine common fields and 16-flag object;
- each message type has the same two negative-case classes;
- builder vectors repeat stable source records while varying one input; and
- hash-chain vectors repeat the vector envelope.

These repetitions are contract coverage, not candidates for silent
deduplication. Consolidating them would change fixture readability or test
failure locality and requires a separate authorized proposal.

## Orphan result

**No confirmed orphan fixture.** All 50 files are covered by an exact inventory,
directory glob, direct test reference, or a fixture-path loader exercised by
the named tests. Basename-only search produced apparent false orphans for
parameterized Blackboard cases and glob-loaded hash vectors; tracing the load
pattern resolves them.

This conclusion does not authorize deletion if future reference counts change.

