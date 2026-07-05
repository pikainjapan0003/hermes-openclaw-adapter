# Hermes × OpenClaw v0.8.5-C
# Worker → Mock Gateway Dry-run

## 0. Status

- Phase: v0.8.5-C
- Type: local-only / mock-only / dry-run-only helper implementation
- Base commit: `218e98c4bc89ee6508611ae860a1a021b45d0bcf`
- Latest commit message: `feat: add v0.8.5 OpenClaw mock gateway helper`
- Implementation status: HELPER IMPLEMENTED, LOCAL-ONLY, MOCK-ONLY, DRY-RUN-ONLY
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- `CLAUDE.md` status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
- Worker loop status: NOT STARTED
- Worker dispatch status: NOT DISPATCHED
- Real OpenClaw status: NOT CALLED
- Hermes status: NOT CONNECTED / NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ / NOT WRITTEN
- Audit trail status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Secrets status: NOT READ
- Network status: NOT USED
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.8.5-D status: NOT STARTED

## 1. Purpose / Positioning

v0.8.5-C builds a synthetic, local-only, mock-only, dry-run-only bridge from a Worker's
perspective to the v0.8.5-B mock gateway helper. It takes an OpenClaw Command Envelope
(as shaped by v0.8.5-A), forwards it to the local `build_mock_openclaw_response()`
helper, and returns a synthetic local-only Worker dry-run result — without ever starting
a real Worker, running a Worker loop, dispatching a real task, calling real OpenClaw, or
producing any external side effect.

- Worker to mock gateway dry-run is not Worker execution.
- Worker to mock gateway dry-run is not Worker dispatch.
- Mock gateway call is not real OpenClaw call.
- Mock gateway response is not actual execution result.
- Dry-run result is not audit trail persistence.
- Command envelope validation is not execution permission.
- External side effects remain forbidden by default.

v0.8.5-C is not a Worker loop. v0.8.5-C is not Worker dispatch. v0.8.5-C is not a real
OpenClaw call. v0.8.5-C is not a production gateway. v0.8.5-C is not a queue write.
v0.8.5-C is not an audit trail write. v0.8.5-C is not a Dashboard control.

## 2. How v0.8.5-C Uses the v0.8.5-A Command Envelope

The public function `run_worker_to_mock_gateway_dry_run(command_envelope: dict) -> dict`
takes a plain dict/mapping matching the v0.8.5-A Command Envelope shape (`command_id`,
`task_id`, `tool_target`, `requested_action`, `risk_level`, `approval_snapshot`,
`execution_mode`, `dry_run`, `mock_only`, `external_touchpoints`, `rollback_plan`,
`external_side_effects_allowed`). It is a pure function: it does not mutate the input,
does not read any file, does not open a network connection, and does not call any other
subsystem beyond the local v0.8.5-B helper.

## 3. How v0.8.5-C Calls the v0.8.5-B Mock Gateway Helper

Before calling the gateway, v0.8.5-C first confirms the envelope's own safety flags
(`mock_only = true`, `dry_run = true`, `external_side_effects_allowed = false`,
`dispatch_allowed = false`, `worker_allowed = false`, `openclaw_allowed = false`; fields
absent from the envelope are treated as their safe default of `false`). Only if this
layer's own check passes does it load and call the local
`app/mock_openclaw_gateway.build_mock_openclaw_response()` function directly (via a
same-directory dynamic file load, not a package-level import), forwarding the same
envelope unchanged. The gateway's own `accepted` / `rejection_reason` /
`rejection_details` are reflected back into the dry-run result exactly as returned.

## 4. Response Shape

```
{
  "source": "synthetic_local_only",
  "worker_dry_run": true,
  "worker_loop_started": false,
  "worker_dispatched": false,
  "mock_gateway_called": true | false,
  "real_openclaw_called": false,
  "external_side_effects_performed": false,
  "queue_written": false,
  "audit_trail_written": false,
  "dashboard_control_added": false,
  "accepted": true | false,
  "rejection_reason": null | "<reason>",
  "rejection_details": [],
  "gateway_response": null | { ...v0.8.5-B mock gateway response... }
}
```

## 5. Rejection Behavior

- If the envelope's own safety flags are unsafe (per §3), v0.8.5-C returns a rejection
  result with `mock_gateway_called = false` and `gateway_response = null` — the local
  mock gateway is never called in this case.
- If the envelope's own safety flags pass, but the underlying v0.8.5-B gateway itself
  rejects the envelope (e.g. a required field is missing), v0.8.5-C returns
  `mock_gateway_called = true`, `accepted = false`, and reflects the gateway's own
  `rejection_reason` / `rejection_details`.
- A non-mapping input returns a rejection result with
  `rejection_reason = "command_envelope must be a mapping"`.
- Every result, accepted or rejected, always carries the same fixed safety fields:
  `source`, `worker_dry_run`, `worker_loop_started`, `worker_dispatched`,
  `real_openclaw_called`, `external_side_effects_performed`, `queue_written`,
  `audit_trail_written`, `dashboard_control_added`.

## 6. What v0.8.5-C Does Not Do

- v0.8.5-C does not start a real Worker.
- v0.8.5-C does not start a Worker loop.
- v0.8.5-C does not dispatch a Worker task.
- v0.8.5-C does not call real OpenClaw.
- v0.8.5-C does not call Hermes.
- v0.8.5-C does not touch Google Sheets.
- v0.8.5-C does not read or write the real queue DB.
- v0.8.5-C does not write the audit trail.
- v0.8.5-C does not add a Dashboard control.
- v0.8.5-C does not add a route, endpoint, POST, or webhook.
- v0.8.5-C does not perform a network call.
- v0.8.5-C does not execute a subprocess or shell command.
- v0.8.5-C does not read secrets.
- v0.8.5-C does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.8.5-C does not modify `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, or `CLAUDE.md`.
- v0.8.5-C does not start v0.8.5-D.

## 7. v0.8.5-C Completion Criteria

- `docs/HERMES_OPENCLAW_WORKER_MOCK_GATEWAY_DRY_RUN_V0_8_5_C.md` exists (this document).
- `app/worker_mock_gateway_dry_run.py` exists and is local-only, mock-only,
  dry-run-only, deterministic, side-effect-free.
- `scripts/check_hermes_openclaw_worker_mock_gateway_dry_run_v0_8_5_c.py` exists and
  PASSes.
- The helper imports no network client, no OpenClaw SDK, no `app.main`, and performs no
  subprocess or shell execution.
- The helper enforces the mandatory safety flags in §3 before calling the v0.8.5-B
  gateway, and returns a rejection result when they are not satisfied.
- No existing tracked file is modified: `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, `CLAUDE.md` all remain untouched.
- No route, endpoint, POST, form, button, or action URL is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.8.5-D work is started.

## 8. Handoff

Future phase:
v0.8.5-D — Dashboard Mock Result View

v0.8.5-D is not started by v0.8.5-C.
