# Phase 7 Local Audit Write and Rollback Preview Design

Status: **PLANNING ONLY, NOT AUTHORIZED**

This document defines the Phase 7 contract before the first authorized persistent
write. It does not authorize implementation, file creation, audit append, queue or
Blackboard mutation, rollback execution, worker dispatch, or runtime wiring.

This document contains no example code. If a later revision adds example code, every
example must be immediately preceded by the exact line:
`PLANNING ONLY, NOT AUTHORIZED`.

## 1. Authority and scope

The governing requirements are `05_VERIFIED_LONG_TERM_PLAN.md` Phase 7 and
`01_SAFETY_BOUNDARIES.md` sections 2 and 4. Phase 7 is the first planned exception to
"No audit trail write". The exception is deliberately narrow:

- one local development file only: `data/audit_dev.jsonl`;
- append-only audit events;
- one SHA-256 hash chain;
- one N=1 harmless-query rehearsal chain;
- rollback output is descriptive preview data only;
- no queue write, Blackboard write, production/shared storage, external service,
  execution, dispatch, connector, remote API, callback, or runtime connection.

The design and implementation must occur in different reviewed packages. This design
package cannot be treated as implied permission to implement or write the audit file.

## 2. Existing contract inputs

The future implementation may consume only already-validated values from:

1. `docs/schemas/blackboard/audit_event.schema.json`;
2. `docs/schemas/blackboard/rollback_event.schema.json`;
3. `docs/schemas/evidence_bundle.json`;
4. the corresponding validated N=1 fixture or in-memory builder result.

The audit writer must not accept a caller-provided output path. Its persistence target
is a constant resolved inside the repository to `data/audit_dev.jsonl`. The writer must
reject an audit event that has not first passed the canonical audit-event validator.

For an authorized persisted entry, the contract posture is expected to be:

- `message_type` is `audit_event`;
- `audit_status` is `persisted`;
- `persistence_target` is the literal repository-relative label
  `data/audit_dev.jsonl`;
- `preview_only` is `false`;
- `safety_flags.audit_trail_write_allowed` is `true` only under the exact Phase 7
  authorization described in section 8;
- `queue_write_allowed`, `blackboard_write_allowed`, `worker_dispatch_allowed`,
  `openclaw_call_allowed`, `hermes_runtime_allowed`, `connector_call_allowed`, and
  `google_sheets_write_allowed` remain `false`.

These values do not grant execution permission. They describe one authorized audit
append only.

## 3. File format and append discipline

`data/audit_dev.jsonl` is the only file the future writer may create or modify.

Each physical line contains exactly one canonical JSON audit-event object followed by
one LF byte. Requirements:

- UTF-8 without BOM;
- LF line endings, including one final LF after the last complete entry;
- no blank lines, comments, headers, trailers, indexes, sidecar hashes, lock files,
  temporary mirrors, backups, or secondary ledgers;
- no in-place update, rewrite, compaction, rotation, truncation, or deletion by the
  writer;
- no arbitrary filename, environment override, symlink escape, or caller-selected
  directory;
- a failed validation or chain check performs zero append bytes.

Before every append, the future writer must acquire exclusive local process/file
coordination appropriate to the platform, re-read and verify the complete existing
file under that coordination, derive the expected previous hash, validate the new
event, append one complete canonical line, flush, and request durable file sync before
reporting success. The exact cross-platform locking mechanism requires fresh-context
review during implementation; this document does not choose or implement one.

The public writer input must be a validated event object, not raw JSON text. It must not
offer update, delete, replace, rotate, repair, import, bulk append, or path parameters.

## 4. Canonical JSON specification

This section is the formal Phase 3 hash-canonicalization completion required before
the hash chain can be implemented.

### 4.1 Input domain

Canonicalization accepts one JSON-compatible object that has already passed the
audit-event schema. It rejects:

- non-string object keys;
- floating-point values, NaN, or infinity;
- byte strings or non-JSON Python objects;
- strings or keys that are not Unicode NFC;
- duplicate keys in decoded JSON input;
- additional fields rejected by the audit-event schema.

The future audit writer must decode every JSON record with
`json.loads(..., object_pairs_hook=...)` using a hook that rejects duplicate keys
before constructing a dictionary. The in-memory `hash_chain` module cannot recover
duplicate-key information after ordinary decoding, so writer-side rejection is
mandatory and must be tested before audit persistence is authorized.

The current audit-event schema needs strings, Booleans, null, arrays, objects, and may
use integers only if a later schema revision explicitly adds them. Floating-point
numbers remain forbidden until a separately reviewed canonical-number rule exists.

### 4.2 Serialization rules

Canonical bytes are produced recursively with these rules:

1. Object keys are sorted by Unicode code-point order after NFC validation.
2. No insignificant whitespace is emitted. Object separators are comma and colon
   bytes only.
3. Arrays retain their original order.
4. JSON strings use double quotes and standard JSON escaping for quotation mark,
   reverse solidus, and control characters. Printable non-ASCII characters are emitted
   as UTF-8 rather than ASCII `\u` escapes.
5. Boolean and null literals are lowercase JSON literals.
6. Integers, if later permitted by schema, use base-10 with no leading plus sign or
   leading zero; negative zero is forbidden.
7. The resulting JSON text is encoded as UTF-8 without BOM.
8. No trailing LF is included in the bytes being hashed. The LF belongs only to the
   physical JSONL record separator.

The normative Python-equivalent configuration for the supported value domain is
`sort_keys=True`, `ensure_ascii=False`, separators comma/colon without spaces, and
`allow_nan=False`, plus the explicit NFC and no-float checks above. This is a parameter
description, not implementation code.

### 4.3 Hash coverage

The entry hash is lowercase hexadecimal SHA-256 over the canonical UTF-8 bytes of the
entire validated audit-event object, including its `prev_entry_hash` field. No audit
field is excluded. The physical LF is excluded.

An `entry_hash` property is not added to the event because the current closed Phase 3
schema does not contain it. The next entry's `prev_entry_hash` stores the computed hash
of the preceding complete event. A verifier recomputes each entry hash while walking
the file.

Changing any covered field, including a safety flag, timestamp, identifier, status,
note, persistence label, or previous hash, changes the computed entry hash and breaks
the following link.

### 4.4 Genesis rule

For a nonexistent or zero-byte audit file, the first entry is the genesis entry and
must have `prev_entry_hash` equal to null. The hash of that complete genesis event is
then the required `prev_entry_hash` of the second entry.

Only the first entry may use null. A nonempty file whose first entry has a string
previous hash, or whose later entry has null, is invalid and must not be appended to.

## 5. Verification and broken-chain detection

Verification walks the physical file from the first byte to the final LF and fails
closed on any of the following:

- malformed UTF-8, BOM, CRLF, blank line, missing final LF, malformed JSON, or duplicate
  JSON key;
- event schema failure or additional property;
- invalid genesis rule;
- a `prev_entry_hash` that differs from the recomputed preceding entry hash;
- event reordering, insertion, deletion from the middle, or modification;
- duplicate `event_id` within the verified file;
- a persistence target other than `data/audit_dev.jsonl` for a persisted record;
- a persisted record with `preview_only` true or unauthorized safety posture.

The verifier returns structured metadata only: valid/invalid, entry count, computed
tail hash when valid, and a zero-based failing entry number plus non-secret reason when
invalid. It never repairs, rewrites, truncates, or appends.

### Hash-chain limitation

A self-contained append-only file cannot prove that a complete suffix was removed if
there is no separately trusted expected tail hash or entry count. It can detect middle
tampering and broken links, but a clean truncation after an earlier complete entry
still forms a valid shorter chain.

Phase 7 must not claim suffix-truncation detection unless the Owner separately approves
a trusted anchor mechanism. This design does not add a sidecar file, remote anchor, or
second write target. The verifier may accept an expected tail hash supplied by a
trusted caller for comparison, but it must not persist that anchor itself in Phase 7.

## 6. Rollback preview builder design

**2026-07-19 二次裁決（B 案）定案；implementation 本批實作。**

The rollback preview builder is a pure function. It accepts a validated `audit_event`
and the related validated N=1 `evidence_bundle` plus validated `result_message`, then
produces one object conforming to `rollback_event.schema.json`.

### 6.1 19 欄精確規格

| 欄位 | 來源／const |
|---|---|
| `schema_version` | 抄 `audit_event`；必須 == `result_message.schema_version`（不與 bundle 比對，bundle 屬 evidence contract 版本空間） |
| `message_type` | const `rollback_event` |
| `created_at` | 抄 `audit_event.created_at`（確定性，禁取當下時間） |
| `safety_flags` | 抄 `audit_event`；必須逐鍵 == `result_message.safety_flags` == 16 鍵安全 profile |
| `prev_entry_hash` | const null（07 §4 hash-chain 實裝前） |
| `execution_class` | 抄 `audit_event`；必須 == `result_message.execution_class` == `evidence_bundle.task.execution_class` == `AUTO` |
| `produced_by` | const `rollback-preview-builder` |
| `parent_task_id` | 抄 `audit_event`；必須 == `result_message.parent_task_id` |
| `role` | const `rollback_reviewer` |
| `rollback_id` | 確定性組字 `rollback-{source_audit_id}-{related_result_id}` |
| `task_id` | 抄 `audit_event`；必須 == `result_message.task_id` == `evidence_bundle.task.task_id` |
| `related_result_id` | 抄 `audit_event`；必須 == `result_message.result_id` |
| `source_audit_id` | 抄 `audit_event.audit_id` |
| `rollback_status` | const `NOT_REQUIRED` |
| `rollback_required` | const false |
| `preview_only` | const true |
| `rollback_note` | const `No rollback is needed because no execution or side effect occurred.` |
| `rollback_path` | const null |
| `reason` | 確定性組句 `Audit {source_audit_id} recorded a preview-only result with no external side effects.` |

### 6.2 Fail-closed 規則

- 三輸入 message/bundle 標識檢查；
- `audit_event.preview_only` 必 true、`audit_status == preview_audit_not_persisted`、
  `persistence_target == none`；
- `verify_bundle_hash` 必過；
- 副作用三重檢查：`result_message.external_side_effects == []`、
  `evidence_bundle.expected_side_effects == []`、
  `evidence_bundle.mock_result.external_side_effects_performed == false`；
- `evidence_bundle.mock_result.worker_dispatched`、`real_openclaw_called`、
  `queue_written`、`audit_trail_written` 四旗皆 false；
- result 三態檢查：`result_status == preview_result_not_executed`、
  `execution_mode == mock_only`、副作用空；
- task/result/audit 三方 id 鏈一致；
- 缺欄、型別錯、旗不符 → raise；
- 禁 mutate 輸入；
- builder 不得提供 token 或任何執行欄位。

The builder must not import the audit writer, queue, worker, OpenClaw, Hermes,
connector, subprocess, HTTP client, filesystem, or runtime modules. A rollback
preview is data for Owner review and never a callable rollback plan.

## 7. Proposed implementation boundaries

The future implementation package described by the governing plan may add only:

- `app/audit_writer_local.py`;
- `app/rollback_preview_builder.py`;
- tests and synthetic fixtures explicitly scoped to Phase 7;
- the one runtime data file `data/audit_dev.jsonl`, but only after the exact Owner
  authorization and only as an observed test artifact for Owner inspection.

It must not modify `app/main.py`, routes, worker startup, queue code, Blackboard runtime,
approval behavior, schemas, remote code, or connector code merely to make the writer
convenient. A required schema change is a new design/HOLD item, not an implicit edit.

## 8. Mandatory authorization gate

Before any implementation package creates, opens for append, or writes the audit file,
the Owner instruction for that session must contain this exact sentence:

`允許寫入 data/audit_dev.jsonl（local dev append-only）`

Paraphrases, references to this document, prior-session approval, general permission to
continue, or permission to modify repository code do not satisfy the gate. The
authorization applies only to that Phase 7 package and that one path. If the exact
sentence is absent, implementation status is HOLD before the writer is called.

## 9. Pre-implementation checklist

- [ ] Exact Owner authorization sentence is present in the active instruction.
- [ ] Work begins from the reviewed design commit, on a non-master branch.
- [ ] `data/audit_dev.jsonl` is resolved inside the repository and is the only runtime
      write target.
- [ ] No caller-controlled or environment-controlled audit path exists.
- [ ] Existing audit and rollback schemas pass their current tests unchanged.
- [ ] Canonicalization implements every rule in section 4 and rejects floats/non-NFC.
- [ ] Genesis, second-entry, multi-entry, tamper, reorder, deletion-from-middle,
      malformed-line, missing-final-LF, and duplicate-ID tests exist.
- [ ] Clean suffix truncation is not falsely claimed detectable without an expected
      trusted tail.
- [ ] Append validation and full-chain verification happen before any write.
- [ ] Failure before append leaves the file byte-for-byte unchanged.
- [ ] Concurrent append behavior is tested on the supported platform.
- [ ] Rollback builder remains pure, descriptive, and schema-valid.
- [ ] AST/import tests prove no queue, worker, dispatch, runtime, connector, HTTP, or
      subprocess path was added.
- [ ] A strongest-available fresh-context reviewer examines the complete write code and
      the exact git diff before merge.
- [ ] Owner inspects the actual development audit file before Phase 7 sign-off.

## 10. Fresh-context adversarial review checklist

The reviewer must start without the implementation author's hidden assumptions and
answer each item with file/line evidence:

1. Is `data/audit_dev.jsonl` literally the only possible write target?
2. Can an argument, environment variable, symlink, path traversal, import hook, or test
   override redirect the write outside the repository?
3. Does import, module initialization, validation, verification, or preview construction
   write anything?
4. Does the writer validate the complete existing chain before append?
5. Is canonicalization deterministic for every schema-permitted value and explicit
   about unsupported numeric/Unicode cases?
6. Is SHA-256 computed over the entire event including `prev_entry_hash`, excluding only
   the physical LF?
7. Is null accepted only for the genesis previous hash?
8. Does any failure or concurrent race permit a partial or unverified append?
9. Do tamper tests actually mutate the file under test and prove verification failure,
   rather than merely testing a helper with unrelated data?
10. Does any code claim to detect clean tail truncation without a trusted anchor?
11. Can audit success enqueue, dispatch, execute, call OpenClaw/Hermes/connectors, change
    task status, or grant permission?
12. Can rollback preview execute, import an executor, or supply executable commands?
13. Were any route, dashboard control, token, runtime, remote, production, queue, or
    Blackboard write paths added?
14. Does the actual diff exactly match the Owner-authorized files and path?
15. Is the exact authorization sentence present in the active implementation request?

Any "yes" to an unsafe capability, any unsupported claim, any second write target, or
any missing evidence makes the Phase 7 implementation HOLD.
