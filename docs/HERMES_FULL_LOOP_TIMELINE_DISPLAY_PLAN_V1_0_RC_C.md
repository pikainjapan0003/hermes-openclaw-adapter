# v1.0-RC-C Full Loop Timeline Display Plan

## 1. Phase Title

v1.0-RC-C Full Loop Timeline Display Plan

## 2. Baseline

v1.0-RC-B Full Loop Preview Adapter Plan completed, pushed, verified, accepted.

```text
HEAD = 8ef7fc5062cf375e192f7952b09ba47edcb9f417
commit = docs: add v1.0-RC full loop preview adapter plan
```

## 3. Purpose

Define a future read-only Dashboard timeline display plan for validated full-loop rehearsal preview data.

## 4. Phase Classification

docs / check-only display plan.

## 5. Relationship to v1.0-RC-A and v1.0-RC-B

- v1.0-RC-A defined the synthetic full-loop fixture contract.
- v1.0-RC-B defined the future preview adapter contract.
- v1.0-RC-C defines the future read-only timeline display contract.
- v1.0-RC-C does not create fixture.
- v1.0-RC-C does not implement adapter.
- v1.0-RC-C does not implement Dashboard display.

## 6. Binding Ruling

- v1.0-RC-C does not create fixture file.
- v1.0-RC-C does not implement preview adapter.
- v1.0-RC-C does not implement Full Blackboard Loop.
- v1.0-RC-C does not implement Dashboard timeline display.
- v1.0-RC-C does not modify app/main.py.
- v1.0-RC-C does not modify templates/system.html.
- v1.0-RC-C does not modify static/dashboard.css.
- v1.0-RC-C does not add Dashboard controls.
- v1.0-RC-C does not activate Hermes runtime.
- v1.0-RC-C does not dispatch Worker.
- v1.0-RC-C does not call OpenClaw.
- v1.0-RC-C does not write Blackboard.
- v1.0-RC-C does not write queue.
- v1.0-RC-C does not write audit trail.
- v1.0-RC-C does not call connector.
- v1.0-RC-C does not perform external side effects.

## 7. Future Display File Recommendations

- templates/system.html may be minimally extended only in a later separately authorized implementation phase.
- static/dashboard.css may be minimally extended only in a later separately authorized implementation phase.
- app/main.py may be minimally extended only in a later separately authorized implementation phase to pass read-only preview data into existing GET-only /dashboard/system render context.
- No new route is recommended.
- No new endpoint is recommended.
- No POST is recommended.

## 8. Future Data Source Boundary

- Display may only consume validated display-safe preview object from future local-only preview adapter.
- Display must not read fixture directly unless separately authorized.
- Display must not read connector data.
- Display must not read production data.
- Display must not read secrets.
- Display must not call network.
- Display must not write storage.

## 9. Future Allowed Display Location

- Existing /dashboard/system page only.
- Existing route must remain GET-only.
- Existing route must remain read-only.
- No new route.
- No new endpoint.
- No webhook.
- No callback receiver.

## 10. Future Display Section Title

```text
FULL BLACKBOARD LOOP REHEARSAL TIMELINE
```

## 11. Required Display Labels

- FULL LOOP REHEARSAL PREVIEW
- READ ONLY
- SYNTHETIC / MOCK ONLY
- DRY RUN ONLY
- VALIDATED PREVIEW DATA ONLY
- NO BLACKBOARD WRITE
- NO QUEUE WRITE
- NO AUDIT TRAIL WRITE
- NO WORKER DISPATCH
- NO OPENCLAW CALL
- NO HERMES RUNTIME
- NO CONNECTOR CALL
- NO EXTERNAL SIDE EFFECTS
- OWNER REVIEW REQUIRED
- DISPLAY IS NOT EXECUTION PERMISSION
- TIMELINE IS NOT DISPATCH PERMISSION
- HERMES READBACK IS ADVISORY ONLY

## 12. Future Allowed Top-Level Displayed Fields

- fixture_id
- fixture_version
- validation_status
- validation_summary
- safety_summary
- owner_review_required
- next_owner_review_question
- fail_closed_reasons
- non_goals
- labels

## 13. Future Allowed Timeline Displayed Fields

- step_order
- step_id
- step_title
- source_component
- target_component
- validation_status
- owner_review_required
- next_step_allowed
- next_step_requires_owner_confirmation
- allowed_behavior_summary
- forbidden_behavior_summary
- safety_flags_summary
- synthetic_input_summary
- synthetic_output_summary
- notes

## 14. Future Forbidden Displayed Fields

- raw private payload
- connector payload
- secrets
- tokens
- passwords
- webhook URLs
- production endpoint URLs
- full external response bodies
- unredacted private content
- real connector content
- real user private content
- write-capable action payload
- dispatch payload
- POST body
- executable command body
- OpenClaw real command body
- Worker execution payload
- Hermes runtime command
- any field implying execution permission

## 15. Future Display Visual Structure

- section header
- safety label row
- validation summary panel
- safety summary panel
- ordered timeline cards
- per-step source/target labels
- per-step validation status
- per-step safety flags summary
- per-step allowed/forbidden behavior summary
- fail-closed reasons panel
- owner review question panel
- non-goals panel

## 16. Future Timeline Status Vocabulary

- validated_preview
- synthetic_only
- read_only
- hold_required
- unsafe_rejected
- owner_review_required

## 17. Future Control Boundary

- No form.
- No button.
- No action URL.
- No POST.
- No approve control.
- No reject control.
- No execute control.
- No dispatch control.
- No send control.
- No retry control.
- No follow-up control.
- No archive/delete/update/write control.

## 18. Future CSS Boundary

- CSS may style read-only cards, labels, timeline rows, warnings, and HOLD states only.
- CSS must not introduce JS behavior.
- CSS must not imply interactive controls.
- CSS must not hide required safety labels.
- CSS must keep warnings visible.

## 19. Future JavaScript Boundary

- No JavaScript is recommended.
- No JS control behavior.
- No client-side dispatch.
- No hidden POST.
- No click-to-execute behavior.

## 20. Future Dashboard Fail-Closed Display Behavior

- If preview object missing = show HOLD / unavailable.
- If validation_status unsafe = show HOLD.
- If required safety labels missing = show HOLD.
- If unsafe safety flag present = show HOLD.
- If timeline missing = show HOLD.
- If timeline out of order = show HOLD.
- If any step unsafe = show HOLD.
- If any forbidden field detected = show HOLD.
- If any control field detected = show HOLD.
- If any ambiguous permission detected = show HOLD.

## 21. Future Route Boundary

- /dashboard/system remains GET-only.
- No POST decorator.
- No new route.
- No new endpoint.
- No webhook.
- No callback receiver.
- No action route.
- No API route for dispatch.
- No API route for writeback.

## 22. Future Sequence

1. v1.0-RC-D Full Loop Read-only Rehearsal Implementation
2. v1.0-RC-E Owner Review / Safety Matrix Check
3. v1.0-RC-R Full Blackboard Loop Rehearsal Closeout

## 23. Safe Next Recommendation

After this plan, Owner may choose v1.0-RC-D Full Loop Read-only Rehearsal Implementation, or HOLD for architecture review.

## 24. Explicit Non-Goals

- no fixture creation
- no adapter implementation
- no Full Blackboard Loop implementation
- no Dashboard timeline display implementation
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

## 25. Safety Reminders

- Display plan is not display implementation.
- Timeline display is not execution.
- Timeline is not dispatch permission.
- Dashboard display is not Owner approval.
- Owner review required is not Owner approval.
- Result Message is not dispatch permission.
- Hermes readback is advisory only.
- Owner approval is still required for any future action.

## 26. Required Safety Statements

- v1.0-RC-C is docs / check-only display plan.
- v1.0-RC-C does not create fixture file.
- No preview adapter implementation occurs in this phase.
- No Full Blackboard Loop implementation occurs in this phase.
- No Dashboard timeline display implementation occurs in this phase.
- No Dashboard controls are added in this phase.
- No app/main.py modification occurs in this phase.
- No templates/system.html modification occurs in this phase.
- No static/dashboard.css modification occurs in this phase.
- No Hermes runtime activation occurs in this phase.
- No Worker dispatch occurs in this phase.
- No OpenClaw call occurs in this phase.
- No Blackboard write occurs in this phase.
- No queue write occurs in this phase.
- No audit trail write occurs in this phase.
- No connector call occurs in this phase.
- No external side effects occur in this phase.
