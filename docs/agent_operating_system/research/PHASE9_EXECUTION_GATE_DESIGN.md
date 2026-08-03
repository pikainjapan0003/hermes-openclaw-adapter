# Phase 9 N=1 Execution Gate Design

Status: **PLANNING ONLY. NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION.**

Date: 2026-08-03  
Scope: a future one-shot gate for one Owner-present harmless query. This design
creates no module, route, token, runtime permission, or OpenClaw call.

## 1. One responsibility

The gate has one responsibility: after independently proving that the frozen
packet, token binding, preflight, audit readiness, Owner presence, and exact
runtime action all match, it may permit **at most one process start**. It does
not plan, edit evidence, choose a command, repair a token, claim a queue item,
dispatch a worker, interpret approval as authority, or retry.

The default answer is deny. The only allowlist member is the exact action hash
that the Owner sees and authorizes in that synchronous session. An action class,
tool name, agent name, or prior successful rehearsal is not an allowlist.

## 2. Explicit non-goals and separation

- The N=1 call does **not** enter `QueueStore`, become `queued`, call
  `claim_next`, start `worker.py`, or use dashboard approval routes.
- Existing `approval_security_gate_v0_7.py` and `security_gates_v0_7.py` are
  historical/pure decision helpers; they are not a Phase 9 execution gate.
- Existing mock gateway and dry-run bridge remain mock evidence producers. They
  cannot be switched into a real mode.
- Existing legacy OpenClaw paths in `app/main.py` are not automatically trusted
  or wired to this gate. The installed CLI contract remains pending the
  Owner-present checks in `OPENCLAW_CLI_FACTS.md`.
- The gate never accepts a result message as follow-up permission.
- No HTTP route is required for N=1. The future authorized runner is a local,
  foreground, single-shot session controlled by the Owner.

## 3. Frozen input set

Before token issuance, the coordinator freezes and hashes this set:

| Input | Required checks |
|---|---|
| Task and command envelope | valid current contracts; one task/command id chain; zero write posture |
| Evidence bundle | schema valid; bundle hash independently recomputed; mock result says no real call, dispatch, queue, audit, or external side effect |
| Approval packet | valid accepted version; decision and timestamp final; exact target/action/timeout match frozen command |
| Rollback preview | valid descriptive record; N=1 outcome is `NOT_REQUIRED` unless an incident is observed |
| Phase 7 audit chain | complete and valid at the exact pre-call tail hash |
| CLI facts sheet | executable/interface/output/timeout/state-write facts verified with no unknowns |
| Owner session | synchronous presence, explicit exact-action instruction, fresh token ceremony selected by Owner |
| Capability posture | worker, queue, connector, follow-up, write tools, background mode, and second-call paths disabled |

Every field that can change argv or behavior belongs in the canonical action
hash. Runtime values are compared field-for-field or byte-for-byte immediately
before the process start. The gate must not coerce, default, trim, repair, or
substitute a mismatching value.

## 4. State machine

| State | Meaning | Permitted transition |
|---|---|---|
| `DENY_ALL` | Initial and normal state; no one-shot capability exists | to `CHECKING` only inside an explicitly authorized Owner-present runner |
| `CHECKING` | Revalidating frozen artifacts, CLI facts, posture, and Owner presence | to `BURNING` if every check is green; otherwise `CLOSED_DENY` |
| `BURNING` | Token binding is validated and a durable pre-call burn is appended and verified | to `ONE_SHOT_READY` only after fsync and chain verification; otherwise `CLOSED_DENY` |
| `ONE_SHOT_READY` | An in-memory capability exists for the exact action hash and attempt 1 | to `STARTING` through one atomic compare-and-swap; any other use closes deny |
| `STARTING` | The one executor start is being issued | immediately to `CLOSED_DENY`, whether start succeeds, throws, or is ambiguous |
| `CLOSED_DENY` | Terminal state for this runner/session | no transition; another attempt needs a new process, packet, and token |

There is deliberately no `RETRY`, `REOPEN`, `SUCCESS_READY`, or “return to
armed” transition. “One attempt” is consumed when the start boundary is crossed,
not when a successful result arrives.

## 5. Gate decision order

The future implementation must preserve this order:

1. Begin in `DENY_ALL`; assert no inherited capability or enabled global flag.
2. Load immutable copies of the frozen artifacts; validate every contract.
3. Recompute bundle, packet, action, and audit-tail hashes independently.
4. Prove the exact Phase 9 contract/version is accepted; v1 Phase 4 packets
   cannot carry a token.
5. Prove Owner synchronous presence and exact instruction for this action.
6. Verify token freshness, expiry, session, packet, action, target, and attempt
   bindings without logging the raw token.
7. Recheck all preflight conditions and the CLI facts sheet at the last possible
   point before burn.
8. Acquire the gate/token-audit coordination lock, recheck the chain and absence
   of the token digest, append the pre-call burn/attempt event, fsync, and verify.
9. Create one process-local capability containing only the action hash and a
   single atomic use bit.
10. Compare the prospective argv/capability posture to the frozen action one
    final time.
11. Atomically consume the use bit and start exactly one foreground process.
12. Enter `CLOSED_DENY` in an unconditional cleanup boundary before interpreting
    the runtime result.
13. Append the post-attempt audit event and produce the report. A post-audit
    failure does not reopen or retry the call.

If any step cannot be proven, stop. A later green check cannot repair an earlier
failure. A token that was validly issued for the session is burned when a later
check fails, so “fix and retry” is structurally impossible.

## 6. Audit contract before and after the call

### 6.1 Required pre-call record

The pre-call record is both evidence and the durable replay barrier. It must be
successfully appended and chain-verified before runtime start. It should contain:

- rehearsal id, event id, timestamp, and prior audit hash;
- approval-packet id/hash and evidence-bundle hash;
- action hash, exact target classification, timeout, and attempt number `1`;
- a non-reversible token digest/reference, never the raw token;
- Owner-session confirmation reference without chat content or identity secret;
- all preflight condition ids and their frozen green result digest;
- transition `CHECKING → BURNING → ONE_SHOT_READY`;
- zero intended business side effects and the reviewed abort rule.

### 6.2 Required post-attempt record

The post record is appended after the gate is already terminally disabled. It
should contain:

- the pre-call event id and token-burn reference;
- whether process start was attempted and whether it was observed to begin;
- completion class: success, nonzero, timeout, exception, Owner abort, or
  ambiguous; plus exit/signal metadata where available;
- stdout/stderr/result digests and bounded redacted summaries, not raw secrets;
- duration, output-format validation result, and post-run filesystem diff result;
- observed external/business side effects, expected to be empty;
- transition to `CLOSED_DENY` and proof that no second start capability exists;
- audit-chain verification result and rollback disposition (`NOT_REQUIRED` for
  the intended harmless call, otherwise incident/HOLD).

The current `audit_event` schema was designed before these structured token and
attempt fields. Free-text packing is not acceptable. A separately approved
machine contract is a prerequisite for implementation.

If the pre-call audit append fails, no process starts. If the post-call append
fails, the call remains spent and disabled; the Owner sees an audit incident,
and no fallback file or automatic retry is permitted.

## 7. Mechanical return to all-disabled

“Automatically disabled” must be proven by construction, not by a final log
message:

1. There is no persisted `enabled=true` setting. Each authorized runner begins
   in deny-all and receives one in-memory capability only after durable burn.
2. The capability carries the exact action hash and an atomic one-use bit. It
   cannot authorize a different argv or a second start.
3. The start boundary consumes the use bit before process creation.
4. An unconditional cleanup boundary sets the runner terminal state to
   `CLOSED_DENY` on success, exception, cancellation, timeout, or Owner stop.
5. The durable burn prevents a new process from recreating the capability for
   the same token.
6. Worker, queue, connectors, write tools, follow-up, and background scheduling
   remain independently disabled; gate closure does not rely on their goodwill.
7. A post-run assertion probes the gate with the same token/action using a fake
   executor and proves denial with executor count unchanged.

Required adversarial tests include exception at every transition, concurrent
presentations, crash after burn, crash at process start, cancellation during
output collection, post-audit failure, and restart replay. All use a fake
executor; none invokes OpenClaw.

## 8. Authorization dependencies and HOLD conditions

Implementation remains HOLD until the Owner has separately selected and
authorized:

- token production and durable burn contract;
- Phase 9 packet/token schema strategy;
- structured pre/post audit-event representation;
- exact OpenClaw CLI facts and the one harmless action;
- allowed operational filesystem effects, if any;
- implementation paths and the one-time execution session; and
- an independent high-risk review plan.

This document is a design proposal. Reading, approving, or merging it does not
arm a gate, issue a token, authorize audit appends, or permit an OpenClaw call.

