# HERMES ↔ OpenClaw Adapter — Hermes Activation with Remote Blackboard Boundary (v0.7.5-E)

> Plan-first document. This is **planning only**. It plans the boundaries for how Hermes
> would, in the future and under Owner supervision, enter a Remote Blackboard / Blackboard
> mode. It activates no Hermes, connects no OpenClaw, starts no Worker, creates no Remote
> Blackboard API runtime, creates no production DB, moves no queue, reads no secrets, and
> introduces no external side effect.

## 1. Purpose

This document plans — and only plans — the boundaries for a future, Owner-directed **Hermes
activation** in which Hermes may participate in a Remote Blackboard / Blackboard mode. It
defines up front that entering Blackboard mode is optional, is not execution permission,
and that Owner remains the final approval authority, so that any future activation stays
Owner-supervised and audit-preserving.

Nothing here is built. This round adds **only** a planning document and a readiness script
that statically verifies that document.

## 2. Current master

```
HEAD = origin/master = c871ecea5dfc1f83c492fdc2415f1c2dffa41cb1
docs: plan core runtime host
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is plan-first. The following define what v0.7.5-E is and is not:

```
v0.7.5-E Hermes Activation with Remote Blackboard Boundary is plan-first.
v0.7.5-E does not activate Hermes.
v0.7.5-E does not connect Hermes.
v0.7.5-E does not connect OpenClaw.
v0.7.5-E does not start Worker.
v0.7.5-E does not create Hermes runtime.
v0.7.5-E does not create Hermes activation runtime.
v0.7.5-E does not create OpenClaw runtime.
v0.7.5-E does not create Worker runtime.
v0.7.5-E does not implement Remote Blackboard API runtime.
v0.7.5-E does not create production DB.
v0.7.5-E does not create shared DB.
v0.7.5-E does not create remote shared DB.
v0.7.5-E does not migrate queue data.
v0.7.5-E does not sync local queue and remote queue.
v0.7.5-E does not open shared write.
v0.7.5-E does not write Google Sheets.
v0.7.5-E does not create webhook.
```

## 4. Relationship to v0.7.5-A / B / C / D

v0.7.5-A planned the Remote Blackboard API. v0.7.5-B planned the local-vs-remote queue
boundary. v0.7.5-C planned how the Dashboard would identify backend sources. v0.7.5-D
planned the core runtime host. v0.7.5-E builds on all four by planning *how Hermes would
enter a Blackboard mode* under Owner supervision — without changing any prior boundary.
Planning Hermes activation is not activating Hermes, and does not connect OpenClaw, start
the Worker, or create a Remote Blackboard API runtime.

## 5. Problem statement

```
Hermes is intended as Owner proxy / strategy / memory layer.
Hermes is not currently active.
Hermes is not currently connected to OpenClaw.
Hermes is not currently connected to Worker.
Hermes is not currently connected to Remote Blackboard API.
Remote Blackboard mode must be optional and Owner-directed.
Entering Blackboard mode must not imply execution permission.
Hermes activation requires a separate future plan and Owner approval.
Planning Hermes activation is not activating Hermes.
```

## 6. Hermes activation definition

```
Hermes activation means a future approved mode where Hermes may participate in Owner-supervised coordination.
Hermes activation may eventually read Blackboard messages after approval.
Hermes activation may eventually write Advice Messages after approval.
Hermes activation may eventually draft Task Messages after approval.
Hermes activation must preserve Owner review.
Hermes activation must preserve decision and dispatch separation.
Hermes activation must preserve audit trail.
Hermes activation is not implemented in v0.7.5-E.
Hermes activation is not Worker dispatch.
Hermes activation is not OpenClaw call.
```

## 7. Hermes remains inactive boundary

```
Hermes remains Not Connected.
Hermes is not activated in v0.7.5-E.
Hermes is not called in v0.7.5-E.
Hermes runtime is not created in v0.7.5-E.
Hermes activation runtime is not created in v0.7.5-E.
Hermes does not read queue data in v0.7.5-E.
Hermes does not write Blackboard messages in v0.7.5-E.
Hermes does not call OpenClaw in v0.7.5-E.
Hermes does not start Worker in v0.7.5-E.
```

## 8. Remote Blackboard mode definition

```
Remote Blackboard mode is a future coordination mode.
Remote Blackboard mode may allow Hermes to read Task Messages after approval.
Remote Blackboard mode may allow Hermes to write Advice Messages after approval.
Remote Blackboard mode may allow Hermes to draft Task Messages after approval.
Remote Blackboard mode is not enabled in v0.7.5-E.
Remote Blackboard mode is not Remote Blackboard API runtime.
Remote Blackboard mode is not shared write by default.
Remote Blackboard mode is not Worker dispatch.
Remote Blackboard mode is not OpenClaw call.
```

## 9. Blackboard mode is optional

```
Blackboard mode is optional.
Owner decides whether to enter Blackboard mode.
Owner decides when to exit Blackboard mode.
Not every conversation enters Blackboard mode.
Not every conversation is logged to Blackboard.
Entering normal chat is not Blackboard mode.
Planning Blackboard mode is not enabling Blackboard mode.
```

## 10. Entering Blackboard mode is not execution permission

```
Entering Blackboard mode is not execution permission.
Writing a task to Blackboard is not Worker dispatch.
Writing Advice Message is not OpenClaw call.
Writing Decision Message is audit record, not command.
Approval readiness is not execution permission.
Owner approval message is not automatic dispatch.
Hermes recommendation is not execution permission.
Hermes advice is not automatic follow-up execution.
```

## 11. Hermes advice boundary

```
Hermes Advice Message is advisory.
Hermes Advice Message is not command.
Hermes Advice Message is not Worker dispatch.
Hermes Advice Message is not OpenClaw call.
Hermes Advice Message is not Google Sheets write.
```

## 12. Hermes task draft boundary

```
Hermes Task Message draft is draft only.
Hermes Task Message draft requires Owner review.
Hermes Task Message draft is not queue write by itself.
Hermes Task Message draft is not execution permission.
```

## 13. Hermes decision boundary

```
Hermes must not make final Owner decisions.
Owner remains final approval authority.
Decision Message remains Owner-supervised audit record.
```

## 14. Owner approval and activation boundary

```
Owner approval is required before activating Hermes.
Owner approval is required before connecting Hermes to Remote Blackboard.
Owner approval is required before allowing Hermes to write Advice Messages.
Owner approval is required before allowing Hermes to draft Task Messages.
Owner approval is required before connecting Hermes to OpenClaw.
Owner approval is required before starting Worker.
Owner approval is required before opening shared write.
Owner approval is required before creating Remote Blackboard API runtime.
Plan approval is not Hermes activation approval.
Plan approval is not OpenClaw connection approval.
Plan approval is not Worker start approval.
Plan approval is not shared write approval.
```

## 15. OpenClaw / Worker / Hermes separation boundary

```
Hermes is strategy / proxy / memory layer.
OpenClaw is execution / gateway / tools layer.
Worker is dispatch runtime.
Hermes must not bypass OpenClaw boundary.
Hermes must not bypass Worker boundary.
Hermes advice is not OpenClaw execution.
Hermes advice is not Worker dispatch.
OpenClaw remains Not Connected.
Worker remains OFF.
Hermes remains Not Connected.
```

## 16. Remote Blackboard API relationship

```
Remote Blackboard API runtime is not implemented in v0.7.5-E.
Remote Blackboard API is not called in v0.7.5-E.
Remote Blackboard API write is not enabled in v0.7.5-E.
Remote Blackboard API read is not enabled in v0.7.5-E.
Remote Blackboard API must preserve Owner review.
Remote Blackboard API must preserve audit trail.
Remote Blackboard API must preserve decision and dispatch separation.
Hermes Remote Blackboard access requires separate future plan and Owner approval.
```

## 17. Memory and learning boundary

```
Hermes memory store is not created in v0.7.5-E.
Hermes learning runtime is not created in v0.7.5-E.
Hermes does not train on queue data in v0.7.5-E.
Hermes does not train on private conversations in v0.7.5-E.
Future Hermes memory requires separate future plan and Owner approval.
```

## 18. Privacy and conversation logging boundary

```
No private conversation log is created in v0.7.5-E.
No all-conversation logging is enabled in v0.7.5-E.
No personal memory migration is performed in v0.7.5-E.
Not every conversation is logged to Blackboard.
Future conversation logging requires separate future plan and Owner approval.
```

## 19. Autonomy and delegation boundary

```
Owner remains final approval authority.
Hermes may eventually propose.
Hermes may eventually advise.
Hermes may eventually draft.
Hermes must not self-approve.
Hermes must not self-dispatch.
Hermes must not execute external actions by itself.
Hermes must not call OpenClaw without explicit future approval.
Hermes autonomy requires separate future plan and Owner approval.
```

## 20. Queue and data boundary

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
No source-of-truth switch is performed.
Hermes activation planning is not queue migration approval.
Hermes activation planning is not shared write approval.
```

## 21. Secrets and credentials boundary

```
No secrets are read in v0.7.5-E.
No secrets are copied in v0.7.5-E.
No secrets are created in v0.7.5-E.
No .env file is created in v0.7.5-E.
No credentials are moved to Hermes in v0.7.5-E.
No credentials are moved to OpenClaw in v0.7.5-E.
No credentials are moved to any runtime host in v0.7.5-E.
Hermes credentials require separate future plan and Owner approval.
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
No Hermes connector is created.
No OpenClaw connector is created.
Network activation requires separate future plan and Owner approval.
```

## 23. Runtime host relationship

```
Core runtime host plan does not activate Hermes.
Runtime host selection is not Hermes activation.
Runtime host activation is not Hermes activation by itself.
Hermes activation may require a future runtime host after approval.
No Core runtime host is created in v0.7.5-E.
No Worker runtime is created in v0.7.5-E.
No Hermes runtime is created in v0.7.5-E.
```

## 24. Failure / rollback / audit boundary

```
Future Hermes actions must be auditable.
Future Hermes actions must include rollback notes when external actions are involved.
Future Hermes failures must not silently retry external actions.
Future Hermes failures must not bypass Owner approval.
Future Hermes failures must not write Google Sheets by default.
Future Hermes failures must not call OpenClaw by default.
Future Hermes failures must not start Worker by default.
No Hermes failure handling runtime is implemented in v0.7.5-E.
```

## 25. Source-of-truth boundary

```
Hermes activation is not source-of-truth switch.
Hermes Blackboard participation is not queue migration by itself.
Current source of truth remains local to each environment.
Future remote authority requires separate future plan and Owner approval.
GitHub remains clean source of code and docs, not queue DB.
```

## 26. Blackboard message compatibility

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

## 27. Candidate future Hermes activation modes

These are planning notes only — none is implemented or enabled:

```
Candidate Hermes activation mode: inactive planning only.
Candidate Hermes activation mode: read-only Blackboard observer.
Candidate Hermes activation mode: Advice Message writer after Owner approval.
Candidate Hermes activation mode: Task Message draft proposer after Owner approval.
Candidate Hermes activation mode: Owner-supervised strategy agent.
Candidate Hermes activation modes are planning notes only.
No Hermes activation mode is implemented in v0.7.5-E.
No Hermes activation mode is enabled in v0.7.5-E.
```

## 28. Current safe system posture

```
Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
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

## 29. Validation summary

```
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

## 30. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 31. Non-goals

- Not activating Hermes; not connecting Hermes; not creating a Hermes runtime or Hermes
  activation runtime.
- Not connecting OpenClaw; not starting the Worker; not creating an OpenClaw or Worker
  runtime.
- Not implementing a Remote Blackboard API runtime; not enabling Remote Blackboard read or
  write.
- Not enabling Blackboard mode, Blackboard shared write, or Hermes blackboard mode.
- Not creating a Hermes memory store, learning runtime, all-conversation logging, or
  private conversation log.
- Not creating a production DB, shared DB, or remote shared DB.
- Not adding any API route, FastAPI router, Hermes client, OpenClaw client, database
  client, or migration.
- Not reading, copying, creating, or moving any secrets; not creating a `.env` file.
- Not creating a webhook, webhook receiver, or connector.
- Not synchronizing, migrating, moving, copying, merging, or backfilling any queue data;
  not implementing a conflict resolver or source-of-truth switch.
- Not opening shared write; not reading a real queue DB; not sending any POST.
- Not writing Google Sheets.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.

## 32. Acceptance criteria

- This plan document exists and contains sections 1–33.
- The current-master marker records `c871ece` on `origin/master`.
- The v0.7.5-E plan-first markers are present.
- The problem statement, Hermes activation definition, Hermes-remains-inactive boundary,
  Remote Blackboard mode definition, Blackboard-mode-optional, entering-Blackboard-mode-
  is-not-execution-permission, Hermes advice / task draft / decision boundary, Owner
  approval and activation boundary, OpenClaw / Worker / Hermes separation boundary, Remote
  Blackboard API relationship, memory and learning boundary, privacy and conversation
  logging boundary, autonomy and delegation boundary, queue and data boundary, secrets and
  credentials boundary, network / webhook / connector boundary, runtime host relationship,
  failure / rollback / audit boundary, source-of-truth boundary, blackboard message
  compatibility, candidate future Hermes activation mode, current safe posture, validation
  summary, and safety grep summary markers are present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script
  `check_hermes_openclaw_hermes_activation_remote_blackboard_boundary_v0_7_5_e.py` passes
  ALL.

## 33. Next recommended step

```
v0.7.5-R — Remote Blackboard Preparation Closeout
```

with the constraints:

```
v0.7.5-R must remain docs-only closeout.
v0.7.5-R must not activate Hermes.
v0.7.5-R must not connect OpenClaw.
v0.7.5-R must not start Worker.
v0.7.5-R must not create production DB.
v0.7.5-R must not create Remote Blackboard API runtime.
v0.7.5-R must not migrate queue data.
v0.7.5-R must not open shared write.
v0.7.5-R must not write Google Sheets.
```
