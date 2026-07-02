# Hermes × OpenClaw — Local Mock Fixture Dashboard Preview Adapter Integration Implementation Plan (v0.8.1-Z)

## 1. Purpose

v0.8.1-Z is an implementation plan only.
v0.8.1-Z does not implement Dashboard integration.
v0.8.1-Z does not modify Dashboard.
v0.8.1-Z does not modify adapter.
v0.8.1-Z does not modify loader.
v0.8.1-Z does not create or modify route, endpoint, template, static asset, QueueStore, approval route, Worker, OpenClaw, Hermes, or Google Sheets integration.
v0.8.1-Z only plans the future Dashboard preview adapter read-only display integration.

It defines the future minimum implementation steps, the future Dashboard display contract, the future
candidate files discovered by read-only repository inspection, the future validation requirements, the
future rollback boundary, and the exact v0.8.2-A phrase a future, separately approved implementation
round must obtain before touching any candidate file. It creates no Dashboard file, no route, no
endpoint, no template, no static asset, and modifies no existing file other than adding this doc and
its readiness script.

## 2. Base

Base HEAD / origin/master:
dc71aa73cbe162cab5a0e913d6d05701e9e69fc6

Base commit:
dc71aa7 docs: plan dashboard preview adapter integration authorization

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

v0.8.1-X Dashboard preview adapter integration boundary plan:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_BOUNDARY_PLAN_V0_8_1_X.md
scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py

v0.8.1-Y Dashboard preview adapter integration authorization plan:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_DASHBOARD_PREVIEW_ADAPTER_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_Y.md
scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py

These artifacts remain tracked and unchanged. v0.8.1-Z does not modify the fixture JSON artifact.
v0.8.1-Z does not modify the v0.8.1-M/N/O/Q/R/S/T/U artifacts. v0.8.1-Z does not modify the v0.8.1-P
loader. v0.8.1-Z does not modify the v0.8.1-V adapter or its readiness script. v0.8.1-Z does not modify
the v0.8.1-W runtime check script. v0.8.1-Z does not modify the v0.8.1-X boundary plan doc or its
readiness script. v0.8.1-Z does not modify the v0.8.1-Y authorization plan doc or its readiness script.

## 4. Dependency on v0.8.1-Y

v0.8.1-Z depends on v0.8.1-Y.
v0.8.1-Y defines the exact explicit Owner authorization phrase.
The exact explicit Owner authorization phrase was provided before v0.8.1-Z began.

## 5. Exact explicit Owner authorization phrase (from v0.8.1-Y)

```
批准進入 v0.8.1 Dashboard preview adapter integration 下一步，僅允許未來 Dashboard 透過 build_dashboard_preview_model() 從 v0.8.1-V read-only preview adapter 取得 synthetic local-only read-only preview model，並以 read-only display 呈現；不直接讀 fixture JSON，不呼叫 load_local_mock_fixture_preview()，不讀 real queue DB，不 POST，不啟 Worker/OpenClaw/Hermes/Google Sheets，不讀 secrets，不暴露 execution/dispatch/external action controls，不建立 production/shared DB，不建立 Remote Blackboard API runtime。
```

This phrase authorized v0.8.1-Z to begin as a plan-only round. It does not, by itself, authorize any
Dashboard file modification. Dashboard file modification requires the separate v0.8.2-A phrase defined
in Section 14 of this doc.

## 6. Future integration data source, plan-only

Future Dashboard integration must import only:
build_dashboard_preview_model()

Allowed source module:
scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py

Optional display-only helper:
build_dashboard_preview_rows()

Future Dashboard integration must not import or call:
load_local_mock_fixture_preview()
validate_local_mock_fixture_preview_object()
fixture JSON path
QueueStore
real queue DB
Worker
OpenClaw
Hermes
Google Sheets

## 7. Future Dashboard display contract, plan-only

The future Dashboard display must be read-only.
The future Dashboard display must show synthetic local-only preview rows.
The future Dashboard display must preserve model-level local_only = True.
The future Dashboard display must preserve model-level read_only = True.
The future Dashboard display must preserve model-level is_mock = True.
The future Dashboard display must preserve row-level local_only = True.
The future Dashboard display must preserve row-level read_only = True.
The future Dashboard display must preserve row-level is_mock = True.
The future Dashboard display must preserve execution_permission = False.
The future Dashboard display must preserve dispatch_permission = False.
The future Dashboard display must preserve external_side_effects_permission = False.

## 8. Future disabled runtime badges, plan-only

DISPATCH OFF
WORKER OFF
OPENCLAW NOT CONNECTED
HERMES NOT CONNECTED
GOOGLE SHEETS DISABLED

## 9. Future UI forbidden controls, plan-only

No Run button.
No Execute button.
No Dispatch button.
No Approve and Dispatch button.
No Send button.
No POST form.
No webhook control.
No endpoint control.
No action_url.
No post_url.
No webhook_url.
No endpoint_url.
No execute_url.
No dispatch_url.
No external action control.

## Future candidate files from read-only repository inspection

Read-only repository inspection (`git ls-files app templates static` plus `grep -RIn` for
`dashboard`, `reviews`, `task_detail`, `Audit Trail`, `Blackboard`, and the five disabled-runtime-badge
strings) was performed to enumerate the future Dashboard candidate files. No files were modified during
this inspection.

Candidate route/controller files:
- app/main.py (owns the existing `/dashboard`, `/dashboard/tasks`, `/dashboard/tasks/{task_id}`,
  `/dashboard/reviews`, `/dashboard/system` GET routes; a future read-only preview surface would be an
  additional GET-only route added here, not a modification of the approval/control POST routes already
  present in this file)

Candidate template/display files:
- templates/dashboard.html
- templates/task_detail.html
- templates/reviews.html
- templates/system.html
- templates/tasks.html
- templates/base.html (only if a new nav link is ever separately approved)

Candidate static/style files:
- static/dashboard.css

Candidate validation/check files:
- scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py

Reference precedent (not a candidate file, not modified): `app/audit_trail_display_v0_7.py` is an
existing pure-function, read-only, display-only derivation module wired only into GET display paths in
`app/main.py`. It is cited here only as an architectural precedent that a future v0.8.2-A read-only
Dashboard preview surface may follow; v0.8.1-Z does not propose changing it.

These candidate files are not modified by v0.8.1-Z.
These candidate files are not authorized for modification by v0.8.1-Z.
Future modification requires a separate Owner-approved implementation round.

## 10. Future minimum implementation steps, plan-only

1. Import build_dashboard_preview_model() from scripts/local_mock_fixture_dashboard_preview_adapter_v0_8_1.py in the explicitly approved Dashboard display-only surface.
2. Call build_dashboard_preview_model() only for synthetic local-only read-only preview.
3. Pass the returned preview model into a read-only Dashboard view context.
4. Render rows as display-only records.
5. Render disabled runtime badges.
6. Render all permission flags as false.
7. Do not add state-changing buttons, forms, links, or routes.
8. Do not call P loader.
9. Do not read fixture JSON directly.
10. Do not read real queue DB.

## 11. Future validation requirements, plan-only

Future implementation validation must confirm:
- Dashboard imports V adapter only, not P loader.
- Dashboard does not read fixture JSON directly.
- Dashboard does not read real queue DB.
- Dashboard does not call QueueStore.
- Dashboard does not define POST route.
- Dashboard does not expose action/execution/dispatch controls.
- Dashboard renders disabled badges.
- Dashboard renders permission flags false.
- Dashboard remains read-only.
- W runtime check passes.
- V readiness passes.
- X readiness passes.
- Y readiness passes.
- Z readiness passes.
- M/K/J/I/H/G/F/E/D/C/B/A/v0.8.0-G/v0.8.0-F pass.
- compileall passes.
- safety grep shows only benign matches.

## 12. Future rollback boundary, plan-only

Rollback of any future Dashboard preview adapter read-only display integration must remove only the
future Dashboard integration changes.
Rollback must not modify fixture JSON.
Rollback must not modify P loader.
Rollback must not modify V adapter.
Rollback must not modify W runtime check.
Rollback must not modify X boundary plan.
Rollback must not modify Y authorization plan.
Rollback must not modify Z implementation plan.
Rollback must not clean patches/.

## 13. Known pre-commit coupling

During v0.8.1-Z Owner Review, older Y/X/W/V/U/T/S/R/Q/O/N readiness scripts may fail only because the
two new Z files are untracked.
This is the same strict-untracked-file coupling observed in v0.8.1-O, v0.8.1-P, v0.8.1-Q, v0.8.1-R,
v0.8.1-S, v0.8.1-T, v0.8.1-U, v0.8.1-V, v0.8.1-X, and v0.8.1-Y.
This is acceptable only if the failure reason is exactly the two untracked Z files.
No other regression failure is acceptable.
After Z files are committed in a separately approved round, Y/X/W/V/U/T/S/R/Q/O/N must recover to PASS.

## 14. Future implementation authorization phrase for v0.8.2-A

Only the following phrase, verbatim, authorizes v0.8.2-A — Dashboard Preview Adapter Read-only Display
Integration:

```
批准實作 v0.8.2-A — Dashboard Preview Adapter Read-only Display Integration，僅允許在已於 v0.8.1-Z 列明並經 Owner Review 的 Dashboard display-only surface 中呼叫 build_dashboard_preview_model()，將 v0.8.1-V read-only preview adapter 回傳的 synthetic local-only read-only preview model 以 read-only rows / disabled badges / false permission flags 呈現；不直接讀 fixture JSON，不呼叫 P loader，不讀 real queue DB，不 POST，不暴露 execution/dispatch/external action controls，不啟 Worker/OpenClaw/Hermes/Google Sheets，不讀 secrets，不建立 production/shared DB，不建立 Remote Blackboard API runtime。
```

v0.8.2-A is not started by v0.8.1-Z.
Only the exact v0.8.2-A phrase above may authorize future implementation.
General approval does not authorize v0.8.2-A.
Commit approval does not authorize v0.8.2-A.
Push approval does not authorize v0.8.2-A.

## 15. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
loader_change_permission = false
adapter_change_permission = false
dashboard_change_permission = false
authorization_granted_for_v0_8_2_a = false

In v0.8.1-Z execution_permission remains false.
In v0.8.1-Z dispatch_permission remains false.
In v0.8.1-Z external_side_effects_permission remains false.
In v0.8.1-Z authorization_granted_for_v0_8_2_a remains false until the exact v0.8.2-A phrase in Section
14 is given for a future separately approved round.

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
Fixture JSON is unchanged in v0.8.1-Z.
P loader exists and is tracked.
P loader is unchanged in v0.8.1-Z.
V adapter exists and is tracked.
V adapter is unchanged in v0.8.1-Z.
W runtime check exists and is tracked.
W runtime check is unchanged in v0.8.1-Z.
X boundary plan exists and is tracked.
X boundary plan is unchanged in v0.8.1-Z.
Y authorization plan exists and is tracked.
Y authorization plan is unchanged in v0.8.1-Z.
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

## 17. v0.8.1-Z acceptance criteria

- Z implementation plan doc exists.
- Z readiness script exists.
- Z is implementation-plan-only.
- Z depends on v0.8.1-Y and includes the Y exact explicit Owner authorization phrase exactly once.
- Z defines the future data source, display contract, disabled badges, forbidden controls, candidate files, minimum implementation steps, validation requirements, and rollback boundary.
- Z defines the exact v0.8.2-A future implementation authorization phrase.
- P loader remains tracked and unchanged.
- V adapter remains tracked and unchanged.
- W runtime check remains tracked and unchanged.
- X boundary plan remains tracked and unchanged.
- Y authorization plan remains tracked and unchanged.
- L fixture remains tracked and unchanged.
- M/N/O/Q/R/S/T/U artifacts remain tracked and unchanged.
- No Dashboard route/endpoint/template/static is created or modified.
- No app/templates/static files are modified.
- No real queue DB is read.
- No queue data is written.
- No POST is sent.
- No network call is made.
- No Worker/OpenClaw/Hermes/Google Sheets/secrets integration is introduced.
- Z does not commit / push / tag.

## 18. Non-goals

v0.8.1-Z does not modify the Dashboard.
v0.8.1-Z does not modify the adapter.
v0.8.1-Z does not modify the loader.
v0.8.1-Z does not modify the fixture JSON.
v0.8.1-Z does not modify the v0.8.1-M/N/O/Q/R/S/T/U/V/W/X/Y artifacts.
v0.8.1-Z does not start v0.8.2-A.

## 19. Next recommended step

Recommended next step:
v0.8.2-A — Dashboard Preview Adapter Read-only Display Integration

v0.8.2-A is not started by v0.8.1-Z.
v0.8.2-A requires the exact v0.8.2-A phrase defined in Section 14 of this doc.
