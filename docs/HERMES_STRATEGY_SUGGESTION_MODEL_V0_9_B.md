# Hermes × OpenClaw v0.9-B
# Strategy Suggestion Model

## 0. Status

- Phase: v0.9-B
- Type: local-only / mock-only / advisory-only model implementation
- Base commit: `5d6718178849cd7ddc09f0452ed9756873847721`
- Latest commit message: `docs: add v0.9 Hermes strategy contract plan`
- Implementation status: MODEL IMPLEMENTED, LOCAL-ONLY, MOCK-ONLY, ADVISORY-ONLY
- Dashboard route status: NOT MODIFIED IN THIS PHASE
- Dashboard template status: NOT MODIFIED IN THIS PHASE
- Dashboard CSS status: NOT MODIFIED IN THIS PHASE
- `CLAUDE.md` status: NOT MODIFIED IN THIS PHASE
- Commit status: NOT COMMITTED (this round, until Owner Review passes)
- Push status: NOT PUSHED
- Tag status: NOT TAGGED
- Hermes runtime status: NOT ACTIVATED
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
- v0.9-C status: NOT STARTED

## 1. Purpose / Positioning

v0.9-B builds a synthetic, local-only, mock-only, advisory-only Hermes Strategy
Suggestion Model. It takes a synthetic source context (referencing synthetic Blackboard
messages, mock gateway results, and Owner decision previews by id only) and produces a
Hermes Strategy Suggestion dict shaped as defined by v0.9-A — without ever activating a
Hermes runtime, reading Hermes memory, calling a Hermes tool, writing the Blackboard,
dispatching Worker, calling real OpenClaw, or producing any external side effect.

- Strategy suggestion model is not Hermes activation.
- Strategy suggestion model is not mock Hermes generator.
- Hermes suggestion is not Blackboard write.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up execution.
- Hermes strategy suggestion is not Worker dispatch.
- Hermes strategy suggestion is not OpenClaw call.
- Hermes cannot bypass Owner Review.
- Hermes cannot bypass Blackboard Activation Policy.
- External side effects remain forbidden by default.

v0.9-B is not a Hermes runtime. v0.9-B is not a route, endpoint, or webhook. It is a
plain Python module (`app/hermes_strategy_suggestion_model.py`), imported directly, not
served over HTTP.

## 2. How the Model Builds a Suggestion

The public function `build_hermes_strategy_suggestion(source_context: dict) -> dict`
takes a plain dict/mapping containing `task_id`, `source_message_ids`,
`source_result_ids`, `source_decision_ids`, `strategy_summary`, `recommended_action`,
`risk_assessment`, `missing_information`, `owner_question`, `suggested_next_step`, and
`confidence`. It is a pure function: it does not mutate the input, does not read any
file, does not open a network connection, and does not call any other subsystem.

`suggestion_id` is derived deterministically from `task_id` (`f"suggestion-{task_id}"`)
— no randomness, no timestamp — keeping the builder deterministic. The six safety fields
(`must_not_execute`, `requires_owner_confirmation`, `blackboard_write_allowed`,
`worker_dispatch_allowed`, `openclaw_call_allowed`, `external_side_effects_allowed`) are
always forced by the model itself to their safe values, regardless of anything the
caller's `source_context` contains — the caller cannot override them.

## 3. How the Model Validates a Suggestion

The public function `validate_hermes_strategy_suggestion(suggestion: dict) -> dict`
checks any suggestion dict (built by this model or constructed elsewhere) for the
required fields and the six mandatory safety values. It never raises: a non-mapping
input, missing fields, or any safety field set to an unsafe value all produce
`{"valid": False, "violations": [...]}` instead of a crash. A fully valid suggestion
produces `{"valid": True, "violations": []}`.

## 4. Suggestion Shape

```
{
  "suggestion_source": "synthetic_local_only",
  "accepted": true | false,
  "rejection_reason": null | "<reason>",
  "rejection_details": [],
  "suggestion_id": "<derived from task_id>",
  "task_id": "<echoed from source_context>",
  "source_message_ids": [...],
  "source_result_ids": [...],
  "source_decision_ids": [...],
  "strategy_summary": "<human-readable summary>",
  "recommended_action": "<human-readable description, never an instruction actually sent anywhere>",
  "risk_assessment": "<human-readable risk classification>",
  "missing_information": "<human-readable description>",
  "owner_question": "<a question for the Owner, if any>",
  "suggested_next_step": "<human-readable description only>",
  "confidence": "<plan-only classification, e.g. low/medium/high>",
  "must_not_execute": true,
  "requires_owner_confirmation": true,
  "blackboard_write_allowed": false,
  "worker_dispatch_allowed": false,
  "openclaw_call_allowed": false,
  "external_side_effects_allowed": false
}
```

## 5. Mandatory Safety Values

```text
must_not_execute = true
requires_owner_confirmation = true
blackboard_write_allowed = false
worker_dispatch_allowed = false
openclaw_call_allowed = false
external_side_effects_allowed = false
```

These six fields are never sourced from caller input. `build_hermes_strategy_suggestion`
always sets them itself. `validate_hermes_strategy_suggestion` flags any suggestion where
one of them holds a different value as a violation.

## 6. Unsafe Suggestion Rejection Behavior

- Missing any required source context field → `build_hermes_strategy_suggestion` returns
  a rejection dict (`accepted: false`, `rejection_reason`, `rejection_details`), still
  carrying the six forced-safe fields.
- A non-mapping `source_context` → rejection dict with
  `rejection_reason = "source_context must be a mapping"`.
- A non-mapping `suggestion` passed to `validate_hermes_strategy_suggestion` →
  `{"valid": False, "violations": ["suggestion must be a mapping"]}`.
- A suggestion dict (built elsewhere) that sets `must_not_execute = false`,
  `requires_owner_confirmation = false`, `blackboard_write_allowed = true`,
  `worker_dispatch_allowed = true`, `openclaw_call_allowed = true`, or
  `external_side_effects_allowed = true` is fail-safe rejected by
  `validate_hermes_strategy_suggestion` (`valid: false`, one violation entry per unsafe
  field) — never executed, never raised.

## 7. What v0.9-B Does Not Do

- v0.9-B does not activate a Hermes runtime.
- v0.9-B does not read Hermes memory.
- v0.9-B does not call a Hermes tool.
- v0.9-B does not write the Blackboard.
- v0.9-B does not read or write the real queue DB.
- v0.9-B does not write the audit trail.
- v0.9-B does not call Worker.
- v0.9-B does not call real OpenClaw.
- v0.9-B does not touch Google Sheets.
- v0.9-B does not add a Dashboard control.
- v0.9-B does not add a route, endpoint, POST, or webhook.
- v0.9-B does not perform a network call.
- v0.9-B does not execute a subprocess or shell command.
- v0.9-B does not read secrets.
- v0.9-B does not create a production/shared DB or a Remote Blackboard API runtime.
- v0.9-B does not modify `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, or `CLAUDE.md`.
- v0.9-B does not start v0.9-C.

## 8. Safety Sentences

Strategy suggestion model is not Hermes activation.
Strategy suggestion model is not mock Hermes generator.
Hermes suggestion is not Blackboard write.
Hermes advice is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes strategy suggestion is not Worker dispatch.
Hermes strategy suggestion is not OpenClaw call.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

## 9. v0.9-B Completion Criteria

- `docs/HERMES_STRATEGY_SUGGESTION_MODEL_V0_9_B.md` exists (this document).
- `app/hermes_strategy_suggestion_model.py` exists and is local-only, mock-only,
  advisory-only, deterministic, side-effect-free.
- `scripts/check_hermes_strategy_suggestion_model_v0_9_b.py` exists and PASSes.
- The model imports no network client, no Hermes runtime, no `app.main`, and performs no
  subprocess or shell execution.
- The model enforces the six mandatory safety values and fail-safe rejects unsafe
  suggestions via `validate_hermes_strategy_suggestion`.
- No existing tracked file is modified: `app/main.py`, `templates/system.html`,
  `static/dashboard.css`, `CLAUDE.md` all remain untouched.
- No route, endpoint, POST, form, button, or action URL is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-C work is started.

## 10. Handoff

Future phase:
v0.9-C — (not yet defined; requires separate Owner authorization)

v0.9-C is not started by v0.9-B.
