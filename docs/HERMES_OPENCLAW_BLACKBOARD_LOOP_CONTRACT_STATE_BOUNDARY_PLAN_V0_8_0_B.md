# HERMES ↔ OpenClaw Adapter — Blackboard Loop Contract and State Boundary Plan (v0.8.0-B)

> Plan-first document. This is **documentation only**. It plans the future Blackboard Loop
> contract and its state boundaries: the message contract, the state boundary distinctions,
> the Owner review state, the Decision audit state, the dispatch-disabled state, the dry-run
> preview state, and the Result / Advice observation states. It implements no Blackboard Loop
> runtime, no loop contract runtime, no state machine runtime, no loop scheduler, enables no
> dispatch gate, activates no Hermes, connects no OpenClaw, starts no Worker, creates no
> Remote Blackboard API runtime, creates no production DB, moves no queue, reads no secrets,
> and introduces no external side effect.

## 1. Purpose

This document plans — and only plans — the future Blackboard Loop contract and the state
boundaries that surround it. It defines what the contract is, what each state means, where
each state stops, and which runtime stays disabled, so that a future runtime loop and state
machine can be designed against an agreed contract before any code or runtime is built.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. Planning contract and state boundaries is not running the
loop.

## 2. Current master

```
HEAD = origin/master = 9debb74b05007428a137fe35342eb00e8183fb28
docs: plan owner supervised blackboard loop
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first round. The following define what v0.8.0-B is and is not:

```
v0.8.0-B Blackboard Loop Contract and State Boundary Plan is plan-first.
v0.8.0-B does not implement Blackboard Loop runtime.
v0.8.0-B does not implement loop contract runtime.
v0.8.0-B does not implement state machine runtime.
v0.8.0-B does not create loop scheduler.
v0.8.0-B does not enable dispatch gate.
v0.8.0-B does not enable autonomous execution.
v0.8.0-B does not activate Hermes.
v0.8.0-B does not connect Hermes.
v0.8.0-B does not connect OpenClaw.
v0.8.0-B does not start Worker.
v0.8.0-B does not create Hermes runtime.
v0.8.0-B does not create OpenClaw runtime.
v0.8.0-B does not create Worker runtime.
v0.8.0-B does not implement Remote Blackboard API runtime.
v0.8.0-B does not create production DB.
v0.8.0-B does not create shared DB.
v0.8.0-B does not create remote shared DB.
v0.8.0-B does not migrate queue data.
v0.8.0-B does not sync local queue and remote queue.
v0.8.0-B does not open shared write.
v0.8.0-B does not write Google Sheets.
v0.8.0-B does not create webhook.
```

## 4. Relationship to v0.8.0-A Owner-supervised Blackboard Loop MVP Plan

```
v0.8.0-A Owner-supervised Blackboard Loop MVP Plan is complete.
v0.8.0-B starts the Blackboard Loop contract and state boundary planning step.
v0.8.0-B builds on Owner-supervised Blackboard Loop MVP planning.
v0.8.0-B defines contract and state boundaries before any runtime loop.
v0.8.0-B preserves Owner final approval authority.
v0.8.0-B preserves decision and dispatch separation.
v0.8.0-B preserves audit trail.
v0.8.0-B does not change any v0.8.0-A boundary.
v0.8.0-B does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned Blackboard Loop contract before any runtime loop can be implemented.
The system needs planned state boundaries before any state machine can be implemented.
The loop contract must not become an execution command.
The loop state must not become execution permission.
The Owner review state must not become Worker dispatch.
The Decision audit state must not become command.
The dispatch-disabled state must remain disabled.
The dry-run preview state must not write queue data.
Planning contract and state boundaries is not running the loop.
```

## 6. Blackboard Loop contract definition

```
Blackboard Loop contract means a future agreement about allowed message families, allowed states, required Owner review, and disabled dispatch.
Blackboard Loop contract is a planning artifact in v0.8.0-B.
Blackboard Loop contract is not runtime code.
Blackboard Loop contract is not API route.
Blackboard Loop contract is not database schema.
Blackboard Loop contract is not Worker dispatch.
Blackboard Loop contract is not OpenClaw call.
Blackboard Loop contract is not Hermes activation.
Blackboard Loop contract requires separate future plan and Owner approval before implementation.
```

## 7. Blackboard Loop state boundary definition

```
Blackboard Loop state boundary means a planned distinction between display state, review state, audit state, preview state, and dispatch state.
Display state is not execution permission.
Review state is not execution permission.
Audit state is not command.
Preview state is not queue write.
Dispatch state remains disabled.
State boundary is planning only in v0.8.0-B.
No state machine runtime is implemented in v0.8.0-B.
No state persistence runtime is implemented in v0.8.0-B.
```

## 8. Blackboard message contract boundary

```
Task Message
Decision Message
Result Message
Advice Message
Task Message is draft or request, not Worker dispatch.
Decision Message is audit record, not command.
Result Message is observation, not next dispatch permission.
Advice Message is advisory, not command.
Hermes Advice Message is not automatic execution.
Hermes Task Message draft requires Owner review.
No new Blackboard message family is implemented in v0.8.0-B.
No message schema migration is performed in v0.8.0-B.
```

## 9. Task state boundary

```
Task state is draft or pending review until Owner decision.
Task draft is not queue write by itself.
Task draft is not Worker dispatch.
Task draft is not OpenClaw call.
Task draft is not Hermes action.
Task state must show review requirement.
Task state must not imply execution permission.
No Task state runtime is implemented in v0.8.0-B.
```

## 10. Owner review state boundary

```
Owner review state is required before any future dispatch.
Owner review state must be visible.
Owner review state must be auditable.
Owner review state must preserve approve is not execute.
Owner review state must preserve approval readiness is not execution permission.
Owner review state must preserve Owner decision event is not Worker dispatch.
Owner review state is not implemented as runtime in v0.8.0-B.
Owner approval remains separate from runtime dispatch.
```

## 11. Decision audit state boundary

```
Decision audit state records Owner decision.
Decision audit state is audit record, not command.
Decision audit state is not Worker dispatch.
Decision audit state is not OpenClaw call.
Decision audit state is not Hermes action.
Decision audit state is not Google Sheets write.
Decision audit state must remain append-only when future runtime exists.
No Decision audit runtime change is implemented in v0.8.0-B.
```

## 12. Dispatch-disabled state boundary

```
Dispatch-disabled state means future dispatch path is explicitly off.
Dispatch-disabled state must be visible.
Dispatch-disabled state must be auditable.
Dispatch-disabled state must block Worker dispatch.
Dispatch-disabled state must block OpenClaw call.
Dispatch-disabled state must block Hermes action.
Dispatch-disabled state must block Google Sheets write.
Dispatch gate remains disabled in v0.8.0-B.
No dispatch gate runtime is implemented in v0.8.0-B.
```

## 13. Dry-run preview state boundary

```
Dry-run preview state means future loop preview without external side effects.
Dry-run preview state is not queue write.
Dry-run preview state is not Worker dispatch.
Dry-run preview state is not OpenClaw call.
Dry-run preview state is not Hermes action.
Dry-run preview state is not Google Sheets write.
Dry-run preview state must not read real queue DB unless separately approved.
Dry-run preview state must not modify local queue or Replit queue.
No dry-run preview runtime is implemented in v0.8.0-B.
```

## 14. Result observation state boundary

```
Result observation state is read-only observation.
Result observation state is not next dispatch permission.
Result observation state is not automatic follow-up execution.
Result observation state is not Google Sheets write.
No Result observation runtime is implemented in v0.8.0-B.
```

## 15. Advice observation state boundary

```
Advice observation state is read-only advisory display.
Advice observation state is not command.
Advice observation state is not Worker dispatch.
Advice observation state is not OpenClaw call.
Advice observation state is not automatic execution.
No Advice observation runtime is implemented in v0.8.0-B.
```

## 16. Contract is not execution permission

```
Contract approval is not runtime approval.
Contract approval is not dispatch approval.
Contract approval is not migration approval.
Contract approval is not shared write approval.
Contract approval is not Hermes activation approval.
State label is not execution permission.
Review label is not execution permission.
Approved label is not execute.
Dispatch-ready label is not Worker dispatch.
```

## 17. State transition boundary

```
State transition planning is not runtime transition implementation.
State transition label is not queue mutation.
State transition label is not Worker dispatch.
State transition label is not OpenClaw call.
State transition label is not Hermes action.
State transition requires future runtime plan before implementation.
No state transition runtime is implemented in v0.8.0-B.
No existing status transition is changed in v0.8.0-B.
```

## 18. Candidate state machine draft

These are candidate planning notes only. No candidate state is implemented or enabled.

```
Candidate state: draft.
Candidate state: pending_owner_review.
Candidate state: decision_recorded.
Candidate state: dispatch_disabled.
Candidate state: dry_run_preview.
Candidate state: result_observed.
Candidate state: advice_observed.
Candidate state: closed_by_owner.
Candidate state machine is planning only.
No candidate state is implemented in v0.8.0-B.
No state machine runtime is enabled in v0.8.0-B.
```

## 19. Runtime disabled boundary

```
Blackboard Loop runtime remains disabled.
Loop contract runtime remains disabled.
State machine runtime remains disabled.
Loop scheduler remains disabled.
Dispatch gate remains disabled.
Worker runtime remains disabled.
OpenClaw runtime remains disabled.
Hermes runtime remains disabled.
Remote Blackboard API runtime remains disabled.
Shared write remains disabled.
Google Sheets write remains disabled.
Autonomous execution remains disabled.
```

## 20. Worker / OpenClaw / Hermes separation boundary

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
Worker must not run from plan-only contract.
```

## 21. Dashboard display boundary

```
Dashboard displays state.
Dashboard display is not dispatch.
Dashboard display is not execution permission.
Dashboard contract label is not execution permission.
Dashboard state label is not execution permission.
Dashboard source label is not shared write.
Dashboard source switching requires separate future plan and Owner approval.
No Dashboard runtime change is implemented in v0.8.0-B.
No Dashboard backend source runtime is implemented in v0.8.0-B.
```

## 22. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.0-B.
Remote Blackboard API route is not added in v0.8.0-B.
Remote Blackboard API read is not enabled in v0.8.0-B.
Remote Blackboard API write is not enabled in v0.8.0-B.
Remote Blackboard API is not execution dispatcher.
Remote Blackboard API is not production DB.
Remote Blackboard API runtime requires separate future plan and Owner approval.
```

## 23. Local queue vs remote blackboard boundary

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

## 24. Source-of-truth and data boundary

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

## 25. Secrets / privacy / memory boundary

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

## 26. Network / webhook / connector boundary

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

## 27. Failure / rollback / audit boundary

```
Future contract changes must be auditable.
Future state transitions must be auditable.
Future loop actions must include rollback notes when external actions are involved.
Future loop failures must not silently retry external actions.
Future loop failures must not bypass Owner approval.
Future loop failures must not write Google Sheets by default.
Future loop failures must not call OpenClaw by default.
Future loop failures must not start Worker by default.
No loop failure handling runtime is implemented in v0.8.0-B.
```

## 28. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only contract plan.
Candidate future phase: contract field inventory.
Candidate future phase: local dry-run state preview.
Candidate future phase: read-only Dashboard state display.
Candidate future phase: Owner review state display.
Candidate future phase: Decision audit state confirmation.
Candidate future phase: dispatch-disabled guard display.
Candidate future phase: Result and Advice observation display.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.0-B.
No candidate future phase is enabled in v0.8.0-B.
```

## 29. Disabled runtime list

```
Blackboard Loop runtime is disabled.
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

## 30. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
No Blackboard Loop runtime.
No loop contract runtime.
No state machine runtime.
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

## 31. Validation summary

```
v0.8.0-B readiness: ALL PASS.
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

## 32. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 33. Non-goals

This round is a plan. The following are explicitly out of scope:

- Implementing any Blackboard Loop runtime, loop contract runtime, or state machine runtime.
- Creating any loop scheduler, state transition runtime, or state persistence runtime.
- Enabling any dispatch gate; enabling autonomous execution.
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

## 34. Acceptance criteria

```
v0.8.0-B adds only two files: the plan doc and the readiness script.
v0.8.0-B modifies no existing app / scripts / docs / README / runtime.
v0.8.0-B readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches and safe negations.
No commit, no push, no tag is performed in this round.
```

## 35. Next recommended step

```
v0.8.0-C — Local Dry-run Blackboard Loop Preview Plan
```

The next step must remain plan-first:

```
v0.8.0-C must remain plan-first unless separately approved.
v0.8.0-C must not implement Blackboard Loop runtime.
v0.8.0-C must not enable dispatch gate.
v0.8.0-C must not activate Hermes.
v0.8.0-C must not connect OpenClaw.
v0.8.0-C must not start Worker.
v0.8.0-C must not create production DB.
v0.8.0-C must not create Remote Blackboard API runtime unless separately approved.
v0.8.0-C must not migrate queue data.
v0.8.0-C must not open shared write.
v0.8.0-C must not write Google Sheets.
```
