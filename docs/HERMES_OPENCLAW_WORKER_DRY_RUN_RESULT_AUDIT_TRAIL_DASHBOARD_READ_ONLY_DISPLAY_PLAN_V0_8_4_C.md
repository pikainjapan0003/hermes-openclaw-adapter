# Hermes × OpenClaw v0.8.4-C
# Worker Dry-run Result / Audit Trail Dashboard Read-only Display Plan

## 0. Status

- Phase: v0.8.4-C
- Type: plan-only
- Base commit: `6d6d3ed6153e13ce4f1b155bc11e1c5248427d12`
- Latest commit message: `feat: add worker dry-run result audit trail artifacts`
- Previous phase: v0.8.4-B = DONE / PUSHED / CLOSED
- Implementation status: NOT IMPLEMENTED
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT STARTED
- Task execution status: NOT EXECUTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ
- Queue status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.8.4-D status: NOT STARTED

v0.8.4-C is a plan-only round. It does not implement anything. It does not modify
`app/main.py`, `templates/system.html`, `static/dashboard.css`, the v0.8.4-B
doc/fixture/builder/readiness, the v0.8.4-A plan/readiness, the v0.8.3-G/F/E/D/C/B/A
artifacts, or any other existing tracked file. It does not start a Worker, does not run a
Worker loop, does not call OpenClaw, does not connect Hermes, does not read or write
Google Sheets, does not read the real queue DB, and does not POST anything anywhere.

## 1. Purpose

v0.8.4-C plans, but does not implement, how a future round may display the v0.8.4-B
synthetic local-only Worker dry-run result / audit trail / owner review event / readback
summary model on the existing GET-only `/dashboard/system` page, read-only. It:

- confirms v0.8.4-A and v0.8.4-B are DONE / PUSHED / CLOSED at HEAD
  `6d6d3ed6153e13ce4f1b155bc11e1c5248427d12`;
- confirms `/dashboard/system` remains GET-only and unmodified by this round;
- confirms the v0.8.4-B model remains `synthetic_local_only`, `preview_only`, and all
  flags false;
- plans, but does not implement, four future read-only display cards and their
  surrounding safety displays;
- plans, but does not implement, the future validation hardening a committed Dashboard
  display change would need;
- defines the exact phrase required to authorize a future v0.8.4-D round (the actual
  Dashboard read-only display implementation).

This round produces only a plan document and a readiness/validation script for that plan.
It does not create or modify any Dashboard-facing file, and it does not wire the v0.8.4-B
builder into `app/main.py`.

## 2. v0.8.4-A / v0.8.4-B Closeout State

- v0.8.4-A = DONE / PUSHED / CLOSED
- v0.8.4-B = DONE / PUSHED / CLOSED
- latest HEAD = `6d6d3ed6153e13ce4f1b155bc11e1c5248427d12`
- latest commit = `feat: add worker dry-run result audit trail artifacts`
- the existing `/dashboard/system` route remains GET-only
- the current Worker dry-run result/audit-trail model (from
  `build_worker_dry_run_result_audit_trail_model()`) remains `synthetic_local_only`
- `preview_only` remains `true`
- `dry_run_result.result_status` remains `preview_result_not_executed`
- `audit_trail_record.audit_status` remains `preview_audit_not_persisted`
- `owner_review_event.review_status` remains `owner_review_required`
- `readback_summary.summary_status` remains `preview_readback_only`
- all permission flags remain false (`execution_permission`, `dispatch_permission`,
  `external_side_effects_permission`, `result_persistence_permission`,
  `audit_trail_write_permission`)
- all runtime flags remain false (`worker_started`, `worker_loop_started`,
  `task_executed`, `openclaw_called`, `hermes_called`, `google_sheets_enabled`,
  `real_queue_db_read`, `queue_written`, `post_enabled`, `secrets_read`,
  `webhook_created`, `endpoint_created`, `connector_created`, `production_db_created`,
  `remote_blackboard_api_runtime_created`)

## 3. Future Dashboard Read-only Display Cards (plan-only)

A future v0.8.4-D implementation may add the following read-only display cards to the
existing GET-only `/dashboard/system` page:

### 3.1 Future Dashboard read-only result card

Displays `dry_run_result` fields (`result_id`, `related_dry_run_id`, `result_status`,
`result_summary`, `result_generated_from`, `result_generated_at`) as plain read-only
text. Must always show `result_status = preview_result_not_executed` and must never
imply a real Worker produced this result.

### 3.2 Future Dashboard read-only audit trail card

Displays `audit_trail_record` fields (`audit_id`, `related_result_id`, `audit_source`,
`audit_status`, `events`, `persistence_target`) as a plain read-only list. Must always
show `audit_status = preview_audit_not_persisted` and `persistence_target = none`.

### 3.3 Future Dashboard read-only owner review event card

Displays `owner_review_event` fields (`review_event_id`, `related_audit_id`,
`review_status`, `review_action_available`, `review_notice`) as plain read-only text.
Must always show `review_status = owner_review_required` and
`review_action_available = false`, with no clickable review affordance.

### 3.4 Future Dashboard read-only readback summary card

Displays `readback_summary` fields (`summary_id`, `related_result_id`,
`summary_status`, `operator_summary`, `safety_summary`, `next_step_hint`) as plain
read-only text. Must always show `summary_status = preview_readback_only`.

## 4. Future Permission / Runtime / Boundary Notice Display (plan-only)

Alongside the four cards above, a future v0.8.4-D implementation must display:

- **future permission flags display**: every permission flag from the v0.8.4-B model
  (`execution_permission`, `dispatch_permission`, `external_side_effects_permission`,
  `result_persistence_permission`, `audit_trail_write_permission`), each rendered as a
  disabled/false badge;
- **future runtime flags display**: every runtime flag from the v0.8.4-B model
  (`worker_started`, `worker_loop_started`, `task_executed`, `openclaw_called`,
  `hermes_called`, `google_sheets_enabled`, `real_queue_db_read`, `queue_written`,
  `post_enabled`, `secrets_read`, `webhook_created`, `endpoint_created`,
  `connector_created`, `production_db_created`,
  `remote_blackboard_api_runtime_created`), each rendered as a disabled/false badge;
- **future boundary notice display**: the `boundary_summary` text from the v0.8.4-B
  model, plus a visible "synthetic local-only" / "preview only" / "Owner Review
  required" notice mirroring the existing v0.8.3 Worker dry-run preview section.

## 5. Future Validation Hardening for Committed Dashboard Display (plan-only)

A future v0.8.4-D validator must, mirroring the v0.8.3-D/F validators:

- work during Owner Review, after local commit, and after push;
- read committed file content directly rather than relying only on
  `git diff --unified=0` added-lines output;
- confirm the existing `/dashboard/system` route stays GET-only and that no
  POST/PUT/DELETE/PATCH route was added for it;
- confirm `app/main.py` references `build_worker_dry_run_result_audit_trail_model`
  and does not directly read the v0.8.4-B fixture JSON;
- confirm `templates/system.html` renders all four cards and shows
  `preview_result_not_executed`, `preview_audit_not_persisted`,
  `owner_review_required`, and `preview_readback_only`;
- confirm the new display section contains no `<button`, no `<form`, no `action=`, no
  `method=`, no `onclick`, and no forbidden control URL key;
- confirm `static/dashboard.css` contains no `cursor: pointer`, no
  execute/dispatch/send control styling, and no hidden interactive affordance for the
  new section;
- confirm every permission flag and every runtime flag stays `false`;
- confirm no Worker/OpenClaw/Hermes/Google Sheets/real-queue-DB/secrets involvement;
- scan for unsafe done-claims the same way the v0.8.3-F/G and v0.8.4-A/B readiness
  scripts do.

## 6. Future Dashboard Display Allowed Sources Only

If a future round implements this display, it may only ever:

- reuse the existing GET-only route
- render read-only
- source content from `synthetic_local_only`
- show preview-only result/audit content

and must never:

- add a POST route
- add a form
- add a button
- add an action URL
- add an approve, execute, dispatch, or send control
- start a real Worker
- call OpenClaw
- call Hermes
- read or write Google Sheets
- read or write the real queue DB
- read a secret
- create a webhook, endpoint, or connector

## 7. Handoff

Future phase:
v0.8.4-D — Worker Dry-run Result / Audit Trail Dashboard Read-only Display Implementation

v0.8.4-D should only add read-only display of synthetic local-only result/audit-trail artifacts to existing GET-only /dashboard/system.
v0.8.4-D must not add POST.
v0.8.4-D must not add form/button/action URL.
v0.8.4-D must not add approve/execute/dispatch/send controls.
v0.8.4-D must not start a real Worker.
v0.8.4-D must not call OpenClaw.
v0.8.4-D must not activate Hermes.
v0.8.4-D must not read or write Google Sheets.
v0.8.4-D must not read or write real queue DB.
v0.8.4-D must not create a webhook, endpoint, or connector.
v0.8.4-D must not create a production/shared DB or a Remote Blackboard API runtime.

v0.8.4-D is not started by v0.8.4-C.

## 8. Non-goals

- no Dashboard display implementation
- no Dashboard template change in this phase
- no CSS addition in this phase
- no builder wiring into `app/main.py` in this phase
- no audit trail runtime
- no result DB
- no queue DB
- no production/shared DB
- no Remote Blackboard API runtime
- no v0.8.4-B doc/fixture/builder/readiness change
- no v0.8.4-A plan/readiness change
- no v0.8.3-G/F/E/D/C/B/A change
- no v0.8.2 change
- Worker remains off
- Worker loop remains off
- Task execution remains disabled
- OpenClaw remains uncalled
- Hermes remains uncalled
- Google Sheets remains unused
- real queue DB remains unread
- no queue writes occur
- no POST exists
- secrets remain unread
- no webhook/endpoint/connector is created
- no commit
- no push
- no tag
- no v0.8.4-D work

## 9. Exact Future v0.8.4-D Authorization Phrase

Only the following exact phrase, given verbatim by the Owner, may authorize a future
v0.8.4-D implementation round. Paraphrases, general approval, readiness PASS, Owner
Review PASS, commit approval, or push approval do not authorize v0.8.4-D.

批准實作 v0.8.4-D — Worker Dry-run Result / Audit Trail Dashboard Read-only Display Implementation，僅允許在既有 Dashboard GET-only `/dashboard/system` 中以 read-only、synthetic local-only 方式顯示 v0.8.4-B 的 Worker dry-run result、audit trail、owner review event 與 readback summary artifacts；僅允許修改 app/main.py、templates/system.html、static/dashboard.css 與新增 v0.8.4-D validation script；不得新增 POST，不得新增 form/button/action URL，不得新增 approve/execute/dispatch/send controls，不得啟動 Worker，不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 10. v0.8.4-C Acceptance Criteria

- v0.8.4-C plan doc exists
- v0.8.4-C readiness script exists
- v0.8.4-C readiness PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- the v0.8.4-B doc/fixture/builder/readiness are untouched
- the v0.8.4-A plan/readiness are untouched
- the v0.8.3-G/F/E/D/C/B/A artifacts are untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no POST / no execution / no dispatch occurs
- `patches/` remains untracked
- no tag is created
- a full Owner Review diff is produced
