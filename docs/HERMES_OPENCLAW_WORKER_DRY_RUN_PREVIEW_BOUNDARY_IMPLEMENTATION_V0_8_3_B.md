# Hermes × OpenClaw v0.8.3-B
# Worker Dry-run Preview Boundary Implementation

## 0. Status

- Phase: v0.8.3-B
- Type: synthetic local-only boundary implementation
- Base commit: b9b9afd610d174aca3a9b54d978000399e46622c
- Previous phase: v0.8.3-A = DONE / PUSHED / CLOSED
- Implementation status: OWNER REVIEW
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT IMPLEMENTED
- OpenClaw status: NOT CONNECTED / NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Queue status: REAL QUEUE DB NOT READ / NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- v0.8.3-C status: NOT STARTED

v0.8.3-B is a synthetic local-only boundary implementation. It is **not** a Worker runtime
implementation. It does not start a Worker, does not run a Worker loop, does not call OpenClaw, does not
connect Hermes, does not read or write Google Sheets, does not read the real queue DB, and does not POST
anything anywhere.

## 1. Purpose

v0.8.3-B implements, within the boundary defined by v0.8.3-A, a standalone artifact set that:

- describes a single synthetic local-only "dry-run" task via a fixture, so future rounds have a concrete
  example of what a future Worker dry-run preview object could look like;
- builds a read-only preview model from that fixture, using a standalone module with no dependency on
  the Dashboard, the Adapter app, the Worker, OpenClaw, Hermes, Google Sheets, or the real queue;
- validates that the fixture and the built model never assert an execution, dispatch, or external-side-
  effect permission as true;
- defines the exact phrase required to authorize a future v0.8.3-C round (Dashboard read-only display of
  this preview model).

Everything in this round operates on the new synthetic fixture only. It never touches the v0.8.1 fixture
(`fixtures/local_mock_data/hermes_openclaw_local_mock_messages_v0_8_1.json`), the Dashboard, or any other
existing tracked artifact.

## 2. Implemented Artifacts

v0.8.3-B introduces exactly four new files:

- `docs/HERMES_OPENCLAW_WORKER_DRY_RUN_PREVIEW_BOUNDARY_IMPLEMENTATION_V0_8_3_B.md` (this document)
- `fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json` (synthetic local-only
  dry-run input fixture)
- `scripts/worker_dry_run_preview_boundary_v0_8_3_b.py` (standalone read-only builder)
- `scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py` (this
  round's readiness/validation script)

No existing tracked file is modified.

## 3. Synthetic Local-only Fixture Contract

The fixture at `fixtures/local_mock_data/hermes_openclaw_worker_dry_run_preview_v0_8_3_b.json` contains:

- `schema_version`
- `dry_run_id`
- `source` = `synthetic_local_only`
- `task_title`
- `task_summary`
- `source_role`
- `target_role`
- `proposed_worker_action`
- `dry_run_status` = `preview_only_not_executed`
- `owner_review_required` = `true`
- `execution_permission` = `false`
- `dispatch_permission` = `false`
- `external_side_effects_permission` = `false`
- `worker_started` = `false`
- `worker_loop_started` = `false`
- `openclaw_called` = `false`
- `hermes_called` = `false`
- `google_sheets_enabled` = `false`
- `real_queue_db_read` = `false`
- `queue_written` = `false`
- `post_enabled` = `false`
- `secrets_read` = `false`
- `webhook_created` = `false`
- `endpoint_created` = `false`
- `connector_created` = `false`
- `production_db_created` = `false`
- `remote_blackboard_api_runtime_created` = `false`

Every permission and runtime-state field is hardcoded `false` in the fixture itself — it is data, not a
live status read from any real system.

## 4. Standalone Builder Contract

`scripts/worker_dry_run_preview_boundary_v0_8_3_b.py` exposes
`build_worker_dry_run_preview_model(input_path: Path | None = None) -> dict[str, object]`, which:

- reads only the new synthetic local-only fixture (defaults to the path above; standard library `json`
  and `pathlib` only);
- validates that `source == "synthetic_local_only"`, `dry_run_status == "preview_only_not_executed"`,
  `owner_review_required is True`, all permission flags are `False`, all runtime-state flags are `False`,
  and no forbidden control-URL keys are present;
- raises `ValueError` if any of those validations fail — it never silently returns an unsafe model;
- returns a read-only preview model dict with keys: `schema_version`, `dry_run_id`, `source`,
  `task_title`, `task_summary`, `source_role`, `target_role`, `proposed_worker_action`, `dry_run_status`,
  `owner_review_required`, `permissions` (nested dict: `execution_permission`, `dispatch_permission`,
  `external_side_effects_permission`), `runtime_state` (nested dict: `worker_started`,
  `worker_loop_started`, `openclaw_called`, `hermes_called`, `google_sheets_enabled`,
  `real_queue_db_read`, `queue_written`, `post_enabled`, `secrets_read`, `webhook_created`,
  `endpoint_created`, `connector_created`, `production_db_created`,
  `remote_blackboard_api_runtime_created`), `boundary_summary` (a short read-only human-readable string),
  and `review_notice` (a fixed Owner Review required string);
- imports nothing beyond the Python standard library — no `app.main`, no `QueueStore`, no Worker,
  OpenClaw, Hermes, or Google Sheets module, no `requests`/`httpx`/`socket`/`urllib`, no `subprocess`, no
  `os.environ` secret read;
- emits no side effects: no file write, no DB read/write, no network call, no POST;
- when run as `__main__`, prints the built model as JSON to stdout for local inspection only — it starts
  no server, no loop, and no runtime.

## 5. Boundary Guarantees

v0.8.3-B, and the artifacts it introduces, guarantee:

- no true Worker
- no Worker loop
- no queue consumption
- no OpenClaw call
- no Hermes activation/readback
- no Google Sheets read/write
- no reading or writing of the real queue DB
- no queue write
- no POST
- no execute/dispatch/send controls
- no secrets
- no webhook/endpoint/connector
- no production/shared DB
- no Remote Blackboard API runtime

These guarantees hold both in the fixture data and in the builder's validated output — the builder
refuses (via `ValueError`) to return a model where any of them would not hold.

## 6. What This Enables Later

If a future Owner separately authorizes it:

- v0.8.3-C could plan how to display this builder's read-only preview model on the Dashboard, using the
  same GET-only / read-only / synthetic local-only pattern already used for the v0.8.2 local mock
  preview;
- that plan would still forbid execution, dispatch, Worker startup, OpenClaw calls, Hermes activation,
  and Google Sheets access;
- no true Worker runtime is enabled by v0.8.3-B or by planning v0.8.3-C — a true Worker runtime, if ever
  built, would require its own separate, explicit Owner authorization round.

## 7. Required Validation Gates

Any future round building on v0.8.3-B must keep passing:

- this round's own readiness script,
  `scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_implementation_v0_8_3_b.py`
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

`scripts/check_hermes_openclaw_worker_dry_run_preview_boundary_plan_v0_8_3_a.py` (v0.8.3-A),
`scripts/check_hermes_openclaw_dashboard_read_only_preview_validation_closeout_handoff_plan_v0_8_2_f.py`
(F), and
`scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py` (D)
remain Owner Review phase-limited observations only, not standing regression gates.

## 8. Exact Future v0.8.3-C Authorization Phrase

The following exact phrase, and only this exact phrase, may be used by Owner in the future to authorize
v0.8.3-C planning. Paraphrases, general approval, readiness PASS, or Owner Review PASS do not authorize
v0.8.3-C. v0.8.3-C is not started by v0.8.3-B.

批准規劃 v0.8.3-C — Worker Dry-run Preview Dashboard Read-only Display Plan，僅允許規劃如何在 Dashboard 以 GET-only、read-only、synthetic local-only 方式顯示 v0.8.3-B 的 Worker dry-run preview model；不得修改 Dashboard route，不得新增 POST，不得新增 button/form/action URL，不得啟動 Worker，不得執行 Worker loop，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得寫 queue，不得讀 secrets，不得建立 webhook/endpoint/connector，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 9. Acceptance Criteria

- all four v0.8.3-B files exist
- v0.8.3-B readiness script PASSes
- fixture `source` is `synthetic_local_only`
- builder returns a read-only preview model
- all permission and runtime-state flags in both fixture and built model are `false`
- no existing tracked file is modified
- no Worker / OpenClaw / Hermes / Google Sheets is touched
- no POST / no execution / no dispatch
- a full Owner Review diff is produced for Owner to review before any commit

## 10. Non-goals

v0.8.3-B explicitly does NOT:

- integrate with the Dashboard;
- change any UI, route, template, or CSS;
- implement a true Worker runtime, executor, loop, queue consumer, or dispatcher;
- read or write the real queue DB;
- call OpenClaw;
- activate or connect Hermes;
- read or write Google Sheets;
- perform any execution or dispatch of any kind;
- start v0.8.3-C work of any kind.
