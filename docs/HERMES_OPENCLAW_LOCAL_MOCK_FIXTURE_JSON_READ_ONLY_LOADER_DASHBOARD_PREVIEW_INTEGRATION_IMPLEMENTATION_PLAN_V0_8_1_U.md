# Hermes × OpenClaw — Local Mock Fixture Read-only Loader Dashboard Preview Integration Implementation Plan (v0.8.1-U)

## 1. Purpose

v0.8.1-U is Dashboard preview integration implementation plan-only. It defines the concrete technical
blueprint a future, separately approved implementation round must follow to let Dashboard display the
in-memory preview data object returned by the v0.8.1-P loader. It implements nothing: no Dashboard
change, no loader change, no route, no template, no static asset, no runtime. It only writes down the
planned files, planned function contracts, planned display fields, forbidden actions, required
pre-implementation validation, and rollback boundary for that future implementation round.

## 2. Dashboard preview integration implementation plan-only positioning

v0.8.1-U is Dashboard preview integration implementation plan-only.
v0.8.1-U only defines the future implementation blueprint for Dashboard reading the v0.8.1-P loader in-memory preview object.
v0.8.1-U does not modify Dashboard.
v0.8.1-U does not modify loader.
v0.8.1-U does not create a Dashboard route.
v0.8.1-U does not create a Dashboard endpoint.
v0.8.1-U does not create a Dashboard template.
v0.8.1-U does not create a Dashboard static asset.
v0.8.1-U does not read the fixture JSON directly.
v0.8.1-U does not read real queue DB.
v0.8.1-U does not write queue data.
v0.8.1-U does not send POST.
v0.8.1-U does not make network calls.
v0.8.1-U does not start Worker.
v0.8.1-U does not call OpenClaw.
v0.8.1-U does not activate Hermes.
v0.8.1-U does not read Google Sheets.
v0.8.1-U does not write Google Sheets.
v0.8.1-U does not read secrets.
v0.8.1-U does not create .env.
v0.8.1-U does not create webhook.
v0.8.1-U does not create connector.
v0.8.1-U does not create production DB.
v0.8.1-U does not create shared DB.
v0.8.1-U does not create Remote Blackboard API runtime.
v0.8.1-U does not commit.
v0.8.1-U does not push.
v0.8.1-U does not tag.

## 3. Current master

HEAD = origin/master = 879140f2936ce95f12c72505f44f37d80e7ea086

latest commit = 879140f docs: plan local mock fixture dashboard integration authorization

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

v0.8.1-S Dashboard integration boundary:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_BOUNDARY_PLAN_V0_8_1_S.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_boundary_plan_v0_8_1_s.py

v0.8.1-T Dashboard integration authorization:
docs/HERMES_OPENCLAW_LOCAL_MOCK_FIXTURE_JSON_READ_ONLY_LOADER_DASHBOARD_INTEGRATION_AUTHORIZATION_PLAN_V0_8_1_T.md
scripts/check_hermes_openclaw_local_mock_fixture_json_read_only_loader_dashboard_integration_authorization_plan_v0_8_1_t.py

These artifacts remain tracked and unchanged. v0.8.1-U does not modify the fixture JSON artifact.
v0.8.1-U does not modify the v0.8.1-M validation doc/script. v0.8.1-U does not modify the v0.8.1-N
plan doc/script. v0.8.1-U does not modify the v0.8.1-O authorization doc/script. v0.8.1-U does not
modify the v0.8.1-P loader. v0.8.1-U does not modify the v0.8.1-Q validation doc/script. v0.8.1-U
does not modify the v0.8.1-R runtime check script. v0.8.1-U does not modify the v0.8.1-S boundary
plan doc/script. v0.8.1-U does not modify the v0.8.1-T authorization plan doc/script.

## 5. Owner authorization on record

Owner supplied the exact future implementation authorization phrase defined in v0.8.1-T Section 7:

批准實作 v0.8.1 local mock fixture read-only loader Dashboard preview integration，僅允許 Dashboard 透過 load_local_mock_fixture_preview() 讀取 synthetic local-only in-memory preview object 並以 read-only display 呈現；不讀 fixture JSON direct，不讀 real queue DB，不 POST，不啟 Worker/OpenClaw/Hermes/Google Sheets，不讀 secrets，不暴露 execution/dispatch controls，不建立 production/shared DB，不建立 Remote Blackboard API runtime。

Owner additionally scoped this round explicitly: only a v0.8.1-U Dashboard preview integration
implementation plan doc and readiness script may be added. No Dashboard file, loader file, route,
endpoint, template, or static asset may be created or modified in this round. Real Dashboard/loader
code changes remain deferred to a further, separately approved implementation round (v0.8.1-V), which
must itself be authorized by Owner before any code is written.

## 6. Problem statement

The v0.8.1-S boundary plan fixed the read-only, local-only boundary a future Dashboard integration
must obey. The v0.8.1-T authorization plan fixed the conditions, the exact authorization phrase, the
non-authorizing phrases, the forbidden actions, the required pre-implementation validation, and the
rollback boundary. Owner has now supplied that exact phrase together with an explicit scope limit for
this round. Before any Dashboard or loader file is ever touched, the exact technical shape of the
future implementation — which files it would add, what function contracts it would call, what fields
it would display, and what it must never do — must be fixed in writing. v0.8.1-U is that
implementation planning step and nothing more.

## 7. Planned future implementation blueprint, plan-only (not created in v0.8.1-U):

- A future read-only adapter module, e.g. `app/dashboard_local_mock_preview_adapter_v0_8_1.py`, would
  import `load_local_mock_fixture_preview` from `scripts/load_local_mock_fixture_preview_v0_8_1.py`
  and convert its returned in-memory preview object into a list of read-only display rows.
- The adapter module would expose a single read-only function, e.g.
  `get_local_mock_preview_rows() -> list[dict]`, with no side effects and no persistence.
- A future Dashboard route addition in `app/main.py`, e.g. a `/dashboard/local-mock-preview` GET-only
  route, would call the adapter function and pass its return value to a template context. This route
  is not created in v0.8.1-U.
- A future template addition, e.g. `templates/local_mock_preview.html`, would render the rows as a
  read-only table with disabled runtime badges. This template is not created in v0.8.1-U.
- No existing route in `app/main.py` would be modified to add dispatch, POST handling, or write
  behavior for this preview.
- No existing template (`templates/dashboard.html`, `templates/tasks.html`,
  `templates/task_detail.html`, `templates/reviews.html`, `templates/system.html`,
  `templates/login.html`, `templates/base.html`) would be modified to add execution or dispatch
  controls for this preview.

## 8. Planned future adapter contract, plan-only:

- Input: none (the adapter calls `load_local_mock_fixture_preview()` with no arguments).
- Output: an immutable, read-only list of display rows derived from the loader's in-memory preview
  object.
- The adapter must not mutate the object returned by the loader.
- The adapter must not persist the object returned by the loader.
- The adapter must not dispatch any record.
- The adapter must not call Worker, OpenClaw, Hermes, or Google Sheets.
- The adapter must not send POST or make any network call.
- The adapter must not read secrets.
- The adapter must not read the fixture JSON file directly; it must only call the loader function.
- The adapter must not read real queue DB or write queue data.

## 9. Planned future Dashboard display fields, plan-only:

- local_only = true
- read_only = true
- execution_permission = false
- dispatch_permission = false
- external_side_effects_permission = false
- disabled runtime badges for Worker OFF / OpenClaw Not Connected / Hermes Not Connected / Google
  Sheets Disabled
- no execution control elements (buttons, forms) rendered
- no dispatch control elements (buttons, forms) rendered

## 10. Non-authorizing phrases:

- start Dashboard integration
- implement Dashboard preview
- connect loader to Dashboard
- use loader in Dashboard
- show mock data in Dashboard
- make Dashboard read loader
- proceed to Dashboard
- approved
- LGTM
- looks good
- continue
- do it
- v0.8.1-V

None of the above phrases authorize any future implementation. Only a separately supplied exact
authorization phrase for v0.8.1-V, given by Owner after this plan is reviewed, authorizes writing
actual Dashboard or loader code.

## 11. Forbidden implementation actions in v0.8.1-U:

- creating the future adapter module
- creating the future Dashboard route
- creating the future template
- modifying `app/main.py`
- modifying any existing template
- modifying the v0.8.1-P loader
- reading the fixture JSON directly
- reading real queue DB
- writing queue data
- sending POST
- making network calls
- starting Worker
- calling OpenClaw
- activating Hermes
- reading or writing Google Sheets
- reading secrets
- creating .env
- creating webhook
- creating connector
- creating production DB
- creating shared DB
- creating Remote Blackboard API runtime
- committing
- pushing
- tagging

## 12. Required validation before v0.8.1-V implementation begins:

- v0.8.1-M validation must pass.
- v0.8.1-Q readiness must pass.
- v0.8.1-R runtime check must pass.
- v0.8.1-S boundary readiness must pass.
- v0.8.1-T authorization readiness must pass.
- v0.8.1-U implementation-plan readiness must pass.
- P loader must remain tracked and unchanged unless separately approved by Owner.
- Owner must supply a separate exact authorization phrase for v0.8.1-V before any Dashboard or loader
  file is created or modified.
- v0.8.1-V diff must include only the adapter module, the new route, and the new template described
  in Section 7, and nothing else, unless separately approved by Owner.
- v0.8.1-V must prove no real queue DB / POST / network / secrets access.
- v0.8.1-V must prove no Worker/OpenClaw/Hermes/Google Sheets activation.

## 13. Rollback boundary:

If a future v0.8.1-V implementation violates any read-only or no-side-effect rule, rollback must
remove only the v0.8.1-V adapter module, route, and template files/changes.
Rollback must not modify fixture JSON.
Rollback must not modify P loader unless separately approved by Owner.
Rollback must not modify M/N/O/Q/R/S/T/U artifacts unless separately approved by Owner.
Rollback must not delete historical docs or readiness scripts.
Rollback must not clean patches/.

## 14. Validation method, plan-only:

1. Static inspection of this U implementation plan doc.
2. Git tracked-state check for L/M/N/O/P/Q/R/S/T artifacts.
3. Confirm P loader remains tracked and unchanged.
4. Confirm T authorization plan remains tracked and available.
5. Confirm no Dashboard/app/templates/static files changed.
6. Confirm no real queue DB / POST / network / secrets integration is introduced.
7. Confirm U readiness script does not modify repo files or git index.

## 15. Known pre-commit coupling:

During v0.8.1-U Owner Review, older T/S/R/Q/O/N readiness scripts may fail only because the two new U
files are untracked.
This is the same strict-untracked-file coupling observed in v0.8.1-O, v0.8.1-P, v0.8.1-Q, v0.8.1-R,
v0.8.1-S, and v0.8.1-T.
This is acceptable only if the failure reason is exactly the two untracked U files.
No other regression failure is acceptable.
After U files are committed in a separately approved round, T/S/R/Q/O/N must recover to PASS.

## 16. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
loader_change_permission = false
dashboard_change_permission = false

In v0.8.1-U execution_permission remains false.
In v0.8.1-U dispatch_permission remains false.
In v0.8.1-U external_side_effects_permission remains false.

## 17. Current safe system posture

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
Fixture JSON is unchanged in v0.8.1-U.
P loader exists and is tracked.
P loader is unchanged in v0.8.1-U.
T authorization plan exists and is tracked.
T authorization plan is unchanged in v0.8.1-U.
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

## 18. v0.8.1-U acceptance criteria:

- U implementation plan doc exists.
- U readiness script exists.
- U is implementation plan-only.
- P loader remains tracked and unchanged.
- T authorization plan remains tracked and unchanged.
- S boundary plan remains tracked and unchanged.
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
- Planned future implementation blueprint is present.
- Planned future adapter contract is present.
- Non-authorizing phrases are present.
- Rollback boundary is present.
- U does not commit / push / tag.

## 19. Non-goals

v0.8.1-U does not modify the Dashboard.
v0.8.1-U does not modify the loader.
v0.8.1-U does not modify the fixture JSON.
v0.8.1-U does not modify the v0.8.1-M/N/O/Q/R/S/T artifacts.
v0.8.1-U does not start v0.8.1-V.

## 20. Next recommended step

v0.8.1-V — Local Mock Fixture Read-only Loader Dashboard Preview Integration Implementation

v0.8.1-V must not start unless separately approved by Owner using a separate exact authorization phrase.
v0.8.1-V must not modify Dashboard unless separately approved by Owner using a separate exact authorization phrase.
v0.8.1-V must not modify loader unless separately approved by Owner.
v0.8.1-V must not enable dispatch.
v0.8.1-V must not connect Worker/OpenClaw/Hermes/Google Sheets.
