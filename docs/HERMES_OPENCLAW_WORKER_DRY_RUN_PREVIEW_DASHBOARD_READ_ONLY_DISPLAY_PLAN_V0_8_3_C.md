# Hermes × OpenClaw v0.8.3-C
# Worker Dry-run Preview Dashboard Read-only Display Plan

## 0. Status

- Phase: v0.8.3-C
- Type: plan-only / Dashboard read-only display plan
- Base commit: 8d99aea9a214b40359a2fd47cab413d47a0ae017
- Previous phase: v0.8.3-B = DONE / PUSHED / CLOSED
- Implementation status: NOT IMPLEMENTED
- Dashboard route status: NOT MODIFIED
- Dashboard template status: NOT MODIFIED
- Dashboard CSS status: NOT MODIFIED
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT IMPLEMENTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Queue status: REAL QUEUE DB NOT READ / NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- v0.8.3-D status: NOT STARTED

v0.8.3-C is a plan-only round. It does not implement anything. It does not modify
`app/main.py`, `templates/system.html`, or `static/dashboard.css`. It does not wire the
v0.8.3-B standalone builder into the Dashboard. It does not start a Worker, does not run a
Worker loop, does not call OpenClaw, does not connect Hermes, does not read or write Google
Sheets, does not read the real queue DB, and does not POST anything anywhere.

## 1. Purpose

v0.8.3-C plans, but does not implement, how a future round could display the v0.8.3-B Worker
dry-run preview model on the Dashboard. Specifically it plans:

- how the model could be shown in a GET-only, read-only, synthetic local-only way;
- where on the existing Dashboard the display section would live;
- which fields, permission flags, and runtime-state flags must be visible and must remain
  false;
- how Owner Review required status stays visible;
- how the display avoids any button, form, or action URL;
- how the display avoids any Worker/OpenClaw/Hermes/Google Sheets/queue side effect;
- what a future implementation round (v0.8.3-D) may be allowed to touch, and only under a
  separately granted exact authorization phrase;
- what this round explicitly must not do.

This round produces only a plan document and a readiness/validation script for that plan. It
does not create or modify any Dashboard-facing file.

## 2. Inherited v0.8.3-B Model

v0.8.3-B already provides, as standalone synthetic local-only artifacts:

- a synthetic fixture (`fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json`)
- a standalone builder (`scripts/worker_dry_run_preview_boundary_v0_8_3_b.py`) exposing
  `build_worker_dry_run_preview_model()`
- a read-only preview model dict returned by that builder, containing:
  - `permissions` dict (`execution_permission`, `dispatch_permission`,
    `external_side_effects_permission`, all `false`)
  - `runtime_state` dict (all runtime flags `false`)
  - `boundary_summary`
  - `review_notice`

v0.8.3-C does not modify the v0.8.3-B builder, fixture, doc, or readiness script. It only
reads them for reference and re-runs the builder as a read-only sanity check.

## 3. Proposed Future Dashboard Display Location

A future implementation round (v0.8.3-D) could:

- add a read-only section to the existing `/dashboard/system` route;
- name the section `worker-dry-run-preview`;
- place it after the existing v0.8.2 local mock preview block
  (`section.local-mock-preview`), as a separate, clearly labeled read-only panel;
- not replace or alter the existing v0.8.2 preview block;
- not change any existing Dashboard behavior;
- not add any new route.

## 4. Proposed Future Display Fields

A future v0.8.3-D display could show, read-only, the following fields from the v0.8.3-B
model:

- `dry_run_id`
- `source`
- `task_title`
- `task_summary`
- `source_role`
- `target_role`
- `proposed_worker_action`
- `dry_run_status`
- `owner_review_required`
- `review_notice`
- `boundary_summary`

## 5. Required Permission Flags Display

A future v0.8.3-D display must show, and they must remain:

- `execution_permission = false`
- `dispatch_permission = false`
- `external_side_effects_permission = false`

## 6. Required Runtime State Flags Display

A future v0.8.3-D display must show, and they must remain:

- `worker_started = false`
- `worker_loop_started = false`
- `openclaw_called = false`
- `hermes_called = false`
- `google_sheets_enabled = false`
- `real_queue_db_read = false`
- `queue_written = false`
- `post_enabled = false`
- `secrets_read = false`
- `webhook_created = false`
- `endpoint_created = false`
- `connector_created = false`
- `production_db_created = false`
- `remote_blackboard_api_runtime_created = false`

## 7. Required Read-only UI Boundaries

A future v0.8.3-D display must:

- be GET-only
- be read-only
- be synthetic local-only
- show Owner Review required
- show disabled runtime badges
- show permission flags false
- show runtime state flags false
- include no form
- include no button
- include no action_url
- include no post_url
- include no webhook_url
- include no endpoint_url
- include no execute_url
- include no dispatch_url
- include no send_url
- include no POST

## 8. Proposed Future Implementation Candidate Scope

If separately authorized, a future v0.8.3-D round may be allowed to modify only:

- `app/main.py`, only to call the existing standalone v0.8.3-B builder on the existing
  GET-only `/dashboard/system` path
- `templates/system.html`, only to render read-only v0.8.3-B model fields
- `static/dashboard.css`, only for read-only styling of the new section
- one new v0.8.3-D validation script

v0.8.3-C does not implement any of these changes. v0.8.3-C itself creates none of these
changes and modifies none of these files.

## 9. Explicitly Forbidden Unless Separately Authorized

- no Worker runtime
- no Worker loop
- no queue consumer
- no dispatcher
- no OpenClaw call
- no Hermes activation
- no Google Sheets read/write
- no reading or writing of the real queue DB
- no queue write
- no POST
- no execute/dispatch/send controls
- no secrets
- no webhook/endpoint/connector
- no production/shared DB
- no Remote Blackboard API runtime

## 10. Required Validation Gates Before Any Future D

Before any future v0.8.3-D implementation round, the following must be checked:

- v0.8.3-C readiness script must PASS
- `python -m compileall scripts` must PASS
- v0.8.3-B builder local preview must PASS with all permission/runtime flags false
- E / C / v0.8.2-A / v0.8.2-B / V / W / Z / Y / X regressions must PASS
- v0.8.3-B / v0.8.3-A / F / D readiness scripts may be observed only, not required to PASS in
  Owner Review phase

## 11. Exact Future v0.8.3-D Authorization Phrase

Only the following exact phrase, given verbatim by the Owner, may authorize a future
v0.8.3-D implementation round. Paraphrases, general approval, readiness PASS, Owner Review
PASS, commit approval, or push approval do not authorize v0.8.3-D.

批准實作 v0.8.3-D — Worker Dry-run Preview Dashboard Read-only Display Implementation，僅允許在既有 Dashboard GET-only `/dashboard/system` 中以 read-only、synthetic local-only 方式顯示 v0.8.3-B 的 Worker dry-run preview model；僅允許修改 app/main.py、templates/system.html、static/dashboard.css 與新增 v0.8.3-D validation script；不得新增 POST，不得新增 button/form/action URL，不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

v0.8.3-D is not started by v0.8.3-C.

## 12. Acceptance Criteria For v0.8.3-C

- v0.8.3-C plan doc exists
- v0.8.3-C readiness script exists
- v0.8.3-C readiness script PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- the v0.8.3-B builder is untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no POST / no execution / no dispatch occurs
- a full Owner Review diff is produced

## 13. Non-goals

- no implementation
- no Dashboard route change
- no template change
- no CSS change
- no v0.8.3-B builder change
- no Worker runtime
- no queue read/write
- no execution
- no dispatch
- no v0.8.3-D work
