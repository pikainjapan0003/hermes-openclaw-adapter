# HERMES ↔ OpenClaw Adapter — Local vs Remote Queue Boundary (v0.7.5-B)

> Plan-first document. This is **planning only**. It plans the boundary between the current
> local queue and a future remote blackboard / remote queue. It implements no runtime,
> creates no database, migrates no queue data, synchronizes nothing, opens no shared write,
> and introduces no external side effect.

## 1. Purpose

This document plans — and only plans — the boundary between the **local queue** (the local
runtime/development data store that may exist in Windows WSL and in Replit Preview) and a
future **remote blackboard / remote queue** (a future shared coordination backend). It
defines where local ends and remote begins so that any future synchronization or migration
stays inside Owner-supervised, audit-preserving limits.

Nothing here is built. This round adds **only** a planning document and a readiness script
that statically verifies that document.

## 2. Current master

```
HEAD = origin/master = eda58e5976bda6f313e10071ca4733dd2f465aad
docs: plan remote blackboard api
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is plan-first. The following define what v0.7.5-B is and is not:

```
v0.7.5-B Local vs Remote Queue Boundary is plan-first.
v0.7.5-B does not implement Remote Blackboard API runtime.
v0.7.5-B does not create production DB.
v0.7.5-B does not create shared DB.
v0.7.5-B does not create remote shared DB.
v0.7.5-B does not migrate queue data.
v0.7.5-B does not sync local queue and remote queue.
v0.7.5-B does not open shared write.
v0.7.5-B does not start Worker.
v0.7.5-B does not call OpenClaw.
v0.7.5-B does not call Hermes.
v0.7.5-B does not write Google Sheets.
v0.7.5-B does not create webhook.
```

## 4. Relationship to v0.7.5-A

v0.7.5-A planned the future Remote Blackboard API / shared Blackboard backend and recorded
its boundaries (no runtime, no DB, no migration, no shared write, no external side effect).
v0.7.5-B narrows in on one specific boundary that v0.7.5-A left open: the relationship
between the current local queue and that future remote blackboard. It does not change any
v0.7.5-A boundary; it refines the local-vs-remote distinction so a future synchronization or
migration plan starts from an explicit separation rather than an implicit one.

## 5. Problem statement

```
Windows WSL local queue and Replit local queue are currently separate.
Local queue is a local development/runtime data store.
Remote blackboard is a future shared coordination backend.
Local queue is not automatically synced to remote blackboard.
Remote blackboard is not automatically authoritative.
Dashboard update is not queue synchronization.
GitHub push is not queue synchronization.
Future synchronization requires a separate future plan and Owner approval.
```

## 6. Local queue definition

```
Local queue may exist in Windows WSL.
Local queue may exist in Replit Preview.
Windows WSL local queue and Replit local queue are separate.
Local queue is local runtime/development data.
Local queue is not GitHub.
Local queue is not remote shared DB.
Local queue is not Remote Blackboard API.
Local queue must not store secrets.
Local queue must not imply Worker dispatch.
```

## 7. Remote blackboard definition

```
Remote blackboard is a future shared coordination surface.
Remote blackboard may eventually store Task Messages.
Remote blackboard may eventually store Decision Messages.
Remote blackboard may eventually store Result Messages.
Remote blackboard may eventually store Advice Messages.
Remote blackboard is not implemented in v0.7.5-B.
Remote blackboard is not production DB in v0.7.5-B.
Remote blackboard is not an execution dispatcher.
Remote blackboard is not OpenClaw.
Remote blackboard is not Hermes.
Remote blackboard is not Google Sheets.
```

## 8. Local queue is not remote blackboard

The local queue and any future remote blackboard are distinct concerns. The local queue is
a per-environment runtime/development data store; the remote blackboard is a future shared
coordination surface for Blackboard messages. One is not silently the other: reading or
writing the local queue is not reading or writing the remote blackboard, and the existence
of a remote blackboard does not make the local queue obsolete or absorbed.

## 9. Current WSL / Replit queue separation

```
Current Windows WSL local queue remains separate.
Current Replit local queue remains separate.
No queue data is copied.
No queue data is moved.
No queue data is merged.
No queue data is backfilled.
No queue data is synchronized.
No conflict resolver is implemented.
No source-of-truth switch is performed.
```

## 10. GitHub / WSL / Replit boundary

GitHub remains the clean source of code and docs, not a queue DB or secrets store. Windows
WSL remains the primary local development environment with its own local queue. Replit
remains a remote observation station / Preview Dashboard with its own separate local queue.
A future remote blackboard does not change these roles in v0.7.5-B.

## 11. Dashboard read boundary

The Dashboard reads and displays; it does not synchronize queues. A Dashboard update is a
`git pull` plus a Dashboard restart, not a queue synchronization. Dashboard read is not
queue write, and Dashboard display is not execution permission.

## 12. Local write boundary

Writing the local queue is a local runtime action only. It is not a write to a remote
blackboard, not a Worker dispatch, and not an external side effect. The local queue remains
local to its environment and is never moved by this plan.

## 13. Remote write boundary

A future remote blackboard write — if it ever existed — would be a write to a shared
coordination surface only. It is not an OpenClaw call, not a Hermes action, and not an
external side effect by itself. Shared write remains disabled in v0.7.5-B.

The combined read / write boundary is:

```
Dashboard read is not queue write.
Dashboard display is not execution permission.
Reading local queue is not reading remote blackboard.
Reading remote blackboard is not Worker dispatch.
Writing local queue is not writing remote blackboard.
Writing remote blackboard is not OpenClaw call.
Writing remote blackboard is not Hermes action.
Writing remote blackboard is not external side effect by itself.
Shared write remains disabled in v0.7.5-B.
```

## 14. Sync boundary

```
No queue synchronization is performed.
No queue migration is performed.
No local queue data is moved.
No Replit queue data is moved.
No production queue data is created.
No remote shared DB is created.
No data backfill is performed.
No queue merge is performed.
No conflict resolver is implemented.
Sync requires a separate future plan and Owner approval.
Migration requires a separate future plan and Owner approval.
```

## 15. Migration boundary

No queue migration is performed in v0.7.5-B. No local queue data and no Replit queue data is
moved. No production queue data is created and no remote shared DB is created. Migration
requires a separate future plan and Owner approval; planning the boundary is not approving a
migration.

## 16. Backfill / merge / conflict boundary

No queue data is backfilled. No queue data is merged. No conflict resolver is implemented.
Any future backfill, merge, or conflict-resolution behavior is out of scope here and would
require a separate future plan and explicit Owner approval before any data is touched.

## 17. Source-of-truth planning boundary

```
Current source of truth remains local to each environment.
Windows WSL local queue is not automatically source of truth for Replit.
Replit local queue is not automatically source of truth for WSL.
Future remote blackboard authority is not enabled in v0.7.5-B.
Future source-of-truth switch requires separate Owner approval.
GitHub remains clean source of code and docs, not queue DB.
```

## 18. Blackboard message compatibility

```
Task Message
Decision Message
Result Message
Advice Message
Decision Message is audit record, not command.
approve is not execute.
Writing a task to Blackboard is not Worker dispatch.
Entering Blackboard mode is not execution permission.
Result Message is not next dispatch permission.
Advice Message is not automatic follow-up execution.
```

## 19. Owner approval and activation boundary

```
Owner approval is required before any remote blackboard runtime.
Owner approval is required before any shared DB.
Owner approval is required before any queue migration.
Owner approval is required before any queue synchronization.
Owner approval is required before any shared write.
Owner approval is required before any source-of-truth switch.
Plan approval is not runtime approval.
Plan approval is not migration approval.
Plan approval is not shared write approval.
```

## 20. Worker / OpenClaw / Hermes boundary

A local queue write or a future remote blackboard write is not a Worker dispatch, not an
OpenClaw call, and not a Hermes action. Worker remains OFF, OpenClaw remains Not Connected,
and Hermes remains Not Connected. Execution dispatch stays separately gated behind Owner
approval.

## 21. Data and secrets boundary

The local queue stores local runtime/development data and must not store secrets. A future
remote blackboard stores Blackboard messages only and must not store secrets or raw
credentials, and must not expose any secret in a UI or in logs. Authentication material, if
any, lives outside the message store and is never committed to GitHub.

## 22. Candidate future transition models

These are planning notes only — none is implemented or provisioned:

```
Candidate transition model: local-only remains source.
Candidate transition model: remote read mirror.
Candidate transition model: remote write draft only.
Candidate transition model: remote authoritative blackboard.
Candidate transition model: hybrid local runtime with remote audit mirror.
Candidate transition models are planning notes only.
No transition model is implemented in v0.7.5-B.
```

## 23. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
No cleanup demo task.
No cleanup apply.
No --apply.
No task deletion.
No task archive.
No queue DB change.
No local queue data change.
No Replit queue data change.
No real queue DB read.
No POST.
No live local queue write validation.
No Worker execution.
No OpenClaw call.
No Hermes call.
No Google Sheets write.
No secrets read.
No webhook.
No external side effects.
No production DB.
No shared DB.
No remote shared DB.
No Remote Blackboard API runtime.
No queue synchronization.
No queue migration.
No queue backfill.
No queue merge.
No conflict resolver.
No connector.
No tag.
```

## 24. Validation summary

```
v0.7.5-B readiness: ALL PASS.
v0.7.5-A readiness: ALL PASS.
v0.7.4-R readiness: ALL PASS.
v0.7.4-F-R readiness: ALL PASS.
v0.7.4-F readiness: ALL PASS.
v0.7.4-F dry-run tool test: ALL PASS.
v0.7.4-E check: ALL PASS.
v0.7.4-D-R check: ALL PASS.
v0.7.4-D readiness and helper test: ALL PASS.
v0.7.4-C / B / A checks: ALL PASS.
v0.7.3 checks: ALL PASS.
prior F-line checks: ALL PASS.
compileall scripts: PASS.
```

## 25. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 26. Non-goals

- Not implementing a Remote Blackboard API runtime.
- Not creating a production DB, shared DB, or remote shared DB.
- Not adding any API route, FastAPI router, database client, or migration.
- Not synchronizing the local queue and any remote queue.
- Not migrating, moving, copying, merging, or backfilling any queue data.
- Not implementing a conflict resolver or a source-of-truth switch.
- Not opening shared write.
- Not reading a real queue DB; not sending any POST.
- Not starting the Worker; not calling OpenClaw / Hermes; not writing Google Sheets.
- Not creating a webhook, webhook receiver, or connector.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.

## 27. Acceptance criteria

- This plan document exists and contains sections 1–28.
- The current-master marker records `eda58e5` on `origin/master`.
- The v0.7.5-B plan-first markers are present.
- The problem statement, local queue definition, remote blackboard definition, queue
  separation, read/write boundary, sync/migration boundary, source-of-truth planning
  boundary, blackboard message compatibility, Owner approval and activation boundary,
  candidate future transition model, current safe posture, validation summary, and safety
  grep summary markers are present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script `check_hermes_openclaw_local_vs_remote_queue_boundary_v0_7_5_b.py`
  passes ALL.

## 28. Next recommended step

```
v0.7.5-C — Dashboard Backend Source Plan
```

with the constraints:

```
v0.7.5-C must remain plan-first unless separately approved.
v0.7.5-C must not create production DB.
v0.7.5-C must not create Remote Blackboard API runtime.
v0.7.5-C must not migrate queue data.
v0.7.5-C must not open shared write.
v0.7.5-C must not start Worker / OpenClaw / Hermes / Google Sheets.
```
