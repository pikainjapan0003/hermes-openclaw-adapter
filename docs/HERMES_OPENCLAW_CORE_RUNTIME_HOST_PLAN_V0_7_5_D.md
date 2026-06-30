# HERMES ↔ OpenClaw Adapter — Core Runtime Host Plan (v0.7.5-D)

> Plan-first document. This is **planning only**. It plans the role and boundaries of a
> future core runtime host. It deploys no host, starts no Worker, connects no OpenClaw,
> connects no Hermes, creates no Remote Blackboard API runtime, creates no production DB,
> moves no queue, reads no secrets, and introduces no external side effect.

## 1. Purpose

This document plans — and only plans — the role and boundaries of a future **core runtime
host**: the machine or service that may, after separate Owner approval, run long-lived
runtime processes (Worker, OpenClaw coordination, Hermes coordination, or a Remote
Blackboard API). It defines these boundaries up front so that any future host selection,
provisioning, or deployment stays Owner-supervised and audit-preserving.

Nothing here is built. This round adds **only** a planning document and a readiness script
that statically verifies that document.

## 2. Current master

```
HEAD = origin/master = 7b5337cc88354626b41e414ea70d5a71189c9d76
docs: plan dashboard backend source
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is plan-first. The following define what v0.7.5-D is and is not:

```
v0.7.5-D Core Runtime Host Plan is plan-first.
v0.7.5-D does not create Core runtime host.
v0.7.5-D does not deploy VPS.
v0.7.5-D does not deploy Mac mini.
v0.7.5-D does not deploy home server.
v0.7.5-D does not create systemd service.
v0.7.5-D does not create daemon.
v0.7.5-D does not create Docker deployment.
v0.7.5-D does not implement Worker runtime.
v0.7.5-D does not implement OpenClaw runtime.
v0.7.5-D does not implement Hermes runtime.
v0.7.5-D does not implement Remote Blackboard API runtime.
v0.7.5-D does not create production DB.
v0.7.5-D does not create shared DB.
v0.7.5-D does not create remote shared DB.
v0.7.5-D does not migrate queue data.
v0.7.5-D does not sync local queue and remote queue.
v0.7.5-D does not open shared write.
v0.7.5-D does not start Worker.
v0.7.5-D does not call OpenClaw.
v0.7.5-D does not call Hermes.
v0.7.5-D does not write Google Sheets.
v0.7.5-D does not create webhook.
```

## 4. Relationship to v0.7.5-A / B / C

v0.7.5-A planned the future Remote Blackboard API and its boundaries. v0.7.5-B planned the
local-vs-remote queue boundary. v0.7.5-C planned how the Dashboard would identify and label
backend sources. v0.7.5-D builds on all three by planning *where* future runtime processes
would live — the core runtime host — without changing any prior boundary. Selecting or
planning a host is not deploying one, and does not activate Worker, OpenClaw, Hermes, or a
Remote Blackboard API.

## 5. Problem statement

```
Core runtime host is not yet selected.
Dashboard host and core runtime host may be separate.
Replit is a remote observation station, not production executor.
GitHub is clean source of code and docs, not runtime host.
Windows WSL is primary local development environment, not always-on production runtime.
Future Worker / OpenClaw / Hermes execution requires a controlled runtime host.
Runtime host activation requires a separate future plan and Owner approval.
Planning a host is not deploying a host.
```

## 6. Core runtime host definition

```
Core runtime host means the future machine or service that may run long-lived runtime processes.
Core runtime host may eventually run Worker.
Core runtime host may eventually coordinate OpenClaw.
Core runtime host may eventually coordinate Hermes.
Core runtime host may eventually read or write Remote Blackboard API after approval.
Core runtime host is not implemented in v0.7.5-D.
Core runtime host is not Dashboard by default.
Core runtime host is not GitHub.
Core runtime host must preserve Owner approval.
Core runtime host must preserve audit trail.
Core runtime host must preserve decision and dispatch separation.
```

## 7. Runtime host is not Dashboard host

```
Dashboard host displays state.
Runtime host executes long-lived processes only after approval.
Dashboard update is not runtime deployment.
Dashboard restart is not Worker start.
Dashboard backend source selection is not runtime host activation.
Dashboard host must not imply execution permission.
Runtime host must not be activated by Dashboard display.
No Dashboard runtime host coupling is implemented in v0.7.5-D.
```

## 8. GitHub / WSL / Replit / runtime host boundary

```
GitHub remains clean source of code and docs, not queue DB and not secrets store.
Windows WSL remains primary local development environment.
Replit remains remote observation station / Preview Dashboard.
Future runtime host is separate from GitHub.
Future runtime host is separate from Replit Preview unless separately approved.
Future runtime host is separate from Dashboard display.
No host role is changed in v0.7.5-D.
```

## 9. Candidate host options

These are planning notes only — none is provisioned or selected:

```
Candidate runtime host option: VPS.
Candidate runtime host option: Mac mini.
Candidate runtime host option: home server.
Candidate runtime host option: Windows WSL local development only.
Candidate runtime host option: Replit Preview observation only.
Candidate runtime host options are planning notes only.
No candidate runtime host is provisioned in v0.7.5-D.
No candidate runtime host is selected in v0.7.5-D.
```

## 10. Replit boundary

```
Replit remains Preview / observation station.
Replit must not become production executor in v0.7.5-D.
Replit must not start Worker in v0.7.5-D.
Replit must not receive production secrets in v0.7.5-D.
Replit local queue remains separate.
Replit Dashboard update remains git pull plus Dashboard restart only.
No Replit runtime deployment is performed in v0.7.5-D.
```

## 11. Windows WSL boundary

```
Windows WSL remains primary local development environment.
Windows WSL may run local development checks.
Windows WSL local queue remains local.
Windows WSL is not automatically always-on production runtime.
Windows WSL does not become Core runtime host in v0.7.5-D.
No WSL runtime deployment is performed in v0.7.5-D.
```

## 12. VPS / Mac mini / home server boundary

```
VPS is a candidate runtime host only.
Mac mini is a candidate runtime host only.
Home server is a candidate runtime host only.
No VPS is provisioned in v0.7.5-D.
No Mac mini is configured in v0.7.5-D.
No home server is configured in v0.7.5-D.
No SSH setup is performed in v0.7.5-D.
No production process is installed in v0.7.5-D.
```

## 13. Worker host boundary

```
Worker remains OFF.
Worker host is not selected in v0.7.5-D.
Worker runtime is not implemented in v0.7.5-D.
Worker is not started in v0.7.5-D.
```

## 14. OpenClaw host boundary

```
OpenClaw remains Not Connected.
OpenClaw host is not selected in v0.7.5-D.
OpenClaw runtime is not implemented in v0.7.5-D.
OpenClaw is not called in v0.7.5-D.
```

## 15. Hermes host boundary

```
Hermes remains Not Connected.
Hermes host is not selected in v0.7.5-D.
Hermes runtime is not implemented in v0.7.5-D.
Hermes is not called in v0.7.5-D.
```

## 16. Remote Blackboard API host boundary

```
Remote Blackboard API runtime is not implemented in v0.7.5-D.
Remote Blackboard API host is not selected in v0.7.5-D.
Remote Blackboard API host is not provisioned in v0.7.5-D.
Remote Blackboard API deployment requires separate future plan and Owner approval.
Remote Blackboard API must preserve Owner review.
Remote Blackboard API must preserve audit trail.
Remote Blackboard API must preserve decision and dispatch separation.
```

## 17. Dashboard backend source relationship

```
Dashboard backend source plan does not activate runtime host.
Dashboard source label is not execution permission.
Dashboard read is not Worker dispatch.
Dashboard read is not OpenClaw call.
Dashboard read is not Hermes action.
Dashboard source switching is not runtime host activation.
No Dashboard backend source runtime is implemented in v0.7.5-D.
```

## 18. Queue and data boundary

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
Runtime host planning is not queue migration approval.
Runtime host planning is not shared write approval.
```

## 19. Secrets and credentials boundary

```
No secrets are read in v0.7.5-D.
No secrets are copied in v0.7.5-D.
No secrets are created in v0.7.5-D.
No .env file is created in v0.7.5-D.
No credentials are moved to any host in v0.7.5-D.
GitHub must not store secrets.
Replit must not receive production secrets in v0.7.5-D.
Runtime host secrets require separate future plan and Owner approval.
```

## 20. Network / webhook / connector boundary

```
No webhook is created.
No webhook receiver is created.
No connector is created.
No external network call is added.
No inbound listener is added.
No outbound integration is added.
No port exposure is configured.
Network activation requires separate future plan and Owner approval.
```

## 21. Deployment and process boundary

```
No systemd service is created.
No daemon is created.
No Docker deployment is created.
No process manager is configured.
No cron job is created.
No background worker is started.
No long-lived process is started.
No production deployment is performed.
Deployment requires separate future plan and Owner approval.
```

## 22. Owner approval and activation boundary

```
Owner approval is required before selecting runtime host.
Owner approval is required before provisioning runtime host.
Owner approval is required before deploying runtime process.
Owner approval is required before starting Worker.
Owner approval is required before connecting OpenClaw.
Owner approval is required before connecting Hermes.
Owner approval is required before using production secrets.
Owner approval is required before creating Remote Blackboard API runtime.
Owner approval is required before opening shared write.
Plan approval is not runtime approval.
Plan approval is not deployment approval.
Plan approval is not Worker start approval.
Plan approval is not OpenClaw connection approval.
Plan approval is not Hermes activation approval.
```

## 23. Failure / rollback / audit boundary

```
Future runtime host actions must be auditable.
Future runtime host actions must include rollback notes.
Future runtime host failures must not silently retry external actions.
Future runtime host failures must not bypass Owner approval.
Future runtime host failures must not write Google Sheets by default.
Future runtime host failures must not call OpenClaw or Hermes by default.
No runtime failure handling is implemented in v0.7.5-D.
```

## 24. Source-of-truth boundary

```
Runtime host selection is not source-of-truth switch.
Runtime host activation is not queue migration by itself.
Current source of truth remains local to each environment.
Future remote authority requires separate future plan and Owner approval.
GitHub remains clean source of code and docs, not queue DB.
```

## 25. Blackboard message compatibility

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

## 26. Current safe system posture

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
No Hermes runtime.
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

- Not creating a Core runtime host, Worker runtime, OpenClaw runtime, or Hermes runtime.
- Not implementing a Remote Blackboard API runtime.
- Not creating a production DB, shared DB, or remote shared DB.
- Not deploying a VPS, Mac mini, or home server.
- Not creating a systemd service, daemon, Docker deployment, process manager, or cron job.
- Not adding any API route, FastAPI router, runtime host client, database client, or
  migration.
- Not reading, copying, creating, or moving any secrets; not creating a `.env` file.
- Not creating a webhook, webhook receiver, connector, inbound listener, or outbound
  integration; not exposing a port.
- Not synchronizing, migrating, moving, copying, merging, or backfilling any queue data;
  not implementing a conflict resolver or source-of-truth switch.
- Not opening shared write; not reading a real queue DB; not sending any POST.
- Not starting the Worker; not calling OpenClaw / Hermes; not writing Google Sheets.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.

## 30. Acceptance criteria

- This plan document exists and contains sections 1–31.
- The current-master marker records `7b5337c` on `origin/master`.
- The v0.7.5-D plan-first markers are present.
- The problem statement, core runtime host definition, runtime-host-is-not-Dashboard-host,
  GitHub / WSL / Replit / runtime host boundary, candidate host option, Replit boundary,
  Windows WSL boundary, VPS / Mac mini / home server boundary, Worker / OpenClaw / Hermes
  boundary, Remote Blackboard API host boundary, Dashboard backend source relationship,
  queue and data boundary, secrets and credentials boundary, network / webhook / connector
  boundary, deployment and process boundary, Owner approval and activation boundary,
  failure / rollback / audit boundary, source-of-truth boundary, blackboard message
  compatibility, current safe posture, validation summary, and safety grep summary markers
  are present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script `check_hermes_openclaw_core_runtime_host_plan_v0_7_5_d.py` passes
  ALL.

## 31. Next recommended step

```
v0.7.5-E — Hermes Activation with Remote Blackboard Boundary
```

with the constraints:

```
v0.7.5-E must remain plan-first unless separately approved.
v0.7.5-E must not activate Hermes.
v0.7.5-E must not connect OpenClaw.
v0.7.5-E must not start Worker.
v0.7.5-E must not create production DB.
v0.7.5-E must not create Remote Blackboard API runtime.
v0.7.5-E must not migrate queue data.
v0.7.5-E must not open shared write.
v0.7.5-E must not write Google Sheets.
```
