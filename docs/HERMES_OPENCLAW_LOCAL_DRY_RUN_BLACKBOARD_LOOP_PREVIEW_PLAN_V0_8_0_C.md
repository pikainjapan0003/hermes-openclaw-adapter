# HERMES ↔ OpenClaw Adapter — Local Dry-run Blackboard Loop Preview Plan (v0.8.0-C)

> Plan-first document. This is **documentation only**. It plans the future local-only dry-run
> Blackboard Loop preview: its preview contract, preview input/output, preview state, Owner
> review preview, Decision audit preview, dispatch-disabled preview, Task / Result / Advice
> previews, local-only boundary, and queue/data boundary. It implements no preview runtime,
> creates no dry-run preview tool, reads no real queue DB, writes no queue, sends no POST,
> starts no Worker, calls no OpenClaw, activates no Hermes, writes no Google Sheets, creates
> no Remote Blackboard API runtime, creates no DB, and opens no shared write.

## 1. Purpose

This document plans — and only plans — the future local dry-run Blackboard Loop preview. It
defines what the preview may show, what input it may take, what output it may produce, which
states it represents, and which runtime stays disabled, so that a future local preview can be
designed against an agreed boundary before any code or runtime is built.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. Planning local dry-run preview is not running the loop.

## 2. Current master

```
HEAD = origin/master = 389125a58993ae2f30db5f017097cc5cad515b19
docs: plan blackboard loop contract state boundary
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.0-C is and is not:

```
v0.8.0-C Local Dry-run Blackboard Loop Preview Plan is plan-first.
v0.8.0-C does not implement Blackboard Loop runtime.
v0.8.0-C does not implement dry-run preview runtime.
v0.8.0-C does not create dry-run preview tool.
v0.8.0-C does not create preview renderer runtime.
v0.8.0-C does not implement loop contract runtime.
v0.8.0-C does not implement state machine runtime.
v0.8.0-C does not create loop scheduler.
v0.8.0-C does not enable dispatch gate.
v0.8.0-C does not enable autonomous execution.
v0.8.0-C does not activate Hermes.
v0.8.0-C does not connect Hermes.
v0.8.0-C does not connect OpenClaw.
v0.8.0-C does not start Worker.
v0.8.0-C does not create Hermes runtime.
v0.8.0-C does not create OpenClaw runtime.
v0.8.0-C does not create Worker runtime.
v0.8.0-C does not implement Remote Blackboard API runtime.
v0.8.0-C does not create production DB.
v0.8.0-C does not create shared DB.
v0.8.0-C does not create remote shared DB.
v0.8.0-C does not read real queue DB.
v0.8.0-C does not modify queue data.
v0.8.0-C does not migrate queue data.
v0.8.0-C does not sync local queue and remote queue.
v0.8.0-C does not open shared write.
v0.8.0-C does not write Google Sheets.
v0.8.0-C does not send POST.
v0.8.0-C does not create webhook.
```

## 4. Relationship to v0.8.0-B Blackboard Loop Contract and State Boundary Plan

```
v0.8.0-B Blackboard Loop Contract and State Boundary Plan is complete.
v0.8.0-C starts the Local Dry-run Blackboard Loop Preview planning step.
v0.8.0-C builds on Blackboard Loop contract and state boundary planning.
v0.8.0-C plans local dry-run preview before any preview runtime.
v0.8.0-C preserves Owner final approval authority.
v0.8.0-C preserves decision and dispatch separation.
v0.8.0-C preserves audit trail.
v0.8.0-C preserves dispatch-disabled boundary.
v0.8.0-C does not change any v0.8.0-B boundary.
v0.8.0-C does not change any v0.8.0-A boundary.
v0.8.0-C does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned local dry-run preview before any loop preview runtime can be implemented.
The local dry-run preview must not read real queue DB.
The local dry-run preview must not write queue data.
The local dry-run preview must not send POST.
The local dry-run preview must not become Worker dispatch.
The local dry-run preview must not call OpenClaw.
The local dry-run preview must not activate Hermes.
The local dry-run preview must not write Google Sheets.
Planning local dry-run preview is not running the loop.
```

## 6. Local dry-run Blackboard Loop preview definition

```
Local dry-run Blackboard Loop preview means a future local-only preview of planned loop states and messages.
Local dry-run Blackboard Loop preview is a planning artifact in v0.8.0-C.
Local dry-run Blackboard Loop preview is not runtime code.
Local dry-run Blackboard Loop preview is not queue write.
Local dry-run Blackboard Loop preview is not real queue DB read.
Local dry-run Blackboard Loop preview is not Worker dispatch.
Local dry-run Blackboard Loop preview is not OpenClaw call.
Local dry-run Blackboard Loop preview is not Hermes activation.
Local dry-run Blackboard Loop preview is not Google Sheets write.
Local dry-run Blackboard Loop preview requires separate future plan and Owner approval before implementation.
```

## 7. Preview contract boundary

```
Preview contract describes what a future dry-run preview may display.
Preview contract is not execution permission.
Preview contract is not runtime approval.
Preview contract is not API route.
Preview contract is not database schema.
Preview contract is not Worker dispatch.
Preview contract is not OpenClaw call.
Preview contract is not Hermes action.
No preview contract runtime is implemented in v0.8.0-C.
```

## 8. Preview input boundary

```
Preview input may be future mock Task Message data.
Preview input may be future mock Decision Message data.
Preview input may be future mock Result Message data.
Preview input may be future mock Advice Message data.
Preview input must not require real queue DB read in v0.8.0-C.
Preview input must not require secrets.
Preview input must not require Google Sheets.
Preview input must not require Remote Blackboard API runtime.
No preview input reader is implemented in v0.8.0-C.
```

## 9. Preview output boundary

```
Preview output may be future read-only text summary.
Preview output may be future read-only state table.
Preview output may be future read-only Owner review checklist.
Preview output must not write queue data.
Preview output must not send POST.
Preview output must not dispatch Worker.
Preview output must not call OpenClaw.
Preview output must not call Hermes.
Preview output must not write Google Sheets.
No preview output renderer is implemented in v0.8.0-C.
```

## 10. Preview state boundary

```
Preview state is display-only planning state.
Preview state is not execution permission.
Preview state is not queue mutation.
Preview state is not Worker dispatch.
Preview state is not OpenClaw call.
Preview state is not Hermes action.
Preview state is not Google Sheets write.
No preview state runtime is implemented in v0.8.0-C.
```

## 11. Preview lifecycle draft

```
Preview lifecycle draft step: prepare mock or planned message.
Preview lifecycle draft step: show local preview.
Preview lifecycle draft step: show Owner review requirement.
Preview lifecycle draft step: show dispatch-disabled state.
Preview lifecycle draft step: show result or advice observation.
Preview lifecycle draft is planning only.
Preview lifecycle is not implemented in v0.8.0-C.
Preview lifecycle does not read real queue DB.
Preview lifecycle does not write queue data.
Preview lifecycle does not start Worker.
Preview lifecycle does not call OpenClaw.
Preview lifecycle does not activate Hermes.
```

## 12. Owner review preview boundary

```
Owner review preview is display-only.
Owner review preview is not execution permission.
Owner review preview is not Worker dispatch.
Owner review preview must preserve approve is not execute.
Owner review preview must preserve approval readiness is not execution permission.
No Owner review preview runtime is implemented in v0.8.0-C.
```

## 13. Decision audit preview boundary

```
Decision audit preview is display-only.
Decision audit preview is audit preview, not command.
Decision audit preview is not Worker dispatch.
Decision audit preview is not OpenClaw call.
Decision audit preview is not Hermes action.
No Decision audit preview runtime is implemented in v0.8.0-C.
```

## 14. Dispatch-disabled preview boundary

```
Dispatch-disabled preview means future preview must visibly show dispatch is off.
Dispatch-disabled preview must block Worker dispatch.
Dispatch-disabled preview must block OpenClaw call.
Dispatch-disabled preview must block Hermes action.
Dispatch-disabled preview must block Google Sheets write.
Dispatch gate remains disabled in v0.8.0-C.
No dispatch-disabled preview runtime is implemented in v0.8.0-C.
```

## 15. Task draft preview boundary

```
Task draft preview is display-only.
Task draft preview is not queue write.
Task draft preview is not Worker dispatch.
Task draft preview is not OpenClaw call.
Task draft preview is not Hermes action.
No Task draft preview runtime is implemented in v0.8.0-C.
```

## 16. Result observation preview boundary

```
Result observation preview is display-only.
Result observation preview is not next dispatch permission.
Result observation preview is not automatic follow-up execution.
Result observation preview is not Google Sheets write.
No Result observation preview runtime is implemented in v0.8.0-C.
```

## 17. Advice observation preview boundary

```
Advice observation preview is display-only.
Advice observation preview is advisory display, not command.
Advice observation preview is not Worker dispatch.
Advice observation preview is not OpenClaw call.
Advice observation preview is not automatic execution.
No Advice observation preview runtime is implemented in v0.8.0-C.
```

## 18. Local-only boundary

```
Local-only preview plan does not select production host.
Local-only preview plan does not create runtime host.
Local-only preview plan does not deploy service.
Local-only preview plan does not create systemd service.
Local-only preview plan does not create daemon.
Local-only preview plan does not create Docker deployment.
```

## 19. Queue and data boundary

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

## 20. Dashboard relationship

```
Dashboard may eventually display preview state.
Dashboard preview display is not dispatch.
Dashboard preview display is not execution permission.
No Dashboard runtime change is implemented in v0.8.0-C.
No Dashboard preview display runtime is implemented in v0.8.0-C.
```

## 21. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.0-C.
Remote Blackboard API read is not enabled in v0.8.0-C.
Remote Blackboard API write is not enabled in v0.8.0-C.
Remote Blackboard API is not required for local dry-run preview planning.
```

## 22. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Worker must not run from plan-only preview.
OpenClaw must not execute from plan-only preview.
Hermes must not act from plan-only preview.
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
Future preview changes must be auditable.
Future preview actions must include rollback notes when external actions are involved.
Future preview failures must not silently retry external actions.
Future preview failures must not bypass Owner approval.
Future preview failures must not write Google Sheets by default.
Future preview failures must not call OpenClaw by default.
Future preview failures must not start Worker by default.
No preview failure handling runtime is implemented in v0.8.0-C.
```

## 27. Candidate preview fields

These are candidate planning notes only. No candidate preview field is implemented.

```
Candidate preview field: preview_id.
Candidate preview field: preview_mode.
Candidate preview field: message_family.
Candidate preview field: planned_state.
Candidate preview field: owner_review_required.
Candidate preview field: dispatch_enabled.
Candidate preview field: external_side_effects.
Candidate preview field: queue_read_required.
Candidate preview field: queue_write_required.
Candidate preview field: worker_dispatch_allowed.
Candidate preview field: openclaw_call_allowed.
Candidate preview field: hermes_action_allowed.
Candidate preview field: google_sheets_write_allowed.
Candidate preview field: safety_notes.
Candidate preview field: next_owner_action.
Candidate preview fields are planning only.
No candidate preview field is implemented in v0.8.0-C.
No schema migration is performed in v0.8.0-C.
```

## 28. Candidate validation rules

These are candidate planning notes only. No validation runtime is implemented.

```
Candidate validation rule: dispatch_enabled must remain false.
Candidate validation rule: external_side_effects must remain false.
Candidate validation rule: queue_read_required must remain false unless separately approved.
Candidate validation rule: queue_write_required must remain false.
Candidate validation rule: worker_dispatch_allowed must remain false.
Candidate validation rule: openclaw_call_allowed must remain false.
Candidate validation rule: hermes_action_allowed must remain false.
Candidate validation rule: google_sheets_write_allowed must remain false.
Candidate validation rules are planning only.
No validation runtime is implemented in v0.8.0-C.
```

## 29. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only preview plan.
Candidate future phase: candidate preview field inventory.
Candidate future phase: local mock-data dry-run preview.
Candidate future phase: read-only Dashboard preview display.
Candidate future phase: Owner review preview checklist display.
Candidate future phase: dispatch-disabled guard preview display.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.0-C.
No candidate future phase is enabled in v0.8.0-C.
```

## 30. Disabled runtime list

```
Blackboard Loop runtime is disabled.
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
No Dashboard preview display runtime.
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

- Implementing any Blackboard Loop runtime, dry-run preview runtime, preview renderer runtime, loop contract runtime, or state machine runtime.
- Creating any dry-run preview tool, loop scheduler, or preview validation runtime.
- Enabling any dispatch gate; enabling autonomous execution.
- Activating or connecting Hermes; connecting OpenClaw; starting Worker.
- Creating any Hermes / OpenClaw / Worker runtime.
- Implementing the Remote Blackboard API runtime, route, read, or write.
- Creating any production DB, shared DB, or remote shared DB.
- Reading the real queue DB; modifying, migrating, syncing, backfilling, or merging queue data.
- Opening shared write; enabling Hermes blackboard mode; writing Google Sheets.
- Reading, copying, or creating secrets; creating `.env`; moving credentials.
- Creating any webhook, connector, listener, or external integration.
- Sending any POST or performing live local queue write validation.
- Any commit, push, or tag in this round.

## 35. Acceptance criteria

```
v0.8.0-C adds only two files: the plan doc and the readiness script.
v0.8.0-C modifies no existing app / scripts / docs / README / runtime.
v0.8.0-C readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 36. Next recommended step

```
v0.8.0-D — Read-only Dashboard Blackboard Loop Preview Display Plan
```

The next step must remain plan-first:

```
v0.8.0-D must remain plan-first unless separately approved.
v0.8.0-D must not implement Blackboard Loop runtime.
v0.8.0-D must not implement preview runtime.
v0.8.0-D must not enable dispatch gate.
v0.8.0-D must not activate Hermes.
v0.8.0-D must not connect OpenClaw.
v0.8.0-D must not start Worker.
v0.8.0-D must not create production DB.
v0.8.0-D must not create Remote Blackboard API runtime unless separately approved.
v0.8.0-D must not migrate queue data.
v0.8.0-D must not open shared write.
v0.8.0-D must not write Google Sheets.
```
