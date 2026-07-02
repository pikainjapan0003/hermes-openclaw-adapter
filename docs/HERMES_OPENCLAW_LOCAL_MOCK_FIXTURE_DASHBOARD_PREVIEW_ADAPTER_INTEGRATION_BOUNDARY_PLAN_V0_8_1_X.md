# Hermes × OpenClaw — Local Mock Fixture Dashboard Preview Adapter Integration Boundary Plan (v0.8.1-X)

## 1. Purpose

v0.8.1-X is a boundary plan only.
v0.8.1-X does not implement Dashboard integration.
v0.8.1-X does not modify Dashboard.
v0.8.1-X does not modify adapter.
v0.8.1-X does not modify loader.
v0.8.1-X only defines the future safe boundary for Dashboard to consume the v0.8.1-V read-only preview adapter.

It defines nothing but the boundary a future, separately approved implementation round must obey if it
ever lets Dashboard display the v0.8.1-V adapter's read-only preview model. It creates no Dashboard
file, no route, no endpoint, no template, no static asset, and modifies no existing file other than
adding this doc and its readiness script.

## 2. Base

Base HEAD / origin/master:
3b1b1bcaa248b5f2706d75a84ccaa366198cf91f

Base commit:
3b1b1bc test: add dashboard preview adapter runtime check

## 3. Preceding artifacts

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

v0.8.1-S Dashboard integration boundary:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py

v0.8.1-T Dashboard integration authorization:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py

v0.8.1-U Dashboard preview integration implementation plan:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_PREVIEW_INTEGRATION_IMPLEMENTATION_PLAN_V0_8_1_U.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_preview_integration_implementation_plan_v0_8_1_u.py

v0.8.1-V read-only Dashboard preview adapter:
scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py
scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py

v0.8.1-W adapter runtime check:
scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py

These artifacts remain tracked and unchanged. v0.8.1-X does not modify the fixture JSON artifact.
v0.8.1-X does not modify the v0.8.1-M/N/O/Q/R/S/T/U artifacts. v0.8.1-X does not modify the v0.8.1-P
loader. v0.8.1-X does not modify the v0.8.1-V adapter or its readiness script. v0.8.1-X does not
modify the v0.8.1-W runtime check script.

## 4. Future Dashboard integration data entry point, plan-only:

Future Dashboard integration must consume only:
scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py

Allowed callable:
build_dashboard_preview_model()

Optional allowed callable:
build_dashboard_preview_rows()

Dashboard must not call:
load_local_mock_fixture_preview()
validate_local_mock_fixture_preview_object()
fixture JSON file
real queue DB
QueueStore
Worker
OpenClaw
Hermes
Google Sheets

The v0.8.1-V adapter is the only sanctioned boundary between Dashboard and the loader. Dashboard code
must never import or call the loader functions directly, never open the fixture JSON path itself, and
never reach past the adapter into QueueStore, Worker, OpenClaw, Hermes, or Google Sheets integration.

## 5. Future Dashboard safe output requirements, plan-only:

Dashboard display must be read-only.
Dashboard display must show disabled runtime badges.
Dashboard display must show or preserve local_only = True.
Dashboard display must show or preserve read_only = True.
Dashboard display must show or preserve is_mock = True.
Dashboard display must show or preserve execution_permission = False.
Dashboard display must show or preserve dispatch_permission = False.
Dashboard display must show or preserve external_side_effects_permission = False.
Dashboard display must not expose execution controls.
Dashboard display must not expose dispatch controls.
Dashboard display must not expose external action controls.
Dashboard display must not expose action_url, post_url, webhook_url, endpoint_url, execute_url, dispatch_url.

## 6. Future candidate Dashboard files, plan-only:

Future separately approved integration may modify only explicitly approved Dashboard preview files.
Examples of future candidate files may include:
- app route file that already owns local Dashboard preview routes
- template file that already owns local Dashboard preview display
- minimal test/check script for that integration

v0.8.1-X itself creates none of these files.
v0.8.1-X itself modifies none of these files.

## 7. Future implementation forbidden actions, plan-only:

Do not read fixture JSON directly from Dashboard.
Do not read real queue DB.
Do not write queue data.
Do not call QueueStore.
Do not POST.
Do not make network calls.
Do not start Worker.
Do not call OpenClaw.
Do not activate Hermes.
Do not read Google Sheets.
Do not write Google Sheets.
Do not read secrets.
Do not create .env.
Do not create webhook.
Do not create connector.
Do not create production DB.
Do not create shared DB.
Do not create Remote Blackboard API runtime.
Do not expose execution controls.
Do not expose dispatch controls.
Do not expose external actions.

## 8. Future validation requirements, plan-only:

Before any future Dashboard integration commit:
- W runtime check must PASS.
- V readiness must PASS.
- U/T/S/R/Q/O/N checks must PASS after future files are tracked or known benign coupling must be explicitly documented before commit.
- M/K/J/I/H/G/F/E/D/C/B/A/v0.8.0-G/v0.8.0-F checks must PASS.
- compileall must PASS.
- safety grep must show only benign matches.
- git diff must show only approved files.
- no tag should be created.

## 9. Rollback boundary, plan-only:

Rollback of any future Dashboard integration must remove only the future Dashboard integration files/changes.
Rollback must not modify fixture JSON.
Rollback must not modify P loader.
Rollback must not modify V adapter.
Rollback must not modify W runtime check.
Rollback must not clean patches/.

## 10. Known pre-commit coupling:

During v0.8.1-X Owner Review, older W/V/U/T/S/R/Q/O/N readiness scripts may fail only because the two
new X files are untracked.
This is the same strict-untracked-file coupling observed in v0.8.1-O, v0.8.1-P, v0.8.1-Q, v0.8.1-R,
v0.8.1-S, v0.8.1-T, v0.8.1-U, and v0.8.1-V.
This is acceptable only if the failure reason is exactly the two untracked X files.
No other regression failure is acceptable.
After X files are committed in a separately approved round, W/V/U/T/S/R/Q/O/N must recover to PASS.

## 11. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
loader_change_permission = false
adapter_change_permission = false
dashboard_change_permission = false

In v0.8.1-X execution_permission remains false.
In v0.8.1-X dispatch_permission remains false.
In v0.8.1-X external_side_effects_permission remains false.

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
Fixture JSON is unchanged in v0.8.1-X.
P loader exists and is tracked.
P loader is unchanged in v0.8.1-X.
V adapter exists and is tracked.
V adapter is unchanged in v0.8.1-X.
W runtime check exists and is tracked.
W runtime check is unchanged in v0.8.1-X.
No loader change.
No adapter change.
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

## 13. v0.8.1-X acceptance criteria:

- X boundary plan doc exists.
- X readiness script exists.
- X is plan-only.
- P loader remains tracked and unchanged.
- V adapter remains tracked and unchanged.
- W runtime check remains tracked and unchanged.
- L fixture remains tracked and unchanged.
- M/N/O/Q/R/S/T/U artifacts remain tracked and unchanged.
- No Dashboard route/endpoint/template/static is created or modified.
- No app/templates/static files are modified.
- No real queue DB is read.
- No queue data is written.
- No POST is sent.
- No network call is made.
- No Worker/OpenClaw/Hermes/Google Sheets/secrets integration is introduced.
- Future Dashboard integration is restricted to consuming build_dashboard_preview_model() / build_dashboard_preview_rows() only.
- Future Dashboard integration must display disabled runtime badges and all permission flags false.
- X does not commit / push / tag.

## 14. Non-goals

v0.8.1-X does not modify the Dashboard.
v0.8.1-X does not modify the adapter.
v0.8.1-X does not modify the loader.
v0.8.1-X does not modify the fixture JSON.
v0.8.1-X does not modify the v0.8.1-M/N/O/Q/R/S/T/U/V/W artifacts.
v0.8.1-X does not start v0.8.1-Y.

## 15. Next recommended step

Recommended next step:
v0.8.1-Y — Dashboard Preview Adapter Integration Authorization Plan

v0.8.1-Y is not started by v0.8.1-X.
