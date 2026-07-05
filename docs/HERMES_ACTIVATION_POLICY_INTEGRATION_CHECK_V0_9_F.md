# Hermes × OpenClaw v0.9-F
# Hermes Activation Policy Integration Check

## 0. Status

- Phase: v0.9-F
- Type: docs / check-only integration check
- Base commit: `6110f853f30e201a5af1aa31374704ee23adf675`
- Latest commit message: `feat: add v0.9 Hermes result readback mock`
- Implementation status: NOT IMPLEMENTED, DOCS / CHECK-ONLY
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
- Follow-up task auto-creation status: NOT CREATED
- Worker status: OFF / NOT STARTED
- Real OpenClaw status: NOT CALLED
- Google Sheets status: DISABLED / NOT READ / NOT WRITTEN
- Real queue DB status: NOT READ / NOT WRITTEN
- Audit trail status: NOT WRITTEN
- POST status: DISABLED / NOT IMPLEMENTED
- Secrets status: NOT READ
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.9-R / v0.9.5 status: NOT STARTED

## 1. Purpose / Positioning

v0.9-F is a docs / check-only Hermes Activation Policy Integration Check. It confirms
that the accumulated v0.9-A/B/C/D/E Hermes strategy/advice/readback mock series has
consistently honored the Blackboard Activation Policy, Owner Review, dispatch
separation, and external side-effect safety boundaries — it does not add any new
runtime behavior.

- This is a docs / check-only integration check.
- This is not Hermes runtime activation.
- This is not a new mock Hermes generator feature.
- This is not a new Dashboard control.
- This is not Blackboard write.
- This is not queue write.
- This is not audit trail write.
- This is not automatic follow-up task creation.
- This is not Worker dispatch.
- This is not OpenClaw call.
- This is not external action.

## 2. v0.9 Series Sub-Phases Checked

```text
v0.9-A — Hermes Strategy Contract Plan
v0.9-B — Strategy Suggestion Model
v0.9-C — Mock Hermes Generator
v0.9-D — Dashboard Hermes Advice Panel
v0.9-E — Hermes Reads Result Message Mock
v0.9-F — Hermes Activation Policy Integration Check
```

## 3. v0.9 Series Safety Conclusions

Hermes remains mock-only.
Hermes remains advisory-only.
Hermes remains Owner-supervised.
Hermes runtime remains disabled.
Hermes memory is not read.
Hermes tools are not called.
Hermes suggestions do not write Blackboard.
Hermes advice does not approve.
Hermes readback does not auto-create follow-up tasks.
Hermes readback does not execute.
Hermes strategy suggestion does not dispatch Worker.
Hermes strategy suggestion does not call OpenClaw.
Dashboard Hermes advice panel remains read-only.
Owner confirmation remains required before any future Blackboard task creation.
Blackboard Activation Policy remains enforced as a boundary.
External side effects remain forbidden by default.

## 4. Mandatory Safety Values Confirmed Across the Series

The following forced safety values were verified to be enforced by the v0.9-B
`hermes_strategy_suggestion_model`, the v0.9-C `mock_hermes_generator`, and the v0.9-E
`hermes_result_readback_mock`:

```text
must_not_execute = true
requires_owner_confirmation = true
blackboard_write_allowed = false
queue_write_allowed = false
audit_trail_write_allowed = false
follow_up_task_auto_create_allowed = false
worker_dispatch_allowed = false
openclaw_call_allowed = false
external_side_effects_allowed = false
real_hermes_called = false
hermes_runtime_activated = false
hermes_memory_read = false
hermes_tool_called = false
```

Not every field exists at every layer:

- v0.9-B `hermes_strategy_suggestion_model` defines and forces: `must_not_execute`,
  `requires_owner_confirmation`, `blackboard_write_allowed`, `worker_dispatch_allowed`,
  `openclaw_call_allowed`, `external_side_effects_allowed`.
- v0.9-C `mock_hermes_generator` additionally defines and forces: `mock_hermes`,
  `real_hermes_called`, `hermes_runtime_activated`, `hermes_memory_read`,
  `hermes_tool_called`, `queue_write_allowed`, `audit_trail_write_allowed`.
- v0.9-E `hermes_result_readback_mock` additionally defines and forces:
  `follow_up_task_auto_create_allowed`, `result_readback_only`.

`follow_up_task_auto_create_allowed` exists only at the v0.9-E readback mock layer —
it is not a field of the v0.9-B model or the v0.9-C generator, since only the readback
mock ever handles the "reads a result and might suggest a follow-up" scenario.

## 5. What v0.9-F Does Not Do

不開始 v0.9-R
不開始 v0.9.5
不開始 Limited Connector Trial
不開始 Callback Contract
不修改 app/main.py
不修改 templates/system.html
不修改 static/dashboard.css
不修改 CLAUDE.md
不新增 Dashboard controls
不新增 POST
不新增 form / button / action URL
不新增 approve / reject / execute / dispatch / send controls
不啟動 Hermes runtime
不讀 Hermes memory
不呼叫 Hermes tools
不寫 Blackboard
不寫 queue
不寫 audit trail
不自動建立 follow-up task
不呼叫 Worker
不呼叫 OpenClaw
不呼叫 Google Sheets
不新增 route / endpoint / webhook / connector
不讀 secrets
不建立 production/shared DB
不建立 Remote Blackboard API runtime
不 touch patches/

## 6. Safety Sentences

Hermes activation policy integration check is not Hermes activation.
Hermes remains mock-only and advisory-only.
Hermes suggestion is not Blackboard write.
Hermes advice is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes readback is not automatic follow-up task creation.
Hermes strategy suggestion is not Worker dispatch.
Hermes strategy suggestion is not OpenClaw call.
Dashboard Hermes advice panel is read-only.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

## 7. v0.9-F Completion Criteria

- `docs/HERMES_ACTIVATION_POLICY_INTEGRATION_CHECK_V0_9_F.md` exists (this document).
- `scripts/check_hermes_activation_policy_integration_v0_9_f.py` exists and PASSes.
- Every v0.9-A/B/C/D/E doc, model, generator, mock, and readiness script still exists.
- `app/main.py`, `templates/system.html`, `static/dashboard.css`, `CLAUDE.md` are all
  untouched by this round.
- No new file other than the two files named above is added.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-R, v0.9.5, or later work is started.

## 8. Handoff

Future phase:
v0.9-R / v0.9.5 — (not yet defined; requires separate Owner authorization)

v0.9-R and v0.9.5 are not started by v0.9-F.
