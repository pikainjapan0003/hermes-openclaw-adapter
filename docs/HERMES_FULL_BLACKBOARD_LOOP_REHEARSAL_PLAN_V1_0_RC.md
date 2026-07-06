# v1.0-RC Full Blackboard Loop Rehearsal Plan

## 1. Phase Title

v1.0-RC Full Blackboard Loop Rehearsal Plan

## 2. Baseline

v0.9.6-R completed, pushed, verified, closed.

```text
HEAD = 306c1def1b917dee36c876b8b4f078559358030c
commit = docs: close out v0.9.6 result feedback loop
```

## 3. Purpose

Define a future full-loop rehearsal plan for the Owner-supervised Blackboard Loop MVP.

## 4. Phase Classification

docs / check-only rehearsal plan.

## 5. Relationship to Prior Phases

- v0.8.4 established Worker dry-run result / audit trail preview boundary.
- v0.8.5 established OpenClaw mock gateway boundary.
- v0.9 established Hermes Strategy Mock and advisory readback boundary.
- v0.9.5 established Limited Connector Trial boundary without real connector use.
- v0.9.6 established Result Feedback Loop boundary and read-only synthetic result display.

## 6. Binding Ruling

- v1.0-RC plan does not implement Full Blackboard Loop.
- v1.0-RC plan does not write Blackboard.
- v1.0-RC plan does not write queue.
- v1.0-RC plan does not write audit trail.
- v1.0-RC plan does not add Dashboard controls.
- v1.0-RC plan does not activate Hermes runtime.
- v1.0-RC plan does not dispatch Worker.
- v1.0-RC plan does not call OpenClaw.
- v1.0-RC plan does not call connector.
- v1.0-RC plan does not perform external side effects.

## 7. Future Rehearsal Flow

- Owner starts with explicit rehearsal request.
- Hermes remains advisory/mock-only.
- Blackboard task draft remains synthetic/local-only.
- Annotation remains preview-only.
- Approval readiness remains preview-only.
- Owner decision remains decision preview unless separately authorized.
- Worker remains dry-run-only.
- OpenClaw remains mock gateway only.
- Result Message remains synthetic/mock-only.
- Result Feedback Display remains read-only.
- Hermes readback remains advisory-only.
- Follow-up suggestion remains not task creation.
- Owner decides next step.

## 8. Required Future Rehearsal Artifacts

- synthetic task draft
- annotation preview
- approval readiness preview
- Owner decision preview
- Worker dry-run preview
- OpenClaw mock command envelope
- mock gateway result
- synthetic Result Message
- Result Feedback Display
- Hermes advisory readback
- Follow-up Suggestion Guard output
- final Owner Review summary

## 9. Required Future Safety Flags

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

## 10. Future Dashboard Boundary

- Dashboard may display rehearsal timeline only if separately authorized.
- Dashboard remains GET-only.
- Dashboard remains read-only.
- Dashboard display is not execution permission.
- No POST/form/button/action URL/control.
- No approve/reject/execute/dispatch/send/retry/follow-up controls.

## 11. Future Hermes Boundary

- Hermes remains advisory-only unless separately authorized.
- Hermes advice is not Owner approval.
- Hermes readback is not automatic follow-up task creation.
- Hermes readback is not Worker dispatch.
- Hermes readback is not OpenClaw call.
- Hermes readback is not connector call.

## 12. Future Worker Boundary

- Worker remains dry-run-only.
- Worker preview is not Worker execution.
- Worker result preview is not actual execution result.
- Worker must not dispatch from Owner decision preview.

## 13. Future OpenClaw Boundary

- OpenClaw remains mock gateway only.
- OpenClaw command envelope is not OpenClaw call.
- Mock gateway is not production gateway.
- No real OpenClaw call.

## 14. Future Blackboard / Queue / Audit Boundary

- Blackboard write remains forbidden unless separately authorized.
- Queue write remains forbidden unless separately authorized.
- Audit trail write remains forbidden unless separately authorized.
- Decision event is not dispatch.
- Owner approval is not Worker execution.
- owner_review_required is not Owner approval.

## 15. Future Connector Boundary

- No real connector trial.
- No connector selected.
- No connector call.
- No connector metadata read.
- No connector content read.
- No connector write.
- Connector read is not connector write.
- Connector preview is not external side effect permission.

## 16. Fail-Closed Rules

- Missing Owner explicit rehearsal request = HOLD.
- Missing synthetic fixture = HOLD.
- Missing safety flags = HOLD.
- Any safety flag allowing external side effect = HOLD.
- Any Blackboard write implication = HOLD.
- Any queue write implication = HOLD.
- Any audit trail write implication = HOLD.
- Any Worker dispatch implication = HOLD.
- Any OpenClaw call implication = HOLD.
- Any Hermes runtime activation implication = HOLD.
- Any connector call implication = HOLD.
- Any Dashboard control implication = HOLD.
- Any POST/form/button/action URL implication = HOLD.
- Any automatic follow-up implication = HOLD.
- Any ambiguous permission = HOLD.

## 17. Future Acceptance Criteria for v1.0-RC Implementation (Not Authorized Now)

- end-to-end synthetic loop can be displayed or reported.
- every step is clearly labeled read-only/mock/dry-run.
- no external side effects occur.
- no controls are added.
- no runtime is activated.
- Owner can understand each step and decide HOLD/PASS.

## 18. Safe Next Recommendation

After this plan, Owner may choose v1.0-RC-A Synthetic Full Loop Fixture Plan, or HOLD for architecture review.

## 19. Explicit Non-Goals

- no implementation
- no Dashboard implementation
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

- Rehearsal plan is not rehearsal implementation.
- Full loop rehearsal is not production automation.
- Dashboard display is not execution permission.
- Owner approval is not Worker execution.
- Decision event is not dispatch.
- Result Message is not next dispatch permission.
- Hermes advice is not Owner approval.
- Hermes readback is advisory only.

## 21. Required Safety Statements

- v1.0-RC is docs / check-only rehearsal plan.
- v1.0-RC does not implement Full Blackboard Loop.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No Dashboard controls are added in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker dispatch occurs in this phase.
- No OpenClaw call occurs in this phase.
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
- Any automatic follow-up implication = HOLD.
- Any Dashboard control implication = HOLD.
