# Hermes × OpenClaw v0.8.5-A
# OpenClaw Command Envelope Plan

## 0. Status

- Phase: v0.8.5-A
- Type: plan-only
- Base commit: `7d9030c071ecc3fa9f75b13e2348005beaa465f5`
- Latest commit message: `docs: add v0.8.4 roadmap amendment closeout`
- Implementation status: NOT IMPLEMENTED
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ
- Queue status: NOT WRITTEN
- Audit trail status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Task execution status: NOT EXECUTED
- Dispatch status: NOT SENT
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- OpenClaw Mock Gateway Helper status: NOT IMPLEMENTED / NOT STARTED
- `patches/` status: UNTRACKED (unchanged)
- v0.8.5-B status: NOT STARTED

v0.8.5-A is a plan-only round. It does not implement anything. It does not modify
`app/main.py`, `templates/system.html`, `static/dashboard.css`, any v0.8.4 series
artifact, any v0.8.3 artifact, any v0.8.2 artifact, or any other existing tracked file.
It does not start a Worker, does not call real OpenClaw, does not connect Hermes, does
not read or write Google Sheets, does not read the real queue DB, does not write the
queue or the audit trail, and does not POST anything anywhere.

## 1. Purpose

v0.8.4-I closed out the v0.8.4 series and amended the roadmap: v0.8.5 is reserved for the
OpenClaw Mock Gateway, beginning with v0.8.5-A. v0.8.5-A defines, in plan-only form, the
shape of an **OpenClaw Command Envelope** — the data structure a future v0.8.5-B mock
gateway helper may use to describe a command *as if* it were being sent to OpenClaw,
without ever actually calling OpenClaw, executing a task, or producing any external side
effect.

This round produces only a plan document and a readiness/validation script for that plan.
It does not create a command envelope builder, a mock gateway helper, a fixture, or any
Dashboard-facing file.

## 2. v0.8.4 Series Closeout State

- v0.8.4-A through v0.8.4-I = DONE / PUSHED / CLOSED
- latest HEAD = `7d9030c071ecc3fa9f75b13e2348005beaa465f5`
- latest commit = `docs: add v0.8.4 roadmap amendment closeout`
- the Owner Review Decision Boundary was folded into v0.8.4-H and does not occupy v0.8.5
- v0.8.5 is reserved for the OpenClaw Mock Gateway

## 3. Future OpenClaw Command Envelope Shape (plan-only)

A future v0.8.5-B implementation may define an **OpenClaw Command Envelope** object with
fields such as:

- `command_id` — synthetic local-only identifier
- `task_id` — reference to the originating Worker dry-run task, if any
- `tool_target` — the name of the tool/action the envelope *would* address, descriptive
  only
- `requested_action` — a human-readable description of the action being described, never
  an instruction actually sent anywhere
- `risk_level` — a plan-only classification (e.g. `low`, `medium`, `high`), informational
  only
- `approval_snapshot` — a read-only copy of the Owner Review Decision Preview state at
  envelope-creation time; never itself an approval
- `execution_mode` — must be `mock_only`
- `dry_run` — must be `true`
- `mock_only` — must be `true`
- `external_touchpoints` — must be an empty list; a future envelope must never name a
  real external system it actually touches
- `rollback_plan` — a human-readable description only; never an executable rollback
  action
- `external_side_effects_allowed` — must be `false`

This object shape is a plan-only definition. No command envelope object, no command
envelope file, and no command envelope builder is created by v0.8.5-A.

## 4. Mandatory Safety Values

- `mock_only` must always be `true`.
- `dry_run` must always be `true`.
- `external_side_effects_allowed` must always be `false`.

A future command envelope that sets any of these three fields to a value other than the
one specified above is out of scope for the OpenClaw Mock Gateway and must not be built
under this plan.

## 5. Command Envelope Boundary Statements

- A command envelope is not a call to real OpenClaw.
- A command envelope is not a call to Worker.
- A command envelope is not a call to Hermes.
- A command envelope does not touch Google Sheets.
- A command envelope does not read or write the real queue DB.
- A command envelope does not write the audit trail.
- A command envelope does not add a Dashboard control.
- A command envelope is not an execution.
- A command envelope is not a dispatch.
- v0.8.5-A does not implement the OpenClaw Mock Gateway Helper.
- v0.8.5-A does not start v0.8.5-B.

## 6. Safety Boundary

- v0.8.5-A does not call real OpenClaw.
- v0.8.5-A does not call Worker.
- v0.8.5-A does not call Hermes.
- v0.8.5-A does not touch Google Sheets.
- v0.8.5-A does not read or write the real queue DB.
- v0.8.5-A does not write the audit trail.
- v0.8.5-A does not add Dashboard controls.
- v0.8.5-A does not modify `app/main.py`.
- v0.8.5-A does not modify `templates/system.html`.
- v0.8.5-A does not modify `static/dashboard.css`.
- v0.8.5-A does not add a route, endpoint, POST, webhook, or connector.
- v0.8.5-A does not read secrets.
- v0.8.5-A does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.8.5-A does not touch `patches/`.

## 7. Handoff

Future phase:
v0.8.5-B — OpenClaw Mock Gateway Helper

v0.8.5-B should only create synthetic, local-only, `mock_only` command envelope
artifacts.
v0.8.5-B must not call real OpenClaw.
v0.8.5-B must not call Worker.
v0.8.5-B must not call Hermes.
v0.8.5-B must not touch Google Sheets.
v0.8.5-B must not read or write the real queue DB.
v0.8.5-B must not write the audit trail.
v0.8.5-B must not add Dashboard controls.
v0.8.5-B must not create a webhook, endpoint, or connector.
v0.8.5-B must not create a production/shared DB or a Remote Blackboard API runtime.

v0.8.5-B is not started by v0.8.5-A.

## 8. Non-goals

- no OpenClaw Mock Gateway Helper implementation
- no command envelope builder
- no command envelope fixture
- no new Dashboard feature
- no Dashboard route change in this phase
- no template change in this phase
- no CSS change in this phase
- no change to any v0.8.4 series artifact
- no change to any v0.8.3 artifact
- no change to any v0.8.2 artifact
- no change to any v0.8.1 artifact
- no Worker call
- no real OpenClaw call
- no Hermes call
- no Google Sheets
- no real queue DB read/write
- no audit trail write
- no execution
- no dispatch
- no secrets
- no commit
- no push
- no tag
- no v0.8.5-B work

## 9. v0.8.5-A Acceptance Criteria

- v0.8.5-A plan doc exists
- v0.8.5-A readiness script exists
- v0.8.5-A readiness PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- every v0.8.4 series artifact is untouched
- every v0.8.3 artifact is untouched
- every v0.8.2 artifact is untouched
- every v0.8.1 artifact is untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no audit trail is written
- no POST / no execution / no dispatch occurs
- `patches/` remains untracked
- no tag is created
- no v0.8.5-B work is started
