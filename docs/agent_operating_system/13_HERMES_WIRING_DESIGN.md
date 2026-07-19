# Hermes Advisory-to-Blackboard Wiring Design

Status: **PLANNING ONLY, NOT AUTHORIZED**

接線實作屬 Owner 閘。本文件不授權啟動 Hermes runtime、呼叫任何模型供應商、
寫入 Blackboard、建立 queue task、dispatch Worker、呼叫 OpenClaw、建立 POST route、
傳送 remote payload 或自動 follow-up。本文只有資料映射與 fail-closed 設計。

## 1. Authority and semantic boundary

The governing rules remain:

- Owner is the sole approver;
- Hermes advice is not Owner approval;
- Hermes readback is advisory only;
- Blackboard display is not execution permission;
- a task draft or annotation is not queue admission, Worker dispatch, or a runtime call;
- `produced_by` records provenance only and never changes permissions.

The proposed adapter converts one bounded Hermes advisory result into either a
`task_draft` preview or an `annotation` preview. Validation success means only that the
data matches a closed contract. No consumer may interpret it as permission to persist,
dispatch, execute, retry, or create a follow-up task.

## 2. N=1 scope

The first wiring proposal supports one Owner-reviewed planning request and one task
chain:

1. Owner or an already-authorized plan supplies a bounded planning question;
2. exactly one selected Hermes brain returns advisory content;
3. a deterministic adapter projects allowlisted content into one `task_draft` preview;
4. after that draft validates, one separately requested advisory pass may produce one
   `annotation` preview;
5. both previews stop for Owner review.

There is no multi-worker fan-out, background poll, retry loop, continuous monitoring,
automatic brain debate, majority vote, fallback-generated second task, or downstream
dispatch in this design.

## 3. Component boundary

| Component | Reads | May produce in memory | Must never do in this design |
|---|---|---|---|
| Hermes brain | Bounded advisory prompt and redacted task context | Untrusted advisory text/fields | Write Blackboard, select permissions, call another brain, issue commands |
| Projection adapter | Untrusted advisory result plus trusted envelope metadata | Closed `task_draft` or `annotation` preview | Preserve unknown fields, obey advisory instructions, write files/queue/runtime |
| Blackboard validator | Projected mapping | Structured valid/error result | Repair content, grant permission, trigger next step |
| Future writer | Not present | Nothing | Any operation until separately authorized by Owner |
| Dashboard | Validated preview only | Read-only display | POST, approve-to-dispatch, runtime call |

Hermes-generated text is data, not a new instruction channel. Prompt injection or text
such as “ignore previous rules”, “dispatch now”, or “approved” remains ordinary
untrusted content and cannot alter the adapter's field allowlist or safety posture.

## 4. Three-brain provenance

05 and 10 define three equal-authority Hermes brains selected by availability/usage:
GPT-5.5, Minimax M3, and Deepseek v4 Pro. Selection does not create a safety downgrade
or permission difference. Every preview records the actual source in `produced_by`.

Proposed canonical provenance values:

| Brain | `produced_by` value |
|---|---|
| GPT-5.5 | `hermes:gpt-5.5` |
| Minimax M3 | `hermes:minimax-m3` |
| Deepseek v4 Pro | `hermes:deepseek-v4-pro` |

These strings are proposed data conventions, not active schema enums. Unknown source,
empty source, source disagreement, or an inability to prove which brain produced the
result causes HOLD. The adapter must not relabel one brain as another or infer identity
from response style.

`role` and `produced_by` remain separate: `role` describes the artifact author's
functional role, while `produced_by` names the actual brain/source. Neither authenticates
the caller or authorizes an action.

## 5. Trusted envelope versus untrusted advisory

The future adapter must construct these fields from trusted local envelope data rather
than accept them from the model response:

- `schema_version` and `message_type`;
- `created_at` from a reviewed UTC clock source;
- all 16 `safety_flags`;
- `prev_entry_hash` policy;
- `execution_class` after external classification;
- `produced_by` from the selected provider record;
- `parent_task_id`, task/result references, and deterministic ids;
- `role` from the adapter's approved role mapping.

The advisory response may supply only bounded semantic candidates such as title,
summary, display summary, safety notes, or suggested allowed/forbidden behaviors.
Those candidates are length-limited, control-character checked, stripped of unknown
keys, and treated as data. They cannot supply token, command, target path, environment,
URL callback, credential, queue status, approval state, or runtime capability.

## 6. `task_draft` projection

The adapter projects one planning advisory into the existing
`task_draft.schema.json` fields:

| Field | Source and rule |
|---|---|
| `schema_version` | Trusted adapter constant matching the registered contract |
| `message_type` | Constant `task_draft` |
| `created_at` | Trusted adapter UTC timestamp; never model-supplied |
| `safety_flags` | Owner-reviewed safe preview profile; runtime/write flags false in planning mode |
| `prev_entry_hash` | Null for an unpersisted preview; no chain claim |
| `execution_class` | External classifier result; ambiguity defaults to HOLD, never model-selected AUTO |
| `produced_by` | Exact selected-brain provenance from §4 |
| `parent_task_id` | Trusted plan reference or null; not inferred from advisory text |
| `role` | Proposed constant `hermes_planner`; provenance only |
| `task_id` | Deterministic trusted id bound to the planning request |
| `title` | Length-bounded advisory candidate after text safety checks |
| `summary` | Length-bounded advisory candidate; no embedded instruction authority |
| `requested_by` | Trusted requester identity/role from the envelope |
| `task_type` | Existing constant `query` for this N=1 design |
| `target_runtime` | `openclaw_mock` in preview; real target requires a new Owner gate |

If the requested task is not a harmless query-shaped draft, the projection stops. It
does not coerce a write or side-effecting proposal into `AUTO` merely to satisfy the
current N=1 schema.

## 7. `annotation` projection

An annotation can be proposed only for a schema-valid task draft whose trusted task id
is supplied separately. The annotation maps as follows:

| Field group | Source and rule |
|---|---|
| Common fields | Same trusted-envelope rules as §6 |
| `role` | Proposed constant `hermes_annotator`; provenance only |
| `annotation_id` | Deterministic id from request/task/revision; not model-supplied |
| `task_id` | Exact validated source task id |
| `annotation_type` | `advice` or `safety`, selected by the trusted request |
| `annotation_status` | `validated_preview` only after complete schema validation |
| `display_title` / `display_summary` | Bounded advisory display text |
| `allowed_behaviors` | Adapter allowlist intersection, never raw model capability claims |
| `forbidden_behaviors` | Mandatory deny items plus safe bounded advisory notes |
| `safety_notes` | Non-secret, non-command explanatory strings |
| `related_result_id` | Null unless an already-validated result reference is explicitly supplied |
| `next_owner_action` | Review/HOLD wording only; never dispatch or execute wording |

Mandatory forbidden behaviors include Worker dispatch, real OpenClaw/Hermes calls,
queue/Blackboard/audit writes, connectors, remote callbacks, follow-up creation, token
issuance, and treating advice as approval.

## 8. Frequency and duplicate policy

The initial limits are event-driven, not time-driven:

- at most one task-draft advisory request per exact Owner-reviewed planning request;
- at most one annotation advisory request per exact task-draft revision;
- no automatic retry after timeout, provider error, invalid JSON, schema failure, or
  ambiguous result;
- no scheduled polling, watcher, heartbeat generation, or background refresh;
- a repeated request with the same request/task/revision id returns the prior in-memory
  outcome or a duplicate/HOLD result; it does not call a brain again;
- editing any trusted field creates a new revision requiring new review; it cannot
  reuse a previous advisory as if unchanged;
- switching brains after failure is a new explicitly reviewed attempt, not an automatic
  fallback.

These are proposed first-version limits. They do not authorize a cache, ledger, file,
queue, or scheduler implementation.

## 9. Validation sequence

1. Check active Owner instruction and exact scope; missing or ambiguous authority means
   HOLD before any provider call.
2. Validate trusted request envelope and reject secret/production/third-party data that
   exceeds the reviewed scope.
3. Select one verified brain and record provider identity outside the prompt response.
4. Make at most one advisory call under a separately authorized runtime package.
5. Parse the result as untrusted data; reject unknown fields and injection-like control
   content rather than following it.
6. Construct the complete closed message from trusted envelope fields plus allowlisted
   advisory candidates.
7. Run `validate_blackboard_message` with the explicit expected message type.
8. On validation success, return an in-memory preview for Owner display only.
9. On any failure, return a structured non-secret HOLD result and stop.

Schema validity does not activate a writer. A future writer must have its own exact
Owner authorization and must revalidate the immutable message before any mutation.

## 10. Fail-closed matrix

| Failure | Required result | Forbidden fallback |
|---|---|---|
| Brain unavailable/rate-limited | HOLD with provider-unavailable code | Automatically call the next brain |
| Provider identity uncertain | HOLD | Guess `produced_by` |
| Timeout/ambiguous response | HOLD; attempt considered spent | Retry or continue partial output |
| Non-object/unknown fields | Reject the advisory result | Preserve extras in notes/payload |
| Secret, token, callback, command, path, or production endpoint | Reject without echoing value | Redact and continue silently |
| Unsafe or unclear execution class | HOLD/OWNER review | Default to AUTO |
| Task/reference mismatch | Reject | Repair ids or attach to nearest task |
| Schema error | Return structured validator errors | Fill missing fields from model guesses |
| Blackboard writer unavailable/unauthorized | Keep preview in memory and stop | Write another file, queue, or remote store |
| Owner absent | Display-only HOLD | Treat prior approval as current authority |

Failure to create an annotation must not invalidate or mutate the source task draft.
Failure to create a task draft must not create an annotation, queue item, or follow-up.

## 11. Leakage and retention

The future advisory prompt should contain only fields explicitly approved for the
selected brain. Provider response, raw prompt, chain-of-thought, credentials, headers,
environment values, local paths, and full payloads must not enter Blackboard messages.

05 currently treats the three brains as equal for Owner-owned project data, but §6.11
T1 still requires re-review when third-party personal data enters Blackboard. This
design does not pre-authorize that transition and adds no sensitivity-bypass rule.

## 12. Required tests before implementation

A separately authorized implementation package must prove:

- exact trusted/untrusted field separation for both message types;
- all three provenance values are recorded without changing safety decisions;
- unknown provider and spoofed `produced_by` fail closed;
- prompt-injection text cannot change flags, type, role, target, ids, or permissions;
- schema-invalid, extra-field, timeout, duplicate, retry, and brain-switch cases stop;
- provider error content is not echoed into logs or validation messages;
- no import/call path reaches queue, worker, OpenClaw, writer, route, connector,
  subprocess, filesystem mutation, or remote callback;
- valid previews still do not trigger the next message automatically;
- runtime call count is at most one per exact reviewed request/revision.

## 13. Owner-gated implementation questions

Before any wiring code exists, Owner must separately decide:

1. exact provider API/adapter and authentication scope;
2. active model identifiers and canonical `produced_by` strings;
3. prompt field allowlist, maximum lengths, and data classification;
4. timeout and whether any manually requested brain switch is permitted;
5. task/revision id derivation and duplicate handling without unauthorized persistence;
6. exact Blackboard write target and authorization, if persistence is desired;
7. route/runtime entrypoint, if any, under a separate red-line review;
8. treatment of third-party personal data under §6.11 T1.

Until those decisions and a new Owner instruction exist, this document remains a
planning artifact and no Hermes-to-Blackboard connection is authorized.
