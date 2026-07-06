# v1.0-RC-A Synthetic Full Loop Fixture Plan

## 1. Phase Title

v1.0-RC-A Synthetic Full Loop Fixture Plan

## 2. Baseline

v1.0-RC Full Blackboard Loop Rehearsal Plan completed, pushed, verified, accepted.

```text
HEAD = 12831bcb3cc2ca786c6d322330365c2b5f41b78e
commit = docs: add v1.0-RC full blackboard loop rehearsal plan
```

## 3. Purpose

Define the future synthetic full-loop rehearsal fixture structure.

## 4. Phase Classification

docs / check-only fixture plan.

## 5. Relationship to v1.0-RC

- v1.0-RC defined the rehearsal plan.
- v1.0-RC-A defines the synthetic fixture contract.
- v1.0-RC-A does not create the fixture.

## 6. Binding Ruling

- v1.0-RC-A does not create fixture file.
- v1.0-RC-A does not implement Full Blackboard Loop.
- v1.0-RC-A does not implement preview adapter.
- v1.0-RC-A does not implement Dashboard display.
- v1.0-RC-A does not add Dashboard controls.
- v1.0-RC-A does not activate Hermes runtime.
- v1.0-RC-A does not dispatch Worker.
- v1.0-RC-A does not call OpenClaw.
- v1.0-RC-A does not write Blackboard.
- v1.0-RC-A does not write queue.
- v1.0-RC-A does not write audit trail.
- v1.0-RC-A does not call connector.
- v1.0-RC-A does not perform external side effects.

## 7. Future Fixture File Recommendation

```text
fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_b.json
```

## 8. Future Fixture Top-Level Fields

- fixture_id
- fixture_version
- fixture_kind
- synthetic_local_only
- mock_only
- dry_run
- read_only
- owner_review_required
- external_side_effects_allowed
- external_side_effects_occurred
- created_for_phase
- source_baseline
- loop_summary
- safety_flags
- timeline
- artifacts
- validation_expectations
- fail_closed_rules
- non_goals
- next_owner_review_question

## 9. Future Timeline Steps

1. owner_rehearsal_request
2. blackboard_task_draft
3. annotation_preview
4. approval_readiness_preview
5. owner_decision_preview
6. worker_dry_run_preview
7. openclaw_mock_command_envelope
8. openclaw_mock_gateway_result
9. synthetic_result_message
10. result_feedback_display_preview
11. hermes_advisory_readback
12. follow_up_suggestion_guard_output
13. final_owner_review_summary

## 10. Required Safety Flags

- synthetic_local_only = true
- mock_only = true
- dry_run = true
- read_only = true
- owner_review_required = true
- external_side_effects_allowed = false
- external_side_effects_occurred = false
- blackboard_write_allowed = false
- queue_write_allowed = false
- audit_trail_write_allowed = false
- worker_dispatch_allowed = false
- openclaw_call_allowed = false
- hermes_runtime_allowed = false
- connector_call_allowed = false
- google_sheets_write_allowed = false
- follow_up_task_creation_allowed = false
- dashboard_controls_allowed = false

## 11. Required Artifact References

- synthetic_task_draft
- annotation_preview
- approval_readiness_preview
- owner_decision_preview
- worker_dry_run_preview
- openclaw_mock_command_envelope
- openclaw_mock_gateway_result
- synthetic_result_message
- result_feedback_display_preview
- hermes_advisory_readback
- follow_up_suggestion_guard_output
- final_owner_review_summary

## 12. Each Timeline Step Must Include

- step_id
- step_order
- step_title
- source_component
- target_component
- synthetic_input
- synthetic_output
- allowed_behavior
- forbidden_behavior
- safety_flags
- validation_status
- owner_review_required
- next_step_allowed
- next_step_requires_owner_confirmation
- notes

## 13. Each Timeline Step Must Explicitly State

- no external side effects
- no production data
- no secrets
- no connector call
- no Blackboard write
- no queue write
- no audit trail write
- no Worker dispatch
- no OpenClaw call
- no Hermes runtime activation
- no automatic follow-up task creation

## 14. Future Validation Requirements

- every timeline step exists
- every timeline step is ordered
- every timeline step has required fields
- every safety flag has safe value
- no raw private payload
- no connector payload
- no secret value
- no production endpoint
- no webhook URL
- no POST/action/control field
- no write permission flag set true
- no dispatch permission flag set true
- no automatic follow-up flag set true

## 15. Future Display Boundary

- fixture may support future read-only timeline display only if separately authorized.
- display is not execution permission.
- no controls.
- no POST/form/button/action URL.
- no approve/reject/execute/dispatch/send/retry/follow-up controls.

## 16. Future Adapter Boundary

- fixture may support future preview adapter only if separately authorized.
- adapter must be read-only.
- adapter must not import app runtime.
- adapter must not import Hermes runtime.
- adapter must not import Worker runtime.
- adapter must not import OpenClaw runtime.
- adapter must not call network.
- adapter must not read secrets.
- adapter must not write storage.
- adapter must not trigger execution.

## 17. Fail-Closed Rules

- Missing fixture_id = HOLD.
- Missing safety_flags = HOLD.
- Missing timeline = HOLD.
- Missing any required timeline step = HOLD.
- Out-of-order timeline step = HOLD.
- Missing Owner review field = HOLD.
- Any unsafe safety flag = HOLD.
- Any write permission true = HOLD.
- Any dispatch permission true = HOLD.
- Any connector call permission true = HOLD.
- Any external side effect permission true = HOLD.
- Any Dashboard control implication = HOLD.
- Any automatic follow-up implication = HOLD.
- Any ambiguous permission = HOLD.

## 18. Safe Next Recommendation

After this plan, Owner may choose v1.0-RC-B Full Loop Preview Adapter Plan, or HOLD for architecture review.

## 19. Explicit Non-Goals

- no fixture creation
- no implementation
- no preview adapter
- no Dashboard timeline display
- no Dashboard controls
- no Hermes runtime
- no Worker execution
- no OpenClaw call
- no connector trial
- no Blackboard write
- no queue write
- no audit trail write
- no production/shared DB
- no Remote Blackboard API runtime
- no external side effects

## 20. Safety Reminders

- Fixture plan is not fixture creation.
- Synthetic fixture is not production data.
- Timeline preview is not execution.
- Full loop preview is not Full Loop implementation.
- Dashboard display is not execution permission.
- Result Message is not dispatch permission.
- Hermes readback is advisory only.
- Owner approval is still required for any future action.

## 21. Required Safety Statements

- v1.0-RC-A is docs / check-only fixture plan.
- v1.0-RC-A does not create fixture file.
- No Full Blackboard Loop implementation occurs in this phase.
- No preview adapter implementation occurs in this phase.
- No Dashboard timeline display implementation occurs in this phase.
- No Dashboard controls are added in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker dispatch occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No connector call occurs in this phase.
- No external side effects occur in this phase.
- external_side_effects_allowed = false
- blackboard_write_allowed = false
- queue_write_allowed = false
- audit_trail_write_allowed = false
- worker_dispatch_allowed = false
- openclaw_call_allowed = false
- hermes_runtime_allowed = false
- connector_call_allowed = false
- follow_up_task_creation_allowed = false
- dashboard_controls_allowed = false
- Fixture plan is not fixture creation.
