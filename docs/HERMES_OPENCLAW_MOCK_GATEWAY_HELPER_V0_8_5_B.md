# Hermes × OpenClaw v0.8.5-B
# OpenClaw Mock Gateway Helper

## 0. Status

- Phase: v0.8.5-B
- Type: local-only / mock-only helper implementation
- Base commit: `737d361a8b60cb74b799cb479916124a86895c86`
- Latest commit message: `docs: add Claude Code loop format contract`
- Note: `737d361` is a local, Owner-approved, not-yet-pushed commit on top of pushed
  `564827aa5801cf6bbc03e4c51fd3983eb31e5735` (`docs: add v0.8.5 OpenClaw command
  envelope plan`); this round does not push either commit.
- Implementation status: HELPER IMPLEMENTED, LOCAL-ONLY, MOCK-ONLY
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Worker status: OFF / NOT STARTED
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
- v0.8.5-C status: NOT STARTED

## 1. Purpose / Positioning

v0.8.5-B builds a synthetic, local-only, mock-only OpenClaw gateway helper. It receives
an OpenClaw Command Envelope (as shaped by v0.8.5-A) and returns a synthetic local-only
mock response describing what a *future* real gateway might acknowledge — without ever
calling real OpenClaw, dispatching Worker, or producing any external side effect.

- v0.8.5-B is not a production gateway.
- v0.8.5-B is not a route, endpoint, or webhook. It is a plain Python helper module
  (`app/mock_openclaw_gateway.py`), imported directly, not served over HTTP.
- Mock gateway helper is not production gateway.
- Mock gateway helper is not an OpenClaw call.
- Mock gateway helper is not Worker dispatch.
- Mock gateway response is not actual execution result.
- Mock gateway response is not audit trail persistence.
- Command envelope validation is not execution permission.
- External side effects remain forbidden by default.

## 2. How the Helper Receives a Command Envelope

The public function `build_mock_openclaw_response(command_envelope: dict) -> dict` takes
a plain dict/mapping matching the v0.8.5-A Command Envelope shape (`command_id`,
`task_id`, `tool_target`, `requested_action`, `risk_level`, `approval_snapshot`,
`execution_mode`, `dry_run`, `mock_only`, `external_touchpoints`, `rollback_plan`,
`external_side_effects_allowed`). It is a pure function: it does not mutate the input,
does not read any file, does not open a network connection, and does not call any other
subsystem.

## 3. How the Helper Returns a Mock Response

If the envelope is valid and safe (see §4), the helper returns a synthetic local-only
mock response dict containing `accepted: true`, an echo of `command_id` / `task_id` /
`tool_target`, and a human-readable `mock_response_summary` stating plainly that this is
a synthetic acknowledgement, not a real execution. If the envelope is missing required
fields or fails a safety check, the helper returns a rejection response
(`accepted: false`, `rejection_reason`, `rejection_details`) instead of raising — this
lets a caller safely inspect the outcome without a crash.

Every response, accepted or rejected, always carries the same fixed safety fields:

- `response_source = synthetic_local_only`
- `mock_gateway = true`
- `production_gateway = false`
- `real_openclaw_called = false`
- `worker_dispatched = false`
- `external_side_effects_performed = false`
- `queue_written = false`
- `audit_trail_written = false`

## 4. Mandatory Safety Flags

Before building an accepted mock response, the helper forces confirmation that:

- `mock_only = true`
- `dry_run = true`
- `external_side_effects_allowed = false`
- `dispatch_allowed = false`
- `worker_allowed = false`
- `openclaw_allowed = false`

Fields not present on the input envelope (`dispatch_allowed`, `worker_allowed`,
`openclaw_allowed` are optional, since the v0.8.5-A envelope shape does not mandate
them) are treated as their safe default of `false`; a present value other than `false`
still fails validation. If any of these flags is unsafe, the helper returns a rejection
response rather than a mock response.

## 5. Rejection Behavior

- Missing any required envelope field → rejection response with
  `rejection_reason = "missing required command envelope fields"` and one
  `rejection_details` entry per missing field.
- Any unsafe safety flag → rejection response with
  `rejection_reason = "unsafe command envelope flags"` and one `rejection_details`
  entry per violated flag.
- A non-mapping input → rejection response with
  `rejection_reason = "command_envelope must be a mapping"`.
- Rejection responses still carry the same fixed `mock_gateway` / `production_gateway`
  / `real_openclaw_called` / `worker_dispatched` / `external_side_effects_performed` /
  `queue_written` / `audit_trail_written` safety fields as accepted responses.

## 6. Response Shape

```
{
  "response_source": "synthetic_local_only",
  "mock_gateway": true,
  "production_gateway": false,
  "real_openclaw_called": false,
  "worker_dispatched": false,
  "external_side_effects_performed": false,
  "queue_written": false,
  "audit_trail_written": false,
  "accepted": true | false,
  "rejection_reason": null | "<reason>",
  "rejection_details": [],
  "command_id": "<echoed from envelope, only when accepted>",
  "task_id": "<echoed from envelope, only when accepted>",
  "tool_target": "<echoed from envelope, only when accepted>",
  "mock_response_summary": "<human-readable synthetic acknowledgement, only when accepted>"
}
```

## 7. What v0.8.5-B Does Not Do

- v0.8.5-B does not call real OpenClaw.
- v0.8.5-B does not call Worker.
- v0.8.5-B does not call Hermes.
- v0.8.5-B does not touch Google Sheets.
- v0.8.5-B does not read or write the real queue DB.
- v0.8.5-B does not write the audit trail.
- v0.8.5-B does not add a Dashboard control.
- v0.8.5-B does not add a route, endpoint, POST, or webhook.
- v0.8.5-B does not perform a network call.
- v0.8.5-B does not execute a subprocess or shell command.
- v0.8.5-B does not read secrets.
- v0.8.5-B does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.8.5-B does not modify `app/main.py`, `templates/system.html`, or
  `static/dashboard.css`.
- v0.8.5-B does not start v0.8.5-C.

## 8. v0.8.5-B Completion Criteria

- `docs/HERMES_OPENCLAW_MOCK_GATEWAY_HELPER_V0_8_5_B.md` exists (this document).
- `app/mock_openclaw_gateway.py` exists and is local-only, mock-only, dry-run-only,
  deterministic, side-effect-free.
- `scripts/check_hermes_openclaw_mock_gateway_helper_v0_8_5_b.py` exists and PASSes.
- The helper imports no network client, no OpenClaw SDK, no `app.main`, and performs no
  subprocess or shell execution.
- The helper enforces the mandatory safety flags in §4 and returns a rejection response
  when they are not satisfied.
- No existing tracked file is modified: `app/main.py`, `templates/system.html`,
  `static/dashboard.css` all remain untouched.
- No route, endpoint, POST, form, button, or action URL is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.8.5-C work is started.

## 9. Handoff

Future phase:
v0.8.5-C — Worker → Mock Gateway Dry-run

v0.8.5-C is not started by v0.8.5-B.
