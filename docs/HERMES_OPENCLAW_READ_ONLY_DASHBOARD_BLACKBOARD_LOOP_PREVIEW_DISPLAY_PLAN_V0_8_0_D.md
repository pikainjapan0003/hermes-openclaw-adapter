# HERMES ↔ OpenClaw Adapter — Read-only Dashboard Blackboard Loop Preview Display Plan (v0.8.0-D)

> Plan-first document. This is **documentation only**. It plans the future read-only Dashboard
> display of the Blackboard Loop preview: its Dashboard display contract, display source
> boundary, mock / planned preview input/output, read-only display state, Owner review
> checklist display, dispatch-disabled display, Task / Result / Advice display, Dashboard
> route/template/static boundary, and local-only display boundary. It modifies no Dashboard,
> adds no route, changes no template, changes no static, implements no preview display
> runtime, reads no real queue DB, writes no queue, sends no POST, starts no Worker, calls no
> OpenClaw, activates no Hermes, reads/writes no Google Sheets, creates no Remote Blackboard
> API runtime, creates no DB, and opens no shared write.

## 1. Purpose

This document plans — and only plans — the future read-only Dashboard display of the
Blackboard Loop preview. It defines what the Dashboard may show, where its display data may
come from, what input it may take, what output it may render, and which runtime stays
disabled, so that a future read-only Dashboard preview display can be designed against an
agreed boundary before any Dashboard code or runtime is changed.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. Planning read-only Dashboard preview display is not
implementing Dashboard runtime.

## 2. Current master

```
HEAD = origin/master = 94f5f51dfcf404b5ebc87aa9d1830a05ee8be353
docs: plan local dry-run blackboard loop preview
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.0-D is and is not:

```
v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan is plan-first.
v0.8.0-D does not implement Blackboard Loop runtime.
v0.8.0-D does not implement Dashboard preview display runtime.
v0.8.0-D does not implement preview runtime.
v0.8.0-D does not create preview renderer runtime.
v0.8.0-D does not create Dashboard route.
v0.8.0-D does not create Dashboard endpoint.
v0.8.0-D does not create Dashboard template.
v0.8.0-D does not create Dashboard static asset.
v0.8.0-D does not modify Dashboard runtime.
v0.8.0-D does not modify app.
v0.8.0-D does not modify templates.
v0.8.0-D does not modify static.
v0.8.0-D does not implement loop contract runtime.
v0.8.0-D does not implement state machine runtime.
v0.8.0-D does not create loop scheduler.
v0.8.0-D does not enable dispatch gate.
v0.8.0-D does not enable autonomous execution.
v0.8.0-D does not activate Hermes.
v0.8.0-D does not connect Hermes.
v0.8.0-D does not connect OpenClaw.
v0.8.0-D does not start Worker.
v0.8.0-D does not create Hermes runtime.
v0.8.0-D does not create OpenClaw runtime.
v0.8.0-D does not create Worker runtime.
v0.8.0-D does not implement Remote Blackboard API runtime.
v0.8.0-D does not create production DB.
v0.8.0-D does not create shared DB.
v0.8.0-D does not create remote shared DB.
v0.8.0-D does not read real queue DB.
v0.8.0-D does not modify queue data.
v0.8.0-D does not migrate queue data.
v0.8.0-D does not sync local queue and remote queue.
v0.8.0-D does not open shared write.
v0.8.0-D does not read Google Sheets.
v0.8.0-D does not write Google Sheets.
v0.8.0-D does not send POST.
v0.8.0-D does not create webhook.
```

## 4. Relationship to v0.8.0-C Local Dry-run Blackboard Loop Preview Plan

```
v0.8.0-C Local Dry-run Blackboard Loop Preview Plan is complete.
v0.8.0-D starts the Read-only Dashboard Blackboard Loop Preview Display planning step.
v0.8.0-D builds on Local Dry-run Blackboard Loop Preview planning.
v0.8.0-D plans read-only Dashboard preview display before any Dashboard runtime change.
v0.8.0-D preserves Owner final approval authority.
v0.8.0-D preserves decision and dispatch separation.
v0.8.0-D preserves audit trail.
v0.8.0-D preserves dispatch-disabled boundary.
v0.8.0-D preserves local dry-run preview boundary.
v0.8.0-D does not change any v0.8.0-C boundary.
v0.8.0-D does not change any v0.8.0-B boundary.
v0.8.0-D does not change any v0.8.0-A boundary.
v0.8.0-D does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned read-only Dashboard preview display before any Dashboard preview runtime can be implemented.
The Dashboard preview display must not read real queue DB.
The Dashboard preview display must not write queue data.
The Dashboard preview display must not send POST.
The Dashboard preview display must not become Worker dispatch.
The Dashboard preview display must not call OpenClaw.
The Dashboard preview display must not activate Hermes.
The Dashboard preview display must not write Google Sheets.
Planning read-only Dashboard preview display is not implementing Dashboard runtime.
Planning read-only Dashboard preview display is not running the loop.
```

## 6. Read-only Dashboard Blackboard Loop preview display definition

```
Read-only Dashboard Blackboard Loop preview display means a future Dashboard-only display of planned loop preview states and messages.
Read-only Dashboard Blackboard Loop preview display is a planning artifact in v0.8.0-D.
Read-only Dashboard Blackboard Loop preview display is not runtime code.
Read-only Dashboard Blackboard Loop preview display is not Dashboard route implementation.
Read-only Dashboard Blackboard Loop preview display is not template implementation.
Read-only Dashboard Blackboard Loop preview display is not static asset implementation.
Read-only Dashboard Blackboard Loop preview display is not queue write.
Read-only Dashboard Blackboard Loop preview display is not real queue DB read.
Read-only Dashboard Blackboard Loop preview display is not Worker dispatch.
Read-only Dashboard Blackboard Loop preview display is not OpenClaw call.
Read-only Dashboard Blackboard Loop preview display is not Hermes activation.
Read-only Dashboard Blackboard Loop preview display is not Google Sheets write.
Read-only Dashboard Blackboard Loop preview display requires separate future plan and Owner approval before implementation.
```

## 7. Dashboard display contract boundary

```
Dashboard display contract describes what a future read-only Dashboard preview may show.
Dashboard display contract is not execution permission.
Dashboard display contract is not runtime approval.
Dashboard display contract is not API route.
Dashboard display contract is not database schema.
Dashboard display contract is not Worker dispatch.
Dashboard display contract is not OpenClaw call.
Dashboard display contract is not Hermes action.
No Dashboard display contract runtime is implemented in v0.8.0-D.
```

## 8. Dashboard source boundary

```
Dashboard source boundary is planning only.
Dashboard source boundary does not select production queue.
Dashboard source boundary does not read real queue DB.
Dashboard source boundary does not read Remote Blackboard API.
Dashboard source boundary does not read Google Sheets.
Dashboard source boundary does not switch source-of-truth.
No Dashboard source reader is implemented in v0.8.0-D.
```

## 9. Dashboard preview input boundary

```
Dashboard preview input may be future mock Task Message data.
Dashboard preview input may be future mock Decision Message data.
Dashboard preview input may be future mock Result Message data.
Dashboard preview input may be future mock Advice Message data.
Dashboard preview input must not require real queue DB read in v0.8.0-D.
Dashboard preview input must not require secrets.
Dashboard preview input must not require Google Sheets.
Dashboard preview input must not require Remote Blackboard API runtime.
No Dashboard preview input reader is implemented in v0.8.0-D.
```

## 10. Dashboard preview output boundary

```
Dashboard preview output may be future read-only card display.
Dashboard preview output may be future read-only state table.
Dashboard preview output may be future read-only Owner review checklist.
Dashboard preview output may be future read-only dispatch-disabled badge.
Dashboard preview output must not write queue data.
Dashboard preview output must not send POST.
Dashboard preview output must not dispatch Worker.
Dashboard preview output must not call OpenClaw.
Dashboard preview output must not call Hermes.
Dashboard preview output must not write Google Sheets.
No Dashboard preview output renderer is implemented in v0.8.0-D.
```

## 11. Read-only display state boundary

```
Read-only display state is display-only planning state.
Read-only display state is not execution permission.
Read-only display state is not queue mutation.
Read-only display state is not Worker dispatch.
Read-only display state is not OpenClaw call.
Read-only display state is not Hermes action.
Read-only display state is not Google Sheets write.
No read-only display state runtime is implemented in v0.8.0-D.
```

## 12. Owner review checklist display boundary

```
Owner review checklist display is display-only.
Owner review checklist display is not execution permission.
Owner review checklist display is not Worker dispatch.
Owner review checklist display must preserve approve is not execute.
Owner review checklist display must preserve approval readiness is not execution permission.
No Owner review checklist display runtime is implemented in v0.8.0-D.
```

## 13. Decision audit display boundary

```
Decision audit display is display-only.
Decision audit display is audit display, not command.
Decision audit display is not Worker dispatch.
Decision audit display is not OpenClaw call.
Decision audit display is not Hermes action.
No Decision audit display runtime is implemented in v0.8.0-D.
```

## 14. Dispatch-disabled display boundary

```
Dispatch-disabled display means future Dashboard display must visibly show dispatch is off.
Dispatch-disabled display must block Worker dispatch.
Dispatch-disabled display must block OpenClaw call.
Dispatch-disabled display must block Hermes action.
Dispatch-disabled display must block Google Sheets write.
Dispatch gate remains disabled in v0.8.0-D.
No dispatch-disabled display runtime is implemented in v0.8.0-D.
```

## 15. Task draft display boundary

```
Task draft display is display-only.
Task draft display is not queue write.
Task draft display is not Worker dispatch.
Task draft display is not OpenClaw call.
Task draft display is not Hermes action.
No Task draft display runtime is implemented in v0.8.0-D.
```

## 16. Result observation display boundary

```
Result observation display is display-only.
Result observation display is not next dispatch permission.
Result observation display is not automatic follow-up execution.
Result observation display is not Google Sheets write.
No Result observation display runtime is implemented in v0.8.0-D.
```

## 17. Advice observation display boundary

```
Advice observation display is display-only.
Advice observation display is advisory display, not command.
Advice observation display is not Worker dispatch.
Advice observation display is not OpenClaw call.
Advice observation display is not automatic execution.
No Advice observation display runtime is implemented in v0.8.0-D.
```

## 18. Local-only Dashboard display boundary

```
Local-only Dashboard display plan does not select production host.
Local-only Dashboard display plan does not create runtime host.
Local-only Dashboard display plan does not deploy service.
Local-only Dashboard display plan does not create systemd service.
Local-only Dashboard display plan does not create daemon.
Local-only Dashboard display plan does not create Docker deployment.
```

## 19. Queue and data display boundary

```
No source-of-truth switch is performed.
No queue DB change.
No local queue data change.
No Replit queue data change.
No real queue DB read.
No queue migration is performed.
No queue synchronization is performed.
No queue backfill is performed.
No queue merge is performed.
No conflict resolver is implemented.
No shared write is enabled.
```

## 20. Dashboard route / template / static boundary

```
Dashboard route boundary is planning only.
No Dashboard route is created in v0.8.0-D.
No Dashboard endpoint is created in v0.8.0-D.
No Dashboard template is created in v0.8.0-D.
No Dashboard static asset is created in v0.8.0-D.
No app route is modified in v0.8.0-D.
No template file is modified in v0.8.0-D.
No static file is modified in v0.8.0-D.
```

## 21. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.0-D.
Remote Blackboard API read is not enabled in v0.8.0-D.
Remote Blackboard API write is not enabled in v0.8.0-D.
Remote Blackboard API is not required for read-only Dashboard preview display planning.
```

## 22. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Worker must not run from plan-only Dashboard display.
OpenClaw must not execute from plan-only Dashboard display.
Hermes must not act from plan-only Dashboard display.
```

## 23. Google Sheets boundary

```
Google Sheets remains Disabled.
No Google Sheets read is required.
No Google Sheets write is performed.
No Google Sheets live write is enabled.
```

## 24. Secrets / privacy / memory boundary

```
No secrets are read.
No secrets are copied.
No secrets are created.
No .env file is created.
No credentials are moved.
No production secrets are copied.
No Hermes memory store is created.
No Hermes learning runtime is created.
No private conversation log is created.
No all-conversation logging is enabled.
```

## 25. Network / webhook / connector boundary

```
No webhook is created.
No webhook receiver is created.
No connector is created.
No external network call is added.
No inbound listener is added.
No outbound integration is added.
No port exposure is configured.
No POST is sent.
No live queue write validation is performed.
```

## 26. Failure / rollback / audit boundary

```
Future Dashboard display changes must be auditable.
Future Dashboard display actions must include rollback notes when external actions are involved.
Future Dashboard display failures must not silently retry external actions.
Future Dashboard display failures must not bypass Owner approval.
Future Dashboard display failures must not write Google Sheets by default.
Future Dashboard display failures must not call OpenClaw by default.
Future Dashboard display failures must not start Worker by default.
No Dashboard display failure handling runtime is implemented in v0.8.0-D.
```

## 27. Candidate Dashboard display fields

These are candidate planning notes only. No candidate Dashboard display field is implemented.

```
Candidate Dashboard display field: preview_id.
Candidate Dashboard display field: preview_mode.
Candidate Dashboard display field: message_family.
Candidate Dashboard display field: planned_state.
Candidate Dashboard display field: owner_review_required.
Candidate Dashboard display field: dispatch_enabled.
Candidate Dashboard display field: dispatch_disabled_badge.
Candidate Dashboard display field: external_side_effects.
Candidate Dashboard display field: queue_read_required.
Candidate Dashboard display field: queue_write_required.
Candidate Dashboard display field: worker_dispatch_allowed.
Candidate Dashboard display field: openclaw_call_allowed.
Candidate Dashboard display field: hermes_action_allowed.
Candidate Dashboard display field: google_sheets_write_allowed.
Candidate Dashboard display field: safety_notes.
Candidate Dashboard display field: next_owner_action.
Candidate Dashboard display fields are planning only.
No candidate Dashboard display field is implemented in v0.8.0-D.
No schema migration is performed in v0.8.0-D.
```

## 28. Candidate Dashboard display validation rules

These are candidate planning notes only. No Dashboard display validation runtime is implemented.

```
Candidate Dashboard display validation rule: dispatch_enabled must remain false.
Candidate Dashboard display validation rule: external_side_effects must remain false.
Candidate Dashboard display validation rule: queue_read_required must remain false unless separately approved.
Candidate Dashboard display validation rule: queue_write_required must remain false.
Candidate Dashboard display validation rule: worker_dispatch_allowed must remain false.
Candidate Dashboard display validation rule: openclaw_call_allowed must remain false.
Candidate Dashboard display validation rule: hermes_action_allowed must remain false.
Candidate Dashboard display validation rule: google_sheets_write_allowed must remain false.
Candidate Dashboard display validation rules are planning only.
No Dashboard display validation runtime is implemented in v0.8.0-D.
```

## 29. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only Dashboard display plan.
Candidate future phase: candidate Dashboard display field inventory.
Candidate future phase: local mock-data read-only Dashboard preview display.
Candidate future phase: read-only Owner review checklist display.
Candidate future phase: read-only dispatch-disabled badge display.
Candidate future phase: read-only Result and Advice observation display.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.0-D.
No candidate future phase is enabled in v0.8.0-D.
```

## 30. Disabled runtime list

```
Blackboard Loop runtime is disabled.
Dashboard preview display runtime is disabled.
Local dry-run preview runtime is disabled.
Preview renderer runtime is disabled.
Loop contract runtime is disabled.
State machine runtime is disabled.
Loop scheduler is disabled.
Dispatch gate is disabled.
Worker runtime is disabled.
OpenClaw runtime is disabled.
Hermes runtime is disabled.
Remote Blackboard API runtime is disabled.
Shared write is disabled.
Google Sheets write is disabled.
Autonomous execution is disabled.
```

## 31. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
No Blackboard Loop runtime.
No Dashboard preview display runtime.
No local dry-run preview runtime.
No preview renderer runtime.
No loop contract runtime.
No state machine runtime.
No loop scheduler.
No dispatch gate enabled.
No autonomous execution.
No Hermes activation.
No Hermes blackboard mode.
No Hermes runtime.
No Hermes memory store.
No all-conversation logging.
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
No Google Sheets read.
No Google Sheets write.
No secrets read.
No secrets copied.
No .env created.
No webhook.
No external side effects.
No production DB.
No shared DB.
No remote shared DB.
No Remote Blackboard API runtime.
No Dashboard route created.
No Dashboard endpoint created.
No Dashboard template created.
No Dashboard static asset created.
No app route modified.
No template file modified.
No static file modified.
No Core runtime host.
No Worker runtime.
No OpenClaw runtime.
No systemd service.
No daemon.
No Docker deployment.
No queue synchronization.
No queue migration.
No queue backfill.
No queue merge.
No conflict resolver.
No connector.
No tag.
```

## 32. Validation summary

```
v0.8.0-D readiness: ALL PASS.
v0.8.0-C readiness: ALL PASS.
v0.8.0-B readiness: ALL PASS.
v0.8.0-A readiness: ALL PASS.
v0.7.5-R readiness: ALL PASS.
v0.7.5-E readiness: ALL PASS.
v0.7.5-D readiness: ALL PASS.
v0.7.5-C readiness: ALL PASS.
v0.7.5-B readiness: ALL PASS.
v0.7.5-A readiness: ALL PASS.
compileall scripts: PASS.
```

## 33. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 34. Non-goals

This round is a plan. The following are explicitly out of scope:

- Implementing any Blackboard Loop runtime, Dashboard preview display runtime, preview renderer runtime, loop contract runtime, or state machine runtime.
- Creating or modifying any Dashboard route, endpoint, template, or static asset.
- Modifying app, templates, or static.
- Creating any loop scheduler or Dashboard display validation runtime.
- Enabling any dispatch gate; enabling autonomous execution.
- Activating or connecting Hermes; connecting OpenClaw; starting Worker.
- Creating any Hermes / OpenClaw / Worker runtime.
- Implementing the Remote Blackboard API runtime, route, read, or write.
- Creating any production DB, shared DB, or remote shared DB.
- Reading the real queue DB; modifying, migrating, syncing, backfilling, or merging queue data.
- Opening shared write; enabling Hermes blackboard mode; reading or writing Google Sheets.
- Reading, copying, or creating secrets; creating `.env`; moving credentials.
- Creating any webhook, connector, listener, or external integration.
- Sending any POST or performing live local queue write validation.
- Any commit, push, or tag in this round.

## 35. Acceptance criteria

```
v0.8.0-D adds only two files: the plan doc and the readiness script.
v0.8.0-D modifies no existing app / scripts / docs / README / templates / static / runtime.
v0.8.0-D readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 36. Next recommended step

```
v0.8.0-E — Owner Review Dashboard Preview Checklist Plan
```

The next step must remain plan-first:

```
v0.8.0-E must remain plan-first unless separately approved.
v0.8.0-E must not implement Blackboard Loop runtime.
v0.8.0-E must not implement Dashboard preview display runtime.
v0.8.0-E must not implement preview runtime.
v0.8.0-E must not enable dispatch gate.
v0.8.0-E must not activate Hermes.
v0.8.0-E must not connect OpenClaw.
v0.8.0-E must not start Worker.
v0.8.0-E must not create production DB.
v0.8.0-E must not create Remote Blackboard API runtime unless separately approved.
v0.8.0-E must not migrate queue data.
v0.8.0-E must not open shared write.
v0.8.0-E must not write Google Sheets.
```
