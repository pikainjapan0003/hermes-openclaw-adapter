# Hermes × OpenClaw v0.8.4-E
# Worker Dry-run Result / Audit Trail Dashboard Display Closeout / Validation Hardening Plan

## Status

This is plan-only. No implementation happens in this round.

- v0.8.4-A is DONE / PUSHED / CLOSED
- v0.8.4-B is DONE / PUSHED / CLOSED
- v0.8.4-C is DONE / PUSHED / CLOSED
- v0.8.4-D is DONE / PUSHED / VERIFIED / CLOSED
- latest HEAD = bf7777f8850822b083f7c868e8136bb5caf932d1
- latest commit = feat: display worker dry-run result audit trail on dashboard

## Committed safety boundary (unchanged by this plan)

- /dashboard/system remains GET-only
- Dashboard display is read-only
- source remains synthetic_local_only
- preview_only remains true
- dry_run_result.result_status remains preview_result_not_executed
- audit_trail_record.audit_status remains preview_audit_not_persisted
- owner_review_event.review_status remains owner_review_required
- readback_summary.summary_status remains preview_readback_only
- all permission flags remain false
- all runtime flags remain false

Worker remains off. Task execution remains disabled. OpenClaw remains uncalled. Hermes remains
uncalled. Google Sheets remains disabled. The real queue DB remains unread and unwritten. No
POST route exists on /dashboard/system. No secrets are read by this display path. No webhook,
endpoint, or connector exists for this display path.

## v0.8.4-D committed display scope (reference only, not re-implemented here)

- `app/main.py` loads the v0.8.4-B builder through a file-path `importlib` import
  (`_load_v0_8_4_d_build_worker_dry_run_result_audit_trail_model`), mirroring the v0.8.3-D
  loader pattern.
- `app/main.py` calls `build_worker_dry_run_result_audit_trail_model()` inside the existing
  `GET /dashboard/system` route and passes `worker_dry_run_result_audit_trail` into the
  `system.html` template context.
- `templates/system.html` displays the dry-run result, audit trail record, owner review event,
  and readback summary inside `<section id="worker-dry-run-result-audit-trail">`, along with
  permission-flag and runtime-flag grids and a boundary notice.
- `templates/system.html` contains no `<form>`, `<button>`, `action=`, `method=`, `onclick=`,
  or control-URL keys (`action_url`, `post_url`, `webhook_url`, `endpoint_url`, `execute_url`,
  `dispatch_url`, `send_url`) inside that section.
- `static/dashboard.css` only adds display-only styling for the new section's classes
  (`.worker-dry-run-result-audit-trail`, `.dry-run-result-grid`, `.dry-run-result-card`,
  `.audit-trail-card`, `.owner-review-event-card`, `.readback-summary-card`,
  `.boundary-notice`, `.permission-flag-list`, `.runtime-flag-list`), with no `cursor: pointer`
  or other interactive affordance.

## Future validation hardening (to be implemented in v0.8.4-F, not this round)

A future, stable validator for the v0.8.4-D Dashboard display should:

- read the committed contents of `app/main.py`, `templates/system.html`, and
  `static/dashboard.css` directly, the same way the v0.8.3-F validator reads v0.8.3-D content,
  rather than relying only on `git diff` added-lines output
- treat the v0.8.4-D files as a committed baseline that does not change across Owner Review /
  post-commit / post-push phases, so the same content checks stay valid in all phases
- assert that `/dashboard/system` remains GET-only, with no POST/PUT/PATCH/DELETE route variant
- assert that the `worker-dry-run-result-audit-trail` section contains no form/button/action
  URL/approve/execute/dispatch/send controls
- re-run the v0.8.4-B builder (read-only reference) and assert its output stays
  `source == synthetic_local_only` and `preview_only == true`
- assert all v0.8.4-B permission flags and runtime-state flags remain false
- preserve the existing regression expectations for v0.8.4-C/B/A, v0.8.3-F/G, v0.8.2, and
  v0.8.1 artifacts — none of those should be modified by v0.8.4-F

## Future phase: v0.8.4-F

Future phase:
v0.8.4-F — Worker Dry-run Result / Audit Trail Dashboard Display Validation Hardening Implementation

v0.8.4-F should only add a committed-state validation hardening script for the v0.8.4-D
Dashboard read-only display.

v0.8.4-F must not modify app/main.py.
v0.8.4-F must not modify templates/system.html.
v0.8.4-F must not modify static/dashboard.css.
v0.8.4-F must not add POST.
v0.8.4-F must not add form/button/action URL.
v0.8.4-F must not add approve/execute/dispatch/send controls.
v0.8.4-F must not start Worker.
v0.8.4-F must not call OpenClaw.
v0.8.4-F must not activate Hermes.
v0.8.4-F must not read/write Google Sheets.
v0.8.4-F must not read or write real queue DB.
v0.8.4-F must not create webhook/endpoint/connector.
v0.8.4-F must not create production/shared DB or Remote Blackboard API runtime.

v0.8.4-F is not started by this plan. This round only documents its scope for future Owner
Review approval.

## Authorization phrase (future v0.8.4-F, quoted here once for reference only)

批准實作 v0.8.4-F — Worker Dry-run Result / Audit Trail Dashboard Display Validation Hardening Implementation，僅允許新增 committed-state validation hardening script，用於穩定驗證 v0.8.4-D 已提交的 Dashboard read-only result/audit-trail display；不得修改 app/main.py，不得修改 templates/system.html，不得修改 static/dashboard.css，不得新增 POST，不得新增 form/button/action URL，不得新增 approve/execute/dispatch/send controls，不得啟動 Worker，不得執行 Worker loop，不得執行任務，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## Closeout

This plan does not implement validation hardening. It does not modify the Dashboard. It does
not start Worker, call OpenClaw, activate Hermes, use Google Sheets, read the real queue DB, or
write the queue. It reads no secrets and creates no webhook, endpoint, connector, production
database, or Remote Blackboard API runtime. v0.8.4-F is not started by this round.
