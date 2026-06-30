# HERMES ↔ OpenClaw Adapter — Dashboard Backend Source Plan (v0.7.5-C)

> Plan-first document. This is **planning only**. It plans how the Dashboard would, in the
> future, identify, read, and label different backend sources. It implements no runtime,
> changes no Dashboard UI, adds no route, adds no backend client, performs no source switch,
> performs no queue sync, performs no migration, opens no shared write, and introduces no
> external side effect.

## 1. Purpose

This document plans — and only plans — how the Dashboard would in the future identify which
**backend source** it is reading (local WSL queue, Replit local queue, or a future remote
blackboard), how it would label that source, and how it would surface freshness, staleness,
and safety state to the Owner. It defines these boundaries up front so that any future
Dashboard source selection stays read-only, Owner-supervised, and audit-preserving.

Nothing here is built. This round adds **only** a planning document and a readiness script
that statically verifies that document.

## 2. Current master

```
HEAD = origin/master = 12e1286196753e181200eb0aea8f0797a9833e53
docs: plan local versus remote queue boundary
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is plan-first. The following define what v0.7.5-C is and is not:

```
v0.7.5-C Dashboard Backend Source Plan is plan-first.
v0.7.5-C does not implement Dashboard backend source runtime.
v0.7.5-C does not implement source switching runtime.
v0.7.5-C does not implement Remote Blackboard API runtime.
v0.7.5-C does not create production DB.
v0.7.5-C does not create shared DB.
v0.7.5-C does not create remote shared DB.
v0.7.5-C does not migrate queue data.
v0.7.5-C does not sync local queue and remote queue.
v0.7.5-C does not open shared write.
v0.7.5-C does not start Worker.
v0.7.5-C does not call OpenClaw.
v0.7.5-C does not call Hermes.
v0.7.5-C does not write Google Sheets.
v0.7.5-C does not create webhook.
```

## 4. Relationship to v0.7.5-A and v0.7.5-B

v0.7.5-A planned the future Remote Blackboard API / shared Blackboard backend and its
boundaries. v0.7.5-B planned the boundary between the local queue and that future remote
blackboard, and recorded that the WSL and Replit local queues are separate and never moved.
v0.7.5-C builds on both: it plans how the Dashboard would identify and label whichever
backend source it reads, without changing any v0.7.5-A or v0.7.5-B boundary. It refines the
display/observation side only; it does not enable a source switch, a sync, or a migration.

## 5. Problem statement

```
Dashboard currently displays local application data from the environment where it runs.
Windows WSL local queue and Replit local queue are currently separate.
Future remote blackboard may become a dashboard-readable backend source.
Dashboard backend source selection is not queue synchronization.
Dashboard backend source selection is not source-of-truth switch.
Dashboard update is not backend source migration.
GitHub push is not backend source migration.
Future dashboard source switching requires a separate future plan and Owner approval.
```

## 6. Dashboard backend source definition

```
Dashboard backend source means the data source the Dashboard reads for display.
Dashboard backend source may be local WSL queue in local development.
Dashboard backend source may be Replit local queue in Replit Preview.
Dashboard backend source may eventually be future remote blackboard.
Dashboard backend source is not Worker dispatch.
Dashboard backend source is not OpenClaw.
Dashboard backend source is not Hermes.
Dashboard backend source is not Google Sheets.
Dashboard backend source is not source-of-truth switch by itself.
```

## 7. Current local source boundary

```
Local WSL source remains local.
Local WSL source is not automatically visible to Replit.
Local WSL source is not automatically remote blackboard.
Reading local WSL source is not shared write.
Reading local WSL source is not Worker dispatch.
No local WSL queue data is moved in v0.7.5-C.
```

## 8. Replit local source boundary

```
Replit local source remains separate.
Replit local source is Preview / observation data.
Replit local source is not production DB.
Replit local source is not automatically authoritative.
Replit local source is not automatically synchronized with WSL.
Reading Replit local source is not reading future remote blackboard.
No Replit queue data is moved in v0.7.5-C.
```

## 9. Future remote blackboard source boundary

```
Future remote blackboard source is planning only.
Future remote blackboard source is not implemented in v0.7.5-C.
Future remote blackboard source is not production DB in v0.7.5-C.
Future remote blackboard source is not an execution dispatcher.
Future remote blackboard source requires separate Owner approval before runtime.
Future remote blackboard source must preserve Owner review.
Future remote blackboard source must preserve audit trail.
Future remote blackboard source must preserve decision and dispatch separation.
```

## 10. Source identity and labeling boundary

```
Dashboard must eventually show which backend source is being viewed.
Dashboard must eventually label local WSL source distinctly.
Dashboard must eventually label Replit local source distinctly.
Dashboard must eventually label remote blackboard source distinctly.
Dashboard source label must not imply execution permission.
Dashboard source label must not imply shared write.
Dashboard source label must not imply queue synchronization.
No source label UI is implemented in v0.7.5-C.
```

## 11. Read-only source selection boundary

```
Dashboard source read is not queue write.
Dashboard source read is not shared write.
Dashboard source read is not Worker dispatch.
Dashboard source read is not OpenClaw call.
Dashboard source read is not Hermes action.
Dashboard source read is not Google Sheets write.
Read-only source selection is planning only in v0.7.5-C.
```

## 12. Source switching boundary

```
No source switching runtime is implemented.
No Dashboard source switch button is added.
No Dashboard source switch route is added.
No backend source client is added.
No source-of-truth switch is performed.
No source configuration is changed.
Source switching requires a separate future plan and Owner approval.
```

## 13. Dashboard update boundary

A Dashboard update remains a `git pull` plus a Dashboard restart. It is not a backend source
migration, not a queue synchronization, and not a source-of-truth switch. Updating the
Dashboard code does not change which backend source an environment reads, and does not move
any queue data.

## 14. Queue sync and migration boundary

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
Dashboard backend source planning is not sync approval.
Dashboard backend source planning is not migration approval.
```

## 15. Source-of-truth boundary

Identifying and labeling a backend source does not make it authoritative. The current source
of truth remains local to each environment; a future remote blackboard does not become the
source of truth merely by being displayed. Any source-of-truth switch requires a separate
future plan and explicit Owner approval.

## 16. Data freshness and staleness boundary

```
Dashboard should eventually show data source freshness.
Dashboard should eventually show when a source is stale.
Dashboard should eventually show when a remote source is unavailable.
Stale data must not be treated as execution permission.
Unavailable source must not trigger fallback writes.
Unavailable source must not start Worker.
Unavailable source must not call OpenClaw or Hermes.
No freshness indicator is implemented in v0.7.5-C.
```

## 17. Owner visibility and safety indicator boundary

```
Owner must be able to see which backend source Dashboard is reading.
Owner must be able to see whether the source is local or remote.
Owner must be able to see whether the source is read-only.
Owner must be able to see whether Worker is OFF.
Owner must be able to see whether OpenClaw is Not Connected.
Owner must be able to see whether Hermes is Not Connected.
Owner must be able to see whether Google Sheets is Disabled.
No safety indicator UI is implemented in v0.7.5-C.
```

## 18. Error / unavailable source boundary

When a backend source is unavailable, the planned behavior is display-only: surface the
unavailability to the Owner and read nothing further. An unavailable source must not trigger
a fallback write, must not start the Worker, and must not call OpenClaw or Hermes. This is a
planning requirement only; no error-handling runtime is implemented in v0.7.5-C.

## 19. Blackboard message compatibility

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

## 20. Owner approval and activation boundary

```
Owner approval is required before any Dashboard backend source runtime.
Owner approval is required before any source switching runtime.
Owner approval is required before any remote blackboard runtime.
Owner approval is required before any shared DB.
Owner approval is required before any queue migration.
Owner approval is required before any queue synchronization.
Owner approval is required before any shared write.
Owner approval is required before any source-of-truth switch.
Plan approval is not runtime approval.
Plan approval is not source switching approval.
Plan approval is not migration approval.
Plan approval is not shared write approval.
```

## 21. Worker / OpenClaw / Hermes boundary

A Dashboard backend source read is not a Worker dispatch, not an OpenClaw call, and not a
Hermes action. Worker remains OFF, OpenClaw remains Not Connected, and Hermes remains Not
Connected. Execution dispatch stays separately gated behind Owner approval.

## 22. Data and secrets boundary

A Dashboard backend source provides display data only and must not store or expose secrets
or raw credentials, and must not expose any secret in a UI or in logs. Authentication
material, if any, lives outside the displayed data and is never committed to GitHub.

## 23. Candidate future dashboard source models

These are planning notes only — none is implemented or provisioned:

```
Candidate dashboard source model: local-only dashboard source.
Candidate dashboard source model: Replit local preview source.
Candidate dashboard source model: remote read-only blackboard source.
Candidate dashboard source model: selectable read-only source view.
Candidate dashboard source model: local runtime with remote audit mirror display.
Candidate dashboard source models are planning notes only.
No dashboard source model is implemented in v0.7.5-C.
```

## 24. Current safe system posture

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
No Dashboard backend source runtime.
No source switching runtime.
No queue synchronization.
No queue migration.
No queue backfill.
No queue merge.
No conflict resolver.
No connector.
No tag.
```

## 25. Validation summary

```
v0.7.5-C readiness: ALL PASS.
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

## 26. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 27. Non-goals

- Not implementing a Dashboard backend source runtime or a source switching runtime.
- Not implementing a Remote Blackboard API runtime.
- Not creating a production DB, shared DB, or remote shared DB.
- Not adding any API route, FastAPI router, dashboard backend client, remote backend client,
  database client, or migration.
- Not changing the Dashboard UI; not adding a source switch button or route.
- Not performing a source switch, source-of-truth switch, or source configuration change.
- Not synchronizing, migrating, moving, copying, merging, or backfilling any queue data.
- Not implementing a conflict resolver.
- Not opening shared write.
- Not reading a real queue DB; not sending any POST.
- Not starting the Worker; not calling OpenClaw / Hermes; not writing Google Sheets.
- Not creating a webhook, webhook receiver, or connector.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.

## 28. Acceptance criteria

- This plan document exists and contains sections 1–29.
- The current-master marker records `12e1286` on `origin/master`.
- The v0.7.5-C plan-first markers are present.
- The problem statement, Dashboard backend source definition, current local source boundary,
  Replit local source boundary, future remote blackboard source boundary, source identity
  and labeling boundary, read-only source selection boundary, source switching boundary,
  queue sync / migration boundary, data freshness / staleness boundary, Owner visibility /
  safety indicator boundary, blackboard message compatibility, Owner approval and activation
  boundary, candidate future dashboard source model, current safe posture, validation
  summary, and safety grep summary markers are present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script `check_hermes_openclaw_dashboard_backend_source_plan_v0_7_5_c.py`
  passes ALL.

## 29. Next recommended step

```
v0.7.5-D — Core Runtime Host Plan
```

with the constraints:

```
v0.7.5-D must remain plan-first unless separately approved.
v0.7.5-D must not create production DB.
v0.7.5-D must not create Remote Blackboard API runtime.
v0.7.5-D must not migrate queue data.
v0.7.5-D must not open shared write.
v0.7.5-D must not start Worker / OpenClaw / Hermes / Google Sheets.
```
