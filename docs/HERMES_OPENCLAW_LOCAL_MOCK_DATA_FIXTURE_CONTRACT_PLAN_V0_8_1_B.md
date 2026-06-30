# HERMES ↔ OpenClaw Adapter — Local Mock Data Fixture Contract Plan (v0.8.1-B)

> Plan-first / contract-first document. This is **documentation only**. It defines the data
> contract that a future Local Mock Data Fixture must satisfy — the fixture file boundary, the
> fixture schema boundary, the synthetic local-only data boundary, the per-message-family fixture
> contracts (Mock Task Message, Mock Decision Message, Mock Result Message, Mock Advice Message,
> Mock Badge Status, Mock Runtime-off Status), the required field contract, the forbidden field
> contract, the boolean safety invariant contract, the preview consumer boundary, the read-only
> fixture output boundary, and the Dashboard / runtime / queue / Worker / OpenClaw / Hermes /
> Google Sheets separation boundaries. It creates no fixture JSON, creates no mock data file,
> creates no seed data file, creates no fixture directory, creates no preview data loader,
> implements no fixture loader runtime, implements no Dashboard preview display runtime, adds no
> route, changes no template, changes no static, reads no real queue DB, writes no queue, sends no
> POST, starts no Worker, calls no OpenClaw, activates no Hermes, reads/writes no Google Sheets,
> creates no Remote Blackboard API runtime, creates no DB, and opens no shared write.

## 1. Purpose

This document plans — and only plans — the data contract for a future Local Mock Data Fixture.
A fixture contract describes what a future synthetic, local-only mock data file may contain, what
fields each mock message family must carry, which fields are forbidden, and which boolean safety
invariants must always hold, so that a future fixture can be drafted against an agreed contract
before any fixture file, loader, or Dashboard runtime is created.

Nothing here is built. This round adds **only** a plan document and a readiness script that
statically verifies that document. A fixture contract is not a fixture, not a loader, and not a
Dashboard preview. Defining the contract is not implementing the fixture.

## 2. Current master

```
HEAD = origin/master = 1492cad3bd473a6cfe3e37ba238e6f223d338e8d
docs: plan local mock data preview boundary
```

The working tree is clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

This round is a plan-first / contract-first round. The following define what v0.8.1-B is and is
not:

```
v0.8.1-B Local Mock Data Fixture Contract Plan is plan-first.
v0.8.1-B does not create fixture JSON.
v0.8.1-B does not create mock data file.
v0.8.1-B does not create seed data file.
v0.8.1-B does not create fixture directory.
v0.8.1-B does not create preview data loader.
v0.8.1-B does not implement fixture loader runtime.
v0.8.1-B does not implement Dashboard preview display runtime.
v0.8.1-B does not implement local mock data preview runtime.
v0.8.1-B does not create Dashboard route.
v0.8.1-B does not create Dashboard endpoint.
v0.8.1-B does not create Dashboard template.
v0.8.1-B does not create Dashboard static asset.
v0.8.1-B does not modify app.
v0.8.1-B does not modify templates.
v0.8.1-B does not modify static.
v0.8.1-B does not read real queue DB.
v0.8.1-B does not write queue data.
v0.8.1-B does not send POST.
v0.8.1-B does not start Worker.
v0.8.1-B does not connect OpenClaw.
v0.8.1-B does not activate Hermes.
v0.8.1-B does not connect Hermes.
v0.8.1-B does not read Google Sheets.
v0.8.1-B does not write Google Sheets.
v0.8.1-B does not read secrets.
v0.8.1-B does not create .env.
v0.8.1-B does not create webhook.
v0.8.1-B does not create connector.
v0.8.1-B does not create Remote Blackboard API runtime.
v0.8.1-B does not create production DB.
v0.8.1-B does not create shared DB.
v0.8.1-B does not open shared write.
```

## 4. Relationship to v0.8.1-A Local Mock Data Preview Implementation Boundary Plan

```
v0.8.1-A Local Mock Data Preview Implementation Boundary Plan is complete.
v0.8.1-B starts the Local Mock Data Fixture Contract planning step.
v0.8.1-B builds on Local Mock Data Preview Implementation Boundary planning.
v0.8.1-B plans the fixture data contract before any fixture file is created.
v0.8.1-B preserves Owner final approval authority.
v0.8.1-B preserves decision and dispatch separation.
v0.8.1-B preserves audit trail.
v0.8.1-B preserves dispatch-disabled boundary.
v0.8.1-B preserves local mock data preview boundary.
v0.8.1-B preserves read-only Dashboard display boundary.
v0.8.1-B does not change any v0.8.1-A boundary.
v0.8.1-B does not change any v0.8.0-G boundary.
v0.8.1-B does not change any v0.8.0-F boundary.
v0.8.1-B does not change any v0.8.0-A boundary.
v0.8.1-B does not change any v0.7.5 boundary.
```

## 5. Problem statement

```
The system needs a planned mock data fixture contract before any fixture file can be drafted.
Fixture contract must not become execution permission.
Fixture contract must not become Worker dispatch.
Fixture contract must not call OpenClaw.
Fixture contract must not activate Hermes.
Fixture contract must not write queue data.
Fixture contract must not read real queue DB.
Fixture contract must not send POST.
Fixture contract must not read or write Google Sheets.
A fixture without an agreed contract could leak real data or be mistaken for an execution surface.
Planning the fixture contract is not creating the fixture.
Planning the fixture contract is not running the loop.
```

## 6. Local Mock Data Fixture Contract definition

```
Local Mock Data Fixture Contract means the agreed data contract a future synthetic local-only mock data fixture must satisfy.
Local Mock Data Fixture Contract is a planning artifact in v0.8.1-B.
Local Mock Data Fixture Contract is not runtime code.
Local Mock Data Fixture Contract is not a fixture JSON file.
Local Mock Data Fixture Contract is not a mock data file.
Local Mock Data Fixture Contract is not a preview data loader.
Fixture contract is not fixture implementation.
Fixture contract is not execution permission.
Fixture contract is not Worker dispatch.
Fixture contract is not OpenClaw call.
Fixture contract is not Hermes action.
Fixture contract must not read real queue DB.
Fixture contract must not send POST.
Fixture contract must not create fixture JSON.
Fixture contract must not create preview data loader.
Local Mock Data Fixture Contract requires separate future plan and Owner approval before fixture implementation.
```

## 7. Fixture file boundary

```
Fixture file boundary is planning only.
A future fixture file must be synthetic local-only sample data.
A future fixture file must not contain real queue data.
A future fixture file must not contain secrets.
A future fixture file must not contain credentials.
A future fixture file must not contain real endpoints.
No fixture file is created in v0.8.1-B.
No fixture JSON is created in v0.8.1-B.
No fixture directory is created in v0.8.1-B.
```

## 8. Fixture schema boundary

```
Fixture schema boundary is planning only.
A future fixture schema must carry a schema_version.
A future fixture schema must mark every record is_mock = true.
A future fixture schema must declare its message_family.
A future fixture schema must not require real queue DB read.
A future fixture schema must not require secrets.
No fixture schema is implemented in v0.8.1-B.
No schema migration is performed in v0.8.1-B.
```

## 9. Synthetic local-only data boundary

```
Mock fixture data is synthetic local-only sample data.
Synthetic local-only data does not come from real queue DB.
Synthetic local-only data does not come from Google Sheets.
Synthetic local-only data does not come from Remote Blackboard API.
Synthetic local-only data does not come from secrets.
Synthetic local-only data does not switch source-of-truth.
No synthetic local-only data source reader is implemented in v0.8.1-B.
```

## 10. Mock Task Message fixture contract

```
Mock Task Message fixture record is synthetic local-only sample data.
Mock Task Message fixture record must set is_mock = true.
Mock Task Message fixture record must set message_family to a task family.
Mock Task Message fixture record is display-only.
Mock Task Message fixture record is not execution permission.
Mock Task Message fixture record is not Worker dispatch.
Mock Task Message fixture record must not contain real queue data.
No Mock Task Message fixture is created in v0.8.1-B.
```

## 11. Mock Decision Message fixture contract

```
Mock Decision Message fixture record is synthetic local-only sample data.
Mock Decision Message fixture record must set is_mock = true.
Mock Decision Message fixture record must set message_family to a decision family.
Mock Decision Message fixture record is display-only.
Mock Decision Message fixture record is not execution permission.
Mock Decision Message fixture record is not decision execution.
Mock Decision Message fixture record must not contain real queue data.
No Mock Decision Message fixture is created in v0.8.1-B.
```

## 12. Mock Result Message fixture contract

```
Mock Result Message fixture record is synthetic local-only sample data.
Mock Result Message fixture record must set is_mock = true.
Mock Result Message fixture record must set message_family to a result family.
Mock Result Message fixture record is display-only.
Mock Result Message fixture record is not execution permission.
Mock Result Message fixture record is not Worker dispatch.
Mock Result Message fixture record must not contain real queue data.
No Mock Result Message fixture is created in v0.8.1-B.
```

## 13. Mock Advice Message fixture contract

```
Mock Advice Message fixture record is synthetic local-only sample data.
Mock Advice Message fixture record must set is_mock = true.
Mock Advice Message fixture record must set message_family to an advice family.
Mock Advice Message fixture record is display-only.
Mock Advice Message fixture record is not execution permission.
Mock Advice Message fixture record is not Hermes action.
Mock Advice Message fixture record must not contain real queue data.
No Mock Advice Message fixture is created in v0.8.1-B.
```

## 14. Mock Badge Status fixture contract

```
Mock Badge Status fixture record is synthetic local-only sample data.
Mock Badge Status fixture record must set is_mock = true.
Mock Badge Status fixture record must set message_family to a badge-status family.
Mock Badge Status fixture record is display-only.
Mock Badge Status fixture record is not execution permission.
Mock Badge Status fixture record must not enable dispatch gate.
Mock Badge Status fixture record must not contain real queue data.
No Mock Badge Status fixture is created in v0.8.1-B.
```

## 15. Mock Runtime-off Status fixture contract

```
Mock Runtime-off Status fixture record is synthetic local-only sample data.
Mock Runtime-off Status fixture record must set is_mock = true.
Mock Runtime-off Status fixture record must set message_family to a runtime-off-status family.
Mock Runtime-off Status fixture record may show DISPATCH OFF.
Mock Runtime-off Status fixture record may show WORKER OFF.
Mock Runtime-off Status fixture record may show OPENCLAW NOT CONNECTED.
Mock Runtime-off Status fixture record may show HERMES NOT CONNECTED.
Mock Runtime-off Status fixture record may show GOOGLE SHEETS DISABLED.
Mock Runtime-off Status fixture record is display-only.
Mock Runtime-off Status fixture record is not execution permission.
Mock Runtime-off Status fixture record must not start Worker.
Mock Runtime-off Status fixture record must not connect OpenClaw.
Mock Runtime-off Status fixture record must not activate Hermes.
No Mock Runtime-off Status fixture is created in v0.8.1-B.
```

## 16. Required field contract

These are candidate required field names only. No fixture field is implemented.

```
Required field candidate: fixture_id.
Required field candidate: schema_version.
Required field candidate: is_mock.
Required field candidate: message_family.
Required field candidate: message_id.
Required field candidate: preview_id.
Required field candidate: created_for.
Required field candidate: display_title.
Required field candidate: display_summary.
Required field candidate: safety_notes.
Required field candidate: next_owner_action.
Required field contract is planning only.
No required field is implemented in v0.8.1-B.
```

## 17. Forbidden field contract

These forbidden field names are allowed planning tokens here; they must never appear in a future
fixture file. No real value of any of these is included.

```
Forbidden field: real_queue_id.
Forbidden field: real_task_id.
Forbidden field: real_user_secret.
Forbidden field: spreadsheet_id.
Forbidden field: refresh_token.
Forbidden field: client_secret.
Forbidden field: private_key.
Forbidden field: webhook_url.
Forbidden field: openclaw_endpoint.
Forbidden field: hermes_endpoint.
Forbidden field: production_db_url.
Forbidden field: remote_blackboard_api_url.
Forbidden field contract is planning only.
No forbidden field value is included in v0.8.1-B.
```

## 18. Boolean safety invariant contract

These are candidate boolean safety invariants every future fixture record must satisfy.

```
Boolean safety invariant: is_mock = true.
Boolean safety invariant: dispatch_enabled = false.
Boolean safety invariant: worker_running = false.
Boolean safety invariant: openclaw_connected = false.
Boolean safety invariant: hermes_connected = false.
Boolean safety invariant: google_sheets_enabled = false.
Boolean safety invariant: external_side_effects = false.
Boolean safety invariant: approval_is_execution = false.
Boolean safety invariant: approval_readiness_is_execution = false.
Boolean safety invariant contract is planning only.
No boolean safety invariant runtime is implemented in v0.8.1-B.
```

## 19. Message family contract

```
Message family contract enumerates the mock fixture families.
Mock Task Message
Mock Decision Message
Mock Result Message
Mock Advice Message
Mock Badge Status
Mock Runtime-off Status
Message family contract is planning only.
No message family runtime is implemented in v0.8.1-B.
```

## 20. Preview consumer boundary

```
A future preview consumer may read the fixture in read-only mode.
Preview consumer is display-only.
Preview consumer is not execution permission.
Preview consumer is not Worker dispatch.
Preview consumer is not OpenClaw call.
Preview consumer is not Hermes action.
Preview consumer must not write the fixture.
Preview consumer must not read real queue DB.
Preview consumer must not send POST.
No preview consumer runtime is implemented in v0.8.1-B.
No preview data loader is implemented in v0.8.1-B.
```

## 21. Read-only fixture output boundary

```
Approval is not execution.
Approval readiness is not execution permission.
Decision and dispatch remain separate.
Fixture output is read-only.
Fixture output is display-only.
Fixture output is not execution permission.
Fixture output must not write queue data.
Fixture output must not send POST.
Fixture output must not dispatch Worker.
Fixture output must not call OpenClaw.
Fixture output must not call Hermes.
Fixture output must not write Google Sheets.
Dashboard preview display is read-only.
No fixture output renderer is implemented in v0.8.1-B.
```

## 22. Dashboard display relationship

```
Dashboard may eventually display local mock data fixture records.
Fixture record display is display-only.
Fixture record display is not execution permission.
Fixture record display is not Worker dispatch.
Fixture record display is not OpenClaw call.
Fixture record display is not Hermes action.
Dashboard preview display is read-only.
No Dashboard fixture display runtime is implemented in v0.8.1-B.
```

## 23. Dashboard route / template / static boundary

```
Dashboard route boundary is planning only.
No Dashboard route is created in v0.8.1-B.
No Dashboard endpoint is created in v0.8.1-B.
No Dashboard template is created in v0.8.1-B.
No Dashboard static asset is created in v0.8.1-B.
No app route is modified in v0.8.1-B.
No template file is modified in v0.8.1-B.
No static file is modified in v0.8.1-B.
```

## 24. App / runtime boundary

```
App / runtime boundary is planning only.
No app module is modified in v0.8.1-B.
No app.main import is performed in v0.8.1-B.
No QueueStore import is performed in v0.8.1-B.
No runtime host is created in v0.8.1-B.
No daemon is created in v0.8.1-B.
No systemd service is created in v0.8.1-B.
No Docker deployment is created in v0.8.1-B.
No fixture loader runtime is created in v0.8.1-B.
```

## 25. Queue and real data boundary

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

## 26. Remote Blackboard API relationship

```
Remote Blackboard API remains planning only.
Remote Blackboard API runtime is not implemented in v0.8.1-B.
Remote Blackboard API read is not enabled in v0.8.1-B.
Remote Blackboard API write is not enabled in v0.8.1-B.
Remote Blackboard API is not required for fixture contract planning.
```

## 27. Worker / OpenClaw / Hermes separation boundary

```
Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Worker is dispatch runtime.
OpenClaw is execution / gateway / tools layer.
Hermes is strategy / proxy / memory layer.
Worker must not run from plan-only fixture contract.
OpenClaw must not execute from plan-only fixture contract.
Hermes must not act from plan-only fixture contract.
```

## 28. Google Sheets boundary

```
Google Sheets remains Disabled.
No Google Sheets read is required.
No Google Sheets write is performed.
No Google Sheets live write is enabled.
```

## 29. Secrets / privacy / memory boundary

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

## 30. Network / webhook / connector boundary

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

## 31. Failure / rollback / audit boundary

```
Future fixture contract changes must be auditable.
Future fixture actions must include rollback notes when external actions are involved.
Future fixture failures must not silently retry external actions.
Future fixture failures must not bypass Owner approval.
Future fixture failures must not write Google Sheets by default.
Future fixture failures must not call OpenClaw by default.
Future fixture failures must not start Worker by default.
No fixture failure handling runtime is implemented in v0.8.1-B.
```

## 32. Candidate fixture validation rules

These are candidate planning notes only. No fixture validation runtime is implemented.

```
Candidate fixture validation rule: is_mock must remain true.
Candidate fixture validation rule: schema_version must be present.
Candidate fixture validation rule: message_family must be one of the agreed families.
Candidate fixture validation rule: dispatch_enabled must remain false.
Candidate fixture validation rule: worker_running must remain false.
Candidate fixture validation rule: openclaw_connected must remain false.
Candidate fixture validation rule: hermes_connected must remain false.
Candidate fixture validation rule: google_sheets_enabled must remain false.
Candidate fixture validation rule: approval_is_execution must remain false.
Candidate fixture validation rule: approval_readiness_is_execution must remain false.
Candidate fixture validation rule: external_side_effects must remain false.
Candidate fixture validation rule: no forbidden field may be present.
Candidate fixture validation rule: fixture output must remain read-only.
Candidate fixture validation rules are planning only.
No fixture validation runtime is implemented in v0.8.1-B.
```

## 33. Candidate future phases

These are candidate planning notes only. No candidate phase is implemented or enabled.

```
Candidate future phase: docs-only local mock data fixture contract plan.
Candidate future phase: local mock data fixture draft plan.
Candidate future phase: candidate fixture record inventory.
Candidate future phase: read-only Mock Task Message fixture draft.
Candidate future phase: read-only Mock Decision Message fixture draft.
Candidate future phase: read-only Mock Result Message fixture draft.
Candidate future phase: read-only Mock Advice Message fixture draft.
Candidate future phase: read-only Mock Badge Status fixture draft.
Candidate future phase: read-only Mock Runtime-off Status fixture draft.
Candidate future phases are planning notes only.
No candidate future phase is implemented in v0.8.1-B.
No candidate future phase is enabled in v0.8.1-B.
```

## 34. Disabled runtime list

```
Fixture loader runtime is disabled.
Preview data loader runtime is disabled.
Local mock data preview runtime is disabled.
Dashboard fixture display runtime is disabled.
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

## 35. Current safe system posture

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
No fixture JSON.
No mock data file.
No seed data file.
No fixture directory.
No fixture loader runtime.
No preview data loader.
No local mock data preview runtime.
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

## 36. Validation summary

```
v0.8.1-B readiness: ALL PASS.
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

## 37. Safety grep summary

```
No real unsafe claim was found.
No real secret was found.
Forbidden field names are allowed planning tokens.
Readiness forbidden-pattern matches are benign.
```

## 38. Non-goals

This round is a plan. The following are explicitly out of scope:

- Creating any fixture JSON, mock data file, seed data file, or fixture directory.
- Creating any preview data loader or fixture loader runtime.
- Implementing any local mock data preview runtime, Dashboard fixture display runtime, Dashboard preview display runtime, Blackboard Loop runtime, Dashboard badge display runtime, Decision audit display runtime, Owner review checklist runtime, preview renderer runtime, loop contract runtime, or state machine runtime.
- Creating or modifying any Dashboard route, endpoint, template, or static asset.
- Modifying app, templates, or static.
- Creating any loop scheduler or fixture validation runtime.
- Enabling any dispatch gate; enabling autonomous execution.
- Activating or connecting Hermes; connecting OpenClaw; starting Worker.
- Creating any Hermes / OpenClaw / Worker runtime.
- Implementing the Remote Blackboard API runtime, route, read, or write.
- Creating any production DB, shared DB, or remote shared DB.
- Reading the real queue DB; modifying, migrating, syncing, backfilling, or merging queue data.
- Opening shared write; enabling Hermes blackboard mode; reading or writing Google Sheets.
- Reading, copying, or creating secrets; creating `.env`; moving credentials.
- Including any real value for a forbidden field.
- Creating any webhook, connector, listener, or external integration.
- Sending any POST or performing live local queue write validation.
- Any commit, push, or tag in this round.
- Starting v0.8.1-C, v0.8.1-D, or any real fixture implementation in this round.

## 39. Acceptance criteria

```
v0.8.1-B adds only two files: the plan doc and the readiness script.
v0.8.1-B modifies no existing app / scripts / docs / README / templates / static / runtime.
v0.8.1-B creates no fixture JSON, no mock data file, no loader, and no runtime.
v0.8.1-B readiness check: ALL PASS.
All prior readiness checks remain: ALL PASS.
compileall scripts: PASS.
Safety grep over the two new files yields only benign matches, forbidden-field planning tokens, and safe negations.
No commit, no push, no tag is performed in this round.
```

## 40. Next recommended step

```
v0.8.1-C — Local Mock Data Fixture Draft Plan
```

The next step must remain fixture draft planning, and must not start unless separately approved
by the Owner:

```
v0.8.1-C must not start unless separately approved by Owner.
v0.8.1-C must remain fixture draft planning unless separately approved.
v0.8.1-C must not create fixture JSON unless separately approved.
v0.8.1-C must not create preview data loader.
v0.8.1-C must not modify Dashboard route/template/static.
v0.8.1-C must not read real queue DB.
v0.8.1-C must not send POST.
v0.8.1-C must not start Worker.
v0.8.1-C must not call OpenClaw.
v0.8.1-C must not activate Hermes.
v0.8.1-C must not read or write Google Sheets.
```
