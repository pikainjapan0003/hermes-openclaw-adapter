# Hermes × OpenClaw — Local Mock Fixture JSON Read-only Loader Plan (v0.8.1-N)

## 1. Purpose

v0.8.1-N is plan-only. It plans how a future read-only loader would read the already-validated
synthetic local-only fixture JSON artifact. v0.8.1-N only plans a future read-only loader. It does
not implement anything. No loader, runtime, or Dashboard change is created in v0.8.1-N.

## 2. Plan-only positioning

v0.8.1-N is plan-only.
v0.8.1-N only plans a future read-only loader.
v0.8.1-N does not create a loader.
v0.8.1-N does not create a read-only loader.
v0.8.1-N does not create a preview data loader.
v0.8.1-N does not create a fixture loader runtime.
v0.8.1-N does not create a runtime.
v0.8.1-N does not modify Dashboard.
v0.8.1-N does not create a Dashboard route.
v0.8.1-N does not create a Dashboard endpoint.
v0.8.1-N does not create a Dashboard template.
v0.8.1-N does not create a Dashboard static asset.
v0.8.1-N does not modify app.
v0.8.1-N does not modify templates.
v0.8.1-N does not modify static.
v0.8.1-N does not read real queue DB.
v0.8.1-N does not write queue data.
v0.8.1-N does not send POST.
v0.8.1-N does not start Worker.
v0.8.1-N does not connect OpenClaw.
v0.8.1-N does not activate Hermes.
v0.8.1-N does not connect Hermes.
v0.8.1-N does not read Google Sheets.
v0.8.1-N does not write Google Sheets.
v0.8.1-N does not create production DB.
v0.8.1-N does not create shared DB.
v0.8.1-N does not create Remote Blackboard API runtime.
v0.8.1-N does not open shared write.
v0.8.1-N does not read secrets.
v0.8.1-N does not create .env.
v0.8.1-N does not create webhook.
v0.8.1-N does not create connector.
v0.8.1-N does not commit.
v0.8.1-N does not push.
v0.8.1-N does not tag.

## 3. Current master

HEAD = origin/master = 6db5764409cd8d4da766a2a992e572156848db2b

latest commit = 6db5764 docs: validate local mock fixture json artifact

## 4. Preceding artifacts

v0.8.1-L created:
fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json

v0.8.1-M validated:
docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md
scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py

These artifacts remain tracked and unchanged. v0.8.1-N does not modify the fixture JSON artifact.
v0.8.1-N does not modify the v0.8.1-M validation doc. v0.8.1-N does not modify the v0.8.1-M
validation script.

## 5. Problem statement

The fixture JSON artifact exists, is tracked, and passed v0.8.1-M validation. A future Dashboard
preview would need a read-only loader to read this fixture and expose it as read-only preview data.
Before any such loader is built, its contract must be planned so it stays read-only, local-only,
and free of any execution, dispatch, or external side effect. v0.8.1-N is that planning step and
nothing more.

## 6. Future read-only loader contract, plan-only:

Input:
- fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json

Precondition:
- v0.8.1-M validation must pass before any loader reads the fixture.

Allowed future behavior:
- read the local fixture JSON
- parse JSON locally
- validate schema_version
- validate is_mock = true
- validate records count = 6
- return an in-memory read-only preview data object
- include runtime-disabled badge values only as display data
- expose no execution interface
- expose no dispatch interface

Forbidden future behavior:
- no real queue DB read
- no queue write
- no POST
- no Worker dispatch
- no OpenClaw call
- no Hermes activation/call
- no Google Sheets read/write
- no secrets read
- no Dashboard mutation
- no route/endpoint/template/static creation in N
- no production DB/shared DB/Remote Blackboard API runtime

## 7. Future loader output, plan-only:

```json
{
  "source": "local_mock_fixture",
  "schema_version": "v0.8.1-local-mock-1",
  "is_mock": true,
  "local_only": true,
  "read_only": true,
  "records": [...],
  "runtime_badges": [
    "DISPATCH OFF",
    "WORKER OFF",
    "OPENCLAW NOT CONNECTED",
    "HERMES NOT CONNECTED",
    "GOOGLE SHEETS DISABLED"
  ],
  "execution_permission": false,
  "dispatch_permission": false,
  "external_side_effects_permission": false
}
```

This output contract is plan-only.
No code in v0.8.1-N returns this object.
No loader in v0.8.1-N reads this fixture.
No Dashboard in v0.8.1-N consumes this output.

## 8. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
loader_permission = false
dashboard_change_permission = false

In v0.8.1-N execution_permission remains false.
In v0.8.1-N dispatch_permission remains false.
In v0.8.1-N external_side_effects_permission remains false.

## 9. No-loader boundary

No loader is created in v0.8.1-N.
No read-only loader is created in v0.8.1-N.
No preview data loader is created in v0.8.1-N.
No fixture loader runtime is created in v0.8.1-N.
future loader implementation requires separate Owner approval.

## 10. No-Dashboard boundary

No Dashboard route is created in v0.8.1-N.
No Dashboard endpoint is created in v0.8.1-N.
No Dashboard template is created in v0.8.1-N.
No Dashboard static asset is created in v0.8.1-N.
No app route is modified in v0.8.1-N.
No template file is modified in v0.8.1-N.
No static file is modified in v0.8.1-N.

## 11. No-real-queue-DB boundary

No real queue DB read is performed in v0.8.1-N.
No queue write is performed in v0.8.1-N.
No queue migration is performed in v0.8.1-N.
No queue synchronization is performed in v0.8.1-N.
No source-of-truth switch is performed in v0.8.1-N.

## 12. No-POST boundary

No POST is sent in v0.8.1-N.
No external network call is added in v0.8.1-N.
No inbound listener is added in v0.8.1-N.
No outbound integration is added in v0.8.1-N.

## 13. No-Worker/OpenClaw/Hermes/Google Sheets boundary

Worker remains OFF.
OpenClaw remains Not Connected.
Hermes remains Not Connected.
Google Sheets remains Disabled.
No Worker execution in v0.8.1-N.
No OpenClaw call in v0.8.1-N.
No Hermes activation in v0.8.1-N.
No Hermes call in v0.8.1-N.
No Google Sheets read in v0.8.1-N.
No Google Sheets write in v0.8.1-N.
GOOGLE_SHEETS_ENABLED remains unset.

## 14. Secrets / privacy / memory boundary

No secrets are read in v0.8.1-N.
No secrets are copied in v0.8.1-N.
No .env file is created in v0.8.1-N.
No credentials are moved in v0.8.1-N.
No Hermes memory store is created in v0.8.1-N.

## 15. Disabled runtime list

Read-only loader runtime is disabled.
Preview data loader runtime is disabled.
Fixture loader runtime is disabled.
Dashboard preview display runtime is disabled.
Dispatch gate is disabled.
Worker runtime is disabled.
OpenClaw runtime is disabled.
Hermes runtime is disabled.
Remote Blackboard API runtime is disabled.
Shared write is disabled.
Google Sheets write is disabled.
Autonomous execution is disabled.

## 16. Current safe system posture

Dashboard read-only / controlled local route behavior.
Worker OFF.
OpenClaw Not Connected.
Hermes Not Connected.
Google Sheets Disabled.
DISPATCH OFF.
WORKER OFF.
OPENCLAW NOT CONNECTED.
HERMES NOT CONNECTED.
GOOGLE SHEETS DISABLED.
Fixture JSON exists and is tracked.
Fixture JSON is synthetic local-only.
Fixture JSON is unchanged in v0.8.1-N.
No loader runtime.
No read-only loader.
No preview data loader.
No Dashboard preview display runtime.
No dispatch gate enabled.
No autonomous execution.
No real queue DB read.
No POST.
No Worker execution.
No OpenClaw call.
No Hermes call.
No Google Sheets read.
No Google Sheets write.
No secrets read.
No .env created.
No webhook.
No connector.
No production DB.
No shared DB.
No Remote Blackboard API runtime.
No tag.

## 17. v0.8.1-N acceptance criteria:

- plan doc exists
- readiness script exists
- L fixture artifact remains tracked and unchanged
- M validation doc/script remain tracked and unchanged
- N clearly defines future read-only loader input
- N clearly defines future read-only loader precondition
- N clearly defines future read-only loader output contract
- N clearly forbids real queue DB reads
- N clearly forbids POST
- N clearly forbids Worker/OpenClaw/Hermes/Google Sheets
- N clearly forbids Dashboard changes
- N clearly says no loader is created in N
- N clearly says future loader implementation requires separate Owner approval

## 18. Validation summary

v0.8.1-N readiness: ALL PASS.
L fixture JSON artifact: tracked and unchanged.
M validation doc/script: tracked and unchanged.
compileall scripts: PASS.

## 19. Safety grep summary

No real unsafe claim was found.
No real secret was found.
Forbidden done-claim names are allowed planning tokens.

## 20. Non-goals

v0.8.1-N does not build a loader.
v0.8.1-N does not modify the Dashboard.
v0.8.1-N does not modify the fixture JSON.
v0.8.1-N does not modify the v0.8.1-M validation files.
v0.8.1-N does not start v0.8.1-O.

## 21. Next recommended step

v0.8.1-O — Local Mock Fixture JSON Read-only Loader Implementation Authorization Plan

v0.8.1-O must not start unless separately approved by Owner.
v0.8.1-O must not implement a loader unless separately approved by Owner.
v0.8.1-O must not modify Dashboard unless separately approved by Owner.
