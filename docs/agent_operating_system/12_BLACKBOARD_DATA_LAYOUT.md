# Blackboard Local Data Layout Design

Status: **PLANNING ONLY, NOT AUTHORIZED**

This document proposes a local N=1 board layout and documents the read-only helper
`app/blackboard_board_reader.py`. It does not authorize creation of the proposed
`data/` tree, Blackboard mutation, queue writes, audit persistence, runtime wiring,
remote synchronization, dispatch, or execution.

## 1. Scope

The first layout is deliberately small: one synthetic board, one worker chain, ten
Blackboard message contracts, and at most one entry of each message type. It is not a
multi-worker journal, database, queue, event bus, or concurrency mechanism.

The reader accepts an already-existing directory chosen by its caller. It reads only
the immediate files in that directory and never creates, repairs, sorts on disk,
renames, deletes, or writes any entry.

## 2. Proposed directory tree

The following tree is a design target only and is not created in this phase:

- `data/blackboard_dev/boards/<board_id>/`
  - `0001_task_draft.json`
  - `0002_annotation.json`
  - `0003_approval_readiness.json`
  - `0004_owner_decision.json`
  - `0005_worker_dry_run.json`
  - `0006_openclaw_command_envelope.json`
  - `0007_result_message.json`
  - `0008_approval_packet.json`
  - `0009_audit_event.json`
  - `0010_rollback_event.json`

`<board_id>` must eventually receive a separately reviewed syntax and leak policy.
The reader exposes only the final directory name as `board_name`; it does not return
the caller's absolute path.

## 3. Filename contract

Each immediate entry uses `NNNN_message_type.json`:

- `NNNN` is a four-digit decimal sequence used only for deterministic read order;
- `message_type` must be one of the ten keys in
  `app.blackboard_validators.SCHEMA_FILES`;
- the sequence and message type are each unique inside one N=1 board;
- the filename-selected type must agree with the record's `message_type` through
  normal schema validation;
- symlinks, nested directories, unexpected extensions, malformed JSON, duplicate
  sequences, and duplicate message types fail closed;
- an empty existing directory is a legal empty board;
- the reader does not recursively follow any directory.

Sequence is presentation order, not hash-chain order, execution order, approval, or
dispatch permission. `prev_entry_hash` remains governed by its message contract and
Phase 7 rules.

## 4. Ten-schema mapping

| Message type | Schema | N=1 purpose |
|---|---|---|
| `task_draft` | `docs/schemas/blackboard/task_draft.schema.json` | Initial synthetic task proposal |
| `annotation` | `docs/schemas/blackboard/annotation.schema.json` | Safety annotation |
| `approval_readiness` | `docs/schemas/blackboard/approval_readiness.schema.json` | Owner-readiness preview |
| `owner_decision` | `docs/schemas/blackboard/owner_decision.schema.json` | Inert decision data |
| `worker_dry_run` | `docs/schemas/blackboard/worker_dry_run.schema.json` | Non-executing worker preview |
| `openclaw_command_envelope` | `docs/schemas/blackboard/openclaw_command_envelope.schema.json` | Mock command envelope |
| `result_message` | `docs/schemas/blackboard/result_message.schema.json` | Synthetic result data |
| `approval_packet` | `docs/schemas/blackboard/approval_packet.schema.json` | Offline Owner review packet |
| `audit_event` | `docs/schemas/blackboard/audit_event.schema.json` | Non-persisted audit preview |
| `rollback_event` | `docs/schemas/blackboard/rollback_event.schema.json` | Descriptive rollback preview |

The layout does not add an eleventh contract, manifest, lock file, tail anchor, token
file, or metadata sidecar.

## 5. Reader result contract

`read_blackboard_board(directory)` returns an in-memory summary:

- `valid`: false if any directory, filename, decode, inventory, or schema error exists;
- `board_name`: the supplied directory's final component only;
- `entry_count`: number of decoded entries that reached schema validation;
- `entries`: filename, sequence, selected type, validation result, and the message only
  when schema-valid;
- `errors`: non-secret directory/file error codes and messages.

Invalid payload contents are not echoed. A malformed or schema-invalid file cannot
be treated as a partial success merely because other entries validate.

## 6. Read and validation boundary

The helper:

1. verifies that the supplied path already exists and is a directory;
2. enumerates only immediate children in deterministic filename order;
3. rejects symlinks and unexpected entries;
4. decodes UTF-8 JSON with `json.loads`;
5. selects the expected contract from the filename allowlist;
6. calls `validate_blackboard_message` for every decoded entry;
7. returns structured data in memory.

It does not import `app.main`, queue, worker, OpenClaw, Hermes, connector, HTTP,
subprocess, or remote modules. It has no mutation, persistence, repair, callback,
watcher, polling, or execution behavior.

## 7. Git flow

Only code, schemas, documentation, tests, and explicitly synthetic fixtures belong in
normal Git review. The proposed runtime tree under `data/blackboard_dev/` must remain
absent until a new Owner instruction explicitly authorizes its creation and retention.

If a future board is promoted to a regression fixture, a separate reviewed package
must copy a redacted, schema-valid snapshot into a fixture-specific path, prove that it
contains no secrets or real payload, and commit that fixture explicitly. Runtime board
files must never be swept into Git by a broad add command.

GitHub-to-Replit transport, pull schedules, remote authentication, and shared-backend
storage remain outside this design. A committed fixture is test evidence, not a live
Blackboard and not permission to create a remote receiver.

## 8. Future HOLD items

Before creating the proposed `data/` layout, Owner review must settle:

- the exact `board_id` syntax and whether it may contain task identifiers;
- data retention and deletion authority;
- whether multiple entries of one message type are required;
- locking and concurrency if more than one writer ever exists;
- full-chain ordering versus filename presentation ordering;
- leak scanning and promotion rules for synthetic Git fixtures;
- authorization for the exact local directory and any write path.

Until those items and an explicit Owner instruction exist, only the read-only helper
and tmp-path synthetic tests are in scope.
