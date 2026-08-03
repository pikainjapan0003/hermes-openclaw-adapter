# Phase 9 N=1 Owner-Present Six-Step Script

Status: **PLANNING ONLY. NOT AUTHORIZED FOR EXECUTION OR PERSISTENCE.**

Date: 2026-08-03
Purpose: the exact reading order for the future day on which the Owner may
authorize one harmless, query-shaped OpenClaw attempt. This is not a runnable
script and contains no verified CLI command.

Authorization ladder: an Owner design selection chooses options only; a later
exact instruction must separately authorize implementation; after that work
passes independent review, another exact Owner-present instruction must
authorize the one execution. No layer implies the next.

## Threat model

Source: `05_VERIFIED_LONG_TERM_PLAN.md` §6.16, commit `e34ca1c`.

> 在範圍內（設計必須擋住）：模型過度熱心、誤解授權、自作主張、把顯示當授權、意外重放、崩潰後誤續跑。
>
> 明確不在範圍內：一個刻意規避的對抗性模型。
>
> 已知並接受的殘餘風險（不得再被當成待修缺陷）：模型可經 `wsl.exe -u root` 取得 root；gate 程式碼與 `.venv` 對模型可寫；burn ledger 與 frozen artifact 可被有意刪改；`~/.openclaw/` config 可被有意竄改。

Accordingly, this document relies on **procedural constraint plus best-effort
technical isolation, effective against a non-adversarial model**. It makes no
claim that a deliberately evasive model is mechanically excluded.

## 1. Scope in one sentence

Freeze evidence, obtain one exact Owner decision and fresh token, permit one
foreground query attempt, record it in the Phase 7 audit chain, verify that
nothing else happened, and rehearse the pre-reviewed no-op rollback conclusion.

“Zero write” means zero intended business/target mutation and, under the current
§6.8 premise, no unavoidable OpenClaw operational write. Control-plane evidence
and separately authorized Phase 9 audit appends are explicit records. If
OpenClaw necessarily writes cache/session/state, the premise breaks: stop until
the Owner explicitly revises §6.8 and separately authorizes the exact new scope.

## 2. Roles

| Role | What this role may do that day | What it may not do |
|---|---|---|
| Owner | remain synchronously present; inspect facts/evidence; choose channel/schema/token design beforehand; issue the exact redacted action instruction and separately deliver the token/response OOB; say stop; sign or reject closeout | delegate the live decision to a model; put a raw token in the instruction; give broad/standing permission |
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
| pre/post attempt audit events | proposed `data/audit_dev.jsonl` via Phase 7 writer; **requires new Phase 9 Owner authorization** | token digest/reference only |

The `data/phase9_rehearsal/` path is **not currently authorized**. If the Owner
does not authorize it, the implementation brief must choose another exact,
reviewed evidence location or keep evidence in memory until a separately
authorized closeout write. It must never improvise a path on execution day.

## 4. Before step 1 — hard entry conditions

Do not begin the six steps unless all are true:

- Phase 3, 4, 5, and 7 accepted outputs are present and independently valid;
- Owner has selected token-generation, burn, schema, and structured audit
  contracts in the applicable decision records;
- Owner has selected distinct-principal/off-host ingress and egress, plus the
  independent frozen packet/action digest display or reader method;
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
7. Capture a read-only baseline of queue depth and queued-record identities;
   prove no worker/claimer is running and that no rehearsal id exists in
   `QueueStore`.

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

1. Present the frozen packet and action digests through the approved non-model
   egress, or let the Owner read the frozen artifact bytes through the approved
   independent reader. A model-chat/model-terminal display does not count.
2. Owner chooses `approve`, `edit`, `reject`, or `respond` through the Phase 9
   instruction flow. The decision creates only an inert approval packet.
   Anything except a final exact `approve` stops the run; edits require a new
   Step 1.
3. Validate the approval packet under the Owner-selected schema strategy.
4. After final evidence is frozen, perform the selected token ceremony.
5. Immediately after the Owner response, rerun all applicable principal, ACL,
   endpoint, `/proc`, descriptor, tty/device, and peer-credential exclusion
   probes; freeze their attestation digest and stop on any drift.
6. Bind token to rehearsal, packet id/hash, bundle hash, action hash, target,
   expiration, and attempt number `1`.
7. Display the no-retry rule and wait for the Owner's exact go/no-go statement.

The Owner must **not** click `/dashboard/tasks/{id}/approve`, and the coordinator
must not call that route or any queue-writing route. The existing dashboard
approve path can create a `queued` task that an external worker may claim,
bypassing the Phase 9 token and gate.

**Owner sees:** all binding fields, expiry, one-attempt meaning, and the sentence
“timeout or failure spends this token; there is no automatic retry.”

**Stop immediately if:** Owner is absent/uncertain; packet changed; token is
missing, stale, reused, exposed, or mismatched; schema choice is unresolved; or
an unreviewed path/capability is enabled. Use of a queue-writing approval path or
any queue-baseline drift is an immediate HOLD. A known fresh token is burned on
any later failure.

**Artifacts:** proposed inert `02-approval-packet.json` and redacted
`03-token-receipt.json`. The raw token is memory-only and never enters a file,
fixture, argv, error, or audit text.

## 7. Step 3 — burn then make exactly one foreground call

**Who:** future separately authorized one-shot runner; Owner remains present;
independent reviewer observes counters/state.

**Actions:**

1. Re-run all preflight and exact-action comparisons at the final boundary.
2. Send the second fresh packet/action/rehearsal-bound challenge through the
   approved egress; accept the Owner response only through the approved ingress;
   then rerun all channel-isolation probes and recompute the full six-predicate
   `owner_synchronously_present` AND. Any changed result stops before burn.
3. Under the selected durable mechanism and only after a new verbatim Phase 9
   audit-write authorization, append and verify the pre-call audit burn event
   using the Phase 7 writer. §6.15 does not authorize this execution-coupled
   append.
4. Create one in-memory capability for the exact action hash.
5. Atomically consume that capability before starting the process.
6. Start exactly one foreground OpenClaw process using only the Owner-verified
   argv contract. The exact argv remains **待驗證** until that session.
7. Unconditionally return the runner to terminal deny-all at the start boundary,
   regardless of success, timeout, exception, cancellation, or ambiguous output.
8. Capture bounded stdout/stderr, exit/signal state, timestamps, and digests.

**Owner sees:** final action comparison, durable burn confirmation, start count,
live stop control, and terminal gate state.

**Stop immediately if:** any preflight turns red; audit burn fails; Owner says
stop; argv differs; a second start is attempted; output cannot be bounded; or an
unexpected write/tool/connector appears. Do not retry.

**Artifact:** proposed `04-execution-result.json`; the raw runtime output would
be stored only if its exact redaction/location policy were authorized. Proposed
pre-call audit evidence would be appended to `data/audit_dev.jsonl` only after
the new exact Phase 9 audit-write authorization.

## 8. Step 4 — append and verify the audit chain

**Who:** coordinator invokes only the accepted Phase 7 writer; independent
reviewer recomputes; Owner sees the human summary.

**Actions:**

1. Prove the gate is already `CLOSED_DENY` and start count is at most one.
2. Build a structured post-attempt audit event referencing the burn event.
3. Record completion class, exit/timeout state, output digests, empty or observed
   side effects, gate-disabled proof, and rollback disposition.
4. Append once through the Phase 7 writer and fsync, only within the new exact
   Phase 9 audit-write authorization.
5. Re-read and verify the complete hash chain independently.

**Owner sees:** pre/post audit ids and hashes, token digest/reference (not token),
attempt count, result class, side-effect result, and chain verification.

**Stop immediately if:** post event cannot validate/append, chain fails, raw
token appears, or a side effect is observed. Post-audit failure is an incident;
the spent token and disabled gate do not reopen.

**Artifact:** proposed two structured events in `data/audit_dev.jsonl`, only
after the new exact Phase 9 audit-write authorization, and their references in
the proposed session report.

## 9. Step 5 — post-run verification

**Who:** independent reviewer performs comparisons; coordinator displays; Owner
decides whether facts are acceptable.

**Actions:**

1. Compare actual executable identity, argv hash, target, timeout, and attempt
   count with frozen evidence.
2. Validate and classify output without treating parse success as execution
   authority.
3. Compare before/after target and OpenClaw state inventories.
4. Assert no business target, connector, worker, follow-up, background task, or
   second call occurred; compare the queue snapshot and prove queue depth and
   queued-record identities are unchanged, with no new `queued` record.
5. Present a replay negative check using the fake executor/gate path only; the
   same token must deny without any OpenClaw call.
6. Verify gate terminal state and audit chain again.
7. Scan every persistent and displayed surface, including the verbatim Owner
   instruction citation, report, commit/closeout text, audit bytes, errors,
   argv/environment evidence, and fixtures. The citation must contain only
   `token=<REDACTED:hmac-sha256/<key-id>[0:8]>`, packet/action digests, and no raw
   token.

**Owner sees:** one-page delta: expected vs actual action/output/effects, file
changes, audit state, replay denial, and remaining unknowns.

**Stop immediately if:** any mismatch, unreviewed filesystem write, missing
evidence, ambiguous runtime state, replay acceptance, or gate reopening occurs.

**Artifact:** proposed `05-postcheck.json`, referenced by the closeout report;
its no-secret proof explicitly covers the Owner-instruction citation.

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

This document is a checklist, not an execution mechanism. It must never be
imported, parsed, or treated as dispatch input.
