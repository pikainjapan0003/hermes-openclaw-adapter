# v0.9.6-B Mock Callback Receiver Boundary

## 1. Phase Title

v0.9.6-B Mock Callback Receiver Boundary

## 2. Baseline

v0.9.6-A completed, pushed, verified, closed.

```text
HEAD = a932bebf81d1f7264f672a5e9d82825689beb1fd
commit = docs: add v0.9.6 callback contract plan
```

## 3. Purpose

Define the boundary for a future synthetic/mock callback receiver.

## 4. Phase Classification

docs / check-only boundary plan.

## 5. Relationship to v0.9.6-A

- v0.9.6-A defined the callback contract.
- v0.9.6-B defines the mock receiver boundary.
- v0.9.6-B does not implement the receiver.

## 6. Binding Ruling

- v0.9.6-B does not implement callback receiver.
- v0.9.6-B does not create webhook.
- v0.9.6-B does not create route or endpoint.
- v0.9.6-B does not add POST/form/button/action URL/control.
- v0.9.6-B does not receive real external callbacks.
- v0.9.6-B does not write Blackboard.
- v0.9.6-B does not write queue.
- v0.9.6-B does not write audit trail.
- v0.9.6-B does not activate Hermes runtime.
- v0.9.6-B does not call Worker.
- v0.9.6-B does not call OpenClaw.
- v0.9.6-B does not trigger follow-up task creation.
- v0.9.6-B does not perform external side effects.

## 7. Future Mock Receiver Input Boundary

- input must be synthetic local-only callback fixture or explicitly Owner-approved mock payload.
- input must not come from public webhook.
- input must not come from production OpenClaw.
- input must not come from production Worker.
- input must not come from connector runtime.
- input must not contain secrets.
- input must not contain private connector payloads.
- input must not contain real external callback data unless separately authorized.

## 8. Future Mock Receiver Allowed Behavior

- parse synthetic callback message
- validate required Result Message fields
- validate safety flags
- validate mock_only / dry_run / no external side effects
- produce local validation report
- produce read-only preview artifact only if separately authorized
- fail closed on missing or ambiguous fields

## 9. Future Mock Receiver Forbidden Behavior

- listen on network
- expose webhook
- expose route
- expose endpoint
- accept unsigned source
- accept unknown source
- write Blackboard
- write queue
- write audit trail
- write production/shared DB
- write Remote Blackboard API
- trigger Worker
- call OpenClaw
- activate Hermes runtime
- create follow-up task
- call connector
- write Google Sheets
- perform external side effects

## 10. Required Future Mock Receiver Validation Checks

- callback_id exists
- source_system exists
- source_phase exists
- task_id exists
- command_id exists
- result_type exists
- result_status exists
- execution_mode exists
- dry_run is true
- mock_only is true
- external_side_effects_allowed is false
- external_side_effects_occurred is false
- owner_review_required is true
- follow_up_allowed is false by default
- follow_up_requires_owner_confirmation is true
- worker_dispatch_allowed is false
- openclaw_call_allowed is false
- hermes_runtime_allowed is false
- connector_call_allowed is false
- google_sheets_write_allowed is false

## 11. Fail-Closed Rules

- Missing callback_id = HOLD.
- Missing source_system = HOLD.
- Missing task_id = HOLD.
- Missing result_status = HOLD.
- Missing execution_mode = HOLD.
- Missing dry_run flag = HOLD.
- Missing mock_only flag = HOLD.
- Missing owner_review_required flag = HOLD.
- dry_run not true = HOLD.
- mock_only not true = HOLD.
- external_side_effects_allowed not false = HOLD.
- external_side_effects_occurred not false = HOLD.
- follow_up_allowed not false by default = HOLD.
- worker_dispatch_allowed not false = HOLD.
- openclaw_call_allowed not false = HOLD.
- hermes_runtime_allowed not false = HOLD.
- connector_call_allowed not false = HOLD.
- google_sheets_write_allowed not false = HOLD.
- unsigned or unknown source = HOLD.
- any callback claiming real external side effects = HOLD.
- any callback requesting follow-up execution = HOLD.
- any callback attempting storage write = HOLD.
- any ambiguous result status = HOLD.

## 12. Future Output Boundary

- output may only be validation summary.
- output may only be local read-only preview if separately authorized.
- output must not persist private payload.
- output must not write queue.
- output must not write audit trail.
- output must not write Blackboard.
- output must not trigger any next action.

## 13. Future Dashboard Boundary

- v0.9.6-B does not implement Dashboard display.
- Later v0.9.6-C may plan read-only Result Feedback Display.
- Dashboard display remains not execution permission.
- Dashboard display must not add controls.
- Dashboard display must not add POST/form/button/action URL.

## 14. Future Hermes Boundary

- Hermes may later read validated synthetic Result Message as advisory input only.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up task creation.
- Hermes readback is not Worker dispatch.
- Hermes readback is not OpenClaw call.

## 15. Future Sequence

1. v0.9.6-C Result Feedback Display Plan
2. v0.9.6-D Result Feedback Display Implementation, only if separately authorized
3. v0.9.6-E Result-driven Follow-up Suggestion Guard
4. v0.9.6-R Result Feedback Closeout

## 16. Explicit Non-Goals

- no callback receiver implementation
- no webhook
- no route
- no endpoint
- no POST/form/button/action URL/control
- no Dashboard implementation
- no connector selected
- no connector called
- no connector metadata read
- no connector content read
- no connector write
- no Hermes runtime activation
- no Worker call
- no OpenClaw call
- no Blackboard write
- no queue write
- no audit trail write
- no production/shared DB
- no Remote Blackboard API runtime
- no external side effects

## 17. Safety Reminders

- Mock Callback Receiver Boundary is not receiver implementation.
- Mock receiver is not public webhook.
- Callback is not trusted automatically.
- Result Message is not execution success without validation.
- Result Message is not next dispatch permission.
- Hermes readback is not automatic follow-up execution.
- Decision event is not dispatch.
- Owner approval is still required for any future action.

## 18. Required Safety Statements

- v0.9.6-B is docs / check-only boundary plan.
- v0.9.6-B does not implement callback receiver.
- No webhook is created in this phase.
- No route or endpoint is created in this phase.
- No POST/form/button/action URL/control is added in this phase.
- No real external callbacks are received in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No automatic follow-up task creation occurs in this phase.
- Mock receiver is not public webhook.
- Callback is not trusted automatically.
- Result message is not execution success without validation.
- Output must not write queue, audit trail, or Blackboard.
- Output must not trigger next action.
- Unsigned or unknown source = HOLD.
