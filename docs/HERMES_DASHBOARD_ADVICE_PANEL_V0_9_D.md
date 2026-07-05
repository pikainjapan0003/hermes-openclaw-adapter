# Hermes × OpenClaw v0.9-D
# Dashboard Hermes Advice Panel

## 0. Status

- Phase: v0.9-D
- Type: read-only Dashboard display implementation
- Base commit: `6f58d3ba1feb490b670c8a8e95d6fcc4e3bd6dda`
- Latest commit message: `feat: add v0.9 mock Hermes generator`
- Implementation status: IMPLEMENTED, READ-ONLY DISPLAY ONLY
- Dashboard route status: EXISTING GET-ONLY `/dashboard/system` UNCHANGED IN METHOD
- Dashboard template status: NEW READ-ONLY SECTION ADDED
- Dashboard CSS status: NEW READ-ONLY DISPLAY STYLING ADDED
- `CLAUDE.md` status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Hermes runtime status: NOT ACTIVATED
- Real Hermes status: NOT CALLED
- Hermes memory status: NOT READ
- Hermes tool call status: NOT CALLED
- Blackboard write status: NOT WRITTEN
- Worker status: OFF / NOT STARTED
- Real OpenClaw status: NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ / NOT WRITTEN
- Audit trail status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.9-E status: NOT STARTED

## 1. Purpose / Positioning

v0.9-D adds a read-only Dashboard section that displays a synthetic local-only mock
Hermes advice preview, built from the v0.9-C `build_mock_hermes_advice()` generator. It
is a display-only addition to the existing GET-only `/dashboard/system` route: no new
route, no new HTTP method, no interactive control.

- Dashboard Hermes advice panel is read-only.
- Dashboard Hermes advice panel is not Hermes activation.
- Dashboard Hermes advice panel is not real Hermes call.
- Dashboard Hermes advice panel is not Hermes memory read.
- Dashboard Hermes advice panel is not Hermes tool call.
- Mock Hermes advice is not Owner approval.
- Mock Hermes advice is not Blackboard write.
- Mock Hermes advice is not queue write.
- Mock Hermes advice is not audit trail write.
- Mock Hermes advice is not automatic follow-up execution.
- Mock Hermes advice is not Worker dispatch.
- Mock Hermes advice is not OpenClaw call.
- Mock Hermes cannot bypass Owner Review.
- Mock Hermes cannot bypass Blackboard Activation Policy.
- External side effects remain forbidden by default.

v0.9-D is not a Dashboard control. v0.9-D does not add an approve, reject, execute,
dispatch, or send control. v0.9-D does not add a form, button, or action URL.

## 2. Data Source

The Dashboard section is fed by `build_dashboard_hermes_advice_view_model()` in
`app/main.py`, which calls the v0.9-C `build_mock_hermes_advice()` generator with a
fixed, deterministic, synthetic source context constant (not user input), then flattens
the result into a display-only view model. The generator itself calls the v0.9-B
`hermes_strategy_suggestion_model` to derive the underlying strategy suggestion. This
mirrors the existing v0.8.2-A / v0.8.3-D / v0.8.4-D / v0.8.5-D builder pattern already
used elsewhere on `/dashboard/system`.

## 3. Displayed Fields

The Hermes advice panel displays:

- `advice_source = synthetic_local_only`
- `mock_hermes = true`
- `real_hermes_called = false`
- `hermes_runtime_activated = false`
- `hermes_memory_read = false`
- `hermes_tool_called = false`
- `must_not_execute = true`
- `requires_owner_confirmation = true`
- `blackboard_write_allowed = false`
- `queue_write_allowed = false`
- `audit_trail_write_allowed = false`
- `worker_dispatch_allowed = false`
- `openclaw_call_allowed = false`
- `external_side_effects_allowed = false`
- `preview_only = true`

alongside `strategy_summary`, `recommended_action`, `owner_question`,
`suggested_next_step`, `confidence`, and fixed safety badges: `MOCK HERMES ONLY`,
`ADVISORY ONLY`, `READ-ONLY PREVIEW`, `NOT OWNER APPROVAL`, `NOT BLACKBOARD WRITE`,
`NOT WORKER DISPATCH`, `NOT OPENCLAW CALL`, `NO EXTERNAL SIDE EFFECTS`,
`OWNER CONFIRMATION REQUIRED`.

## 4. What v0.9-D Does Not Do

- v0.9-D does not add a POST route.
- v0.9-D does not add a new endpoint.
- v0.9-D does not add a form, button, or action URL.
- v0.9-D does not add an approve, reject, execute, dispatch, or send control.
- v0.9-D does not add a webhook or connector.
- v0.9-D does not activate a Hermes runtime.
- v0.9-D does not call real Hermes.
- v0.9-D does not read Hermes memory.
- v0.9-D does not call a Hermes tool.
- v0.9-D does not write the Blackboard.
- v0.9-D does not read or write the real queue DB.
- v0.9-D does not write the audit trail.
- v0.9-D does not call Worker, Worker loop, real OpenClaw, or Google Sheets.
- v0.9-D does not read secrets.
- v0.9-D does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.9-D does not modify `CLAUDE.md`.
- v0.9-D does not start v0.9-E.

## 5. Completion Criteria

- `docs/HERMES_DASHBOARD_ADVICE_PANEL_V0_9_D.md` exists (this document).
- `scripts/check_hermes_dashboard_advice_panel_v0_9_d.py` exists and PASSes.
- `app/main.py` only adds a read-only synthetic mock Hermes advice view model to the
  existing GET-only `/dashboard/system` context; no new route, no POST, no
  queue/Worker/OpenClaw/Hermes-runtime/Google Sheets call, no secrets read.
- `templates/system.html` only adds a read-only display section; no `<form>`, no
  `<button>`, no action URL, no approve/reject/execute/dispatch/send UI.
- `static/dashboard.css` only adds read-only display styling; no control-implying
  styling.
- No existing tracked file other than `app/main.py`, `templates/system.html`,
  `static/dashboard.css` is modified.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-E or later work is started.

## 6. Handoff

Future phase:
v0.9-E — (not yet defined; requires separate Owner authorization)

v0.9-E is not started by v0.9-D.
