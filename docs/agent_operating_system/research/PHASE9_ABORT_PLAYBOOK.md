# Phase 9 N=1 Failure and Abort Playbook

Status: **PLANNING ONLY. NOT AUTHORIZED FOR EXECUTION OR PERSISTENCE.**

Date: 2026-08-03
Scope: future Owner-present handling for one harmless query attempt. This
playbook is human-readable policy, not machine input.

## 1. Universal rule

**No retry without a new packet and new token.** A timeout, error, ambiguous
result, or partial start is an attempt. No model may “helpfully” retry, continue,
repair argv, switch agents, change targets, or finish after the Owner says stop.

For every failure:

1. deny process start if it has not happened;
2. otherwise stop/contain the one observed process using only the pre-reviewed
   stop path;
3. move the one-shot runner to terminal `CLOSED_DENY` in an unconditional cleanup
   boundary;
4. ensure the presented session token cannot authorize later work;
5. append only the authorized, redacted audit event when the audit path is
   healthy;
6. preserve/display bounded evidence without creating an improvised file; and
7. require a completely new evidence/packet/token ceremony for any future try.

“Token disposition” below distinguishes a known valid token from an unknown
string. A known fresh token is burned on a later failure. An invalid/unknown
string is denied and fingerprinted only if the audit contract permits; it cannot
be promoted into a real token record.

## 2. Required abort-state evidence

When audit is healthy, each failure event should record:

- rehearsal and event ids, timestamp, prior hash, and phase/step;
- packet/evidence/action hashes and non-reversible token reference if known;
- failure class and bounded redacted detail;
- whether token was absent, expired, denied, burned-before-attempt, or
  burned-attempt;
- whether process start was attempted/observed and the executor start count;
- stop/termination observation and ambiguity flag;
- gate transition to `CLOSED_DENY`;
- observed side-effect summary;
- `retry_permitted: false`; and
- Owner notification/stop acknowledgement reference without secret content.

The current audit schema does not yet contain all structured fields. This is a
future contract requirement, not permission to encode them in free text.

## 3. Failure matrix

| # | Scenario | Detection | Immediate action | Token disposition | Audit content | Return-to-disabled proof |
|---|---|---|---|---|---|---|
| 1 | OpenClaw not on resolved PATH / executable missing | frozen executable identity check or process-start `not found` result | do not search alternate PATHs or binaries; stop | if before issuance, none; if known token presented, burn deny | expected path identity, missing class, start count zero | no capability created; gate terminal deny |
| 2 | Installed CLI interface is still unverified | CLI facts sheet has any `待驗證`/BLOCK item or exact argv lacks authoritative confirmation | stop before token issuance; do not probe help/version under this playbook | none; if already issued, expire/burn deny | unresolved fact ids, no command bytes or secret | preflight stays BLOCKED; start count zero |
| 3 | Timeout | external bounded timer expires or CLI reports timeout; completion cannot be proven | terminate using only pre-reviewed process/child stop method; do not start another process | burn attempt; token permanently spent | timeout source, configured/observed duration, termination/child ambiguity, output digest | cleanup closes gate; fake replay probe denies |
| 4 | Nonzero exit code or signal | captured process status is nonzero/signaled | capture bounded redacted stdout/stderr and stop; do not reinterpret partial output as success | burn attempt | exit/signal class, digests, bounded summary, start count one | gate already closed before result interpretation |
| 5 | Output absent, malformed, oversized, wrong encoding, streaming, or otherwise unparseable | output contract/size/UTF-8/schema validator fails | stop parsing; retain only authorized bounded digest/summary; no fallback parser that changes acceptance | burn attempt | parse failure class, length/digest, truncation indicator; never raw secret | no second parser may call runtime; gate closed |
| 6 | Pre-call audit burn append or verification fails | append exception, fsync failure, schema failure, tail mismatch, or chain verification false | **do not start OpenClaw**; keep original audit bytes; do not write a fallback file | known token burns/invalidates in session policy; if durable burn cannot be proven, future use still denied and requires new token | audit path itself unavailable, so show in-memory incident to Owner; persist nothing elsewhere | capability is never created; start count zero |
| 7 | Token missing, malformed, expired, mismatched, already used, or replayed | token-binding, controlled-clock, digest, or burn-ledger check fails | deny without revealing which secret component matched; do not refresh or ask model to retry | missing/unknown: deny; known expired/used: terminal; known fresh but mismatched: burn deny | redacted reason class, binding hashes, no raw token | no transition beyond checking; fake executor count zero |
| 8 | A preflight condition turns red after token issuance | final revalidation differs from frozen green report | stop; do not edit packet/evidence in place | burn deny | changed condition id, previous/current result digests, no payload | no burn-attempt capability; gate terminal deny |
| 9 | Owner says stop, disconnects, or cannot confirm | any Owner stop phrase, lost synchronous channel, or ambiguous response | stop immediately; before start do not call; after start use reviewed termination path | before start: burn deny; after start: burn attempt | Owner-stop class/time, process observation, no chat transcript | cleanup is unconditional; no later “resume” state |
| 10 | Evidence, packet, target, argv, timeout, agent, session, or action hash differs | byte/field comparison against frozen inputs fails | stop; do not normalize, default, trim, repair, or substitute | burn deny | mismatched field name and old/new digests only | exact-action capability never created |
| 11 | Unexpected target, connector, queue, tool, local-state, network, or filesystem side effect | capability posture check or before/after inventory shows unreviewed effect | freeze execution, preserve authorized evidence, notify Owner; follow only reviewed incident path | burn attempt if process started, otherwise burn deny | effect class/path category/digest, expected-vs-observed, incident/HOLD | global/layer deny asserted; no rollback improvisation or retry |
| 12 | Post-call audit append or chain verification fails | post event cannot validate/fsync or complete chain is invalid | keep execution frozen; show Owner in-memory incident; do not use alternate persistence | burn attempt remains permanent | if audit unavailable, no false success claim; record later only under a new explicit recovery instruction | gate was closed before post-audit; replay denies |
| 13 | Runner crash/cancellation after durable burn but before observed process start | burn exists but start record is absent/ambiguous after restart | classify as spent/ambiguous; do not “complete” the call | burned permanently | burn event plus restart incident, observed start unknown | durable burn denies recreation; new token required |
| 14 | Second start request, follow-up, or automatic retry path appears | start counter >1 request, reused capability, scheduler/worker activity, or follow-up flag | reject request and freeze the session; treat any actual second start as a safety incident | original token already burned; no new authority exists | replay/second-start attempt, source, executor count | atomic one-use bit and durable burn deny; all schedulers off |
| 15 | Raw token appears in any persistent or model-visible output | redaction scan finds token bytes in Owner instruction, report, commit/closeout text, audit, file, argv/environment evidence, exception, or fixture | stop before any call; restrict further display; do not copy the exposed value into an incident report | revoke the exposed token immediately; require a fresh OOB ceremony | record only leak surface/class, packet/action digests, and a new non-secret incident id | no capability is created or retained; new token and full ceremony required |

## 4. Scenario-specific notes

### 4.1 Missing binary is not permission to search

The runner may not try `which`, Windows PATH, another installation, a shell
alias, package runner, or a guessed absolute path after the frozen executable is
missing. Changing executable identity changes the action and requires fresh
evidence plus Owner review.

### 4.2 Timeout is deliberately ambiguous

Unless child termination and external effects are proven, timeout means
“attempted, outcome uncertain,” not “nothing happened.” The token is spent. The
postcheck must inspect the authorized effect surfaces before the Owner decides
whether the rehearsal is rejected or treated as an incident.

### 4.3 Output parsing never controls retry

A readable answer with an invalid envelope is still a failed/ambiguous contract.
An empty answer with exit zero is not automatically success. A parser fallback
may only classify already captured bytes; it cannot trigger another call or
change the reviewed acceptance rules.

### 4.4 Audit failure has no secret backup channel

When `data/audit_dev.jsonl` cannot accept/verify the required event, the runner
must not write a temporary JSONL, database, clipboard log, queue note, or session
folder as an automatic fallback. Before-call audit failure means no call.
After-call audit failure means the call is spent, the phase cannot pass, and the
Owner receives an on-screen incident summary pending a separate recovery
instruction.

### 4.5 Owner stop is edge-triggered and irreversible

Any clear stop phrase takes priority over prior approval. A later conversational
“continue” in the same token/session cannot reopen the gate. Continuing requires
a new packet, fresh token, and complete preflight ceremony.

### 4.6 Unexpected write invalidates `NOT_REQUIRED`

The harmless-query rollback claim is valid only while observed target and
operational effects match the reviewed empty set. If OpenClaw updates an
unapproved cache/session/state file, that is an incident/HOLD. The system cannot
delete, revert, or edit it unless that exact rollback was already reviewed and
separately authorized.

### 4.7 Raw-token exposure invalidates the ceremony

The Phase 9 Owner instruction must be authored with
`token=<REDACTED:sha256[0:8]>`; it must never contain a raw token that is later
masked for reporting. If any retainable or model-visible surface receives the
raw value, that token is compromised and revoked. Do not quote it while
reporting the leak. Close the gate and begin only with a new token, new OOB
ceremony, and renewed preflight under separate authorization.

## 5. Mechanical all-disabled checklist

After every success or failure, independently assert:

- runner state is terminal `CLOSED_DENY`;
- no in-memory one-shot capability remains;
- token digest is durably burned or the session records deny with no capability;
- a replay through a fake executor is rejected;
- process start count is zero or one, never two;
- worker is not started; queue claim count is zero; queue depth and the set of
  queued-record identities equal the frozen preflight snapshot; and no new
  `queued` record exists;
- connector, target write, follow-up, and background flags remain false;
- no retry timer/task/process exists;
- no raw token appears in memory dumpable reports, audit bytes, errors, or files;
- audit chain verifies, or the session is explicitly failed because it cannot be
  verified; and
- Owner sees the final disabled/incident state.

Failure of this checklist is a blocking safety incident, not a reason to rerun.

## 6. Closeout language

The only valid disposition after a failed attempt is: this token/session is
closed; no retry is authorized; the observed evidence is accepted for incident
review only. A future attempt requires a newly frozen bundle, new approval
packet, new token, renewed Owner presence, and a fully green preflight.

No sentence in this playbook grants that future authorization.
