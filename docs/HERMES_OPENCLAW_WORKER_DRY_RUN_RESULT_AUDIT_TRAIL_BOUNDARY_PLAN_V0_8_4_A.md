# Hermes × OpenClaw v0.8.4-A
# Worker Dry-run Result / Audit Trail Boundary Plan

## 0. Status

- Phase: v0.8.4-A
- Type: plan-only / boundary plan
- Base commit: `dca6393e0d400266d6725298831394013eb3b0f1`
- Latest commit message: `docs: close out worker dry-run dashboard display`
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
- v0.8.4-B status: NOT STARTED

v0.8.4-A is a plan-only round. It does not implement anything. It does not modify
`app/main.py`, `templates/system.html`, `static/dashboard.css`, the v0.8.3-G report or
readiness script, the v0.8.3-F validator, or any other existing tracked file. It does not
start a Worker, does not run a Worker loop, does not call OpenClaw, does not connect
Hermes, does not read or write Google Sheets, does not read the real queue DB, and does
not POST anything anywhere.

## 1. Purpose

v0.8.4-A closes out the v0.8.3 Worker dry-run preview Dashboard display series' handoff
and plans, but does not implement, the next phase: how a future round may produce, store,
display, or read back a Worker dry-run **result**, an **audit trail** record, an **owner
review event**, and a **readback summary** — all while the real Worker remains off.
Specifically it:

- confirms the v0.8.3 series closeout state (v0.8.3-A through v0.8.3-G);
- confirms `/dashboard/system` remains read-only and the v0.8.3-B Worker dry-run preview
  model remains synthetic local-only, preview-only, all flags false;
- defines the future shape of a dry-run result object, an audit trail record, an owner
  review event, and a readback summary — as plan-only definitions, not implementations;
- defines the synthetic local-only fixture boundary, validation boundary, and Dashboard
  display boundary a future implementation must respect;
- defines the exact phrase required to authorize a future v0.8.4-B round (the actual
  boundary implementation).

This round produces only a plan document and a readiness/validation script for that plan.
It does not create or modify any Dashboard-facing file, any fixture, any result file, or
any audit trail file.

## 2. v0.8.3 Series Closeout State

- v0.8.3-A = DONE / PUSHED / CLOSED
- v0.8.3-B = DONE / PUSHED / CLOSED
- v0.8.3-C = DONE / PUSHED / CLOSED
- v0.8.3-D = DONE / PUSHED / CLOSED
- v0.8.3-E = DONE / PUSHED / CLOSED
- v0.8.3-F = DONE / PUSHED / CLOSED
- v0.8.3-G = DONE / PUSHED / CLOSED
- latest HEAD = `dca6393e0d400266d6725298831394013eb3b0f1`
- latest commit = `docs: close out worker dry-run dashboard display`
- current Dashboard display (`/dashboard/system`) is read-only
- current Worker dry-run preview model remains `synthetic_local_only`
- current `dry_run_status` remains `preview_only_not_executed`
- `owner_review_required` remains true
- all permission flags on the current model remain false
  (`execution_permission`, `dispatch_permission`, `external_side_effects_permission`)
- all runtime flags on the current model remain false (`worker_started`,
  `worker_loop_started`, `openclaw_called`, `hermes_called`, `google_sheets_enabled`,
  `real_queue_db_read`, `queue_written`, `post_enabled`, `secrets_read`,
  `webhook_created`, `endpoint_created`, `connector_created`, `production_db_created`,
  `remote_blackboard_api_runtime_created`)

## 3. Future Dry-run Result Object Shape (plan-only)

A future v0.8.4-B implementation may define a dry-run **result** object with fields such
as:

- `result_id` — synthetic local-only identifier
- `dry_run_id` — reference to the originating v0.8.3-B dry-run preview
- `source` — must be `synthetic_local_only`
- `result_status` — must be `preview_only_not_executed`
- `summary` — a human-readable description of what a future Worker *would* have done,
  never a claim that anything was done
- `owner_review_required` — must be `true`
- `permissions` — `execution_permission`, `dispatch_permission`,
  `external_side_effects_permission`, all `false`
- `runtime_state` — the same disabled-flag family as the v0.8.3-B model, all `false`

This object shape is a plan-only definition. No result object, no result file, and no
result builder is created by v0.8.4-A.

## 4. Future Audit Trail Record Shape (plan-only)

A future v0.8.4-B implementation may define an **audit trail** record with fields such
as:

- `audit_id` — synthetic local-only identifier
- `event_type` — e.g. `dry_run_preview_generated`, `dry_run_result_generated`,
  `owner_review_recorded`
- `source` — must be `synthetic_local_only`
- `timestamp` — local, synthetic, not tied to any real execution
- `actor` — must be a local/plan-only label, never `Worker`, `OpenClaw`, or `Hermes` as an
  active executor
- `related_result_id` / `related_dry_run_id` — cross-references only
- `owner_review_required` — must be `true`
- `permissions` / `runtime_state` — same disabled-flag family, all `false`

This record shape is a plan-only definition. No audit trail record, file, or builder is
created by v0.8.4-A.

## 5. Future Owner Review Event Shape (plan-only)

A future v0.8.4-B implementation may define an **owner review event** with fields such
as:

- `review_event_id` — synthetic local-only identifier
- `reviewed_result_id` / `reviewed_audit_id` — cross-references only
- `review_notice` — text stating Owner Review is required before any permission or
  runtime flag may change away from `false`
- `decision` — plan-only enum, e.g. `pending`, `not_yet_reviewed` (never a value implying
  an execution or dispatch approval was already granted)
- `source` — must be `synthetic_local_only`

This event shape is a plan-only definition. No owner review event, file, or builder is
created by v0.8.4-A.

## 6. Future Readback Summary Shape (plan-only)

A future v0.8.4-B implementation may define a **readback summary** with fields such as:

- `summary_id` — synthetic local-only identifier
- `covers_result_ids` / `covers_audit_ids` — cross-references only
- `display_text` — read-only, human-readable rollup for future Dashboard display
- `source` — must be `synthetic_local_only`
- `owner_review_required` — must be `true`
- `permissions` / `runtime_state` — same disabled-flag family, all `false`

This summary shape is a plan-only definition. No readback summary, file, or builder is
created by v0.8.4-A.

## 7. Future Synthetic Local-only Fixture Boundary (plan-only)

A future v0.8.4-B implementation must:

- store any result / audit trail / owner review event / readback summary fixture only as
  local, synthetic, static data (e.g. local JSON), mirroring the v0.8.3-B fixture pattern
- never derive a fixture value from a real Worker execution
- never derive a fixture value from reading the real queue DB
- never derive a fixture value from an OpenClaw or Hermes call
- never derive a fixture value from Google Sheets
- never read secrets, `.env`, or any credential store when producing a fixture

## 8. Future Validation Boundary (plan-only)

A future v0.8.4-B validator must, mirroring the v0.8.3-F / v0.8.3-G validators:

- work during Owner Review, after local commit, and after push
- read committed file content directly rather than relying only on
  `git diff --unified=0` added-lines output
- confirm every new result/audit-trail/review/readback fixture and builder keeps
  `source == synthetic_local_only`
- confirm every new result/audit-trail/review/readback object keeps
  `owner_review_required == true`
- confirm every permission flag stays `false`
- confirm every runtime flag stays `false`
- confirm no POST, form, button, or action URL was added
- confirm no webhook/endpoint/execute/dispatch/send control was added
- confirm no Worker/OpenClaw/Hermes/Google Sheets/real-queue-DB/secrets involvement
- scan for unsafe done-claims the same way the v0.8.3-F/G validators do

## 9. Future Dashboard Display Boundary (plan-only)

If a future round chooses to surface any result/audit-trail/readback data on
`/dashboard/system`, it must, mirroring the v0.8.3-D/F Dashboard boundary:

- remain GET-only; no new route, no POST route
- remain read-only; no form, no button, no action URL, no onclick
- remain display-only in CSS; no execution/dispatch/send control styling, no hidden
  interactive affordance
- always show the disabled runtime badges and false permission flags alongside any
  result/audit-trail/readback content
- never let displayed content imply a real Worker executed anything

This is a plan-only boundary. No Dashboard file is modified by v0.8.4-A.

## 10. Future Result / Audit Trail Allowed Sources Only

Any future dry-run result, audit trail record, owner review event, or readback summary
may only ever be:

- from a synthetic local-only source
- a preview-only result

and must never be:

- an execution result from a real Worker
- derived from a real queue DB
- accompanied by any external side effect
- delivered via POST
- the product of a dispatch
- the product of an OpenClaw call
- the product of a Hermes call
- derived from Google Sheets
- derived from secrets

## 11. Handoff

Future phase:
v0.8.4-B — Worker Dry-run Result / Audit Trail Boundary Implementation

v0.8.4-B should only create local synthetic result/audit-trail artifacts.
v0.8.4-B must not start a real Worker.
v0.8.4-B must not run a Worker loop.
v0.8.4-B must not execute any task.
v0.8.4-B must not write the real queue DB.
v0.8.4-B must not call OpenClaw.
v0.8.4-B must not activate Hermes.
v0.8.4-B must not read or write Google Sheets.
v0.8.4-B must not create a webhook, endpoint, or connector.
v0.8.4-B must not create a production/shared DB or a Remote Blackboard API runtime.

v0.8.4-B is not started by v0.8.4-A.

## 12. Non-goals

- no Worker result implementation
- no audit trail runtime
- no result DB
- no queue DB
- no production/shared DB
- no Remote Blackboard API runtime
- no new Dashboard feature
- no Dashboard route change in this phase
- no template change in this phase
- no CSS change in this phase
- no v0.8.3-G report/readiness change in this phase
- no v0.8.3-F validator change in this phase
- no Worker runtime
- no Worker loop
- no queue read/write
- no execution
- no dispatch
- no OpenClaw
- no Hermes
- no Google Sheets
- no secrets
- no commit
- no push
- no tag
- no v0.8.4-B work

## 13. Exact Future v0.8.4-B Authorization Phrase

Only the following exact phrase, given verbatim by the Owner, may authorize a future
v0.8.4-B implementation round. Paraphrases, general approval, readiness PASS, Owner
Review PASS, commit approval, or push approval do not authorize v0.8.4-B.

批准實作 v0.8.4-B — Worker Dry-run Result / Audit Trail Boundary Implementation，僅允許新增 synthetic local-only 的 Worker dry-run result、audit trail、owner review event 與 readback summary artifacts，用於描述 preview-only result boundary；不得啟動 Worker，不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得新增 POST，不得新增 form/button/action URL，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 14. v0.8.4-A Acceptance Criteria

- v0.8.4-A plan doc exists
- v0.8.4-A readiness script exists
- v0.8.4-A readiness PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- the v0.8.3-G report and readiness script are untouched
- the v0.8.3-F validator is untouched
- the v0.8.3-B builder is untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no POST / no execution / no dispatch occurs
- `patches/` remains untracked
- no tag is created
- a full Owner Review diff is produced
