# v0.7 Mock E2E to Blackboard Contract Migration Assessment

Status: **REVIEW ONLY — NO CODE CHANGE**

Scope: `app/mock_e2e_v0_7.py`, its v0.7 TaskEnvelope/CallbackEvent dependencies,
and the current ten Blackboard schemas. This assessment neither changes the legacy
mock nor authorizes a queue, worker, dispatch, runtime, or migration adapter.

## 1. Current roles are different

The v0.7 mock is a compact procedural rehearsal:

`mock request -> TaskEnvelope -> approval gate -> in-memory queue -> mock callback -> result dict`

The Phase 3/4 contract is an append-style message sequence. It separates task,
annotation, readiness, decision, dry-run, command, result, approval packet, audit
preview, and rollback preview. Every message has nine common fields, the exact
16-key safety profile, a fixed `message_type`, and `additionalProperties: false`.

Consequently, the v0.7 objects are not old versions of one new schema. One legacy
object would have to fan out into several messages, with new provenance and safety
data supplied by a trusted boundary. A field-name copy is insufficient.

## 2. TaskEnvelope field inventory

| v0.7 TaskEnvelope field | Closest new location | Compatibility assessment |
|---|---|---|
| `task_id` | `task_draft.task_id` and downstream `task_id` | Direct value, but each new message still needs its own id and common fields. |
| `created_at` | Common `created_at` | Direct if it satisfies the new date-time format. |
| `created_by` | Common `produced_by` | Candidate mapping; the legacy value does not establish the new role semantics. |
| `source` | Common `produced_by` or provenance note | Conflicts with `created_by`; both cannot be silently collapsed. |
| `requested_by` | `task_draft.requested_by` | Direct. |
| `risk_level` | `approval_packet.risk_level` | Not direct: legacy integer 0..4 versus current N=1 packet const `low`. Requires an explicit policy decision. |
| `approval_required` | `approval_readiness.next_step_requires_owner_confirmation` | Similar intent, different lifecycle point; must be derived, not copied. |
| `approval_status` | `approval_readiness.readiness_status` / `owner_decision.decision_status` | One legacy enum compresses two message types; values do not match. |
| `intent` | `task_draft.summary` or annotation | No exact field; copying would lose distinction from `goal`. |
| `goal` | `task_draft.title` / `summary` | Transform required; no exact one-to-one mapping. |
| `task_type` | `task_draft.task_type`, command `task_type` | New N=1 contract is const `query`; other legacy strings must be rejected. |
| `priority` | None | Intentionally absent from N=1 contract. |
| `input_summary` | `task_draft.summary` and command `input_summary` | Reusable only after the chosen task summary relationship is specified. |
| `target_runtime` | Task draft and command `target_runtime` | New enum restricts it to `openclaw_mock` or `openclaw`. |
| `target_workspace` | Approval packet `exact_target` | Not direct: new target is a structured, harmless N=1 query target. |
| `idempotency_key` | Command `idempotency_key` | Direct after a command id and dry-run link exist. |
| `max_retries` | None | N=1 contract has no retry mechanism. |
| `retry_count` | None | N=1 contract has no retry mechanism. |
| `status` | Message sequence and per-message status fields | Not direct; `queued/running/...` are procedural queue states, not Blackboard message types. |
| `result_policy` | None | Legacy free-form policy object is outside the new allowlist. |
| `callback_policy` | None | Legacy free-form policy object is outside the new allowlist. |
| `metadata` | None | Must not be copied into `safety_flags`; the legacy object is open-ended and its two mock flags are not the 16-key profile. |
| `input_payload_ref` (optional) | None | Outside the N=1 contract and potentially content-bearing. |
| `allowed_tools` (optional) | Command `allowed_tools` | Direct only for an explicitly approved query command. |
| `denied_tools` (optional) | Command `denied_tools` | Direct only for an explicitly approved query command. |

Fields absent from TaskEnvelope but mandatory in every new message include
`schema_version`, `message_type`, `safety_flags`, `prev_entry_hash`,
`execution_class`, `parent_task_id`, and `role`. The legacy mock cannot invent these
from its free-form `metadata`.

## 3. CallbackEvent field inventory

| v0.7 CallbackEvent field | Closest new location | Compatibility assessment |
|---|---|---|
| `event_id` | `result_message.callback_id` | Direct identifier candidate. |
| `task_id` | Result `task_id` | Direct. |
| `source` | Common `produced_by` | Candidate mapping with an explicit trusted producer identity rule. |
| `created_at` | Common `created_at` or result `completed_at` | Lifecycle meaning must be selected explicitly. |
| `event_type` | Result `result_status` / `result_type` | Enum transform required; no one-to-one values. |
| `status` | Result `result_status` | `completed/failed/cancelled` overlap; `ok/running/rejected` do not. |
| `summary` | Result `summary` | Direct text candidate. |
| `retryable` | None | Retry is intentionally not designed for N=1. |
| `metadata` | None | Open-ended legacy metadata cannot become safety flags. |
| `flow_id` (optional) | None | No approved multi-flow mechanism. |
| `result_ref` (optional) | Result `output_preview` | Not direct; a reference is not a display-safe preview. |
| `error_code` / `error_message` (optional) | Result `error_summary` | Requires bounded redaction and combination rules. |
| `duration_ms` (optional) | None | New result records timestamps, not a duration field. |
| `artifacts` (optional) | None | Outside the N=1 allowlist and may carry content or paths. |

The new result also requires `result_id`, `command_id`, `related_dry_run_id`,
`execution_mode`, `started_at`, `completed_at`, `validation_status`,
`external_side_effects`, `rollback_note`, and `audit_note`. The v0.7 callback does
not prove those facts.

## 4. `run_mock_e2e_dry_run` result inventory

| Legacy result field | Closest new location | Compatibility assessment |
|---|---|---|
| `dry_run` | Safety flag `dry_run`; worker `preview_only` | Boolean alone cannot generate the entire safety profile. |
| `task_id` | All task-linked messages | Direct. |
| `initial_status` / `final_status` | Readiness, dry-run, or result status | Legacy queue states require an explicit event-to-message transform. |
| `approval_required` / `approval_status` | Approval readiness and owner decision | Must become separate messages; null/legacy enum values are not new contract values. |
| `callback_event` | Separate `result_message` | Nested callback cannot be embedded because new schemas reject extra properties. |
| `events` | One or more preview `audit_event` messages | Strings are not audit records and lack identifiers/provenance. |
| `stopped_at` | Readiness reason / next Owner action | Transform required. |
| `summary` | Result or readiness summary/reason | Target depends on which path stopped. |
| `metadata` | None | Cannot be promoted to safety flags. |

## 5. Behavioural differences and risk

1. The legacy low-risk path sets `status=queued` and calls the in-memory
   `claim_next`; the current Blackboard contract is data validation and preview, not
   authority to dispatch or claim work.
2. The legacy approval gate is a local risk heuristic. The new chain separates
   readiness from an Owner decision and still does not create an execution token.
3. Legacy validators check required fields and basic types but allow extra fields.
   New JSON Schemas reject all unknown properties and require exact safety keys.
4. Legacy ids/timestamps are generated inside the procedural mock. A migration must
   state which trusted producer creates every new message id and link.
5. Legacy callback metadata asserts only `mock` and `dry_run`; it does not prove the
   remaining safety flags, execution class, side effects, or audit state.
6. Treating old `queued` or `approved` values as new authority could create an
   approve-to-dispatch shortcut. Any migration must remain preview-only.

## 6. Options

### Option A — keep the v0.7 mock as a frozen legacy rehearsal

Keep its existing tests and clearly label its outputs as non-Blackboard artifacts.
This has the lowest immediate risk and preserves historical regression coverage, but
it leaves two rehearsal languages in the repository.

### Option B — add a one-way explicit migration adapter later

A pure adapter could accept a validated legacy fixture and emit a complete in-memory
Blackboard preview chain. Every derived/defaulted field would be documented, and any
unsupported legacy value would fail closed. It must not enqueue, claim, write, or
dispatch. This offers measurable migration coverage but requires an Owner-approved
field policy for every non-direct row above.

### Option C — retire the v0.7 mock after equivalent coverage exists

Once full-chain contract rehearsal covers the intended cases and historical tests
have a mapped replacement, the legacy mock could be removed in a separately reviewed
cleanup. Early retirement risks losing useful regression cases and hides unmapped
semantics rather than deciding them.

## 7. Recommendation

Use **Option A now**, then consider **Option B as a separately scoped, tests-first,
pure in-memory package**. Do not retrofit the new contract inside
`mock_e2e_v0_7.py`, and do not interpret its queue/approval states as new execution
authority. After the adapter has explicit Owner decisions, negative tests, and full
coverage, reassess Option C.

Minimum decisions before Option B are: `created_by` versus `source` provenance,
integer risk conversion, `intent/goal/input_summary` text mapping, exact target
construction, status-event mapping, safety profile construction, unsupported
task types, and redaction of errors/artifacts. Until then, no lossless automatic
migration exists.
