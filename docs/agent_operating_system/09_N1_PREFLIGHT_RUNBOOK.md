# Phase 9 N=1 Controlled Execution Preflight Runbook

Status: **PLANNING ONLY. Phase 9 execution is not authorized.**

This runbook prepares one future, Owner-supervised, harmless query-shaped
`openclaw agent` rehearsal. It creates no token, grants no permission, starts no
runtime, and authorizes no execution. The governing sources are
`05_VERIFIED_LONG_TERM_PLAN.md` Phase 9 and §6.8, plus the safety boundaries in
`01_SAFETY_BOUNDARIES.md`.

## 1. Fixed scope

- Exactly one N=1 harmless query call, with zero intended writes.
- One exact target, one exact parameter set, one approval packet, and one
  single-use token supplied by the Owner during a synchronous session.
- No connector, Google Sheets write, queue expansion, retry, follow-up action,
  second target, or background execution.
- A successful rehearsal is evidence for this single call only. It is not
  standing permission and does not unlock v1.1 or later actions.

The present repository is not ready to run this procedure: Phase 7 audit
persistence is incomplete, the approval-packet token remains structurally null,
and no Phase 9 execution gate has been authorized or implemented.

## 2. Preconditions: all must be true

### 2.1 Contract and evidence baseline

- [ ] Phase 3 Blackboard schemas and validator are complete and all tests pass.
- [ ] Phase 4 approval packet validates, names the exact target and action, and
      contains the matching dry-run/result references.
- [ ] Phase 5 evidence bundle validates and its hash recomputes exactly.
- [ ] Phase 7 audit writer, hash-chain verification, and rollback preview are
      complete and separately authorized; an actual audit-chain rehearsal has
      passed.
- [ ] The task, command, result, evidence bundle, approval packet, audit preview,
      and rollback preview reference one consistent task/command/result chain.
- [ ] All recorded expected side effects are empty for the harmless query.

If any Phase 7 item is incomplete, stop. The existence of this runbook does not
satisfy that prerequisite.

### 2.2 Owner and authorization gate

- [ ] The Owner is synchronously present for the entire rehearsal.
- [ ] The Owner instruction identifies the exact harmless query action and exact
      target; general permission or a prior-session instruction is invalid.
- [ ] The Owner supplies a fresh single-use token bound to this approval packet,
      exact action, exact target, and expiration window.
- [ ] The token has never been presented, consumed, logged, persisted in a
      fixture, or reused from another session.
- [ ] The approval decision and token are obtained only after the final evidence
      bundle is frozen and verified.

The current `single_use_execution_token: null` Phase 4 contract must not be
changed merely to make this runbook runnable. Phase 9 token design and its gate
require a separate implementation package and Owner-supervised review.

### 2.3 Runtime posture

- [ ] The action is classified `AUTO`, read-only, harmless, and limited to one
      query response.
- [ ] The runtime target, model/agent identifier, arguments, timeout, and output
      destination exactly match the reviewed packet and evidence.
- [ ] Worker dispatch, queue claim, connectors, writes, retries, and follow-ups
      remain disabled.
- [ ] A strong model leads the session; no side-effecting step is delegated to a
      subagent.
- [ ] The abort procedure in §4 is visible to the Owner before token issuance.

## 3. Execution-day sequence

Each gate is sequential. A later gate cannot repair a failed earlier gate.

1. **Freeze inputs.** Record immutable identifiers and hashes for the task,
   evidence bundle, approval packet, audit preview, and rollback preview.
2. **Revalidate.** Run all contract validators, evidence-hash verification, and
   audit-chain verification against the frozen inputs.
3. **Compare exact action.** Confirm the proposed runtime target and parameters
   are byte-for-byte or field-for-field identical to the reviewed packet.
4. **Owner checkpoint.** Display action, target, timeout, expected output,
   expected side effects, and abort rule. The Owner must remain present.
5. **Issue and bind token.** Only the Owner provides the fresh token. Bind it to
   the frozen packet/action/target and one attempt.
6. **Consume once.** Atomically mark the token consumed before allowing the one
   call. A consumed, missing, expired, mismatched, or previously seen token stops
   the procedure.
7. **Make one call.** Perform exactly the approved harmless query. No retry is
   permitted after success, timeout, exception, or ambiguous response.
8. **Return to deny-all.** Disable the execution gate immediately after the one
   attempt, regardless of outcome.
9. **Record and verify.** Append the authorized audit result, verify the chain,
   compare actual output/side effects with the packet, and produce the rehearsal
   report.
10. **Owner closeout.** The Owner reviews the report and explicitly decides
    whether the rehearsal is accepted. Acceptance does not authorize another
    call.

PLANNING ONLY, NOT AUTHORIZED

```text
IF any precondition is false: STOP
IF evidence, packet, target, or parameters differ: INVALIDATE TOKEN; STOP
IF token is absent, expired, consumed, or mismatched: STOP
ALLOW exactly one approved query attempt
DENY execution immediately after that attempt
NEVER retry without a new packet and a new Owner token
```

## 4. Abort and rollback procedure

### 4.1 Abort before the call

Invalidate the token and stop if any of the following occurs:

- the Owner disconnects or cannot confirm the displayed action;
- a schema, bundle hash, audit chain, identifier, target, parameter, timeout, or
  safety flag differs from the reviewed evidence;
- Phase 7 evidence is missing or its audit writer is not authorized;
- any write, connector, dispatch, queue, follow-up, or second-call capability is
  enabled;
- the token cannot be proven fresh, exact-scope, unexpired, and unused.

Do not edit the packet in place. Produce fresh evidence and a new packet before a
future attempt.

### 4.2 Stop during or after the call

- On timeout, exception, ambiguous status, or partial output: consume/invalidate
  the token, return to deny-all, record the observed state, and stop. No retry.
- If any unexpected external side effect or write is observed: freeze all
  execution, preserve evidence, notify the Owner, and follow only the rollback
  path that was reviewed before the call.
- For the intended v1.0 harmless query, the expected rollback is `NOT_REQUIRED`.
  An observed side effect contradicts the approved action and is an incident,
  not permission to improvise a rollback command.
- If the reviewed rollback fails or cannot be verified: keep execution frozen,
  require manual Owner handling, and record the incident in the lessons/audit
  process before any new rehearsal is considered.

## 5. Post-run acceptance checklist

- [ ] Exactly one token-consumption attempt is recorded.
- [ ] Token replay is rejected in a controlled negative check that makes no
      second runtime call.
- [ ] Exactly one approved query attempt occurred; no automatic retry occurred.
- [ ] The runtime target and parameters match the frozen evidence and packet.
- [ ] Actual external side effects are empty.
- [ ] The execution gate returned to deny-all after the attempt.
- [ ] The audit entry is present and the complete hash chain verifies.
- [ ] The rollback result is recorded as `NOT_REQUIRED`, or an unexpected-side-
      effect incident is frozen for Owner handling.
- [ ] The rehearsal report contains the complete evidence bundle, approval
      packet, token issuance/consumption metadata without the secret token value,
      execution output, audit-chain result, post-run validation, and rollback
      outcome.
- [ ] The Owner has reviewed the report and issued a closeout decision.
- [ ] No text in the closeout is treated as permission for another call or a
      broader whitelist.

## 6. Hard-stop reminder

This document is a checklist, not an execution mechanism. It must never be
imported, parsed, or treated as dispatch input. Implementing the token gate,
calling OpenClaw, enabling runtime execution, or writing an audit record each
requires its separately authorized phase and review.
