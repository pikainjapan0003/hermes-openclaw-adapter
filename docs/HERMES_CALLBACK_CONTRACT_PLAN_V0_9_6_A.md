# v0.9.6-A Callback Contract Plan

## 1. Phase Title

v0.9.6-A Callback Contract Plan

## 2. Baseline

v0.9.5-R completed, pushed, verified, closed.

```text
HEAD = 4fe90cfa879e9b97bf0d813aa0740622ef5b5c42
commit = docs: close out v0.9.5 limited connector trial
```

## 3. Purpose

Define the future Callback Contract / Result Feedback Loop boundary.

## 4. Phase Classification

docs / check-only contract plan.

## 5. Relationship to v0.9-E

- v0.9-E Hermes Reads Result Message Mock already completed synthetic result readback.
- v0.9.6-A does not redo v0.9-E.
- v0.9.6-A defines future callback/result message contract boundaries.

## 6. Binding Ruling

- v0.9.6-A does not implement callback receiver.
- v0.9.6-A does not create webhook.
- v0.9.6-A does not create route or endpoint.
- v0.9.6-A does not add POST/form/button/action URL/control.
- v0.9.6-A does not write Blackboard.
- v0.9.6-A does not write queue.
- v0.9.6-A does not write audit trail.
- v0.9.6-A does not activate Hermes runtime.
- v0.9.6-A does not call Worker.
- v0.9.6-A does not call OpenClaw.
- v0.9.6-A does not trigger follow-up task creation.
- v0.9.6-A does not perform external side effects.

## 7. Future Callback Message Family

- Result Message
- Status Message
- Error Message
- Safety Refusal Message
- Retry Recommendation Message
- Human Review Required Message

## 8. Required Future Result Message Fields

- callback_id
- source_system
- source_phase
- task_id
- command_id
- result_type
- result_status
- execution_mode
- dry_run
- mock_only
- external_side_effects_allowed
- started_at
- completed_at
- summary
- output_preview
- error_summary
- safety_flags
- validation_status
- owner_review_required
- follow_up_allowed
- follow_up_requires_owner_confirmation
- blackboard_write_allowed
- queue_write_allowed
- audit_trail_write_allowed
- worker_dispatch_allowed
- openclaw_call_allowed
- hermes_runtime_allowed
- connector_call_allowed
- google_sheets_write_allowed
- external_side_effects_occurred
- rollback_note
- audit_note

## 9. Required Future Safety Flags

- dry_run must remain true unless separately authorized.
- mock_only must remain true unless separately authorized.
- external_side_effects_allowed must remain false by default.
- external_side_effects_occurred must remain false by default.
- owner_review_required must remain true.
- follow_up_allowed must remain false by default.
- follow_up_requires_owner_confirmation must remain true.
- worker_dispatch_allowed must remain false.
- openclaw_call_allowed must remain false.
- hermes_runtime_allowed must remain false.
- connector_call_allowed must remain false.
- google_sheets_write_allowed must remain false.

## 10. Future Validation Rules

- Missing callback_id = HOLD.
- Missing task_id = HOLD.
- Missing result_status = HOLD.
- Missing execution_mode = HOLD.
- Missing dry_run flag = HOLD.
- Missing mock_only flag = HOLD.
- Missing owner_review_required flag = HOLD.
- Any unsigned or unknown callback source = HOLD.
- Any callback claiming external side effects = HOLD.
- Any callback requesting follow-up execution = HOLD.
- Any callback attempting queue write = HOLD.
- Any callback attempting audit trail write = HOLD.
- Any callback attempting Worker dispatch = HOLD.
- Any callback attempting OpenClaw call = HOLD.
- Any callback attempting Hermes runtime activation = HOLD.
- Any callback attempting connector call = HOLD.
- Any ambiguous result status = HOLD.

## 11. Future Trust Boundary

- callback is not automatically trusted.
- result message is not execution success without validation.
- callback receiver is not public webhook by default.
- unknown source must fail closed.
- unsigned source must fail closed.
- callback must not trigger next external action.
- callback must not trigger automatic follow-up task creation.
- Hermes readback is advisory only.
- Hermes readback is not automatic follow-up execution.

## 12. Future Storage Boundary

- v0.9.6-A does not create storage.
- Future result storage must remain mock/read-only until separately authorized.
- No production DB.
- No shared DB.
- No Remote Blackboard API runtime.
- No queue write.
- No audit trail write.
- No Blackboard write.

## 13. Future Dashboard Boundary

- v0.9.6-A does not implement Dashboard display.
- A later phase may plan read-only result feedback display.
- Dashboard display is not execution permission.
- Dashboard display must not add controls.
- Dashboard display must not add POST/form/button/action URL.

## 14. Future Hermes Boundary

- Hermes may later read validated synthetic Result Message as advisory input only.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up task creation.
- Hermes readback is not Worker dispatch.
- Hermes readback is not OpenClaw call.

## 15. Future Sequence

1. v0.9.6-B Mock Callback Receiver Boundary
2. v0.9.6-C Result Feedback Display Plan
3. v0.9.6-D Result Feedback Display Implementation, only if separately authorized
4. v0.9.6-E Result-driven Follow-up Suggestion Guard
5. v0.9.6-R Result Feedback Closeout

## 16. Explicit Non-Goals

- no callback receiver
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

- Callback Contract Plan is not callback implementation.
- Callback is not trust automatically.
- Result Message is not execution success without validation.
- Result Message is not next dispatch permission.
- Callback receiver is not public webhook.
- Hermes readback is not automatic follow-up execution.
- Decision event is not dispatch.
- Owner approval is still required for any future action.

## 18. Required Safety Statements

- v0.9.6-A is docs / check-only contract plan.
- v0.9.6-A does not redo v0.9-E.
- No callback receiver is implemented in this phase.
- No webhook is created in this phase.
- No route or endpoint is created in this phase.
- No POST/form/button/action URL/control is added in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker call occurs in this phase.
- No OpenClaw call occurs in this phase.
- No automatic follow-up task creation occurs in this phase.
- external_side_effects_allowed is false by default.
- owner_review_required is true.
- follow_up_allowed is false by default.
- worker_dispatch_allowed remains false.
- openclaw_call_allowed remains false.
- hermes_runtime_allowed remains false.
- connector_call_allowed remains false.
- google_sheets_write_allowed remains false.
- Unsigned or unknown callback source = HOLD.
- Callback is not automatically trusted.
- Result message is not execution success without validation.
- Callback must not trigger next external action.
- Hermes readback is advisory only.
- Hermes readback is not automatic follow-up execution.
- No production/shared DB or Remote Blackboard API runtime is created in this phase.
