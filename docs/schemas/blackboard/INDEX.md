# Blackboard Contract Schemas

Status: Phase 3 package 2 contract implementation. These schemas validate data only; they are not connected to routes, queue mutation, Worker dispatch, or runtime execution.

## Schemas

| `message_type` | File |
|---|---|
| `task_draft` | `task_draft.schema.json` |
| `annotation` | `annotation.schema.json` |
| `approval_readiness` | `approval_readiness.schema.json` |
| `owner_decision` | `owner_decision.schema.json` |
| `worker_dry_run` | `worker_dry_run.schema.json` |
| `openclaw_command_envelope` | `openclaw_command_envelope.schema.json` |
| `result_message` | `result_message.schema.json` |
| `audit_event` | `audit_event.schema.json` |
| `rollback_event` | `rollback_event.schema.json` |
| `approval_packet` | `approval_packet.schema.json` |

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
