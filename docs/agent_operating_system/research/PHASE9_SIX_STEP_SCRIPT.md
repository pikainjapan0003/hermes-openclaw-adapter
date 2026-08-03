# Phase 9 N=1 Owner-Present Six-Step Script

Status: **PLANNING ONLY. NOT AUTHORIZED FOR EXECUTION OR PERSISTENCE.**

Date: 2026-08-03  
Purpose: the exact reading order for the future day on which the Owner may
authorize one harmless, query-shaped OpenClaw attempt. This is not a runnable
script and contains no verified CLI command.

## 1. Scope in one sentence

Freeze evidence, obtain one exact Owner decision and fresh token, permit one
foreground query attempt, record it in the Phase 7 audit chain, verify that
nothing else happened, and rehearse the pre-reviewed no-op rollback conclusion.

“Zero write” means zero intended business/target mutation by the OpenClaw action.
Control-plane evidence and authorized audit appends are separate, explicit
records. Any OpenClaw cache/session/state write remains a Phase 9 fact to verify
and authorize; it is not silently exempt.

## 2. Roles

| Role | What this role may do that day | What it may not do |
|---|---|---|
| Owner | remain synchronously present; inspect facts/evidence; choose schema/token design beforehand; issue exact action/token instruction; say stop; sign or reject closeout | delegate the live decision to a model; give broad/standing permission |
| Preflight coordinator | display evidence and blockers; run read-only validators; compare frozen hashes; stop on mismatch | mint authority, edit failed evidence in place, invoke OpenClaw |
| Future authorized one-shot runner | after all gates pass, burn token, start one exact foreground process, close deny-all, capture bounded result | use worker/queue/dispatch, retry, alter argv, run in background |
| Independent reviewer | observe logs/hashes and verify post-run evidence | become the executor or reinterpret success as a second authorization |

No side-effecting step is delegated to a subagent.

## 3. Proposed artifact map — not authorized yet

The future Phase 9 implementation brief must explicitly authorize any path it
uses. This document proposes, but does not create, the following session folder:

| Artifact | Proposed location | Secret rule |
|---|---|---|
| frozen CLI facts/preflight report | `data/phase9_rehearsal/<rehearsal_id>/00-preflight.json` | no credentials or raw token |
| evidence bundle | `data/phase9_rehearsal/<rehearsal_id>/01-evidence-bundle.json` | existing evidence allowlist only |
| inert v1 approval packet | `data/phase9_rehearsal/<rehearsal_id>/02-approval-packet.json` | token remains null under proposed schema Option A |
| redacted token authorization receipt | `data/phase9_rehearsal/<rehearsal_id>/03-token-receipt.json` | digest/binding only; raw token never written |
| captured execution result | `data/phase9_rehearsal/<rehearsal_id>/04-execution-result.json` | bounded/redacted output plus digest |
| post-run verification | `data/phase9_rehearsal/<rehearsal_id>/05-postcheck.json` | filesystem/effect summaries, not secret values |
| rollback rehearsal | `data/phase9_rehearsal/<rehearsal_id>/06-rollback-rehearsal.json` | expected `NOT_REQUIRED` for harmless query |
| human closeout report | `data/phase9_rehearsal/<rehearsal_id>/07-report.md` | no raw token or unredacted secret |
| pre/post attempt audit events | accepted `data/audit_dev.jsonl` via Phase 7 writer | token digest/reference only |

The `data/phase9_rehearsal/` path is **not currently authorized**. If the Owner
does not authorize it, the implementation brief must choose another exact,
reviewed evidence location or keep evidence in memory until a separately
authorized closeout write. It must never improvise a path on execution day.

## 4. Before step 1 — hard entry conditions

Do not begin the six steps unless all are true:

- Phase 3, 4, 5, and 7 accepted outputs are present and independently valid;
- Owner has selected token-generation, burn, schema, and structured audit
  contracts in the applicable decision records;
- a separate implementation package has built and independently reviewed the
  gate using only fake executors;
- exact installed OpenClaw CLI facts have been verified in the Owner-present
  session without assuming flags from legacy code;
- the exact harmless action, agent/session posture, timeout, output contract,
  filesystem observation scope, and abort rule are displayed;
- all twelve preflight conditions plus any new contract/CLI conditions are green;
- worker, queue, connectors, write tools, follow-up, background mode, and retry
  remain disabled; and
- every proposed persistent path has separate authorization.

If one item is unknown, show `BLOCKED` and stop before token generation.

## 5. Step 1 — freeze the evidence bundle

**Who:** preflight coordinator computes; independent reviewer checks; Owner
reads the plain-language summary.

**Actions:**

1. Rebuild the N=1 dry-run chain from the exact task and command envelope.
2. Validate all Blackboard messages and the evidence-bundle schema.
3. Independently recompute the bundle hash.
4. Confirm task, command, dry-run, result, approval target, and rollback-preview
   identifiers form one chain.
5. Confirm intended and observed mock side effects are empty and every real-call,
   dispatch, queue, connector, and write flag is false.
6. Freeze the bundle bytes/hash and the exact proposed action hash. No later edit
   is allowed.

**Owner sees:** action summary, exact target, exact query text digest/display,
timeout, expected output class, empty side-effect list, rollback `NOT_REQUIRED`,
and all safety flags.

**Stop immediately if:** validation/hash/id mismatch; any side effect is nonempty;
the CLI fact sheet is incomplete; or runtime parameters differ from dry-run.

**Artifact:** proposed `01-evidence-bundle.json` plus its hash in
`00-preflight.json`. No token exists yet.

## 6. Step 2 — finalize approval and issue one token

**Who:** Owner makes the decision and supplies the fresh token through the
selected ceremony; coordinator only displays and validates bindings.

**Actions:**

1. Display the frozen bundle and exact action hash again.
2. Owner chooses `approve`, `edit`, `reject`, or `respond`. Anything except a
   final exact `approve` stops the run; edits require a new Step 1.
3. Validate the approval packet under the Owner-selected schema strategy.
4. After final evidence is frozen, perform the selected token ceremony.
5. Bind token to rehearsal, packet id/hash, bundle hash, action hash, target,
   expiration, and attempt number `1`.
6. Display the no-retry rule and wait for the Owner's exact go/no-go statement.

**Owner sees:** all binding fields, expiry, one-attempt meaning, and the sentence
“timeout or failure spends this token; there is no automatic retry.”

**Stop immediately if:** Owner is absent/uncertain; packet changed; token is
missing, stale, reused, exposed, or mismatched; schema choice is unresolved; or
an unreviewed path/capability is enabled. A known fresh token is burned on any
later failure.

**Artifacts:** proposed inert `02-approval-packet.json` and redacted
`03-token-receipt.json`. The raw token is memory-only and never enters a file,
fixture, argv, error, or audit text.

## 7. Step 3 — burn then make exactly one foreground call

**Who:** future separately authorized one-shot runner; Owner remains present;
independent reviewer observes counters/state.

**Actions:**

1. Re-run all preflight and exact-action comparisons at the final boundary.
2. Under the selected durable mechanism, append and verify the pre-call audit
   burn event using the Phase 7 writer.
3. Create one in-memory capability for the exact action hash.
4. Atomically consume that capability before starting the process.
5. Start exactly one foreground OpenClaw process using only the Owner-verified
   argv contract. The exact argv remains **待驗證** until that session.
6. Unconditionally return the runner to terminal deny-all at the start boundary,
   regardless of success, timeout, exception, cancellation, or ambiguous output.
7. Capture bounded stdout/stderr, exit/signal state, timestamps, and digests.

**Owner sees:** final action comparison, durable burn confirmation, start count,
live stop control, and terminal gate state.

**Stop immediately if:** any preflight turns red; audit burn fails; Owner says
stop; argv differs; a second start is attempted; output cannot be bounded; or an
unexpected write/tool/connector appears. Do not retry.

**Artifact:** proposed `04-execution-result.json`; the raw runtime output is
stored only if its exact redaction/location policy was authorized. Pre-call
audit evidence is appended to `data/audit_dev.jsonl`.

## 8. Step 4 — append and verify the audit chain

**Who:** coordinator invokes only the accepted Phase 7 writer; independent
reviewer recomputes; Owner sees the human summary.

**Actions:**

1. Prove the gate is already `CLOSED_DENY` and start count is at most one.
2. Build a structured post-attempt audit event referencing the burn event.
3. Record completion class, exit/timeout state, output digests, empty or observed
   side effects, gate-disabled proof, and rollback disposition.
4. Append once through the Phase 7 writer and fsync.
5. Re-read and verify the complete hash chain independently.

**Owner sees:** pre/post audit ids and hashes, token digest/reference (not token),
attempt count, result class, side-effect result, and chain verification.

**Stop immediately if:** post event cannot validate/append, chain fails, raw
token appears, or a side effect is observed. Post-audit failure is an incident;
the spent token and disabled gate do not reopen.

**Artifact:** two structured events in `data/audit_dev.jsonl` and their references
in the proposed session report.

## 9. Step 5 — post-run verification

**Who:** independent reviewer performs comparisons; coordinator displays; Owner
decides whether facts are acceptable.

**Actions:**

1. Compare actual executable identity, argv hash, target, timeout, and attempt
   count with frozen evidence.
2. Validate and classify output without treating parse success as execution
   authority.
3. Compare before/after target and OpenClaw state inventories.
4. Assert no business target, connector, queue, worker, follow-up, background
   task, or second call occurred.
5. Present a replay negative check using the fake executor/gate path only; the
   same token must deny without any OpenClaw call.
6. Verify gate terminal state and audit chain again.

**Owner sees:** one-page delta: expected vs actual action/output/effects, file
changes, audit state, replay denial, and remaining unknowns.

**Stop immediately if:** any mismatch, unreviewed filesystem write, missing
evidence, ambiguous runtime state, replay acceptance, or gate reopening occurs.

**Artifact:** proposed `05-postcheck.json`, referenced by the closeout report.

## 10. Step 6 — rehearse rollback and close out

**Who:** coordinator walks the preview; Owner confirms the disposition;
independent reviewer verifies the fields. No rollback command is executed.

**Actions:**

1. Validate the rollback event/preview contract and id references.
2. Confirm the pre-reviewed rollback path says `NOT_REQUIRED` because the
   approved business action was a zero-write query.
3. Confirm the conditions that would change this to incident/HOLD: any target,
   connector, OpenClaw operational, or other unexpected write/effect.
4. Demonstrate the manual stop/escalation path without executing a rollback.
5. Assemble the six-step report, verify every digest/reference, and show that
   no token plaintext is present.
6. Owner explicitly accepts or rejects this single rehearsal. Acceptance is not
   permission for a second call or wider whitelist.

**Owner sees:** rollback reason, evidence that no rollback is needed, incident
branch if the premise was false, and final all-disabled proof.

**Stop immediately if:** rollback fields do not match the packet/result/audit;
any write makes `NOT_REQUIRED` false; or the report is incomplete.

**Artifacts:** proposed `06-rollback-rehearsal.json` and `07-report.md`; closeout
reference appended only through an explicitly authorized audit contract.

## 11. Completion rule

The rehearsal passes only if all six steps have complete evidence, one and only
one attempt was possible, the target effect set is empty, the audit chain
verifies, replay is denied without a runtime call, rollback is correctly
`NOT_REQUIRED`, the gate is terminally disabled, and the Owner signs this N=1
result. Anything else is HOLD/fail, with no retry and no inferred permission.

