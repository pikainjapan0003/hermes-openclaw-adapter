# Phase 7 Local Audit Writer — Implementation Package Draft

**未取得 Owner 逐字授權句前，本檔不得被當成派工單使用**

Status: **PLANNING ONLY, NOT AUTHORIZED — DRAFT FOR FUTURE OWNER REVIEW**

Authority source: `07_AUDIT_WRITE_DESIGN.md`. This draft compresses that
approved design into a reviewable future package shape. It does not create a
writer, open a file, authorize persistence, change Phase 7 status, or satisfy
the mandatory gate merely by quoting it.

## 1. Activation gate

Before anyone may use the package below, the active Owner instruction for the
implementation session must contain this exact sentence:

`允許寫入 data/audit_dev.jsonl（local dev append-only）`

The sentence in this planning document has no operative effect. A paraphrase,
prior session, generic “continue”, nightly-batch authority, Fable 5 review, or
reference to this draft is insufficient. If the exact sentence is absent, the
package status is `HOLD` before any code or file operation.

## 2. Proposed future package identity

```text
PLANNING ONLY, NOT AUTHORIZED
[PHASE] Phase 7 — Local Audit Writer
[SCOPE] one local append-only JSONL audit file
[EXECUTION_CLASS] OWNER_APPROVAL
[REQUIRED_REVIEW] strongest-available fresh-context adversarial review
```

This is an implementation package only after §1 is satisfied. It is never an
execution/dispatch package and does not authorize Phase 9.

## 3. Exact whitelist

Allowed additions only:

- `app/audit_writer_local.py` — pure validation plus the one append boundary;
- `tests/test_audit_writer_local.py` — unit, failure, concurrency, and
  adversarial tests;
- `fixtures/audit_writer_local/*.jsonl` — synthetic input fixtures only when
  mechanical tests need them; and
- `data/audit_dev.jsonl` — the sole runtime observation file, created/appended
  only during the explicitly authorized local rehearsal and then inspected by
  Owner.

Allowed minimum existing-file modification: none. If implementation discovers
that a schema, validator, dependency, `app/main.py`, route, queue, worker,
approval behavior, token, runtime, remote component, or connector must change,
the package becomes HOLD and returns for a new design/Owner decision.

Forbidden targets include every other `data/` path, caller-selected paths,
environment-selected paths, production/shared storage, logs as a fallback,
temporary side-channel persistence, and a second audit file.

## 4. Required writer contract

The future writer must:

1. accept one in-memory `audit_event` mapping, never a command or arbitrary
   serialized line;
2. validate the exact closed `audit_event` schema before touching the target;
3. resolve an internal repository constant to exactly
   `data/audit_dev.jsonl` and reject symlinks, traversal, path overrides, and a
   repository-root mismatch;
4. decode the complete existing file as UTF-8 JSONL with duplicate-key
   rejection and require a final LF when non-empty;
5. reject malformed lines, schema-invalid events, duplicate audit/event IDs,
   a broken genesis rule, a broken `prev_entry_hash`, and unsupported canonical
   values;
6. verify the complete chain before constructing the append candidate;
7. require the new entry's `prev_entry_hash` to equal the verified current tail
   hash, or `null` only for a genuinely empty genesis file;
8. calculate bytes by `07_AUDIT_WRITE_DESIGN.md` §4: dict root, NFC strings and
   keys, sorted keys, compact JSON, UTF-8, no float, no trailing LF inside the
   hash, and SHA-256 over the entire event including `prev_entry_hash`;
9. append exactly one canonical JSON line plus one physical LF, with no reopen,
   rewrite, repair, rotate, truncate, retry, or second event;
10. use an explicit supported-platform exclusive append/lock strategy and
    re-check the tail inside that protection immediately before append;
11. verify the complete resulting file after append and return structured,
    payload-free evidence; and
12. stop on every ambiguous outcome. No automatic retry or compensating write
    is permitted.

Import, module initialization, input validation, preview generation, chain
verification, and failure before the append boundary must perform zero writes.

## 5. Required tests and acceptance

The future package must provide ordinary passing tests for:

- absent file as genesis and valid first LF-terminated record;
- valid second and multi-entry append;
- canonical bytes/hash parity with existing golden vectors;
- reordered input keys producing the same canonical bytes;
- float, non-NFC value/key, duplicate JSON key, non-object root, and non-JSON
  type rejection;
- tampered content, reordered entries, middle deletion, later null predecessor,
  wrong predecessor, duplicate IDs, malformed line, blank line, invalid UTF-8,
  and missing final LF rejection;
- clean suffix truncation being explicitly **not detectable** without a trusted
  expected tail, so no test claims otherwise;
- target path constant, repository containment, symlink rejection, and absence
  of argument/environment path overrides;
- before-append failures leaving existing bytes exactly unchanged;
- simulated append failure/ambiguous result causing no retry;
- two concurrent append attempts on each supported platform producing either
  two valid serialized entries or one structured rejection, never corruption;
- append-result chain verification; and
- payload/secret/path markers absent from returned errors.

Static/AST tests must prove no import or call path reaches queue, claim,
worker, dispatch, OpenClaw, Hermes, connector, HTTP, subprocess, dashboard,
route registration, token issuance, task-state mutation, or follow-up creation.

Final mechanical acceptance requires:

```text
python -m pytest -p no:cacheprovider -q
python -m mypy
git diff --check
```

The report must also show the exact target resolution, pre/post bytes and
chain verification, full diff/stat, allowed-file inventory, and that no other
tracked or untracked runtime artifact was created.

## 6. Fresh-context adversarial review checklist

The reviewer must start from the implementation commit without relying on the
author's explanation and answer with file:line evidence:

1. Is there literally one writable target?
2. Can an argument, environment value, symlink, junction, traversal,
   repository alias, fixture, or test monkeypatch redirect it?
3. Does import or any pre-append phase mutate a byte?
4. Is every existing line schema-valid and the complete chain verified?
5. Are duplicate keys rejected before a Python mapping erases evidence?
6. Are canonicalization and hash coverage identical to §4 and golden vectors?
7. Is `null` predecessor accepted only for true genesis?
8. Can concurrent state change between tail verification and append?
9. Can a partial/ambiguous append trigger retry or silent repair?
10. Do tamper tests mutate the actual file under test rather than an unrelated
    helper object?
11. Is clean tail truncation ever falsely claimed detectable?
12. Can success enqueue, dispatch, execute, call a tool/model, change state, or
    grant a next-step permission?
13. Can rollback preview execute or supply a command string?
14. Were route, token, runtime, remote, production, queue, and Blackboard write
    surfaces left unchanged?
15. Does the diff exactly match §3 and does the active instruction contain the
    exact §1 sentence?

Any unsupported claim, second target, redirection path, missing negative test,
or unsafe “yes” makes the package HOLD.

## 7. Rollback and recovery steps

These steps describe recovery for the future implementation package; they are
not authorized commands now.

1. Before rehearsal, record the reviewed base commit and confirm a non-master
   branch and clean authorized diff.
2. If code/tests fail before runtime rehearsal, do not create the audit file;
   correct only inside the future whitelist or abandon the package commit.
3. If the authorized append fails before any bytes change, verify byte identity
   and stop; never retry automatically.
4. If bytes changed or outcome is ambiguous, freeze the worktree and exact file
   bytes, run read-only chain diagnosis, and report to Owner. Do not truncate,
   rewrite, delete, “repair”, or append a compensating event.
5. Git rollback of implementation code uses a reviewed revert of the package
   commit. Runtime audit bytes are evidence and must not be erased by Git or a
   cleanup helper.
6. Phase 7 stays incomplete until fresh-context review passes and Owner inspects
   the actual local development file and closes out the package.

## 8. Hard stop

Even a completely green Phase 7 package authorizes no Phase 9 token, Worker
claim, dispatch, OpenClaw call, Hermes runtime, connector, remote transport,
Blackboard writer, v1.1 write, or follow-up. Completion returns to deny-all and
waits for the separate Owner-present Phase 9 process.

**未取得 Owner 逐字授權句前，本檔不得被當成派工單使用**
