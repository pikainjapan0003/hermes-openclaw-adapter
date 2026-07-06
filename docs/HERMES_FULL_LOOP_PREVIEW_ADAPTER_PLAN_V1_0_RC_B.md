# v1.0-RC-B Full Loop Preview Adapter Plan

## 1. Phase Title

v1.0-RC-B Full Loop Preview Adapter Plan

## 2. Baseline

v1.0-RC-A Synthetic Full Loop Fixture Plan completed, pushed, verified, accepted.

```text
HEAD = b477314d618eca6386d9c0ea669f50b2efd0e884
commit = docs: add v1.0-RC synthetic full loop fixture plan
```

## 3. Purpose

Define a future local-only preview adapter plan for validating and normalizing a synthetic full-loop rehearsal fixture.

## 4. Phase Classification

docs / check-only adapter plan.

## 5. Relationship to v1.0-RC-A

- v1.0-RC-A defined the synthetic full-loop fixture contract.
- v1.0-RC-B defines the future preview adapter contract.
- v1.0-RC-B does not create the fixture.
- v1.0-RC-B does not implement the adapter.

## 6. Binding Ruling

- v1.0-RC-B does not create fixture file.
- v1.0-RC-B does not implement preview adapter.
- v1.0-RC-B does not implement Full Blackboard Loop.
- v1.0-RC-B does not implement Dashboard timeline display.
- v1.0-RC-B does not add Dashboard controls.
- v1.0-RC-B does not activate Hermes runtime.
- v1.0-RC-B does not dispatch Worker.
- v1.0-RC-B does not call OpenClaw.
- v1.0-RC-B does not write Blackboard.
- v1.0-RC-B does not write queue.
- v1.0-RC-B does not write audit trail.
- v1.0-RC-B does not call connector.
- v1.0-RC-B does not perform external side effects.

## 7. Future Adapter File Recommendation

```text
app/full_loop_preview_adapter.py
```

## 8. Future Adapter Fixture Input Recommendation

```text
fixtures/local_mock_data/hermes_full_blackboard_loop_rehearsal_v1_0_rc_d.json
```

## 9. Future Adapter Output Recommendation

- read-only in-memory preview model only.
- No file write.
- No queue write.
- No audit trail write.
- No Blackboard write.
- No production/shared DB write.
- No Remote Blackboard API write.

## 10. Future Adapter Responsibilities

- load synthetic local-only fixture
- validate top-level fixture fields
- validate global safety flags
- validate timeline exists
- validate all required timeline steps exist
- validate timeline order
- validate each timeline step fields
- validate each timeline step safety flags
- reject unsafe permission flags
- reject private/raw/secret payloads
- normalize timeline into display-safe preview data
- generate validation summary
- generate fail-closed HOLD reason if unsafe
- return read-only preview object

## 11. Future Adapter Forbidden Responsibilities

- do not write Blackboard
- do not write queue
- do not write audit trail
- do not write files
- do not create tasks
- do not dispatch Worker
- do not call OpenClaw
- do not activate Hermes runtime
- do not call connector
- do not call Google Sheets
- do not call network
- do not read secrets
- do not read production data
- do not create route
- do not create endpoint
- do not create webhook
- do not add Dashboard controls
- do not perform external side effects

## 12. Required Adapter Input Checks

- fixture_id exists
- fixture_version exists
- fixture_kind exists
- synthetic_local_only is true
- mock_only is true
- dry_run is true
- read_only is true
- owner_review_required is true
- external_side_effects_allowed is false
- external_side_effects_occurred is false
- blackboard_write_allowed is false
- queue_write_allowed is false
- audit_trail_write_allowed is false
- worker_dispatch_allowed is false
- openclaw_call_allowed is false
- hermes_runtime_allowed is false
- connector_call_allowed is false
- google_sheets_write_allowed is false
- follow_up_task_creation_allowed is false
- dashboard_controls_allowed is false

## 13. Required Timeline Validation Checks

- owner_rehearsal_request exists
- blackboard_task_draft exists
- annotation_preview exists
- approval_readiness_preview exists
- owner_decision_preview exists
- worker_dry_run_preview exists
- openclaw_mock_command_envelope exists
- openclaw_mock_gateway_result exists
- synthetic_result_message exists
- result_feedback_display_preview exists
- hermes_advisory_readback exists
- follow_up_suggestion_guard_output exists
- final_owner_review_summary exists
- timeline order is deterministic
- each step has step_id
- each step has step_order
- each step has step_title
- each step has source_component
- each step has target_component
- each step has synthetic_input
- each step has synthetic_output
- each step has allowed_behavior
- each step has forbidden_behavior
- each step has safety_flags
- each step has validation_status
- each step has owner_review_required
- each step has next_step_allowed
- each step has next_step_requires_owner_confirmation
- each step has notes

## 14. Required Display-Safe Output Fields

- fixture_id
- fixture_version
- validation_status
- validation_summary
- safety_summary
- timeline_preview
- artifact_preview
- owner_review_required
- next_owner_review_question
- fail_closed_reasons
- non_goals
- labels

## 15. Required Output Labels

- FULL LOOP REHEARSAL PREVIEW
- READ ONLY
- SYNTHETIC / MOCK ONLY
- DRY RUN ONLY
- VALIDATED FIXTURE ONLY
- NO BLACKBOARD WRITE
- NO QUEUE WRITE
- NO AUDIT TRAIL WRITE
- NO WORKER DISPATCH
- NO OPENCLAW CALL
- NO HERMES RUNTIME
- NO CONNECTOR CALL
- NO EXTERNAL SIDE EFFECTS
- OWNER REVIEW REQUIRED
- PREVIEW IS NOT EXECUTION PERMISSION

## 16. Future Adapter Fail-Closed Rules

- Missing fixture = HOLD.
- Missing fixture_id = HOLD.
- Missing timeline = HOLD.
- Missing required timeline step = HOLD.
- Out-of-order timeline = HOLD.
- Missing safety flags = HOLD.
- Unsafe safety flag = HOLD.
- Any write permission true = HOLD.
- Any dispatch permission true = HOLD.
- Any connector permission true = HOLD.
- Any external side effect permission true = HOLD.
- Any raw private payload = HOLD.
- Any secret-like field = HOLD.
- Any webhook URL = HOLD.
- Any production endpoint = HOLD.
- Any Dashboard control implication = HOLD.
- Any automatic follow-up implication = HOLD.
- Any ambiguous permission = HOLD.

## 17. Future Adapter Import Boundary

- adapter must not import app runtime.
- adapter must not import Hermes runtime.
- adapter must not import Worker runtime.
- adapter must not import OpenClaw runtime.
- adapter must not import connector runtime.
- adapter may use only Python standard library unless separately authorized.

## 18. Future Dashboard Boundary

- v1.0-RC-B does not implement Dashboard display.
- Future Dashboard timeline display requires separate Owner instruction.
- Dashboard display must remain GET-only.
- Dashboard display must remain read-only.
- Dashboard display must not add controls.
- Dashboard display must not add POST/form/button/action URL.

## 19. Future Sequence

1. v1.0-RC-C Full Loop Timeline Display Plan
2. v1.0-RC-D Full Loop Read-only Rehearsal Implementation
3. v1.0-RC-E Owner Review / Safety Matrix Check
4. v1.0-RC-R Full Blackboard Loop Rehearsal Closeout

## 20. Safe Next Recommendation

After this plan, Owner may choose v1.0-RC-C Full Loop Timeline Display Plan, or HOLD for architecture review.

## 21. Explicit Non-Goals

- no fixture creation
- no adapter implementation
- no Full Blackboard Loop implementation
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

## 22. Safety Reminders

- Preview adapter plan is not adapter implementation.
- Adapter validation is not execution.
- Timeline preview is not dispatch.
- Dashboard display is not execution permission.
- Result Message is not dispatch permission.
- Hermes readback is advisory only.
- Owner approval is still required for any future action.

## 23. Required Safety Statements

- v1.0-RC-B is docs / check-only adapter plan.
- v1.0-RC-B does not create fixture file.
- No preview adapter implementation occurs in this phase.
- No Full Blackboard Loop implementation occurs in this phase.
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
- external_side_effects_allowed is false
- blackboard_write_allowed is false
- queue_write_allowed is false
- audit_trail_write_allowed is false
- worker_dispatch_allowed is false
- openclaw_call_allowed is false
- hermes_runtime_allowed is false
- connector_call_allowed is false
- follow_up_task_creation_allowed is false
- dashboard_controls_allowed is false
