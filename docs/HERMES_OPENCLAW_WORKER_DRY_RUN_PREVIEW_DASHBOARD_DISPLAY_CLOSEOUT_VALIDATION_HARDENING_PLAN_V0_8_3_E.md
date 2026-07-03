# Hermes × OpenClaw v0.8.3-E
# Worker Dry-run Preview Dashboard Display Closeout / Validation Hardening Plan

## 0. Status

- Phase: v0.8.3-E
- Type: plan-only / closeout and validation hardening plan
- Base commit: 58194a1b17392e050dd8c27f6cee8f8b761d3f4e
- Previous phase: v0.8.3-D = DONE / PUSHED / CLOSED
- Implementation status: NOT IMPLEMENTED
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT IMPLEMENTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Queue status: REAL QUEUE DB NOT READ / NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- v0.8.3-F status: NOT STARTED

v0.8.3-E is a plan-only round. It does not implement anything. It does not modify
`app/main.py`, `templates/system.html`, `static/dashboard.css`, or the v0.8.3-D validation
script. It does not start a Worker, does not run a Worker loop, does not call OpenClaw, does
not connect Hermes, does not read or write Google Sheets, does not read the real queue DB,
and does not POST anything anywhere.

## 1. Purpose

v0.8.3-E closes out v0.8.3-D and plans, but does not implement, future validation hardening.
Specifically it:

- records the v0.8.3-D closeout state (what was implemented, what remains unchanged);
- confirms `/dashboard/system` remains GET-only, read-only, and synthetic local-only;
- confirms the v0.8.3-B Worker dry-run preview model is used only as a display model;
- explains why the v0.8.3-D readiness script's post-push observation (36/52) is a
  diff-phase/tooling limitation, not a Dashboard content or safety-boundary failure;
- plans what a future stable validator must check so it keeps working after local commit
  and after push, not only during the Owner Review diff phase;
- defines the exact phrase required to authorize a future v0.8.3-F round (the actual
  validation hardening implementation).

This round produces only a plan document and a readiness/validation script for that plan. It
does not create or modify any Dashboard-facing file, and it does not modify the v0.8.3-D
validation script.

## 2. v0.8.3-D Closeout State

- v0.8.3-D commit = `58194a1b17392e050dd8c27f6cee8f8b761d3f4e`
- Dashboard route remains the existing GET-only `/dashboard/system`
- the `worker-dry-run-preview` section is visible on that page
- the v0.8.3-B builder (`build_worker_dry_run_preview_model()`) is called only to produce a
  synthetic local-only, read-only preview model for display
- `app/main.py` does not directly read the v0.8.3-B fixture JSON
- no new route was added
- no POST was added
- no form was added
- no button was added
- no action URL was added
- no webhook/endpoint/execute/dispatch/send control was added
- no Worker / Worker loop / OpenClaw / Hermes / Google Sheets was touched
- no real queue DB was read
- no queue was written
- no secrets were read

## 3. Known v0.8.3-D Validation Limitation

- v0.8.3-D readiness was designed for the Owner Review diff phase: its added-lines checks
  use `git diff --unified=0` against the working tree.
- after v0.8.3-D was committed and pushed, the working tree became clean, so those
  added-lines checks no longer see the v0.8.3-D implementation lines (there is no
  uncommitted diff left to inspect).
- the post-push v0.8.3-D readiness observation is 36/52.
- this is not a Dashboard content failure: the actual committed content of `app/main.py`,
  `templates/system.html`, and `static/dashboard.css` is unchanged and correct.
- this is not a safety-boundary failure: every check in the v0.8.3-D script that does not
  depend on the added-lines diff (protected-file-untouched checks, the B builder safety
  re-check, the unsafe-done-claims scan, the script's own self-check, and the `patches/`
  check) still passes.
- the full regression suite (E / C / v0.8.2-A / v0.8.2-B / V / W / Z / Y / X) was 100% PASS
  after both the local commit and the push.
- future hardening should avoid depending on uncommitted `git diff` output as the primary
  source of truth for content that is expected to already be committed.

## 4. Validation Hardening Goal

A future v0.8.3-F validator should:

- work during the Owner Review phase (uncommitted working tree);
- work after local commit;
- work after push;
- read the committed files directly instead of relying only on `git diff --unified=0`
  added-lines output;
- inspect `app/main.py` for the existing GET-only `/dashboard/system` route;
- inspect `templates/system.html` for the `worker-dry-run-preview` section;
- inspect `static/dashboard.css` for display-only styling;
- call the v0.8.3-B builder locally and confirm all permission/runtime flags remain false;
- avoid depending on `git diff --unified=0` as the primary content source;
- clearly distinguish content/safety failures from phase/tracked-state observations, so an
  Owner reading the output can tell at a glance whether something is actually broken.

## 5. Required Stable Dashboard Checks

A future v0.8.3-F validator must check:

- the existing `/dashboard/system` route remains GET-only
- no new route was added
- no POST route was added
- no POST method was added
- no form was added
- no button was added
- no action URL was added
- no onclick was added
- no webhook/endpoint/execute/dispatch/send control was added
- `worker_dry_run_preview` is passed to `system.html`
- `app/main.py` references `build_worker_dry_run_preview_model`
- `app/main.py` does not directly read the fixture JSON
- `app/main.py` does not import QueueStore / Worker / OpenClaw / Hermes / Google Sheets in
  the worker dry-run display path
- the existing v0.8.2 Dashboard preview call path (`build_dashboard_preview_model()`)
  remains intact

## 6. Required Stable Template Checks

A future v0.8.3-F validator must check that `templates/system.html` contains:

- a section with id/class `worker-dry-run-preview`
- rendering of `worker_dry_run_preview`
- "Synthetic local-only" text visible
- "Preview only" text visible
- "Owner Review required" text visible
- task fields visible: Dry-run ID, Source, Task title, Task summary, Source role,
  Target role, Proposed worker action, Dry-run status, Review notice, Boundary summary
- permission flags visible: `execution_permission`, `dispatch_permission`,
  `external_side_effects_permission`
- runtime flags visible: `worker_started`, `worker_loop_started`, `openclaw_called`,
  `hermes_called`, `google_sheets_enabled`, `real_queue_db_read`, `queue_written`,
  `post_enabled`, `secrets_read`, `webhook_created`, `endpoint_created`,
  `connector_created`, `production_db_created`, `remote_blackboard_api_runtime_created`

## 7. Required Stable CSS Checks

A future v0.8.3-F validator must check that `static/dashboard.css` contains:

- `worker-dry-run-preview` display styles
- display-only styling (no interactive/control affordance)
- no `cursor: pointer` inside the `worker-dry-run-preview` block
- no execute/dispatch/send/action control styling
- no hidden control affordance
- no animation implying execution

## 8. Required B Builder Safety Checks

A future v0.8.3-F validator must call or import the v0.8.3-B builder locally and verify:

- `source == synthetic_local_only`
- `dry_run_status == preview_only_not_executed`
- `owner_review_required == true`
- `execution_permission == false`
- `dispatch_permission == false`
- `external_side_effects_permission == false`
- all `runtime_state` flags are false
- no side effects occur when calling the builder
- no Worker/OpenClaw/Hermes/Google Sheets/queue/secrets involvement

## 9. Closeout Acceptance Criteria

The v0.8.3 Dashboard display series can be considered closeout-ready only if:

- v0.8.3-D remains pushed and clean
- the regression suite remains PASS
- a stable v0.8.3-F validator can run post-push without relying on uncommitted diff output
- Dashboard display remains GET-only/read-only/synthetic local-only
- no execution or dispatch control exists anywhere in the Dashboard
- the v0.8.3-B builder remains unchanged
- `patches/` remains untracked
- no tag is created unless separately authorized

## 10. Non-goals

- no new Dashboard feature
- no Dashboard route change in this phase
- no template change in this phase
- no CSS change in this phase
- no v0.8.3-D validator fix in this phase
- no Worker runtime
- no Worker loop
- no queue read/write
- no execution
- no dispatch
- no OpenClaw
- no Hermes
- no Google Sheets
- no secrets
- no v0.8.3-F work

## 11. Exact Future v0.8.3-F Authorization Phrase

Only the following exact phrase, given verbatim by the Owner, may authorize a future
v0.8.3-F implementation round. Paraphrases, general approval, readiness PASS, Owner Review
PASS, commit approval, or push approval do not authorize v0.8.3-F.

批准實作 v0.8.3-F — Worker Dry-run Preview Dashboard Display Validation Hardening Implementation，僅允許新增或調整 validation hardening artifacts，以穩定驗證已完成的 v0.8.3-D `/dashboard/system` Worker dry-run preview read-only display 是否維持 GET-only、read-only、synthetic local-only，且 v0.8.3-B Worker dry-run preview model 僅作為顯示用途；不得修改 Dashboard route，不得新增 POST，不得新增 button/form/action URL，不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

v0.8.3-F is not started by v0.8.3-E.

## 12. v0.8.3-E Acceptance Criteria

- v0.8.3-E plan doc exists
- v0.8.3-E readiness script exists
- v0.8.3-E readiness PASSes
- no existing tracked file is modified
- `app/main.py` is untouched
- `templates/system.html` is untouched
- `static/dashboard.css` is untouched
- the v0.8.3-D validation script is untouched
- the v0.8.3-B builder is untouched
- no Worker/OpenClaw/Hermes/Google Sheets is touched
- no queue is read or written
- no POST / no execution / no dispatch occurs
- a full Owner Review diff is produced
