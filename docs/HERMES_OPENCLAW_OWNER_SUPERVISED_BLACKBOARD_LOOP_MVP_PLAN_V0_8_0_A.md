# HERMES ↔ OpenClaw Adapter — Owner-supervised Blackboard Loop MVP Plan (v0.8.0-A)

> Plan-first document. This is **documentation only**. It plans the future
> Owner-supervised Blackboard Loop MVP: its actors, message families, lifecycle,
> Owner review gate, dispatch boundary, safety boundaries, and candidate phases.
> It implements no loop runtime, starts no loop scheduler, enables no dispatch gate,
> activates no Hermes, connects no OpenClaw, starts no Worker, creates no Remote
> Blackboard API runtime, creates no production DB, moves no queue, reads no secrets,
> and introduces no external side effect.

## 1. Purpose

This document plans — and only plans — the future Owner-supervised Blackboard Loop MVP.
It defines the roles, the Blackboard message families, a draft loop lifecycle, the Owner
review gate, the decision-versus-dispatch boundary, the safety boundaries, and a set of
candidate MVP phases, so that a future runtime loop can be designed against an agreed
plan before any code or runtime is built.

Nothing here is built. This round adds **only** a plan document and a readiness script
that statically verifies that document. Planning the loop is not running the loop.

## 2. Current master

```
HEAD = origin/master = 1c59bd3484729fbe17026a747603d88f5d3ed6de
docs: close out remote blackboard preparation
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.0-A is and is not:

```
v0.8.0-A Owner-supervised Blackboard Loop MVP Plan is plan-first.
v0.8.0-A does not implement Blackboard Loop runtime.
v0.8.0-A does not create loop scheduler.
v0.8.0-A does not enable dispatch gate.
v0.8.0-A does not enable autonomous execution.
v0.8.0-A does not activate Hermes.
v0.8.0-A does not connect Hermes.
v0.8.0-A does not connect OpenClaw.
v0.8.0-A does not start Worker.
v0.8.0-A does not create Hermes runtime.
v0.8.0-A does not create OpenClaw runtime.
v0.8.0-A does not create Worker runtime.
v0.8.0-A does not implement Remote Blackboard API runtime.
v0.8.0-A does not create production DB.
v0.8.0-A does not create shared DB.
v0.8.0-A does not create remote shared DB.
v0.8.0-A does not migrate queue data.
v0.8.0-A does not sync local queue and remote queue.
v0.8.0-A does not open shared write.
v0.8.0-A does not write Google Sheets.
v0.8.0-A does not create webhook.
```

## 4. Relationship to v0.7.5 Remote Blackboard Preparation

```
v0.7.5 Remote Blackboard Preparation line is complete.
v0.8.0-A starts the Owner-supervised Blackboard Loop MVP planning line.
v0.8.0-A builds on Remote Blackboard API planning.
v0.8.0-A builds on local queue vs remote blackboard boundary.
v0.8.0-A builds on Dashboard backend source planning.
v0.8.0-A builds on Core runtime host planning.
v0.8.0-A builds on Hermes activation boundary planning.
v0.8.0-A does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned Owner-supervised loop before any runtime loop can be implemented.
The loop must preserve Owner final approval.
The loop must preserve decision and dispatch separation.
The loop must preserve audit trail.
The loop must not turn Blackboard messages into automatic commands.
The loop must not make Hermes autonomous.
The loop must not start Worker.
The loop must not call OpenClaw.
Planning the loop is not running the loop.
```

## 6. Owner-supervised Blackboard Loop MVP definition

```
Owner-supervised Blackboard Loop MVP means a future workflow that coordinates Blackboard messages under Owner review.
Owner-supervised Blackboard Loop MVP may eventually organize Task Messages, Decision Messages, Result Messages, and Advice Messages.
Owner-supervised Blackboard Loop MVP may eventually support Owner review before any dispatch.
Owner-supervised Blackboard Loop MVP may eventually support dry-run loop previews.
Owner-supervised Blackboard Loop MVP is not implemented in v0.8.0-A.
Owner-supervised Blackboard Loop MVP is not autonomous execution.
Owner-supervised Blackboard Loop MVP is not Worker dispatch.
Owner-supervised Blackboard Loop MVP is not OpenClaw call.
Owner-supervised Blackboard Loop MVP is not Hermes activation.
```

## 7. Loop actors and roles

```
Owner is final approval authority.
ChatGPT is external advisor / prompt writer / architecture reviewer.
Hermes is future strategy / proxy / memory layer, not active.
OpenClaw is future execution / gateway / tools layer, not connected.
Worker is future dispatch runtime, currently OFF.
Dashboard is display / observation surface.
Remote Blackboard API is future shared coordination backend, not implemented.
GitHub is clean source of code and docs, not queue DB and not secrets store.
Windows WSL is primary local development environment.
Replit is remote observation station / Preview Dashboard.
```

## 8. Blackboard message families

```
Task Message
Decision Message
Result Message
Advice Message
Task Message is not Worker dispatch.
Decision Message is audit record, not command.
Result Message is not next dispatch permission.
Advice Message is advisory, not command.
Hermes Advice Message is not automatic execution.
Hermes Task Message draft requires Owner review.
No new Blackboard message family is implemented in v0.8.0-A.
No message schema migration is performed in v0.8.0-A.
```

## 9. Loop lifecycle draft

```
Loop lifecycle draft step: Task draft.
Loop lifecycle draft step: Owner review.
Loop lifecycle draft step: Decision audit.
Loop lifecycle draft step: Dispatch gate remains disabled.
Loop lifecycle draft step: Result observation.
Loop lifecycle draft step: Advice observation.
Loop lifecycle draft is planning only.
Loop lifecycle is not implemented in v0.8.0-A.
Loop lifecycle does not start Worker.
Loop lifecycle does not call OpenClaw.
Loop lifecycle does not activate Hermes.
```

## 10. Owner review gate

```
Owner review gate is required before any future dispatch.
Owner review gate must be visible.
Owner review gate must be auditable.
Owner review gate must preserve approve is not execute.
Owner review gate must preserve approval readiness is not execution permission.
Owner review gate must preserve Owner decision event is not Worker dispatch.
Owner review gate is not implemented in v0.8.0-A.
Owner approval remains separate from runtime dispatch.
```

## 11. Decision vs dispatch boundary

```
Decision is not dispatch.
Approve is not execute.
Approval readiness is not execution permission.
Owner decision message is audit record, not command.
Writing a task to Blackboard is not Worker dispatch.
Entering Blackboard mode is not execution permission.
Dispatch requires separate future runtime plan and Owner approval.
Dispatch gate remains disabled in v0.8.0-A.
```

## 12. Task draft boundary

```
Task draft is draft only.
Task draft requires Owner review.
Task draft is not queue write by itself.
Task draft is not Worker dispatch.
Task draft is not OpenClaw call.
```

## 13. Advice boundary

```
Advice is advisory only.
Advice is not command.
Advice is not Worker dispatch.
Advice is not OpenClaw call.
Advice is not Google Sheets write.
```

## 14. Result boundary

```
Result is observation only.
Result is not next dispatch permission.
Result is not automatic follow-up execution.
Result is not Google Sheets write.
```

## 15. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Hermes must not bypass Owner review.
Hermes must not bypass OpenClaw boundary.
Hermes must not bypass Worker boundary.
OpenClaw must not execute without Owner-approved dispatch path.
Worker must not run from plan-only loop.
```

## 16. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.0-A.
Remote Blackboard API route is not added in v0.8.0-A.
Remote Blackboard API read is not enabled in v0.8.0-A.
Remote Blackboard API write is not enabled in v0.8.0-A.
Remote Blackboard API is not execution dispatcher.
Remote Blackboard API is not production DB.
Remote Blackboard API runtime requires separate future plan and Owner approval.
```

## 17. Local queue vs remote blackboard boundary

```
Local Queue is not Remote Blackboard.
Remote Blackboard is not local queue.
WSL local queue remains local.
Replit local queue remains separate.
Dashboard update is not queue synchronization.
GitHub push is not queue synchronization.
No queue synchronization is performed.
No queue migration is performed.
No queue backfill is performed.
No queue merge is performed.
No conflict resolver is implemented.
```

## 18. Dashboard display boundary

```
Dashboard displays state.
Dashboard display is not dispatch.
Dashboard display is not execution permission.
Dashboard backend source is display data source.
Dashboard source label is not execution permission.
Dashboard source label is not shared write.
Dashboard source switching requires separate future plan and Owner approval.
No Dashboard runtime change is implemented in v0.8.0-A.
No Dashboard backend source runtime is implemented in v0.8.0-A.
```

## 19. Core runtime host relationship

```
Core runtime host is not selected.
Core runtime host is not created.
Runtime host selection is not loop activation.
Runtime host activation is not Worker start by itself.
Dashboard host is not runtime host by default.
Replit remains observation station.
Windows WSL remains local development environment.
No systemd service is created.
No daemon is created.
No Docker deployment is created.
No VPS deployment is created.
```

## 20. Source-of-truth and data boundary

```
No source-of-truth switch is performed.
Current source of truth remains local to each environment.
Future remote authority requires separate future plan and Owner approval.
No queue DB change.
No local queue data change.
No Replit queue data change.
No real queue DB read.
No production queue data is created.
No remote shared DB is created.
No shared write is enabled.
```

## 21. Secrets / privacy / memory boundary

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
No personal memory migration is performed.
GitHub must not store secrets.
Replit must not receive production secrets.
```

## 22. Network / webhook / connector boundary

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
Network activation requires separate future plan and Owner approval.
```

## 23. Failure / rollback / audit boundary

```
Future loop actions must be auditable.
Future loop actions must include rollback notes when external actions are involved.
Future loop failures must not silently retry external actions.
Future loop failures must not bypass Owner approval.
Future loop failures must not write Google Sheets by default.
Future loop failures must not call OpenClaw by default.
Future loop failures must not start Worker by default.
No loop failure handling runtime is implemented in v0.8.0-A.
```

## 24. Candidate MVP phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate MVP phase: docs-only loop plan.
Candidate MVP phase: local dry-run loop preview.
Candidate MVP phase: read-only Dashboard loop display.
Candidate MVP phase: Owner review gate display.
Candidate MVP phase: Decision audit confirmation.
Candidate MVP phase: Result and Advice read-only display.
Candidate MVP phase: Remote Blackboard read-only mirror after approval.
Candidate MVP phases are planning notes only.
No candidate MVP phase is implemented in v0.8.0-A.
No candidate MVP phase is enabled in v0.8.0-A.
```

## 25. Disabled runtime list

```
Blackboard Loop runtime is disabled.
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

## 26. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
No Blackboard Loop runtime.
No loop scheduler.
No dispatch gate enabled.
No autonomous execution.
No Hermes activation.
No Hermes blackboard mode.
No Hermes runtime.
No Hermes activation runtime.
No Hermes memory store.
No Hermes learning runtime.
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
No Dashboard backend source runtime.
No source switching runtime.
No Core runtime host.
No Worker runtime.
No OpenClaw runtime.
No systemd service.
No daemon.
No Docker deployment.
No VPS deployment.
No Mac mini deployment.
No home server deployment.
No queue synchronization.
No queue migration.
No queue backfill.
No queue merge.
No conflict resolver.
No connector.
No tag.
```

## 27. Validation summary

```
v0.8.0-A readiness: ALL PASS.
v0.7.5-R readiness: ALL PASS.
v0.7.5-E readiness: ALL PASS.
v0.7.5-D readiness: ALL PASS.
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

## 28. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 29. Non-goals

This round is a plan. The following are explicitly out of scope:

- Implementing or starting any Blackboard Loop runtime, loop scheduler, or dispatch gate.
- Activating or connecting Hermes; connecting OpenClaw; starting Worker.
- Creating any Hermes / OpenClaw / Worker runtime.
- Implementing the Remote Blackboard API runtime, route, read, or write.
- Creating any production DB, shared DB, or remote shared DB.
- Migrating, syncing, backfilling, or merging queue data; implementing a conflict resolver.
- Opening shared write; enabling Hermes blackboard mode; writing Google Sheets.
- Reading, copying, or creating secrets; creating `.env`; moving credentials.
- Creating any webhook, connector, listener, or external integration.
- Sending any POST or performing live local queue write validation.
- Any commit, push, or tag in this round.

## 30. Acceptance criteria

```
v0.8.0-A adds only two files: the plan doc and the readiness script.
v0.8.0-A modifies no existing app / scripts / docs / README / runtime.
v0.8.0-A readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 31. Next recommended step

```
v0.8.0-B — Blackboard Loop Contract and State Boundary Plan
```

The next step must remain plan-first:

```
v0.8.0-B must remain plan-first unless separately approved.
v0.8.0-B must not implement Blackboard Loop runtime.
v0.8.0-B must not activate Hermes.
v0.8.0-B must not connect OpenClaw.
v0.8.0-B must not start Worker.
v0.8.0-B must not create production DB.
v0.8.0-B must not create Remote Blackboard API runtime unless separately approved.
v0.8.0-B must not migrate queue data.
v0.8.0-B must not open shared write.
v0.8.0-B must not write Google Sheets.
```
