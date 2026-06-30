# HERMES ↔ OpenClaw Adapter — Owner Review Dashboard Preview Checklist Plan (v0.8.0-E)

> Plan-first document. This is **documentation only**. It plans the future read-only Dashboard
> Owner Review Checklist: its checklist contract, checklist item boundary, Owner decision
> visibility, approval-is-not-execution and approval-readiness boundaries, Decision audit
> checklist, dispatch-disabled checklist, Task / Result / Advice checklist, Dashboard display
> relationship, Dashboard route/template/static boundary, and local-only checklist boundary.
> It modifies no Dashboard, adds no route, changes no template, changes no static, implements
> no checklist runtime, implements no Dashboard preview display runtime, reads no real queue
> DB, writes no queue, sends no POST, starts no Worker, calls no OpenClaw, activates no Hermes,
> reads/writes no Google Sheets, creates no Remote Blackboard API runtime, creates no DB, and
> opens no shared write.

## 1. Purpose

This document plans — and only plans — the future read-only Dashboard Owner Review Checklist.
It defines what the checklist may show, what each item may describe, how Owner decision
visibility stays separate from execution, and which runtime stays disabled, so that a future
Owner review checklist can be designed against an agreed boundary before any Dashboard code or
runtime is changed.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. Planning Owner review Dashboard preview checklist is not
implementing Dashboard runtime.

## 2. Current master

```
HEAD = origin/master = 586f5b72c1b66154caa3ba663de7eddfa178d1cd
docs: plan read-only dashboard blackboard preview display
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.0-E is and is not:

```
v0.8.0-E Owner Review Dashboard Preview Checklist Plan is plan-first.
v0.8.0-E does not implement Blackboard Loop runtime.
v0.8.0-E does not implement Owner review checklist runtime.
v0.8.0-E does not implement Dashboard preview display runtime.
v0.8.0-E does not implement preview runtime.
v0.8.0-E does not create preview renderer runtime.
v0.8.0-E does not create Dashboard route.
v0.8.0-E does not create Dashboard endpoint.
v0.8.0-E does not create Dashboard template.
v0.8.0-E does not create Dashboard static asset.
v0.8.0-E does not modify Dashboard runtime.
v0.8.0-E does not modify app.
v0.8.0-E does not modify templates.
v0.8.0-E does not modify static.
v0.8.0-E does not implement loop contract runtime.
v0.8.0-E does not implement state machine runtime.
v0.8.0-E does not create loop scheduler.
v0.8.0-E does not enable dispatch gate.
v0.8.0-E does not enable autonomous execution.
v0.8.0-E does not activate Hermes.
v0.8.0-E does not connect Hermes.
v0.8.0-E does not connect OpenClaw.
v0.8.0-E does not start Worker.
v0.8.0-E does not create Hermes runtime.
v0.8.0-E does not create OpenClaw runtime.
v0.8.0-E does not create Worker runtime.
v0.8.0-E does not implement Remote Blackboard API runtime.
v0.8.0-E does not create production DB.
v0.8.0-E does not create shared DB.
v0.8.0-E does not create remote shared DB.
v0.8.0-E does not read real queue DB.
v0.8.0-E does not modify queue data.
v0.8.0-E does not migrate queue data.
v0.8.0-E does not sync local queue and remote queue.
v0.8.0-E does not open shared write.
v0.8.0-E does not read Google Sheets.
v0.8.0-E does not write Google Sheets.
v0.8.0-E does not send POST.
v0.8.0-E does not create webhook.
```

## 4. Relationship to v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan

```
v0.8.0-D Read-only Dashboard Blackboard Loop Preview Display Plan is complete.
v0.8.0-E starts the Owner Review Dashboard Preview Checklist planning step.
v0.8.0-E builds on Read-only Dashboard Blackboard Loop Preview Display planning.
v0.8.0-E plans Owner review checklist display before any Dashboard runtime change.
v0.8.0-E preserves Owner final approval authority.
v0.8.0-E preserves decision and dispatch separation.
v0.8.0-E preserves audit trail.
v0.8.0-E preserves dispatch-disabled boundary.
v0.8.0-E preserves local dry-run preview boundary.
v0.8.0-E preserves read-only Dashboard display boundary.
v0.8.0-E does not change any v0.8.0-D boundary.
v0.8.0-E does not change any v0.8.0-C boundary.
v0.8.0-E does not change any v0.8.0-B boundary.
v0.8.0-E does not change any v0.8.0-A boundary.
v0.8.0-E does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned Owner review Dashboard preview checklist before any checklist runtime can be implemented.
The Owner review checklist must not become execution permission.
The Owner review checklist must not become Worker dispatch.
The Owner review checklist must not call OpenClaw.
The Owner review checklist must not activate Hermes.
The Owner review checklist must not write queue data.
The Owner review checklist must not read real queue DB.
The Owner review checklist must not send POST.
The Owner review checklist must not read or write Google Sheets.
Planning Owner review Dashboard preview checklist is not implementing Dashboard runtime.
Planning Owner review Dashboard preview checklist is not running the loop.
```

## 6. Owner Review Dashboard Preview Checklist definition

```
Owner Review Dashboard Preview Checklist means a future read-only Dashboard checklist that helps the Owner review planned loop preview items.
Owner Review Dashboard Preview Checklist is a planning artifact in v0.8.0-E.
Owner Review Dashboard Preview Checklist is not runtime code.
Owner Review Dashboard Preview Checklist is not Dashboard route implementation.
Owner Review Dashboard Preview Checklist is not template implementation.
Owner Review Dashboard Preview Checklist is not static asset implementation.
Owner Review Dashboard Preview Checklist is not execution permission.
Owner Review Dashboard Preview Checklist is not queue write.
Owner Review Dashboard Preview Checklist is not real queue DB read.
Owner Review Dashboard Preview Checklist is not Worker dispatch.
Owner Review Dashboard Preview Checklist is not OpenClaw call.
Owner Review Dashboard Preview Checklist is not Hermes activation.
Owner Review Dashboard Preview Checklist is not Google Sheets write.
Owner Review Dashboard Preview Checklist requires separate future plan and Owner approval before implementation.
```

## 7. Owner review checklist contract boundary

```
Owner review checklist contract describes what a future read-only Owner checklist may show.
Owner review checklist contract is not execution permission.
Owner review checklist contract is not runtime approval.
Owner review checklist contract is not API route.
Owner review checklist contract is not database schema.
Owner review checklist contract is not Worker dispatch.
Owner review checklist contract is not OpenClaw call.
Owner review checklist contract is not Hermes action.
No Owner review checklist contract runtime is implemented in v0.8.0-E.
```

## 8. Checklist item boundary

```
Checklist item boundary is planning only.
Checklist item may describe planned message family.
Checklist item may describe planned state.
Checklist item may describe required Owner review.
Checklist item may describe dispatch-disabled status.
Checklist item may describe external side effect status.
Checklist item must not execute action.
Checklist item must not mutate queue.
Checklist item must not start Worker.
Checklist item must not call OpenClaw.
Checklist item must not call Hermes.
No checklist item runtime is implemented in v0.8.0-E.
```

## 9. Owner decision visibility boundary

```
Owner decision visibility means a future checklist may show that Owner decision is required.
Owner decision visibility is not Owner decision execution.
Owner decision visibility is not Worker dispatch.
Owner decision visibility is not OpenClaw call.
Owner decision visibility is not Hermes action.
Owner decision visibility must preserve Owner final approval authority.
No Owner decision visibility runtime is implemented in v0.8.0-E.
```

## 10. Approval is not execution boundary

```
Approval is not execution.
Owner approval display is not runtime dispatch.
Owner approval display is not Worker dispatch.
Owner approval display is not OpenClaw call.
Owner approval display is not Hermes action.
Owner approval display must preserve decision and dispatch separation.
No approval execution runtime is implemented in v0.8.0-E.
```

## 11. Approval readiness boundary

```
Approval readiness is not execution permission.
Approval readiness is not dispatch permission.
Approval readiness is not queue mutation.
Approval readiness is not Worker dispatch.
Approval readiness is not OpenClaw call.
Approval readiness is not Hermes action.
No approval readiness runtime is implemented in v0.8.0-E.
```

## 12. Decision audit checklist boundary

```
Decision audit checklist is display-only.
Decision audit checklist is audit checklist, not command.
Decision audit checklist is not Worker dispatch.
Decision audit checklist is not OpenClaw call.
Decision audit checklist is not Hermes action.
Decision audit checklist must preserve audit trail.
No Decision audit checklist runtime is implemented in v0.8.0-E.
```

## 13. Dispatch-disabled checklist boundary

```
Dispatch-disabled checklist means future checklist must visibly show dispatch is off.
Dispatch-disabled checklist must block Worker dispatch.
Dispatch-disabled checklist must block OpenClaw call.
Dispatch-disabled checklist must block Hermes action.
Dispatch-disabled checklist must block Google Sheets write.
Dispatch gate remains disabled in v0.8.0-E.
No dispatch-disabled checklist runtime is implemented in v0.8.0-E.
```

## 14. Task draft checklist boundary

```
Task draft checklist is display-only.
Task draft checklist is not queue write.
Task draft checklist is not Worker dispatch.
Task draft checklist is not OpenClaw call.
Task draft checklist is not Hermes action.
No Task draft checklist runtime is implemented in v0.8.0-E.
```

## 15. Result observation checklist boundary

```
Result observation checklist is display-only.
Result observation checklist is not next dispatch permission.
Result observation checklist is not automatic follow-up execution.
Result observation checklist is not Google Sheets write.
No Result observation checklist runtime is implemented in v0.8.0-E.
```

## 16. Advice observation checklist boundary

```
Advice observation checklist is display-only.
Advice observation checklist is advisory display, not command.
Advice observation checklist is not Worker dispatch.
Advice observation checklist is not OpenClaw call.
Advice observation checklist is not automatic execution.
No Advice observation checklist runtime is implemented in v0.8.0-E.
```

## 17. Dashboard display relationship

```
Dashboard may eventually display Owner review checklist.
Dashboard Owner review checklist display is read-only.
Dashboard Owner review checklist display is not dispatch.
Dashboard Owner review checklist display is not execution permission.
No Dashboard Owner review checklist display runtime is implemented in v0.8.0-E.
```

## 18. Dashboard route / template / static boundary

```
Dashboard route boundary is planning only.
No Dashboard route is created in v0.8.0-E.
No Dashboard endpoint is created in v0.8.0-E.
No Dashboard template is created in v0.8.0-E.
No Dashboard static asset is created in v0.8.0-E.
No app route is modified in v0.8.0-E.
No template file is modified in v0.8.0-E.
No static file is modified in v0.8.0-E.
```

## 19. Checklist source boundary

```
Checklist source boundary is planning only.
Checklist source boundary does not select production queue.
Checklist source boundary does not read real queue DB.
Checklist source boundary does not read Remote Blackboard API.
Checklist source boundary does not read Google Sheets.
Checklist source boundary does not switch source-of-truth.
No checklist source reader is implemented in v0.8.0-E.
```

## 20. Checklist input boundary

```
Checklist input may be future mock Task Message data.
Checklist input may be future mock Decision Message data.
Checklist input may be future mock Result Message data.
Checklist input may be future mock Advice Message data.
Checklist input must not require real queue DB read in v0.8.0-E.
Checklist input must not require secrets.
Checklist input must not require Google Sheets.
Checklist input must not require Remote Blackboard API runtime.
No checklist input reader is implemented in v0.8.0-E.
```

## 21. Checklist output boundary

```
Checklist output may be future read-only checklist card.
Checklist output may be future read-only checklist table.
Checklist output may be future read-only Owner action reminder.
Checklist output may be future read-only dispatch-disabled badge.
Checklist output must not write queue data.
Checklist output must not send POST.
Checklist output must not dispatch Worker.
Checklist output must not call OpenClaw.
Checklist output must not call Hermes.
Checklist output must not write Google Sheets.
No checklist output renderer is implemented in v0.8.0-E.
```

## 22. Local-only Dashboard checklist boundary

```
Local-only Dashboard checklist plan does not select production host.
Local-only Dashboard checklist plan does not create runtime host.
Local-only Dashboard checklist plan does not deploy service.
Local-only Dashboard checklist plan does not create systemd service.
Local-only Dashboard checklist plan does not create daemon.
Local-only Dashboard checklist plan does not create Docker deployment.
```

## 23. Queue and data boundary

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

## 24. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.0-E.
Remote Blackboard API read is not enabled in v0.8.0-E.
Remote Blackboard API write is not enabled in v0.8.0-E.
Remote Blackboard API is not required for Owner review checklist planning.
```

## 25. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Worker must not run from plan-only Owner review checklist.
OpenClaw must not execute from plan-only Owner review checklist.
Hermes must not act from plan-only Owner review checklist.
```

## 26. Google Sheets boundary

```
Google Sheets remains Disabled.
No Google Sheets read is required.
No Google Sheets write is performed.
No Google Sheets live write is enabled.
```

## 27. Secrets / privacy / memory boundary

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

## 28. Network / webhook / connector boundary

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

## 29. Failure / rollback / audit boundary

```
Future Owner review checklist changes must be auditable.
Future Owner review checklist actions must include rollback notes when external actions are involved.
Future Owner review checklist failures must not silently retry external actions.
Future Owner review checklist failures must not bypass Owner approval.
Future Owner review checklist failures must not write Google Sheets by default.
Future Owner review checklist failures must not call OpenClaw by default.
Future Owner review checklist failures must not start Worker by default.
No Owner review checklist failure handling runtime is implemented in v0.8.0-E.
```

## 30. Candidate Owner review checklist fields

These are candidate planning notes only. No candidate Owner review checklist field is implemented.

```
Candidate Owner review checklist field: checklist_id.
Candidate Owner review checklist field: preview_id.
Candidate Owner review checklist field: checklist_mode.
Candidate Owner review checklist field: message_family.
Candidate Owner review checklist field: planned_state.
Candidate Owner review checklist field: owner_review_required.
Candidate Owner review checklist field: owner_decision_required.
Candidate Owner review checklist field: approval_is_execution.
Candidate Owner review checklist field: approval_readiness_is_execution.
Candidate Owner review checklist field: dispatch_enabled.
Candidate Owner review checklist field: dispatch_disabled_badge.
Candidate Owner review checklist field: external_side_effects.
Candidate Owner review checklist field: queue_read_required.
Candidate Owner review checklist field: queue_write_required.
Candidate Owner review checklist field: worker_dispatch_allowed.
Candidate Owner review checklist field: openclaw_call_allowed.
Candidate Owner review checklist field: hermes_action_allowed.
Candidate Owner review checklist field: google_sheets_write_allowed.
Candidate Owner review checklist field: safety_notes.
Candidate Owner review checklist field: next_owner_action.
Candidate Owner review checklist fields are planning only.
No candidate Owner review checklist field is implemented in v0.8.0-E.
No schema migration is performed in v0.8.0-E.
```

## 31. Candidate Owner review checklist validation rules

These are candidate planning notes only. No Owner review checklist validation runtime is implemented.

```
Candidate Owner review checklist validation rule: approval_is_execution must remain false.
Candidate Owner review checklist validation rule: approval_readiness_is_execution must remain false.
Candidate Owner review checklist validation rule: dispatch_enabled must remain false.
Candidate Owner review checklist validation rule: external_side_effects must remain false.
Candidate Owner review checklist validation rule: queue_read_required must remain false unless separately approved.
Candidate Owner review checklist validation rule: queue_write_required must remain false.
Candidate Owner review checklist validation rule: worker_dispatch_allowed must remain false.
Candidate Owner review checklist validation rule: openclaw_call_allowed must remain false.
Candidate Owner review checklist validation rule: hermes_action_allowed must remain false.
Candidate Owner review checklist validation rule: google_sheets_write_allowed must remain false.
Candidate Owner review checklist validation rules are planning only.
No Owner review checklist validation runtime is implemented in v0.8.0-E.
```

## 32. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only Owner review checklist plan.
Candidate future phase: candidate Owner review checklist field inventory.
Candidate future phase: local mock-data read-only Owner review checklist display.
Candidate future phase: read-only Owner decision visibility display.
Candidate future phase: read-only dispatch-disabled checklist badge display.
Candidate future phase: read-only Decision audit checklist display.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.0-E.
No candidate future phase is enabled in v0.8.0-E.
```

## 33. Disabled runtime list

```
Blackboard Loop runtime is disabled.
Owner review checklist runtime is disabled.
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

## 34. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
No Blackboard Loop runtime.
No Owner review checklist runtime.
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

## 35. Validation summary

```
v0.8.0-E readiness: ALL PASS.
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

## 36. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 37. Non-goals

This round is a plan. The following are explicitly out of scope:

- Implementing any Blackboard Loop runtime, Owner review checklist runtime, Dashboard preview display runtime, preview renderer runtime, loop contract runtime, or state machine runtime.
- Creating or modifying any Dashboard route, endpoint, template, or static asset.
- Modifying app, templates, or static.
- Creating any loop scheduler or checklist validation runtime.
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

## 38. Acceptance criteria

```
v0.8.0-E adds only two files: the plan doc and the readiness script.
v0.8.0-E modifies no existing app / scripts / docs / README / templates / static / runtime.
v0.8.0-E readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 39. Next recommended step

```
v0.8.0-F — Decision Audit Dashboard Preview Display Plan
```

The next step must remain plan-first:

```
v0.8.0-F must remain plan-first unless separately approved.
v0.8.0-F must not implement Blackboard Loop runtime.
v0.8.0-F must not implement Owner review checklist runtime.
v0.8.0-F must not implement Dashboard preview display runtime.
v0.8.0-F must not enable dispatch gate.
v0.8.0-F must not activate Hermes.
v0.8.0-F must not connect OpenClaw.
v0.8.0-F must not start Worker.
v0.8.0-F must not create production DB.
v0.8.0-F must not create Remote Blackboard API runtime unless separately approved.
v0.8.0-F must not migrate queue data.
v0.8.0-F must not open shared write.
v0.8.0-F must not write Google Sheets.
```
