# Phase 9 Single-Use Token Design

Status: **PLANNING ONLY. NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

Date: 2026-08-03  
Scope: one Owner-present N=1 harmless-query attempt. A token authorizes neither
a worker nor a general action class. It is valid only when every independently
checked gate condition is green.

## 1. Non-negotiable properties

The future mechanism must satisfy all of these at the same time:

1. **Owner-originated authority.** A model cannot mint authority for itself.
2. **Unpredictable secret.** A token cannot be a date, task id, packet id, or
   approval word.
3. **Exact binding.** It binds one approval packet, action, target, frozen input
   set, expiration window, and attempt counter.
4. **Consume before call.** The durable burn decision happens before OpenClaw is
   allowed to start.
5. **One attempt, not one success.** Timeout, exception, ambiguous completion,
   or Owner abort still spends the token.
6. **No plaintext persistence.** Fixtures, logs, audit records, reports, argv,
   and error messages contain only a digest/reference, never the raw token.
7. **Fail closed.** Missing, invalid, expired, mismatched, or consumed means
   deny; the gate does not repair, refresh, or retry.
8. **Restart-safe replay denial.** A process restart cannot make a consumed
   token usable again.
9. **Concurrency-safe.** Two simultaneous presentations produce at most one
   winner and at most one OpenClaw start.
10. **No standing permission.** The mechanism returns to deny-all after the
    attempt. A second action needs a new packet and new Owner token.

The raw token is authentication material, not Blackboard content. The present
approval-packet field remains structurally `null` until the Owner chooses and
authorizes a Phase 9 schema design.

## 2. Who produces the token — three options

| Option | Owner experience | Strengths | Weak-model / security risks | Verdict |
|---|---|---|---|---|
| T-A — Owner invents and types it | Owner creates a fresh secret and places it in the synchronous instruction | Authority visibly originates with Owner; no generator trust | Human entropy and reuse are likely; raw secret may enter chat history; hard to prove it was fresh | Not recommended |
| T-B — System generates once, Owner repeats it | After all evidence is frozen, an authorized local generator shows one random token once; Owner copies it into the exact execution instruction | Strong entropy plus explicit Owner act; easy binding to displayed packet digest | Generator/display must be separately authorized; clipboard/chat exposure; model must not treat generation as approval | **Recommended, subject to Owner decision** |
| T-C — System challenge, Owner confirms a derived approval response | System displays a random challenge and frozen-action summary; Owner returns a response produced by an approved authenticator/process | Raw bearer token need not be typed; can strongly bind human confirmation | Highest complexity; authenticator, key custody, and recovery become new systems; weak models may confuse challenge display with authorization | Defer beyond N=1 unless Owner prefers it |

For T-B, “system generates” is not self-authorization. Generation may occur only
after a separate Owner instruction authorizes that exact local generator step.
The token becomes active only when the Owner returns it in the synchronous
instruction that names the exact packet and action.

## 3. Binding contract

The token verifier should compare a canonical binding record, not free text.
The proposed binding fields are:

| Binding field | Required meaning | Mismatch disposition |
|---|---|---|
| `approval_packet_id` | Exact accepted packet identifier | burn presented session token; deny |
| `approval_packet_hash` | Canonical digest of the frozen packet excluding raw token material | burn; deny |
| `evidence_bundle_hash` | Already verified Phase 5 bundle digest | burn; deny |
| `action_hash` | Canonical digest of exact action, target, arguments, timeout, agent/session posture | burn; deny |
| `rehearsal_id` | One Owner-present session identifier | deny tokens from any other session |
| `issued_at` / `expires_at` | Short UTC issuance window; no clock rollback tolerance | expired or indeterminate clock means deny |
| `attempt_number` | Constant `1` for N=1 | any other value means deny |
| `nonce_digest` | Salted/HMAC digest of the raw token; never the raw value | mismatch means deny without revealing which component failed |
| `contract_version` | Exact Phase 9 token-binding version | unknown/downgraded version means deny |

`action_hash` must include every byte/field that can affect the runtime call.
Changing a prompt space, target, timeout, agent id, session id, output mode, or
capability posture invalidates the binding. The verifier must not normalize an
unexpected runtime value to make it match.

## 4. “Use once” persistence — three options

| Option | Mechanical rule | Crash/restart behavior | Risks | Verdict |
|---|---|---|---|---|
| B-A — Separate token marker file | Under an exclusive lock, create/append a consumed digest before the call; existing digest denies | Can be restart-safe if durable and atomic | Introduces a new persistent write target and its own chain/tamper/permission policy; currently unauthorized | Viable only with a new explicit path authorization |
| B-B — Memory claim plus audit result | Atomically claim token in process memory, then append an audit record | Memory claim disappears on restart; audit append races/crashes can leave ambiguity | Cannot prove replay denial after restart unless audit is authoritative; process-local locks do not cover another process | Insufficient alone |
| B-C — Hash-chain burn event | Under one gate-level lock, scan/verify the Phase 7 chain, append a redacted burn event, fsync, reverify, and only then allow the call | A committed burn survives restart; crash after burn safely wastes the token | Existing audit schema does not yet define token-digest/binding/burn fields; uniqueness and atomic gate coordination need a separately authorized contract | **Recommended architecture, not yet implementable** |

The recommended B-C order is deliberately fail-safe: `verify chain → validate
binding → append burn → fsync → verify burn → one call`. A crash anywhere before
the verified burn causes no call. A crash after the burn causes no retry. The
burn record stores only a digest, binding hash, disposition, and timestamps.

The Phase 7 writer validates the current `audit_event` schema and hash chain,
but that does not automatically make it a token ledger. Before implementation,
the Owner must approve a machine contract able to represent the burn without
free-text encoding or raw-token leakage.

## 5. Token lifecycle and failure semantics

| State | Entry condition | Allowed next state | Runtime allowed? |
|---|---|---|---|
| `ABSENT` | default / no fresh Owner token | `ISSUED` only through chosen authorized ceremony | No |
| `ISSUED` | strong random token exists but Owner has not returned it | `PRESENTED` or `EXPIRED` | No |
| `PRESENTED` | Owner instruction supplies it with exact frozen identifiers | `BURNED_DENY` or `BURNED_ATTEMPT` | No |
| `BURNED_DENY` | any binding/preflight/Owner-presence failure | terminal | No |
| `BURNED_ATTEMPT` | burn is durably committed immediately before the call | terminal after at most one start | At most one start |
| `EXPIRED` | expiration reached before verified burn | terminal | No |

There is no `RETRYABLE` state. “Invalid,” “expired,” and “already used” return a
single fail-closed denial class to callers; detailed reason codes may be visible
to the Owner but must not reveal token material. A known freshly issued token is
burned when a later gate fails. An unknown or forged string has no authoritative
token record to burn, but its presentation is denied and may be recorded using
only a non-reversible fingerprint.

## 6. Replay tests that count

A token is not “single-use” merely because a function returns an error twice.
The implementation package must include all of these mechanical proofs:

1. **Sequential replay:** first exact presentation results in one durable burn
   and exactly one fake-executor start; a second presentation of the same raw
   token and same packet returns consumed/deny, while executor start count stays
   exactly one.
2. **Concurrent replay:** two processes or independently locked contenders race
   the same token; exactly one can commit the burn and the executor start count
   is zero or one, never two.
3. **Restart replay:** after the first burn, reconstruct the gate in a fresh
   process and present the same token; denial must come from durable evidence.
4. **Crash boundary:** simulate crash after burn and before executor start;
   restart must deny and must not “finish” the missing call.
5. **Mismatch:** same token with changed packet/action/target/timeout is denied
   before any runtime start and cannot be reused with the original input later.
6. **Expiration:** advancing a controlled clock past expiry denies without call;
   clock uncertainty also denies.
7. **Redaction:** raw token is absent from audit bytes, exceptions, test output,
   reports, argv, environment snapshots, and fixtures.

The controlled test executor must be an in-memory counter, never OpenClaw. The
replay assertion is: **two presentations, one durable burn identity, at most one
executor invocation, and zero real runtime calls.**

## 7. Owner decision record

Token-production option (`T-A`, `T-B`, or `T-C`): ____________________

Burn/persistence option (`B-A`, `B-B`, or `B-C`): ____________________

Maximum validity window: ____________________

Owner notes / required changes: ____________________________________________

Decision date and explicit implementation authorization: ____________________

Until every applicable field is filled by the Owner and converted into a
separate implementation brief, the token remains `null`, the gate remains
absent, and Phase 9 remains blocked.

