# HERMES ↔ OpenClaw Adapter — Remote Blackboard API Plan (v0.7.5-A)

> Plan-first document. This is **planning only**. It plans the future boundaries of a
> shared Blackboard backend / Remote Blackboard API. It implements no runtime, creates no
> database, migrates no queue data, opens no shared write, and introduces no external
> side effect.

## 1. Purpose

This document plans — and only plans — a future **Remote Blackboard API** / shared
Blackboard backend that would let the core Blackboard loop coordinate independently of a
Replit Dashboard update. It defines boundaries up front so that any future implementation
stays inside Owner-supervised, audit-preserving limits.

Nothing here is built. This round adds **only** a planning document and a readiness script
that statically verifies that document.

## 2. Current master

```
HEAD = origin/master = d67c153f6e0a84023b85a0bfd19b6d76c20240d1
docs: close out topology queue audit display line
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is plan-first. The following define what v0.7.5-A is and is not:

```
v0.7.5-A Remote Blackboard API Plan is plan-first.
v0.7.5-A does not implement Remote Blackboard API runtime.
v0.7.5-A does not create production DB.
v0.7.5-A does not create shared DB.
v0.7.5-A does not create remote shared DB.
v0.7.5-A does not migrate queue data.
v0.7.5-A does not open shared write.
v0.7.5-A does not start Worker.
v0.7.5-A does not call OpenClaw.
v0.7.5-A does not call Hermes.
v0.7.5-A does not write Google Sheets.
v0.7.5-A does not create webhook.
```

## 4. Relationship to v0.7.4-R

v0.7.4-R closed out the Topology + Queue + Audit Display line and recorded that the
Windows WSL local queue and the Replit local queue are separate, that Replit is a remote
observation station, and that a Dashboard update is a `git pull` plus a Dashboard restart.
v0.7.5-A builds on that closeout by planning how a future shared backend could remove the
core loop's dependence on a Dashboard update — without changing any of those boundaries.

## 5. Problem statement

```
Windows WSL local queue and Replit local queue are currently separate.
Replit Dashboard is a remote observation station, not the core system.
GitHub is clean source of code and docs, not queue DB or secrets store.
Dashboard update is git pull plus Dashboard restart only.
Core Blackboard loop should not depend on Replit Dashboard update.
Future shared blackboard requires Remote Blackboard API or shared DB.
```

## 6. Remote Blackboard API definition

```
Remote Blackboard API is a future shared coordination backend.
Remote Blackboard API is not implemented in v0.7.5-A.
Remote Blackboard API runtime is not created in v0.7.5-A.
Remote Blackboard API is not a webhook receiver in v0.7.5-A.
Remote Blackboard API is not a production executor.
Remote Blackboard API must preserve Owner review.
Remote Blackboard API must preserve decision and dispatch separation.
Remote Blackboard API must preserve audit trail.
```

## 7. Shared backend role

```
Shared backend may eventually store Task Messages.
Shared backend may eventually store Decision Messages.
Shared backend may eventually store Result Messages.
Shared backend may eventually store Advice Messages.
Shared backend must not store secrets.
Shared backend must not store raw credentials.
Shared backend must not bypass Owner approval.
Shared backend must not imply Worker dispatch.
```

## 8. Local queue vs remote blackboard boundary

The current local queue (Windows WSL) and any future remote blackboard are distinct
concerns. A future remote blackboard is a coordination surface for Blackboard messages; it
is not a replacement that silently absorbs the local queue. Until a separate migration
plan is approved, the local queue remains the source of truth and is never moved.

## 9. GitHub / WSL / Replit boundary

GitHub remains the clean source of code and docs, not a queue DB or secrets store. Windows
WSL remains the primary local development environment. Replit remains a remote observation
station / Preview Dashboard. A future Remote Blackboard API does not change these roles.

## 10. Data and secret boundary

A future shared backend stores Blackboard messages only. It must not store secrets or raw
credentials, and it must not expose any secret in a UI or in logs. Authentication
material, if any, lives outside the message store and is never committed to GitHub.

## 11. Blackboard message compatibility

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

## 12. Future API surface planning

The following are planning notes for a possible future surface. None of them is built in
this round:

```
Future API surface may include read task messages.
Future API surface may include create task draft.
Future API surface may include append decision message.
Future API surface may include append result message.
Future API surface may include append advice message.
Future API surface may include list audit trail.
Future API surface may include owner review state.
No API route is implemented in v0.7.5-A.
No FastAPI router is added in v0.7.5-A.
No database client is added in v0.7.5-A.
No migration is added in v0.7.5-A.
```

## 13. Future auth and permission boundary

```
Future remote blackboard must require authentication.
Future remote blackboard must require authorization.
Future remote blackboard must separate read permission from write permission.
Future remote blackboard must separate Owner decision from Worker dispatch.
Future remote blackboard must not expose secrets in UI or logs.
Future remote blackboard must support audit records.
Future remote blackboard must support rollback notes for external actions.
```

## 14. Read / write boundary

```
Dashboard read is not queue write.
Dashboard display is not execution permission.
Remote blackboard read is not Worker dispatch.
Remote blackboard write is not OpenClaw call.
Remote blackboard write is not Hermes action.
Remote blackboard write is not external side effect by itself.
Shared write remains disabled in v0.7.5-A.
```

## 15. Migration boundary

```
No queue migration is performed.
No local queue data is moved.
No Replit queue data is moved.
No production queue data is created.
No remote shared DB is created.
No data backfill is performed.
Migration requires a separate future plan and Owner approval.
```

## 16. Dashboard backend source boundary

A future Remote Blackboard API could become a backend source the Dashboard reads from, but
that is out of scope here. In v0.7.5-A the Dashboard backend source is unchanged, and the
Dashboard remains read-only / controlled local route behavior.

## 17. Worker / OpenClaw / Hermes boundary

A remote blackboard write is not a Worker dispatch, not an OpenClaw call, and not a Hermes
action. Worker remains OFF, OpenClaw remains Not Connected, and Hermes remains Not
Connected. Execution dispatch stays separately gated behind Owner approval.

## 18. Owner approval and activation boundary

Activating any future remote blackboard, shared DB, or migration requires explicit,
separate Owner approval. No activation flag is set in v0.7.5-A, and planning a surface is
not approving it.

## 19. Failure / rollback / audit planning

Any future external action must be auditable and reversible in record: a future remote
blackboard must support audit records and rollback notes for external actions. This is a
planning requirement only; no external action is taken in v0.7.5-A.

## 20. Candidate backend options

These are planning notes only — none is provisioned:

```
Candidate backend option: VPS-hosted API.
Candidate backend option: Postgres.
Candidate backend option: Redis.
Candidate backend option: Supabase.
Candidate backend option: Neon.
Candidate backend option: Railway.
Candidate backend option: Cloudflare D1.
Candidate backend options are planning notes only.
No candidate backend is provisioned in v0.7.5-A.
```

## 21. Current safe system posture

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
No connector.
No tag.
```

### Validation summary

```
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

### Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Readiness forbidden-pattern matches are benign.
```

## 22. Non-goals

- Not implementing a Remote Blackboard API runtime.
- Not creating a production DB, shared DB, or remote shared DB.
- Not adding any API route, FastAPI router, database client, or migration.
- Not migrating, moving, or backfilling any queue data.
- Not opening shared write.
- Not reading a real queue DB; not sending any POST.
- Not starting the Worker; not calling OpenClaw / Hermes; not writing Google Sheets.
- Not creating a webhook, webhook receiver, or connector.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.

## 23. Acceptance criteria

- This plan document exists and contains sections 1–24.
- The current-master marker records `d67c153` on `origin/master`.
- The v0.7.5-A plan-first markers are present.
- The problem statement, Remote Blackboard API definition, shared backend role, blackboard
  message compatibility, future API surface, future auth, read/write, migration, candidate
  backend, current safe posture, validation summary, and safety grep summary markers are
  present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script `check_hermes_openclaw_remote_blackboard_api_plan_v0_7_5_a.py`
  passes ALL.

## 24. Next recommended step

```
v0.7.5-B — Local vs Remote Queue Boundary
```

with the constraints:

```
v0.7.5-B must remain plan-first unless separately approved.
v0.7.5-B must not create production DB.
v0.7.5-B must not create Remote Blackboard API runtime.
v0.7.5-B must not migrate queue data.
v0.7.5-B must not open shared write.
v0.7.5-B must not start Worker / OpenClaw / Hermes / Google Sheets.
```
