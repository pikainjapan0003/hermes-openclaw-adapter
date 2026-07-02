# Hermes × OpenClaw — Local Mock Fixture Read-only Loader Dashboard Integration Boundary Plan (v0.8.1-S)

## 1. Purpose

v0.8.1-S is Dashboard integration boundary plan-only. It defines the boundaries a future Dashboard
must obey if it ever reads the in-memory preview data object returned by the v0.8.1-P loader. It
implements nothing: no Dashboard change, no loader change, no route, no runtime. It only writes down
the read-only, local-only boundary for a future integration.

## 2. Dashboard integration boundary plan-only positioning

v0.8.1-S is Dashboard integration boundary plan-only.
v0.8.1-S only defines future Dashboard integration boundaries for reading the v0.8.1-P loader in-memory preview object.
v0.8.1-S does not modify Dashboard.
v0.8.1-S does not modify loader.
v0.8.1-S does not create a Dashboard route.
v0.8.1-S does not create a Dashboard endpoint.
v0.8.1-S does not create a Dashboard template.
v0.8.1-S does not create a Dashboard static asset.
v0.8.1-S does not read real queue DB.
v0.8.1-S does not write queue data.
v0.8.1-S does not send POST.
v0.8.1-S does not make network calls.
v0.8.1-S does not start Worker.
v0.8.1-S does not call OpenClaw.
v0.8.1-S does not activate Hermes.
v0.8.1-S does not read Google Sheets.
v0.8.1-S does not write Google Sheets.
v0.8.1-S does not read secrets.
v0.8.1-S does not create .env.
v0.8.1-S does not create webhook.
v0.8.1-S does not create connector.
v0.8.1-S does not create production DB.
v0.8.1-S does not create shared DB.
v0.8.1-S does not create Remote Blackboard API runtime.
v0.8.1-S does not commit.
v0.8.1-S does not push.
v0.8.1-S does not tag.

## 3. Current master

HEAD = origin/master = b9e27dc91a62ea5987f22b0ddf02a87266994898

latest commit = b9e27dc test: add local mock fixture read-only loader runtime check

## 4. Preceding artifacts

v0.8.1-L fixture:
fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json

v0.8.1-M validation:
docs/HERMES_OPENCLAW_LOCAL_MOCK_DATA_FIXTURE_JSON_ARTIFACT_VALIDATION_V0_8_1_M.md
scripts/check_hermes_openclaw_local_mock_data_fixture_json_artifact_validation_v0_8_1_m.py

v0.8.1-N loader plan:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_PLAN_V0_8_1_N.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_plan_v0_8_1_n.py

v0.8.1-O implementation authorization:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_IMPLEMENTATION_AUTHORIZATION_PLAN_V0_8_1_O.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_implementation_authorization_plan_v0_8_1_o.py

v0.8.1-P loader:
scripts/load_local_mock_fixture_preview_v0_8_1.py

v0.8.1-Q loader validation plan:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_VALIDATION_PLAN_V0_8_1_Q.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_validation_plan_v0_8_1_q.py

v0.8.1-R loader runtime check:
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_runtime_check_v0_8_1_r.py

These artifacts remain tracked and unchanged. v0.8.1-S does not modify the fixture JSON artifact.
v0.8.1-S does not modify the v0.8.1-M validation doc/script. v0.8.1-S does not modify the v0.8.1-N
plan doc/script. v0.8.1-S does not modify the v0.8.1-O authorization doc/script. v0.8.1-S does not
modify the v0.8.1-P loader. v0.8.1-S does not modify the v0.8.1-Q validation doc/script. v0.8.1-S
does not modify the v0.8.1-R runtime check script.

## 5. Problem statement

The v0.8.1-P read-only loader returns an in-memory preview data object and has been validated
(v0.8.1-M/Q) and runtime-checked (v0.8.1-R). A future Dashboard preview would consume this object.
Before any Dashboard integration is authorized or built, the exact read-only boundary must be fixed
in writing so the Dashboard can never mutate, persist, dispatch, or externally act on the preview
data. v0.8.1-S is that boundary planning step and nothing more.

## 6. Future Dashboard integration boundary, plan-only:

- Dashboard may only read an in-memory preview data object returned by load_local_mock_fixture_preview().
- Dashboard must not read the fixture JSON directly.
- Dashboard must not read real queue DB.
- Dashboard must not write queue data.
- Dashboard must not dispatch.
- Dashboard must not call Worker.
- Dashboard must not call OpenClaw.
- Dashboard must not call Hermes.
- Dashboard must not read or write Google Sheets.
- Dashboard must not send POST.
- Dashboard must not make network calls.
- Dashboard must not read secrets.
- Dashboard must not expose execution controls.
- Dashboard must not expose dispatch controls.
- Dashboard must display disabled runtime badges.
- Dashboard must display local_only = true.
- Dashboard must display read_only = true.
- Dashboard must display execution_permission = false.
- Dashboard must display dispatch_permission = false.
- Dashboard must display external_side_effects_permission = false.

## 7. Allowed future concept, not implemented in v0.8.1-S:

A future Dashboard preview adapter may import load_local_mock_fixture_preview() and convert its returned in-memory object into read-only display rows.
The adapter must treat the returned object as immutable display data.
The adapter must not mutate records.
The adapter must not persist records.
The adapter must not dispatch records.
The adapter must not call external tools.
The adapter must not create routes or endpoints unless separately approved by Owner.
The adapter must not be connected to production/shared DB unless separately approved by Owner.

## 8. Forbidden future integration actions unless separately approved by Owner:

- modifying Dashboard route
- creating Dashboard endpoint
- creating Dashboard template
- creating Dashboard static asset
- reading real queue DB
- writing queue data
- sending POST
- making network calls
- starting Worker
- calling OpenClaw
- activating Hermes
- calling Hermes
- reading Google Sheets
- writing Google Sheets
- reading secrets
- creating .env
- creating webhook
- creating connector
- creating production DB
- creating shared DB
- creating Remote Blackboard API runtime
- enabling dispatch
- enabling external side effects

## 9. Validation method, plan-only:

1. Static inspection of this S boundary plan doc.
2. Git tracked-state check for L/M/N/O/P/Q/R artifacts.
3. Confirm P loader remains tracked and unchanged.
4. Confirm R runtime check remains tracked and available.
5. Confirm no Dashboard/app/templates/static files changed.
6. Confirm no real queue DB / POST / network / secrets integration is introduced.
7. Confirm S readiness script does not modify repo files or git index.

## 10. Known pre-commit coupling:

During v0.8.1-S Owner Review, older R/Q/O/N readiness scripts may fail only because the two new S files are untracked.
This is the same strict-untracked-file coupling observed in v0.8.1-O, v0.8.1-P, v0.8.1-Q, and v0.8.1-R.
This is acceptable only if the failure reason is exactly the two untracked S files.
No other regression failure is acceptable.
After S files are committed in a separately approved round, R/Q/O/N must recover to PASS.

## 11. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
loader_change_permission = false
dashboard_change_permission = false

In v0.8.1-S execution_permission remains false.
In v0.8.1-S dispatch_permission remains false.
In v0.8.1-S external_side_effects_permission remains false.

## 12. Current safe system posture

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
Fixture JSON is unchanged in v0.8.1-S.
P loader exists and is tracked.
P loader is unchanged in v0.8.1-S.
R runtime check exists and is tracked.
No loader change.
No Dashboard change.
No real queue DB read.
No POST.
No network call.
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

## 13. v0.8.1-S acceptance criteria:

- S boundary plan doc exists.
- S readiness script exists.
- S is plan-only.
- P loader remains tracked and unchanged.
- R runtime check remains tracked and unchanged.
- L fixture remains tracked and unchanged.
- M/N/O/Q artifacts remain tracked and unchanged.
- No Dashboard route/endpoint/template/static is created or modified.
- No app/templates/static files are modified.
- No real queue DB is read.
- No queue data is written.
- No POST is sent.
- No network call is made.
- No Worker/OpenClaw/Hermes/Google Sheets/secrets integration is introduced.
- Future Dashboard integration is restricted to read-only display of the in-memory preview object.
- Future Dashboard integration must display disabled runtime badges and all permission flags false.
- S does not commit / push / tag.

## 14. Non-goals

v0.8.1-S does not modify the Dashboard.
v0.8.1-S does not modify the loader.
v0.8.1-S does not modify the fixture JSON.
v0.8.1-S does not modify the v0.8.1-M/N/O/Q/R artifacts.
v0.8.1-S does not start v0.8.1-T.

## 15. Next recommended step

v0.8.1-T — Local Mock Fixture Read-only Loader Dashboard Integration Authorization Plan

v0.8.1-T must not start unless separately approved by Owner.
v0.8.1-T must not modify Dashboard unless separately approved by Owner.
v0.8.1-T must not modify loader unless separately approved by Owner.
v0.8.1-T must not enable dispatch unless separately approved by Owner.
