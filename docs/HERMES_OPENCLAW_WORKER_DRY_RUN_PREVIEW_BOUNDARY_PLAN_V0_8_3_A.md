# Hermes × OpenClaw v0.8.3-A
# Worker Dry-run Preview Boundary Plan

## 0. Status

- Phase: v0.8.3-A
- Type: plan-only / boundary plan
- Base commit: 706ad9c5eac0db37ab71f033c160effc71cfc7ba
- Previous phase: v0.8.2-F = DONE / PUSHED / CLOSED
- v0.8.2 Dashboard read-only preview validation series = CLOSED
- Implementation status: NOT IMPLEMENTED
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- OpenClaw status: NOT CONNECTED
- Hermes status: NOT CONNECTED
- Google Sheets status: DISABLED
- v0.8.3-B status: NOT STARTED

This document is plan-only. It creates a boundary plan and a readiness check design for a possible
future Worker dry-run preview. It does not implement anything. It does not start a Worker. It does not
call OpenClaw. It does not connect Hermes. It does not read or write Google Sheets.

## 1. Purpose

v0.8.3-A exists to:

- regulate what a future "Worker dry-run preview" is allowed to mean before any implementation round
  touches it;
- define, in plain terms, what a dry-run preview is and is not;
- propose a synthetic local-only dry-run input/output contract for future rounds to implement against,
  without implementing it now;
- restate that no Worker may run, no OpenClaw call may happen, no Hermes connection may happen, no
  Google Sheets read/write may happen, no real queue DB may be read, no POST may happen, and no
  execute/dispatch/send control may be added in this round or by simply reading this document;
- define the exact phrase required to authorize a future v0.8.3-B implementation round.

v0.8.3-A itself does not implement anything described in this document. Everything past Section 4 is a
proposal for a future, separately authorized round.

## 2. Definition: Worker Dry-run Preview

A Worker dry-run preview is a **preview-only planning surface**. If ever implemented under a future
separately authorized round, it:

- may describe what a future Worker would inspect, given a synthetic local-only task;
- may define a synthetic local-only dry-run input contract (Section 4);
- may define expected read-only output fields for that contract;
- may be rendered, if a future round separately authorizes a display, as a read-only, non-interactive
  preview block, similar in spirit to the v0.8.2 Dashboard local mock preview.

A Worker dry-run preview is **not**:

- a Worker loop;
- a Worker that dispatches tasks;
- a call to OpenClaw;
- a call to Hermes;
- a write to queue state (real or otherwise);
- a mutation of any file, database, Google Sheet, remote API, or other external system;
- an executor of any kind.

## 3. Inherited v0.8.2 Baseline

- Latest baseline HEAD = origin/master = 706ad9c5eac0db37ab71f033c160effc71cfc7ba
- v0.8.2-A through v0.8.2-F are each DONE / PUSHED / CLOSED
- The v0.8.2 Dashboard read-only preview validation series is CLOSED
- Dashboard preview (`/dashboard/system`) remains GET-only / read-only / synthetic local-only, backed by
  `build_dashboard_preview_model()` from the v0.8.1-V adapter
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py` (E)
  remains the preferred Dashboard read-only preview content/safety-boundary gate, stable across Owner
  Review / post-commit / post-push phases
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py`
  (D) and `scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py`
  (F) readiness scripts are Owner Review phase-only observations, not standing regression gates
- Current safety boundary carried forward unchanged: GET-only, read-only, synthetic local-only,
  permission flags false, disabled runtime badges visible, no POST, no button/form/action URL, no
  Worker/OpenClaw/Hermes/Google Sheets, no secrets, no real queue DB, no Remote Blackboard API runtime

## 4. Proposed Future Worker Dry-run Preview Contract

The following is a **proposal only**, for a future separately authorized v0.8.3-B (or later) round to
implement. v0.8.3-A does not implement any of it.

- dry_run_id
- source = synthetic_local_only
- task_title
- task_summary
- source_role
- target_role
- proposed_worker_action
- dry_run_status
- execution_permission = false
- dispatch_permission = false
- external_side_effects_permission = false
- worker_started = false
- openclaw_called = false
- hermes_called = false
- google_sheets_enabled = false
- real_queue_db_read = false
- post_enabled = false
- secrets_read = false

All boolean fields above are proposed to be hardcoded `false` for any future dry-run preview object —
never derived from live Worker/OpenClaw/Hermes/Google Sheets/queue state, since none of those systems
may be touched by a dry-run preview.

## 5. Proposed Future Display / Review Rules

The following is also a **proposal only**, describing constraints a future display implementation would
need to satisfy. v0.8.3-A does not change any UI, route, template, or CSS.

- Future display, if implemented, must be read-only.
- It must show disabled runtime badges (Worker OFF, OpenClaw NOT CONNECTED, Hermes NOT CONNECTED,
  Google Sheets DISABLED).
- It must show all permission flags as false.
- It must show an Owner Review required notice.
- It must not include a button, form, action_url, post_url, webhook_url, endpoint_url, execute_url,
  dispatch_url, or send_url.
- It must not POST.
- It must not create any external side effect.

## 6. Future Implementation Candidate Scope

The following file types are **candidates a future v0.8.3-B round might introduce** — v0.8.3-A does not
create any of them:

- possibly one synthetic dry-run preview contract doc;
- possibly one read-only dry-run preview builder module (synthetic local-only input only, no adapter to
  any real system);
- possibly one validation/readiness script for that builder;
- possibly one Dashboard read-only display plan for the dry-run preview, if separately authorized as its
  own round following the same plan-then-implement cadence used in v0.8.1/v0.8.2.

v0.8.3-A creates none of these implementation artifacts. It creates only the two files listed in
Section 8 below (this doc and its own readiness script).

## 7. Forbidden Future Scope Unless Separately Authorized

The following remain forbidden for any future round unless a future Owner explicitly and separately
authorizes them with their own exact authorization phrase:

- no true Worker
- no Worker loop
- no Worker queue consumption
- no OpenClaw call
- no Hermes activation/readback
- no Google Sheets read/write
- no real queue DB read/write
- no POST
- no execute/dispatch/send controls
- no secrets
- no webhook/endpoint/connector
- no production/shared DB
- no Remote Blackboard API runtime

## 8. This Round's Files

v0.8.3-A creates exactly two files:

- `docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_PLAN_V0_8_3_A.md` (this document)
- `scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py` (its readiness script)

v0.8.3-A modifies no existing tracked file. It does not touch `app/main.py`, `templates/system.html`,
`static/dashboard.css`, or any prior v0.8.1/v0.8.2 doc or script.

## 9. Required Validation Gates Before Any Future Implementation

Any future v0.8.3-B (or later) implementation round must, at minimum, keep passing:

- `python -m compileall scripts`
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py` (E) —
  the preferred Dashboard content/safety-boundary gate
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py` (C)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py` (v0.8.2-A)
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py` (B)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py` (V)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py` (W)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py` (Z)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py` (Y)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py` (X)
- this document's own readiness script,
  `scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py`

E may fail its untracked-file allowlist check during a future round's own Owner Review phase solely
because that round's new untracked artifacts are not yet in E's allowlist — this is a scope/phase
warning, not a content or safety-boundary failure, per the nuance already recorded in the v0.8.2-F
closeout doc. E's content/safety-boundary checks themselves must remain passing.

D and F readiness scripts remain Owner Review phase-limited observations only and are not standing
regression gates.

## 10. Exact Future v0.8.3-B Authorization Phrase

The following exact phrase, and only this exact phrase, may be used by Owner in the future to authorize
a v0.8.3-B implementation round. Paraphrases, general approval, readiness PASS, or Owner Review PASS do
not authorize v0.8.3-B. v0.8.3-B is not started by v0.8.3-A.

批准實作 v0.8.3-B — Worker Dry-run Preview Boundary Implementation，僅允許新增 Worker dry-run preview boundary artifacts 與 read-only validation artifacts，用 synthetic local-only preview input 描述未來 Worker 可能檢查的任務，不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得 POST，不得新增 execute/dispatch/send controls，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 11. Acceptance Criteria For v0.8.3-A

- v0.8.3-A boundary plan doc exists
- v0.8.3-A readiness script exists
- readiness script PASSes
- no existing tracked file is modified
- no Worker implementation happens
- no OpenClaw call happens
- no Hermes activation happens
- no Google Sheets read/write happens
- no real queue DB read happens
- no POST happens
- no execute/dispatch/send control is added
- no commit, no push, no tag happens in this round
- a full Owner Review diff is produced for Owner to review before any commit

## 12. Non-goals

v0.8.3-A explicitly does NOT:

- implement anything;
- start a Worker;
- call OpenClaw;
- activate or connect Hermes;
- read or write Google Sheets;
- read the real queue DB;
- change the Dashboard UI, any route, any template, or any CSS;
- begin v0.8.3-B work of any kind.
