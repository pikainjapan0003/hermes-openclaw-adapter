# Contract Schema Index

Status: data-contract inventory through the Owner-approved offline projection.
These schemas validate or project data only; they do not grant permission for
queue mutation, Worker dispatch, runtime execution, or remote connectivity.

## Contract inventory

| Contract/component | Purpose | Artifact | Reference input | Test |
|---|---|---|---|---|
| `task_draft` | N=1 task proposal data. | `docs/schemas/blackboard/task_draft.schema.json` | `fixtures/blackboard_contract/task_draft.valid.json` | `tests/test_blackboard_schemas.py` |
| `annotation` | Safety annotation for a task draft. | `docs/schemas/blackboard/annotation.schema.json` | `fixtures/blackboard_contract/annotation.valid.json` | `tests/test_blackboard_schemas.py` |
| `approval_readiness` | Readiness preview for Owner review. | `docs/schemas/blackboard/approval_readiness.schema.json` | `fixtures/blackboard_contract/approval_readiness.valid.json` | `tests/test_blackboard_schemas.py` |
| `owner_decision` | Inert Owner decision record. | `docs/schemas/blackboard/owner_decision.schema.json` | `fixtures/blackboard_contract/owner_decision.valid.json` | `tests/test_blackboard_schemas.py` |
| `worker_dry_run` | Non-executing single-worker preview. | `docs/schemas/blackboard/worker_dry_run.schema.json` | `fixtures/blackboard_contract/worker_dry_run.valid.json` | `tests/test_blackboard_schemas.py` |
| `openclaw_command_envelope` | Mock-only command preview envelope. | `docs/schemas/blackboard/openclaw_command_envelope.schema.json` | `fixtures/blackboard_contract/openclaw_command_envelope.valid.json` | `tests/test_blackboard_schemas.py` |
| `result_message` | Synthetic unexecuted result data. | `docs/schemas/blackboard/result_message.schema.json` | `fixtures/blackboard_contract/result_message.valid.json` | `tests/test_blackboard_schemas.py` |
| `audit_event` | Non-persisted audit-event preview. | `docs/schemas/blackboard/audit_event.schema.json` | `fixtures/blackboard_contract/audit_event.valid.json` | `tests/test_blackboard_schemas.py` |
| `rollback_event` | Descriptive rollback preview. | `docs/schemas/blackboard/rollback_event.schema.json` | `fixtures/blackboard_contract/rollback_event.valid.json` | `tests/test_blackboard_schemas.py` |
| `approval_packet` | Offline Owner review packet. | `docs/schemas/blackboard/approval_packet.schema.json` | `fixtures/blackboard_contract/approval_packet.valid.json` | `tests/test_approval_packet.py` |
| `evidence_bundle` | Hashed N=1 dry-run evidence. | `docs/schemas/evidence_bundle.json` | `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json` | `tests/test_evidence_bundle.py` |
| `remote_readonly_projection` | Owner-approved offline display projection; no remote transport. | `docs/schemas/remote_readonly_projection.schema.json` | `fixtures/local_mock_data/remote_readonly_projection.valid.json` | `tests/test_remote_readonly_projection.py` |
| `rollback_preview_builder` | Pure three-contract descriptive rollback preview. | `app/rollback_preview_builder.py` | `fixtures/local_mock_data/n1_dry_run_evidence_bundle.json` | `tests/test_rollback_preview_builder.py` |
| `hash_chain` | In-memory canonical JSON and audit-chain verification. | `app/hash_chain.py` | `fixtures/blackboard_contract/audit_event.valid.json` | `tests/test_hash_chain.py` |
| `n1_preflight_runbook` | Planning-only Phase 9 single-query checklist. | `docs/agent_operating_system/09_N1_PREFLIGHT_RUNBOOK.md` | `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` | `tests/test_contract_index.py` |

## Phase 4 Owner approval packet

`approval_packet` is a data-only, offline review packet for one synthetic,
harmless N=1 query. It binds a `worker_dry_run` id and `result_message` id to an
exact task, command, and query action. The risk is fixed to `low`, expected side
effects must be empty, and the inert timeout is fixed to 30 seconds.

The `decision` data verb is one of `approve | edit | reject | respond`.
`single_use_execution_token` is structurally locked to `null` for Phase 4.
Neither a decision nor this packet grants execution or dispatch permission.

## Required common fields

Every message requires these nine common fields: `schema_version`, `message_type`, `created_at`, `safety_flags`, `prev_entry_hash`, `execution_class`, `produced_by`, `parent_task_id`, and `role`.

All root objects use `additionalProperties: false`.

## Canonical safety flags

`safety_flags` is a nested object containing exactly these 16 boolean keys:

- `synthetic_local_only`
- `mock_only`
- `dry_run`
- `owner_review_required`
- `external_side_effects_allowed`
- `external_side_effects_occurred`
- `blackboard_write_allowed`
- `queue_write_allowed`
- `audit_trail_write_allowed`
- `worker_dispatch_allowed`
- `openclaw_call_allowed`
- `hermes_runtime_allowed`
- `connector_call_allowed`
- `google_sheets_write_allowed`
- `follow_up_allowed`
- `follow_up_requires_owner_confirmation`

The legacy RC-D 17-key object and display-only `"key=value"` array are rejected.

## Execution-class boundary

The general enum is `AUTO | OWNER_APPROVAL | OWNER_MANUAL`. `worker_dry_run` and `openclaw_command_envelope` exclude `OWNER_MANUAL`.

## Validation boundary

`app/blackboard_validators.py` loads only these allowlisted schemas and returns structured errors. It is intentionally not imported by `app/main.py` and performs no writes or runtime actions.
