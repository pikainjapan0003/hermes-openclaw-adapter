# Hermes × OpenClaw v0.9-C
# Mock Hermes Generator

## 0. Status

- Phase: v0.9-C
- Type: local-only / mock-only / deterministic generator implementation
- Base commit: `e5a8a380b8d39f4a0a028c9bfd108af19fe6049c`
- Latest commit message: `feat: add v0.9 Hermes strategy suggestion model`
- Implementation status: GENERATOR IMPLEMENTED, LOCAL-ONLY, MOCK-ONLY, ADVISORY-ONLY
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
- v0.9-D status: NOT STARTED

## 1. Purpose / Positioning

v0.9-C builds a synthetic, local-only, mock-only, deterministic Mock Hermes Generator. It
takes a synthetic source context, forwards it to the local v0.9-B
`build_hermes_strategy_suggestion` helper, and wraps the resulting strategy suggestion
into a synthetic mock Hermes advice dict — without ever activating a Hermes runtime,
calling real Hermes, reading Hermes memory, calling a Hermes tool, writing the
Blackboard, writing the queue, writing the audit trail, or producing any external side
effect.

- Mock Hermes generator is not Hermes activation.
- Mock Hermes generator is not real Hermes.
- Mock Hermes advice is not Blackboard write.
- Mock Hermes advice is not Owner approval.
- Mock Hermes advice is not automatic follow-up execution.
- Mock Hermes advice is not Worker dispatch.
- Mock Hermes advice is not OpenClaw call.
- Mock Hermes cannot bypass Owner Review.
- Mock Hermes cannot bypass Blackboard Activation Policy.
- External side effects remain forbidden by default.

v0.9-C is not a Hermes runtime. v0.9-C is not a route, endpoint, or webhook. It is a
plain Python module (`app/mock_hermes_generator.py`), imported directly, not served over
HTTP. v0.9-C is not a Dashboard Hermes Advice Panel.

## 2. How the Generator Uses the v0.9-B Strategy Suggestion Model

The public function `build_mock_hermes_advice(source_context: dict) -> dict` takes the
same synthetic source context shape as v0.9-B (`task_id`, `source_message_ids`,
`source_result_ids`, `source_decision_ids`, `strategy_summary`, `recommended_action`,
`risk_assessment`, `missing_information`, `owner_question`, `suggested_next_step`,
`confidence`). It loads and calls the local
`app/hermes_strategy_suggestion_model.build_hermes_strategy_suggestion()` function
directly (via a same-directory dynamic file load, not a package-level import),
forwarding the same source context unchanged. If the underlying suggestion is rejected
(missing fields or a non-mapping input), the generator returns a rejection advice without
any further processing. If the suggestion is accepted, the generator wraps its fields
into a mock Hermes advice dict and adds `advice_id` (derived deterministically from
`suggestion_id`: `f"advice-{suggestion_id}"`).

## 3. Mock Hermes Advice Shape

```
{
  "advice_id": "<derived from suggestion_id>",
  "suggestion_id": "<from v0.9-B suggestion>",
  "task_id": "<echoed from source_context>",
  "source_message_ids": [...],
  "source_result_ids": [...],
  "source_decision_ids": [...],
  "advice_source": "synthetic_local_only",
  "accepted": true | false,
  "rejection_reason": null | "<reason>",
  "rejection_details": [],
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
  "must_not_execute": true,
  "requires_owner_confirmation": true,
  "blackboard_write_allowed": false,
  "queue_write_allowed": false,
  "audit_trail_write_allowed": false,
  "worker_dispatch_allowed": false,
  "openclaw_call_allowed": false,
  "external_side_effects_allowed": false
}
```

## 4. Mandatory Safety Values

```text
mock_hermes = true
real_hermes_called = false
hermes_runtime_activated = false
hermes_memory_read = false
hermes_tool_called = false
must_not_execute = true
requires_owner_confirmation = true
blackboard_write_allowed = false
queue_write_allowed = false
audit_trail_write_allowed = false
worker_dispatch_allowed = false
openclaw_call_allowed = false
external_side_effects_allowed = false
```

These thirteen fields are never sourced from caller input or from the underlying
suggestion. `build_mock_hermes_advice` always sets them itself, on both accepted and
rejected advice. `validate_mock_hermes_advice` flags any advice where one of them holds a
different value as a violation.

## 5. Unsafe Advice Rejection Behavior

- A non-mapping `source_context` → rejection advice with
  `rejection_reason = "source_context must be a mapping"`.
- A rejected underlying v0.9-B suggestion (missing required source context fields) →
  rejection advice reflecting the same `rejection_reason` / `rejection_details`, still
  carrying the thirteen forced-safe fields.
- A non-mapping `advice` passed to `validate_mock_hermes_advice` →
  `{"valid": False, "violations": ["advice must be a mapping"]}`.
- An advice dict (constructed elsewhere) that sets `must_not_execute = false`,
  `requires_owner_confirmation = false`, `blackboard_write_allowed = true`,
  `queue_write_allowed = true`, `audit_trail_write_allowed = true`,
  `worker_dispatch_allowed = true`, `openclaw_call_allowed = true`,
  `external_side_effects_allowed = true`, `real_hermes_called = true`,
  `hermes_runtime_activated = true`, `hermes_memory_read = true`, or
  `hermes_tool_called = true` is fail-safe rejected by `validate_mock_hermes_advice`
  (`valid: false`, one violation entry per unsafe field) — never executed, never raised.

## 6. What v0.9-C Does Not Do

- v0.9-C does not activate a Hermes runtime.
- v0.9-C does not call real Hermes.
- v0.9-C does not read Hermes memory.
- v0.9-C does not call a Hermes tool.
- v0.9-C does not write the Blackboard.
- v0.9-C does not read or write the real queue DB.
- v0.9-C does not write the audit trail.
- v0.9-C does not call Worker.
- v0.9-C does not call real OpenClaw.
- v0.9-C does not touch Google Sheets.
- v0.9-C does not add a Dashboard control or a Dashboard Hermes Advice Panel.
- v0.9-C does not add a route, endpoint, POST, or webhook.
- v0.9-C does not perform a network call.
- v0.9-C does not execute a subprocess or shell command.
- v0.9-C does not read secrets.
- v0.9-C does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.9-C does not modify `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, or `CLAUDE.md`.
- v0.9-C does not start v0.9-D.

## 7. Safety Sentences

Mock Hermes generator is not Hermes activation.
Mock Hermes generator is not real Hermes.
Mock Hermes advice is not Blackboard write.
Mock Hermes advice is not Owner approval.
Mock Hermes advice is not automatic follow-up execution.
Mock Hermes advice is not Worker dispatch.
Mock Hermes advice is not OpenClaw call.
Mock Hermes cannot bypass Owner Review.
Mock Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

## 8. v0.9-C Completion Criteria

- `docs/HERMES_MOCK_GENERATOR_V0_9_C.md` exists (this document).
- `app/mock_hermes_generator.py` exists and is local-only, mock-only, advisory-only,
  deterministic, side-effect-free.
- `scripts/check_hermes_mock_generator_v0_9_c.py` exists and PASSes.
- The generator imports no network client, no Hermes runtime, no `app.main`, and performs
  no subprocess or shell execution.
- The generator uses the v0.9-B `hermes_strategy_suggestion_model` to derive its advice.
- The generator enforces the thirteen mandatory safety values and fail-safe rejects
  unsafe advice via `validate_mock_hermes_advice`.
- No existing tracked file is modified: `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, `CLAUDE.md` all remain untouched.
- No route, endpoint, POST, form, button, or action URL is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-D work is started.

## 9. Handoff

Future phase:
v0.9-D — (not yet defined; requires separate Owner authorization)

v0.9-D is not started by v0.9-C.
