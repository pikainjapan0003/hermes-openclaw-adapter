# Hermes × OpenClaw v0.8.5-D
# Dashboard Mock Result View

## 0. Status

- Phase: v0.8.5-D
- Type: read-only Dashboard display implementation
- Base commit: `a0bb159dfef4e5b0ef2f6c7333788d5299840df0`
- Latest commit message: `feat: add v0.8.5 worker mock gateway dry-run`
- Implementation status: IMPLEMENTED, READ-ONLY DISPLAY ONLY
- Dashboard route status: EXISTING GET-ONLY `/dashboard/system` UNCHANGED IN METHOD
- Dashboard template status: NEW READ-ONLY SECTION ADDED
- Dashboard CSS status: NEW READ-ONLY DISPLAY STYLING ADDED
- `CLAUDE.md` status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT STARTED
- Worker dispatch status: NOT DISPATCHED
- Real OpenClaw status: NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ / NOT WRITTEN
- Audit trail status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.8.5-R status: NOT STARTED
- v0.9 status: NOT STARTED

## 1. Purpose / Positioning

v0.8.5-D adds a read-only Dashboard section that displays a synthetic local-only mock
gateway dry-run result, built from the v0.8.5-C `run_worker_to_mock_gateway_dry_run()`
bridge. It is a display-only addition to the existing GET-only `/dashboard/system`
route: no new route, no new HTTP method, no interactive control.

- Dashboard mock result view is read-only.
- Dashboard mock result view is not execution permission.
- Mock result preview is not actual execution result.
- Mock result preview is not Worker dispatch.
- Mock result preview is not real OpenClaw call.
- Mock result preview is not audit trail persistence.
- Mock result preview is not queue write.
- Dashboard display does not grant Owner approval.
- External side effects remain forbidden by default.

v0.8.5-D is not a Dashboard control. v0.8.5-D does not add an approve, reject, execute,
dispatch, or send control. v0.8.5-D does not add a form, button, or action URL.

## 2. Data Source

The Dashboard section is fed by `build_dashboard_mock_result_view_model()` in
`app/main.py`, which calls the v0.8.5-C `run_worker_to_mock_gateway_dry_run()` bridge
with a fixed, deterministic, synthetic command envelope constant (not user input), then
flattens the result plus the nested v0.8.5-B gateway response into a display-only view
model. This mirrors the existing v0.8.2-A / v0.8.3-D / v0.8.4-D builder pattern already
used elsewhere on `/dashboard/system`.

## 3. Displayed Fields

The mock result panel displays:

- `source = synthetic_local_only`
- `mock_gateway = true`
- `worker_dry_run = true`
- `worker_loop_started = false`
- `worker_dispatched = false`
- `real_openclaw_called = false`
- `external_side_effects_performed = false`
- `queue_written = false`
- `audit_trail_written = false`
- `dashboard_control_added = false`
- `preview_only = true`

alongside fixed safety badges: `MOCK ONLY`, `DRY RUN ONLY`, `WORKER NOT DISPATCHED`,
`OPENCLAW NOT CONNECTED`, `NO EXTERNAL SIDE EFFECTS`, `READ-ONLY PREVIEW`.

## 4. What v0.8.5-D Does Not Do

- v0.8.5-D does not add a POST route.
- v0.8.5-D does not add a new endpoint.
- v0.8.5-D does not add a form, button, or action URL.
- v0.8.5-D does not add an approve, reject, execute, dispatch, or send control.
- v0.8.5-D does not add a webhook or connector.
- v0.8.5-D does not read or write the real queue DB.
- v0.8.5-D does not write the audit trail.
- v0.8.5-D does not call Worker, Worker loop, real OpenClaw, Hermes, or Google Sheets.
- v0.8.5-D does not read secrets.
- v0.8.5-D does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.8.5-D does not modify `CLAUDE.md`.
- v0.8.5-D does not start v0.8.5-R.
- v0.8.5-D does not start v0.9.

## 5. Completion Criteria

- `docs/HERMES_OPENCLAW_DASHBOARD_MOCK_RESULT_VIEW_V0_8_5_D.md` exists (this document).
- `scripts/check_hermes_openclaw_dashboard_mock_result_view_v0_8_5_d.py` exists and
  PASSes.
- `app/main.py` only adds a read-only synthetic mock result view model to the existing
  GET-only `/dashboard/system` context; no new route, no POST, no queue/Worker/OpenClaw/
  Hermes/Google Sheets call, no secrets read.
- `templates/system.html` only adds a read-only display section; no `<form>`, no
  `<button>`, no action URL, no approve/reject/execute/dispatch/send UI.
- `static/dashboard.css` only adds read-only display styling; no control-implying
  styling.
- No existing tracked file other than `app/main.py`, `templates/system.html`,
  `static/dashboard.css` is modified.
- `patches/` remains untracked.
- No tag is created.
- No v0.8.5-R or v0.9 work is started.

## 6. Handoff

Future phase:
v0.8.5-R — OpenClaw Mock Gateway Closeout

v0.8.5-R is not started by v0.8.5-D.
