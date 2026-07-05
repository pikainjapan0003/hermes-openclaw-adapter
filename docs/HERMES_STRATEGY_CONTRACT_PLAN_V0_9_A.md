# Hermes × OpenClaw v0.9-A
# Hermes Strategy Contract Plan

## 0. Status

- Phase: v0.9-A
- Type: plan-only
- Base commit: `8858f3aeee395379cd7e296cccbf19fbc6caac85`
- Latest commit message: `docs: close out v0.8.5 OpenClaw mock gateway`
- Implementation status: NOT IMPLEMENTED
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
- Webhook / endpoint / connector status: NOT CREATED
- Production / shared DB status: NOT CREATED
- Remote Blackboard API runtime status: NOT CREATED
- `patches/` status: UNTRACKED (unchanged)
- v0.9-B status: NOT STARTED

v0.9-A is a plan-only round. It does not implement Hermes. It does not activate a Hermes
runtime. It does not add a Dashboard panel. It does not modify `app/main.py`,
`templates/system.html`, `static/dashboard.css`, or `CLAUDE.md`. It does not write the
queue, does not call Worker, does not call real OpenClaw, does not touch Google Sheets,
and does not POST anything anywhere.

## 1. v0.9-A Positioning

v0.9-A 只定義 Hermes Strategy Contract。
v0.9-A 不實作 Hermes。
v0.9-A 不啟動 Hermes runtime。
v0.9-A 不新增 Dashboard panel。
v0.9-A 不寫 queue。
v0.9-A 不呼叫 Worker。
v0.9-A 不呼叫 OpenClaw。
v0.9-A 不呼叫 Google Sheets。
v0.9-A 不做 external action。

## 2. Hermes's Role at This Stage

Hermes 在本階段只能是：

- advisory
- strategy-only
- mock-only
- readback-only
- Owner-supervised
- non-executing
- non-approving
- non-dispatching

Hermes 可以做：

- 讀取 synthetic blackboard/task summary
- 讀取 mock gateway result summary
- 讀取 Owner decision preview summary
- 產生 strategy suggestion
- 產生 risk assessment
- 產生 missing information question
- 產生 suggested next step
- 提醒 Owner 需要確認

Hermes 不可以做：

- approve
- reject
- execute
- dispatch
- send
- write queue
- write audit trail
- call Worker
- call OpenClaw
- call Hermes runtime tools
- call Google Sheets
- create external side effects
- auto-create follow-up tasks
- bypass Owner Review
- bypass Blackboard Activation Policy

## 3. Hermes Strategy Suggestion Contract

A future Hermes Strategy Suggestion object must have the following shape (plan-only; no
code, generator, or fixture is created by v0.9-A):

```
{
  "suggestion_id": "<synthetic local-only identifier>",
  "task_id": "<reference to the originating synthetic task, if any>",
  "source_message_ids": ["<referenced synthetic message ids>"],
  "source_result_ids": ["<referenced synthetic mock result ids>"],
  "source_decision_ids": ["<referenced synthetic Owner decision preview ids>"],
  "strategy_summary": "<human-readable summary of the suggested strategy>",
  "recommended_action": "<human-readable description, never an instruction actually sent anywhere>",
  "risk_assessment": "<human-readable risk classification, informational only>",
  "missing_information": "<human-readable description of what is missing, if anything>",
  "owner_question": "<a question for the Owner, if clarification is needed>",
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

## 4. Mandatory Safety Values

```text
must_not_execute = true
requires_owner_confirmation = true
blackboard_write_allowed = false
worker_dispatch_allowed = false
openclaw_call_allowed = false
external_side_effects_allowed = false
```

A future Hermes Strategy Suggestion that sets any of these six fields to a value other
than the one specified above is out of scope for this contract and must not be built
under this plan.

## 5. Hermes Activation Policy Boundary

- Hermes suggestion is not Blackboard write.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up execution.
- Hermes strategy suggestion is not Worker dispatch.
- Hermes strategy suggestion is not OpenClaw call.
- Hermes cannot bypass Owner Review.
- Hermes cannot bypass Blackboard Activation Policy.
- Owner confirmation remains required before any future Blackboard task creation.

## 6. What v0.9-A Does Not Do

不開始 v0.9-B
不實作 Suggestion Model code
不建立 mock Hermes generator
不新增 Dashboard Hermes Advice Panel
不讓 Hermes 讀 real queue DB
不讓 Hermes 寫 queue
不讓 Hermes 寫 audit trail
不讓 Hermes 呼叫 OpenClaw
不讓 Hermes 呼叫 Worker
不讓 Hermes 呼叫 Google Sheets
不建立 Hermes runtime
不讀 Hermes memory
不新增 route
不新增 endpoint
不新增 POST
不新增 webhook
不新增 connector
不讀 secrets
不建立 production/shared DB
不建立 Remote Blackboard API runtime
不 touch patches/

## 7. Safety Sentences

Hermes strategy contract is not Hermes activation.
Hermes suggestion is not Blackboard write.
Hermes advice is not Owner approval.
Hermes readback is not automatic follow-up execution.
Hermes strategy suggestion is not Worker dispatch.
Hermes strategy suggestion is not OpenClaw call.
Hermes cannot bypass Owner Review.
Hermes cannot bypass Blackboard Activation Policy.
External side effects remain forbidden by default.

## 8. Next Phase Hint (Not Started)

```text
v0.9-B — Strategy Suggestion Model
```

v0.9-A does not start v0.9-B.
v0.9-A does not implement suggestion model code.
v0.9-A only defines the Hermes strategy contract for future Owner review.

## 9. v0.9-A Acceptance Criteria

- `docs/HERMES_STRATEGY_CONTRACT_PLAN_V0_9_A.md` plan doc exists (this document).
- `scripts/check_hermes_strategy_contract_plan_v0_9_a.py` readiness script exists.
- v0.9-A readiness PASSes.
- No existing tracked file is modified.
- `app/main.py` is untouched.
- `templates/system.html` is untouched.
- `static/dashboard.css` is untouched.
- `CLAUDE.md` is untouched.
- No Hermes runtime is activated, no Hermes memory is read, no Hermes tool is called.
- No Blackboard write occurs.
- No Worker/OpenClaw/Google Sheets is touched.
- No queue is read or written.
- No audit trail is written.
- No POST / no execution / no dispatch occurs.
- `patches/` remains untracked.
- No tag is created.
- No v0.9-B work is started.

## 10. Handoff

Future phase:
v0.9-B — Strategy Suggestion Model

v0.9-B is not started by v0.9-A.
