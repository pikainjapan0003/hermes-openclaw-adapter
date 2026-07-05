# Hermes × OpenClaw v0.9-E
# Hermes Reads Result Message Mock

## 0. Status

- Phase: v0.9-E
- Type: local-only / mock-only / deterministic readback implementation
- Base commit: `de2f4a5ef9ac3c94d90e22d2de888a8f85f6b536`
- Latest commit message: `feat: add v0.9 dashboard Hermes advice panel`
- Implementation status: MOCK IMPLEMENTED, LOCAL-ONLY, MOCK-ONLY, READBACK-ONLY
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- `CLAUDE.md` status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Hermes runtime status: NOT ACTIVATED
- Real Hermes status: NOT CALLED
- Hermes memory status: NOT READ
- Hermes tool call status: NOT CALLED
- Blackboard write status: NOT WRITTEN
- Follow-up task auto-creation status: NOT CREATED
- Worker status: OFF / NOT STARTED
- Real OpenClaw status: NOT CALLED
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
- v0.9-F status: NOT STARTED

## 1. Purpose / Positioning

v0.9-E builds a synthetic, local-only, mock-only, deterministic Hermes Reads Result
Message Mock. It takes a synthetic mock result message (shaped like the output of the
v0.8.5-C Worker → Mock Gateway Dry-run), verifies it is itself a trustworthy synthetic
mock result, forwards it to the local v0.9-C `build_mock_hermes_advice` generator, and
wraps the resulting advice into a Hermes result readback advice — without ever
activating a Hermes runtime, calling real Hermes, reading Hermes memory, calling a
Hermes tool, writing the Blackboard, writing the queue, writing the audit trail,
automatically creating a follow-up task, dispatching Worker, calling real OpenClaw, or
producing any external side effect.

- Hermes result readback mock is not Hermes activation.
- Hermes result readback mock is not real Hermes readback.
- Hermes result readback mock does not read Hermes memory.
- Hermes result readback mock does not call Hermes tools.
- Hermes readback is not Blackboard write.
- Hermes readback is not Owner approval.
- Hermes readback is not automatic follow-up execution.
- Hermes readback is not automatic follow-up task creation.
- Hermes readback is not Worker dispatch.
- Hermes readback is not OpenClaw call.
- Hermes cannot bypass Owner Review.
- Hermes cannot bypass Blackboard Activation Policy.
- External side effects remain forbidden by default.

v0.9-E is not a Dashboard control. It is a plain Python module
(`app/hermes_result_readback_mock.py`), imported directly, not served over HTTP.

## 2. How the Readback Mock Uses a Synthetic Result Message

The public function `build_hermes_result_readback_advice(result_message: dict) -> dict`
takes a plain dict/mapping containing `result_id`, `task_id`, `status`, `source`,
`mock_gateway`, `worker_dry_run`, `real_openclaw_called`, `worker_dispatched`,
`external_side_effects_performed`, `queue_written`, and `audit_trail_written`. Before
doing anything else, it verifies the result message is itself a trustworthy synthetic
mock result (§4). If it is not, the mock returns a rejection readback without ever
calling the v0.9-C generator.

## 3. How the Readback Mock Uses the v0.9-C Mock Hermes Generator

If the result message passes its own safety check, the readback mock wraps it into a
synthetic source context (`task_id`, `source_message_ids`, `source_result_ids`,
`source_decision_ids`, `strategy_summary`, `recommended_action`, `risk_assessment`,
`missing_information`, `owner_question`, `suggested_next_step`, `confidence`) and loads
the local `app/mock_hermes_generator.build_mock_hermes_advice()` function directly (via
a same-directory dynamic file load, not a package-level import), forwarding the
constructed context. If the underlying advice is rejected, the readback mock reflects
the same `rejection_reason` / `rejection_details`. If accepted, it wraps the advice's
fields into a readback advice dict and adds `readback_id` (derived deterministically
from `result_id`: `f"readback-{result_id}"`).

## 4. Result Message Safety Check

A result message is only treated as a trustworthy synthetic mock result if:

```text
source = synthetic_local_only
mock_gateway = true
worker_dry_run = true
real_openclaw_called = false
worker_dispatched = false
external_side_effects_performed = false
queue_written = false
audit_trail_written = false
```

A result message missing any required field, or with `source != synthetic_local_only`,
`mock_gateway != true`, `worker_dry_run != true`, or any of `real_openclaw_called` /
`worker_dispatched` / `external_side_effects_performed` / `queue_written` /
`audit_trail_written` set to `true`, is fail-safe rejected — the v0.9-C generator is
never called.

## 5. Readback Advice Shape

```
{
  "readback_id": "<derived from result_id>",
  "advice_id": "<from v0.9-C advice>",
  "suggestion_id": "<from v0.9-B suggestion>",
  "task_id": "<echoed from result_message>",
  "source_result_id": "<echoed from result_message.result_id>",
  "source_result_status": "<echoed from result_message.status>",
  "readback_source": "synthetic_local_only",
  "accepted": true | false,
  "rejection_reason": null | "<reason>",
  "rejection_details": [],
  "readback_summary": "<human-readable summary>",
  "strategy_summary": "<human-readable summary>",
  "recommended_action": "<human-readable description, never an instruction actually sent anywhere>",
  "risk_assessment": "<human-readable risk classification>",
  "missing_information": "<human-readable description>",
  "owner_question": "<a question for the Owner, if any>",
  "suggested_next_step": "<human-readable description only>",
  "confidence": "<plan-only classification, e.g. low/medium/high>",
  "mock_hermes": true,
  "real_hermes_called": false,
  "hermes_runtime_activated": false,
  "hermes_memory_read": false,
  "hermes_tool_called": false,
  "result_readback_only": true,
  "must_not_execute": true,
  "requires_owner_confirmation": true,
  "blackboard_write_allowed": false,
  "queue_write_allowed": false,
  "audit_trail_write_allowed": false,
  "follow_up_task_auto_create_allowed": false,
  "worker_dispatch_allowed": false,
  "openclaw_call_allowed": false,
  "external_side_effects_allowed": false
}
```

## 6. Mandatory Safety Values

```text
mock_hermes = true
real_hermes_called = false
hermes_runtime_activated = false
hermes_memory_read = false
hermes_tool_called = false
result_readback_only = true
must_not_execute = true
requires_owner_confirmation = true
blackboard_write_allowed = false
queue_write_allowed = false
audit_trail_write_allowed = false
follow_up_task_auto_create_allowed = false
worker_dispatch_allowed = false
openclaw_call_allowed = false
external_side_effects_allowed = false
```

These fifteen fields are never sourced from the result message or from the underlying
advice. `build_hermes_result_readback_advice` always sets them itself, on both accepted
and rejected readback advice. `validate_hermes_result_readback_advice` flags any
readback advice where one of them holds a different value as a violation.

## 7. Unsafe Result Message Rejection Behavior

- A non-mapping `result_message` → rejection readback with
  `rejection_reason = "result_message must be a mapping"`.
- Missing any required result message field → rejection readback with
  `rejection_reason = "missing required result message fields"`.
- `source != synthetic_local_only`, `mock_gateway != true`, `worker_dry_run != true`, or
  any of `real_openclaw_called` / `worker_dispatched` /
  `external_side_effects_performed` / `queue_written` / `audit_trail_written` set to
  `true` → rejection readback with `rejection_reason = "unsafe result message flags"`,
  one `rejection_details` entry per violated flag — the v0.9-C generator is never
  called. All rejection readbacks still carry the fifteen forced-safe fields.

## 8. Unsafe Readback Advice Rejection Behavior

- A non-mapping `readback_advice` passed to `validate_hermes_result_readback_advice` →
  `{"valid": False, "violations": ["readback_advice must be a mapping"]}`.
- A readback advice dict (constructed elsewhere) that sets `must_not_execute = false`,
  `requires_owner_confirmation = false`, `blackboard_write_allowed = true`,
  `queue_write_allowed = true`, `audit_trail_write_allowed = true`,
  `follow_up_task_auto_create_allowed = true`, `worker_dispatch_allowed = true`,
  `openclaw_call_allowed = true`, `external_side_effects_allowed = true`,
  `real_hermes_called = true`, `hermes_runtime_activated = true`,
  `hermes_memory_read = true`, or `hermes_tool_called = true` is fail-safe rejected by
  `validate_hermes_result_readback_advice` (`valid: false`, one violation entry per
  unsafe field) — never executed, never raised.

## 9. What v0.9-E Does Not Do

- v0.9-E does not activate a Hermes runtime.
- v0.9-E does not call real Hermes.
- v0.9-E does not read Hermes memory.
- v0.9-E does not call a Hermes tool.
- v0.9-E does not write the Blackboard.
- v0.9-E does not read or write the real queue DB.
- v0.9-E does not write the audit trail.
- v0.9-E does not automatically create a follow-up task.
- v0.9-E does not call Worker.
- v0.9-E does not call real OpenClaw.
- v0.9-E does not touch Google Sheets.
- v0.9-E does not add a Dashboard control.
- v0.9-E does not add a route, endpoint, POST, or webhook.
- v0.9-E does not perform a network call.
- v0.9-E does not execute a subprocess or shell command.
- v0.9-E does not read secrets.
- v0.9-E does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.9-E does not modify `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, or `CLAUDE.md`.
- v0.9-E does not start v0.9-F.

## 10. Safety Sentences

Hermes result readback mock is not Hermes activation.
Hermes result readback mock is not real Hermes readback.
Hermes result readback mock does not read Hermes memory.
Hermes result readback mock does not call Hermes tools.
Hermes readback is not Blackboard write.
Hermes readback is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes readback is not automatic follow-up task creation.
Hermes readback is not Worker dispatch.
Hermes readback is not OpenClaw call.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

## 11. v0.9-E Completion Criteria

- `docs/HERMES_RESULT_READBACK_MOCK_V0_9_E.md` exists (this document).
- `app/hermes_result_readback_mock.py` exists and is local-only, mock-only,
  advisory-only, readback-only, deterministic, side-effect-free.
- `scripts/check_hermes_result_readback_mock_v0_9_e.py` exists and PASSes.
- The mock imports no network client, no Hermes runtime, no `app.main`, and performs no
  subprocess or shell execution.
- The mock uses the v0.9-C `mock_hermes_generator` to derive its advice.
- The mock enforces the fifteen mandatory safety values and fail-safe rejects both
  unsafe result messages and unsafe readback advice.
- No existing tracked file is modified: `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, `CLAUDE.md` all remain untouched.
- No route, endpoint, POST, form, button, or action URL is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-F work is started.

## 12. Handoff

Future phase:
v0.9-F — (not yet defined; requires separate Owner authorization)

v0.9-F is not started by v0.9-E.
