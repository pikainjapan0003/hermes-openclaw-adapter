# HERMES ↔ OpenClaw Adapter — Local Mock Data Preview Implementation Boundary Plan (v0.8.1-A)

> Plan-first document. This is **documentation only**. It defines the safety boundary for a
> future Local Mock Data Preview Implementation — how a future read-only Dashboard preview may
> render **mock** (synthetic, local-only) message data so the Owner can review preview layout
> without ever touching real data or execution. It defines the mock data source boundary, the
> per-message-family preview boundaries (Mock Task Message, Mock Decision Message, Mock Result
> Message, Mock Advice Message, Mock Badge Status, Mock Runtime-off Status), the preview input /
> output boundary, the read-only preview boundary, the Dashboard route/template/static boundary,
> and the runtime / queue / Worker / OpenClaw / Hermes / Google Sheets separation boundaries. It
> implements no Dashboard preview display runtime, implements no local mock data preview runtime,
> creates no mock data fixture file, creates no preview data loader, adds no route, changes no
> template, changes no static, reads no real queue DB, writes no queue, sends no POST, starts no
> Worker, calls no OpenClaw, activates no Hermes, reads/writes no Google Sheets, creates no
> Remote Blackboard API runtime, creates no DB, and opens no shared write.

## 1. Purpose

This document plans — and only plans — the safety boundary that a future Local Mock Data Preview
Implementation must respect. v0.8.1 is the first step that prepares to move from pure plan-first
into mock-data / local read-only preview implementation. Because of that transition risk, this
round (v0.8.1-A) does **only** boundary planning: it defines what mock data preview may eventually
display, what each mock message family may contain, how mock preview stays display-only and
local-only, and which runtime stays disabled, so that a future preview can be implemented against
an agreed boundary before any Dashboard code, fixture, loader, or runtime is changed.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. Planning a local mock data preview boundary is not implementing
Dashboard runtime, not creating a fixture file, and not creating a preview data loader.

## 2. Current master

```
HEAD = origin/master = c6dda5017f660a8737955f40d65d9e2acde4be1d
docs: plan dispatch disabled dashboard preview badge
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.1-A is and is not:

```
v0.8.1-A Local Mock Data Preview Implementation Boundary Plan is plan-first.
v0.8.1-A does not implement Dashboard preview display runtime.
v0.8.1-A does not implement local mock data preview runtime.
v0.8.1-A does not create mock data fixture file.
v0.8.1-A does not create preview data loader.
v0.8.1-A does not create Dashboard route.
v0.8.1-A does not create Dashboard endpoint.
v0.8.1-A does not create Dashboard template.
v0.8.1-A does not create Dashboard static asset.
v0.8.1-A does not modify app.
v0.8.1-A does not modify templates.
v0.8.1-A does not modify static.
v0.8.1-A does not read real queue DB.
v0.8.1-A does not write queue data.
v0.8.1-A does not send POST.
v0.8.1-A does not start Worker.
v0.8.1-A does not connect OpenClaw.
v0.8.1-A does not activate Hermes.
v0.8.1-A does not connect Hermes.
v0.8.1-A does not read Google Sheets.
v0.8.1-A does not write Google Sheets.
v0.8.1-A does not read secrets.
v0.8.1-A does not create .env.
v0.8.1-A does not create webhook.
v0.8.1-A does not create connector.
v0.8.1-A does not create Remote Blackboard API runtime.
v0.8.1-A does not create production DB.
v0.8.1-A does not create shared DB.
v0.8.1-A does not open shared write.
```

## 4. Relationship to v0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan

```
v0.8.0-G Dispatch-disabled Dashboard Preview Badge Plan is complete.
v0.8.1-A starts the Local Mock Data Preview Implementation Boundary planning step.
v0.8.1-A builds on Dispatch-disabled Dashboard Preview Badge planning.
v0.8.1-A plans local mock data preview boundaries before any Dashboard runtime change.
v0.8.1-A preserves Owner final approval authority.
v0.8.1-A preserves decision and dispatch separation.
v0.8.1-A preserves audit trail.
v0.8.1-A preserves dispatch-disabled boundary.
v0.8.1-A preserves local dry-run preview boundary.
v0.8.1-A preserves read-only Dashboard display boundary.
v0.8.1-A preserves Owner review checklist boundary.
v0.8.1-A preserves dispatch-disabled Dashboard preview badge boundary.
v0.8.1-A does not change any v0.8.0-G boundary.
v0.8.1-A does not change any v0.8.0-F boundary.
v0.8.1-A does not change any v0.8.0-E boundary.
v0.8.1-A does not change any v0.8.0-D boundary.
v0.8.1-A does not change any v0.8.0-C boundary.
v0.8.1-A does not change any v0.8.0-B boundary.
v0.8.1-A does not change any v0.8.0-A boundary.
v0.8.1-A does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned local mock data preview boundary before any mock data preview runtime can be implemented.
Mock data preview must not become execution permission.
Mock data preview must not become Worker dispatch.
Mock data preview must not call OpenClaw.
Mock data preview must not activate Hermes.
Mock data preview must not write queue data.
Mock data preview must not read real queue DB.
Mock data preview must not send POST.
Mock data preview must not read or write Google Sheets.
A preview built on real data or live runtime could be mistaken for an execution surface.
Planning the local mock data preview boundary is not implementing Dashboard runtime.
Planning the local mock data preview boundary is not running the loop.
```

## 6. Local Mock Data Preview Implementation Boundary definition

```
Local Mock Data Preview Implementation Boundary means the agreed limits for a future read-only Dashboard preview that renders synthetic local-only mock message data.
Local Mock Data Preview Implementation Boundary is a planning artifact in v0.8.1-A.
Local Mock Data Preview Implementation Boundary is not runtime code.
Local Mock Data Preview Implementation Boundary is not Dashboard route implementation.
Local Mock Data Preview Implementation Boundary is not template implementation.
Local Mock Data Preview Implementation Boundary is not static asset implementation.
Local Mock Data Preview Implementation Boundary is not a mock data fixture file.
Local Mock Data Preview Implementation Boundary is not a preview data loader.
Local Mock Data Preview Implementation Boundary is not execution permission.
Local Mock Data Preview Implementation Boundary is not queue write.
Local Mock Data Preview Implementation Boundary is not real queue DB read.
Local Mock Data Preview Implementation Boundary is not Worker dispatch.
Local Mock Data Preview Implementation Boundary is not OpenClaw call.
Local Mock Data Preview Implementation Boundary is not Hermes activation.
Local Mock Data Preview Implementation Boundary is not Google Sheets write.
Local Mock Data Preview Implementation Boundary requires separate future plan and Owner approval before implementation.
```

## 7. Mock data source boundary

```
Mock data source boundary is planning only.
Mock data source is synthetic local-only sample data.
Mock data source does not select production queue.
Mock data source does not read real queue DB.
Mock data source does not read Remote Blackboard API.
Mock data source does not read Google Sheets.
Mock data source does not read secrets.
Mock data source does not switch source-of-truth.
No mock data source reader is implemented in v0.8.1-A.
No mock data fixture file is created in v0.8.1-A.
```

## 8. Mock Task Message preview boundary

```
Mock Task Message is synthetic local-only sample data.
Mock Task Message preview is display-only.
Mock Task Message preview is not execution permission.
Mock Task Message preview is not Worker dispatch.
Mock Task Message preview is not OpenClaw call.
Mock Task Message preview is not Hermes action.
Mock Task Message preview must not write queue data.
Mock Task Message preview must not read real queue DB.
No Mock Task Message preview runtime is implemented in v0.8.1-A.
```

## 9. Mock Decision Message preview boundary

```
Mock Decision Message is synthetic local-only sample data.
Mock Decision Message preview is display-only.
Mock Decision Message preview is not execution permission.
Mock Decision Message preview is not decision execution.
Mock Decision Message preview is not Worker dispatch.
Mock Decision Message preview is not OpenClaw call.
Mock Decision Message preview is not Hermes action.
Mock Decision Message preview must not write queue data.
Mock Decision Message preview must not read real queue DB.
No Mock Decision Message preview runtime is implemented in v0.8.1-A.
```

## 10. Mock Result Message preview boundary

```
Mock Result Message is synthetic local-only sample data.
Mock Result Message preview is display-only.
Mock Result Message preview is not execution permission.
Mock Result Message preview is not Worker dispatch.
Mock Result Message preview is not OpenClaw call.
Mock Result Message preview is not Hermes action.
Mock Result Message preview must not write queue data.
Mock Result Message preview must not read real queue DB.
No Mock Result Message preview runtime is implemented in v0.8.1-A.
```

## 11. Mock Advice Message preview boundary

```
Mock Advice Message is synthetic local-only sample data.
Mock Advice Message preview is display-only.
Mock Advice Message preview is not execution permission.
Mock Advice Message preview is not Worker dispatch.
Mock Advice Message preview is not OpenClaw call.
Mock Advice Message preview is not Hermes action.
Mock Advice Message preview must not write queue data.
Mock Advice Message preview must not read real queue DB.
No Mock Advice Message preview runtime is implemented in v0.8.1-A.
```

## 12. Mock runtime-off Badge preview boundary

```
Mock Badge Status is synthetic local-only sample data.
Mock Runtime-off Status is synthetic local-only sample data.
Mock runtime-off Badge preview may show DISPATCH OFF.
Mock runtime-off Badge preview may show WORKER OFF.
Mock runtime-off Badge preview may show OPENCLAW NOT CONNECTED.
Mock runtime-off Badge preview may show HERMES NOT CONNECTED.
Mock runtime-off Badge preview may show GOOGLE SHEETS DISABLED.
Mock runtime-off Badge preview is display-only.
Mock runtime-off Badge preview is not execution permission.
Mock runtime-off Badge preview must not enable dispatch gate.
Mock runtime-off Badge preview must not start Worker.
Mock runtime-off Badge preview must not connect OpenClaw.
Mock runtime-off Badge preview must not activate Hermes.
Mock runtime-off Badge preview must not enable Google Sheets.
No Mock runtime-off Badge preview runtime is implemented in v0.8.1-A.
```

## 13. Preview input boundary

```
Preview input may be future synthetic local-only mock message data.
Preview input may be future static safety-posture flags.
Preview input must not require real queue DB read in v0.8.1-A.
Preview input must not require secrets.
Preview input must not require Google Sheets.
Preview input must not require Remote Blackboard API runtime.
No preview input reader is implemented in v0.8.1-A.
No preview data loader is implemented in v0.8.1-A.
```

## 14. Preview output boundary

```
Preview output may be future read-only Mock Task Message preview.
Preview output may be future read-only Mock Decision Message preview.
Preview output may be future read-only Mock Result Message preview.
Preview output may be future read-only Mock Advice Message preview.
Preview output may be future read-only Mock Badge Status preview.
Preview output may be future read-only Mock Runtime-off Status preview.
Preview output must not write queue data.
Preview output must not send POST.
Preview output must not dispatch Worker.
Preview output must not call OpenClaw.
Preview output must not call Hermes.
Preview output must not write Google Sheets.
No preview output renderer is implemented in v0.8.1-A.
```

## 15. Read-only preview boundary

```
Approval is not execution.
Approval readiness is not execution permission.
Decision and dispatch remain separate.
Mock data preview is display-only.
Mock data preview is not execution permission.
Mock data preview is not Worker dispatch.
Mock data preview is not OpenClaw call.
Mock data preview is not Hermes action.
Mock data preview must not read real queue DB.
Mock data preview must not send POST.
Dashboard preview display is read-only.
No read-only preview runtime is implemented in v0.8.1-A.
```

## 16. Dashboard display relationship

```
Dashboard may eventually display local mock data preview.
Mock data preview is display-only.
Mock data preview is not execution permission.
Mock data preview is not Worker dispatch.
Mock data preview is not OpenClaw call.
Mock data preview is not Hermes action.
Dashboard preview display is read-only.
No Dashboard mock data preview runtime is implemented in v0.8.1-A.
```

## 17. Dashboard route / template / static boundary

```
Dashboard route boundary is planning only.
No Dashboard route is created in v0.8.1-A.
No Dashboard endpoint is created in v0.8.1-A.
No Dashboard template is created in v0.8.1-A.
No Dashboard static asset is created in v0.8.1-A.
No app route is modified in v0.8.1-A.
No template file is modified in v0.8.1-A.
No static file is modified in v0.8.1-A.
```

## 18. App / runtime boundary

```
App / runtime boundary is planning only.
No app module is modified in v0.8.1-A.
No app.main import is performed in v0.8.1-A.
No QueueStore import is performed in v0.8.1-A.
No runtime host is created in v0.8.1-A.
No daemon is created in v0.8.1-A.
No systemd service is created in v0.8.1-A.
No Docker deployment is created in v0.8.1-A.
No local mock data preview runtime is created in v0.8.1-A.
```

## 19. Queue and real data boundary

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

## 20. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.1-A.
Remote Blackboard API read is not enabled in v0.8.1-A.
Remote Blackboard API write is not enabled in v0.8.1-A.
Remote Blackboard API is not required for local mock data preview planning.
```

## 21. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Worker must not run from plan-only mock data preview boundary.
OpenClaw must not execute from plan-only mock data preview boundary.
Hermes must not act from plan-only mock data preview boundary.
```

## 22. Google Sheets boundary

```
Google Sheets remains Disabled.
No Google Sheets read is required.
No Google Sheets write is performed.
No Google Sheets live write is enabled.
```

## 23. Secrets / privacy / memory boundary

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

## 24. Network / webhook / connector boundary

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

## 25. Failure / rollback / audit boundary

```
Future mock data preview changes must be auditable.
Future mock data preview actions must include rollback notes when external actions are involved.
Future mock data preview failures must not silently retry external actions.
Future mock data preview failures must not bypass Owner approval.
Future mock data preview failures must not write Google Sheets by default.
Future mock data preview failures must not call OpenClaw by default.
Future mock data preview failures must not start Worker by default.
No mock data preview failure handling runtime is implemented in v0.8.1-A.
```

## 26. Candidate mock data families

These are candidate planning notes only. No mock data family is implemented.

```
Mock Task Message
Mock Decision Message
Mock Result Message
Mock Advice Message
Mock Badge Status
Mock Runtime-off Status
Candidate mock data families are planning only.
No mock data family is implemented in v0.8.1-A.
No mock data fixture file is created in v0.8.1-A.
```

## 27. Candidate mock data fields

These are candidate planning notes only. No candidate mock data field is implemented.

```
Candidate mock data field: message_id.
Candidate mock data field: preview_id.
Candidate mock data field: family.
Candidate mock data field: mock_mode.
Candidate mock data field: task_summary.
Candidate mock data field: decision_outcome.
Candidate mock data field: result_summary.
Candidate mock data field: advice_text.
Candidate mock data field: badge_status.
Candidate mock data field: runtime_off_status.
Candidate mock data field: dispatch_enabled.
Candidate mock data field: worker_running.
Candidate mock data field: openclaw_connected.
Candidate mock data field: hermes_connected.
Candidate mock data field: google_sheets_enabled.
Candidate mock data field: approval_is_execution.
Candidate mock data field: approval_readiness_is_execution.
Candidate mock data field: external_side_effects.
Candidate mock data field: is_mock.
Candidate mock data field: safety_notes.
Candidate mock data field: next_owner_action.
Candidate mock data fields are planning only.
No candidate mock data field is implemented in v0.8.1-A.
No schema migration is performed in v0.8.1-A.
```

## 28. Candidate preview validation rules

These are candidate planning notes only. No preview validation runtime is implemented.

```
Candidate preview validation rule: is_mock must remain true.
Candidate preview validation rule: dispatch_enabled must remain false.
Candidate preview validation rule: worker_running must remain false.
Candidate preview validation rule: openclaw_connected must remain false.
Candidate preview validation rule: hermes_connected must remain false.
Candidate preview validation rule: google_sheets_enabled must remain false.
Candidate preview validation rule: approval_is_execution must remain false.
Candidate preview validation rule: approval_readiness_is_execution must remain false.
Candidate preview validation rule: external_side_effects must remain false.
Candidate preview validation rule: mock data source must remain synthetic local-only.
Candidate preview validation rule: preview output must remain read-only.
Candidate preview validation rules are planning only.
No preview validation runtime is implemented in v0.8.1-A.
```

## 29. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only local mock data preview boundary plan.
Candidate future phase: local mock data fixture contract plan.
Candidate future phase: candidate mock data field inventory.
Candidate future phase: read-only Mock Task Message preview.
Candidate future phase: read-only Mock Decision Message preview.
Candidate future phase: read-only Mock Result Message preview.
Candidate future phase: read-only Mock Advice Message preview.
Candidate future phase: read-only Mock Badge Status preview.
Candidate future phase: read-only Mock Runtime-off Status preview.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.1-A.
No candidate future phase is enabled in v0.8.1-A.
```

## 30. Disabled runtime list

```
Local mock data preview runtime is disabled.
Mock data fixture loader is disabled.
Preview data loader runtime is disabled.
Dashboard mock data preview runtime is disabled.
Blackboard Loop runtime is disabled.
Dashboard badge display runtime is disabled.
Decision audit display runtime is disabled.
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

## 31. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Google Sheets remains Disabled.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
DISPATCH OFF.
WORKER OFF.
OPENCLAW NOT CONNECTED.
HERMES NOT CONNECTED.
GOOGLE SHEETS DISABLED.
No local mock data preview runtime.
No mock data fixture file.
No preview data loader.
No Blackboard Loop runtime.
No Dashboard badge display runtime.
No Decision audit display runtime.
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
No connector.
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
No tag.
```

## 32. Validation summary

```
v0.8.1-A readiness: ALL PASS.
v0.8.0-G readiness: ALL PASS.
v0.8.0-F readiness: ALL PASS.
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

## 33. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 34. Non-goals

This round is a plan. The following are explicitly out of scope:

- Implementing any local mock data preview runtime, mock data fixture loader, preview data loader, Dashboard mock data preview runtime, Blackboard Loop runtime, Dashboard badge display runtime, Decision audit display runtime, Owner review checklist runtime, Dashboard preview display runtime, preview renderer runtime, loop contract runtime, or state machine runtime.
- Creating any mock data fixture file, JSON fixture, or seed script.
- Creating or modifying any Dashboard route, endpoint, template, or static asset.
- Modifying app, templates, or static.
- Creating any loop scheduler or preview validation runtime.
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
- Starting v0.8.1-B, v0.8.1-C, v0.8.1-D, or any real v0.8.1 implementation in this round.

## 35. Acceptance criteria

```
v0.8.1-A adds only two files: the plan doc and the readiness script.
v0.8.1-A modifies no existing app / scripts / docs / README / templates / static / runtime.
v0.8.1-A readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 36. Next recommended step

```
v0.8.1-B — Local Mock Data Fixture Contract Plan
```

The next step must remain mock-data contract planning, and must not start unless separately
approved by the Owner:

```
v0.8.1-B must not start unless separately approved by Owner.
v0.8.1-B must remain mock-data contract planning unless separately approved.
v0.8.1-B must not modify Dashboard route/template/static.
v0.8.1-B must not create runtime preview loader unless separately approved.
v0.8.1-B must not read real queue DB.
v0.8.1-B must not send POST.
v0.8.1-B must not start Worker.
v0.8.1-B must not call OpenClaw.
v0.8.1-B must not activate Hermes.
v0.8.1-B must not read or write Google Sheets.
```
