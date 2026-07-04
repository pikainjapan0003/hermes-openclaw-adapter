# Hermes × OpenClaw v0.8.4-H
# Owner Review Decision Boundary Addendum Plan

## 0. Status

- Phase: v0.8.4-H
- Type: plan-only / safety addendum
- Base commit: `cd16c0157b55eb6901580eea20fd5d96f90afde3`
- Latest commit message: `docs: close out worker dry-run result dashboard display`
- Implementation status: NOT IMPLEMENTED
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT IMPLEMENTED / NOT STARTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ
- Queue status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Task execution status: NOT EXECUTED
- Dispatch status: NOT SENT
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.8.5 status: NOT STARTED — reserved for the OpenClaw Mock Gateway

v0.8.4-H is a plan-only, addendum round. It does not implement anything. It does not
modify `app/main.py`, `templates/system.html`, `static/dashboard.css`, any v0.8.4-A
through v0.8.4-G artifact, any v0.8.3 artifact, any v0.8.2 artifact, or any other existing
tracked file. It does not start a Worker, does not run a Worker loop, does not call
OpenClaw, does not connect Hermes, does not read or write Google Sheets, does not read the
real queue DB, and does not POST anything anywhere.

## 1. Purpose

v0.8.4-G closed out the Worker dry-run result / audit trail Dashboard read-only display
series. That closeout is a **display** closeout only. It must not be read as meaning that
an Owner decision boundary, an approval readiness, an execution readiness, or a dispatch
readiness has been reached. v0.8.4-H exists to write that boundary down explicitly, as a
safety addendum, before any future round is tempted to treat display-closeout as
decision-readiness.

v0.8.4-H defines, in plan-only form, how an **Owner Review Decision Preview** may be
described on top of the existing v0.8.4 dry-run result / audit trail preview — while
making unambiguous that a decision preview is never itself an approval, a rejection, an
execution, a dispatch, a send, a queue write, or an audit trail write.

This round produces only a plan document and a readiness/validation script for that plan.
It does not create or modify any Dashboard-facing file, any fixture, any builder, or any
decision object.

## 2. v0.8.4 Series Closeout State

- v0.8.4-A = DONE / PUSHED / CLOSED — Worker Dry-run Result / Audit Trail Boundary Plan
- v0.8.4-B = DONE / PUSHED / CLOSED — Worker Dry-run Result / Audit Trail Boundary
  Implementation
- v0.8.4-C = DONE / PUSHED / CLOSED — Worker Dry-run Result / Audit Trail Dashboard
  Read-only Display Plan
- v0.8.4-D = DONE / PUSHED / VERIFIED / CLOSED — Worker Dry-run Result / Audit Trail
  Dashboard Read-only Display Implementation
- v0.8.4-E = DONE / PUSHED / CLOSED — closeout / validation hardening plan
- v0.8.4-F = DONE / PUSHED / VERIFIED / CLOSED — Worker Dry-run Result / Audit Trail
  Dashboard Display Validation Hardening Implementation
- v0.8.4-G = DONE / PUSHED / CLOSED — Worker Dry-run Result / Audit Trail Dashboard
  Display Closeout Report
- latest HEAD = `cd16c0157b55eb6901580eea20fd5d96f90afde3`
- latest commit = `docs: close out worker dry-run result dashboard display`
- current Dashboard display (`/dashboard/system`) is read-only
- current Worker dry-run result / audit trail model remains `synthetic_local_only`

## 3. Core Ruling

- v0.8.4-G closing out the Worker dry-run result / audit trail Dashboard read-only
  display does not close out an Owner decision boundary.
- v0.8.4-G does not establish approval readiness.
- v0.8.4-G does not establish execution readiness.
- v0.8.4-G does not establish dispatch readiness.
- Only this addendum, v0.8.4-H, defines the Owner Review Decision Preview boundary, and
  even this addendum only plans the boundary — it does not implement a decision object,
  a decision builder, or any Dashboard control.

## 4. Owner Review Decision Preview Boundary Statements

- Owner Review Decision Preview is read-only, preview-only, and synthetic local-only.
- Decision preview is not approval.
- Decision preview is not rejection.
- Decision preview is not execution.
- Decision preview is not dispatch.
- Decision preview is not a send action.
- Decision preview is not a queue write.
- Decision preview is not an audit trail write.
- `owner_review_required` is not Owner approval.
- Dry-run result preview is not actual execution result.
- Audit trail preview is not audit trail persistence.
- Readback summary preview is not Hermes activation.
- Owner reading the Dashboard is not Owner decision execution.
- v0.8.5 is reserved for the OpenClaw Mock Gateway.
- v0.8.4-H does not start v0.8.5.

## 5. Future Owner Review Decision Preview Shape (plan-only)

A future round may define an **Owner Review Decision Preview** object with fields such
as:

- `decision_preview_id` — synthetic local-only identifier
- `reviewed_result_id` — reference to the v0.8.4-B dry-run result being reviewed
- `reviewed_audit_id` — reference to the v0.8.4-B audit trail record being reviewed
- `source` — must be `synthetic_local_only`
- `possible_decision_states` — a plan-only enum describing states the Owner *might* end
  up in after reviewing, e.g. `not_yet_reviewed`, `pending`, `informational_only`; this
  enum must never include a state implying an approval, rejection, execution, or dispatch
  already happened
- `decision_recorded` — must be `false`; recording a real Owner decision is out of scope
  for this preview object
- `owner_review_required` — must be `true`
- `permissions` — `execution_permission`, `dispatch_permission`,
  `external_side_effects_permission`, `result_persistence_permission`,
  `audit_trail_write_permission`, `decision_execution_permission`, all `false`
- `runtime_state` — the same disabled-flag family as the v0.8.4-B model, all `false`

This object shape is a plan-only definition. No decision preview object, no decision
preview file, and no decision preview builder is created by v0.8.4-H.

## 6. Safety Boundary

- v0.8.4-H does not add POST, form, button, action URL, approve control, reject
  control, execute control, dispatch control, or send control.
- v0.8.4-H does not touch Worker, OpenClaw, Hermes, Google Sheets, the real queue DB,
  webhook, endpoint, or connector.
- v0.8.4-H does not create a production or shared DB.
- v0.8.4-H does not create a Remote Blackboard API runtime.
- v0.8.4-H does not modify the Dashboard route, template, or CSS.
- v0.8.4-H does not modify runtime code.
- v0.8.4-H does not write to the queue, the audit trail, or any real DB.
- v0.8.4-H does not read secrets, `.env`, tokens, API keys, private keys, full
  spreadsheet IDs, webhook URLs, or production endpoints.

## 7. Handoff

v0.8.5 remains reserved for the OpenClaw Mock Gateway. v0.8.4-H does not start v0.8.5.

Optional next steps (neither is started by v0.8.4-H):

- v0.8.4-I — Roadmap Amendment / Final Closeout Addendum
- v0.8.5-A — OpenClaw Command Envelope Plan

v0.8.4-H does not start v0.8.4-I. v0.8.4-H does not start v0.8.5-A.

## 8. Non-goals

- no Owner Review Decision Preview implementation
- no decision object, decision file, or decision builder
- no new Dashboard feature
- no Dashboard route change in this phase
- no template change in this phase
- no CSS change in this phase
- no change to any v0.8.4-A through v0.8.4-G artifact
- no change to any v0.8.3 artifact
- no change to any v0.8.2 artifact
- no change to any v0.8.1 artifact
- no Worker runtime
- no Worker loop
- no queue read/write
- no audit trail write
- no execution
- no dispatch
- no OpenClaw
- no Hermes
- no Google Sheets
- no secrets
- no commit
- no push
- no tag
- no v0.8.5 work
- no v0.8.4-I work
- no v0.8.5-A work

## 9. v0.8.4-H Acceptance Criteria

- v0.8.4-H plan doc exists
- v0.8.4-H readiness script exists
- v0.8.4-H readiness PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- every v0.8.4-A through v0.8.4-G artifact is untouched
- every v0.8.3 artifact is untouched
- every v0.8.2 artifact is untouched
- every v0.8.1 artifact is untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no audit trail is written
- no POST / no execution / no dispatch occurs
- `patches/` remains untracked
- no tag is created
- no v0.8.5 work is started
