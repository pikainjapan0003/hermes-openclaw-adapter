# Hermes × OpenClaw Adapter — Demo Task Cleanup Plan (v0.7.4-E)

> **Status: PLAN / DOCS-ONLY.** This version adds one planning document and one
> static readiness check. It plans only the safety boundary, the dry-run / apply
> separation, and the Owner approval gate for demo task cleanup. It changes no
> application code, no templates, no static assets, no existing docs, no README, no
> tests, and no seed script; it deletes no task, modifies no queue data, wires no
> route, implements no runtime guard, adds no cleanup tool runtime, and creates no
> tag. It does not touch the Replit SQLite database and does not clean up or seed
> the demo task.
>
> Boundary declarations:
>
> - v0.7.4-E is documentation / planning only.
> - No demo task cleanup.
> - No cleanup apply.
> - No --apply.
> - No queue write.
> - No POST.
> - No live local queue write validation.
> - No task deletion.
> - No queue DB change.
> - No local queue data change.
> - No Replit queue data change.
> - No QueueStore runtime behavior change.
> - No approval routes change.
> - No dashboard auth change.
> - No status transition change.
> - No runtime guard.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No external side effects.
> - No webhook.

---

## 1. Purpose

This is the **Demo Task Cleanup Plan** for the v0.7.4 line. It plans, as a document
and safety contract only, how demo / sample / preview tasks could in the future be
cleaned up safely: the classification rules, the dry-run report format, the
dry-run / apply separation, and the Owner approval gate. It performs no cleanup, no
`--apply`, no queue write, no POST, and no external side effect.

---

## 2. Current master

```
HEAD = origin/master = 17ddd421b5f1c482e2ca74b0933d11b1bfe2c332
docs: close out audit trail display replit validation
```

---

## 3. Scope

In scope (this segment only):

- Add this planning document.
- Add one static readiness script that asserts the document exists, contains the
  required sections and markers, the fixed dry-run safety values, the Owner
  approval gate, and the boundaries — and carries no unsafe claim and no secret.

Explicitly out of scope: any change to runtime code, templates, static assets,
existing docs, README, tests, the seed script, approval routes, QueueStore, status
transitions, the Worker, or any external system. No cleanup tool runtime, no
cleanup apply command, no task deletion, and no queue data change.

---

## 4. Relationship to v0.7.4-D-R

```
v0.7.4-D-R Audit Trail Display Replit GET-only Validation Closeout is complete.
Replit GET-only validation passed.
No POST was sent.
No queue write validation was performed.
No Worker / OpenClaw / Hermes / Google Sheets was called.
```

---

## 5. Relationship to v0.7.4-D

```
v0.7.4-D Audit Trail Display is complete.
Audit Trail Display is read-only.
Audit Trail Display does not change lifecycle state.
Audit Trail Display does not enforce guard.
Audit Trail Display does not grant execution permission.
Audit Trail Display does not dispatch Worker.
Audit Trail Display does not call OpenClaw.
Audit Trail Display does not call Hermes.
Audit Trail Display does not write Google Sheets.
Result Message remains future-only in v0.7.4-E.
Advice Message remains future-only in v0.7.4-E.
```

---

## 6. Relationship to v0.7.4-C

```
v0.7.4-C State Transition Guard Plan is complete.
State Transition Guard is a safety contract.
v0.7.4-C does not modify current status transitions.
v0.7.4-C does not enforce runtime guards.
```

---

## 7. Relationship to v0.7.4-B

```
v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.
Task Message
Decision Message
Result Message
Advice Message
Decision Message is audit record, not command.
approve is not execute.
Owner decision event is not Worker dispatch.
```

---

## 8. Relationship to v0.7.4-A

```
v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.
GitHub is clean source of code and docs, not queue DB or secrets store.
Windows WSL is primary local development environment.
Replit is remote observation station / Preview Dashboard.
Dashboard update means git pull plus Dashboard restart.
Dashboard update does not start Worker.
Dashboard update does not call OpenClaw.
Dashboard update does not call Hermes.
Dashboard update does not write Google Sheets.
Current Windows WSL local queue and Replit local queue are separate.
```

---

## 9. Why demo task cleanup needs a plan

Demo / sample / preview tasks accumulate during UI validation and route
demonstration. Removing them carelessly risks deleting production-looking work,
losing audit history, or touching the wrong environment. Cleanup therefore needs an
explicit safety contract — classification rules, a dry-run report, and an Owner
approval gate — before any apply path is ever built.

---

## 10. Demo task definition

```
Demo task is a local / preview sample task used for UI validation, route validation, or readiness demonstration.
Demo task is not production work.
Demo task cleanup must not affect production task data.
Demo task cleanup must not be inferred from task name alone.
Demo task cleanup requires explicit classification rules.
```

---

## 11. Cleanup candidate rules

```
A cleanup candidate must be explicitly identified as demo / sample / preview / test data.
A cleanup candidate must be local-only or preview-only.
A cleanup candidate must have no production owner dependency.
A cleanup candidate must not be linked to external execution.
A cleanup candidate must not contain secrets.
A cleanup candidate must not be needed for current validation unless Owner approves replacement.
A cleanup candidate must appear in a dry-run report before apply.
```

---

## 12. Non-cleanup candidate rules

```
Production-looking tasks are not cleanup candidates.
Tasks with unclear origin are not cleanup candidates.
Tasks with external side effect history are not cleanup candidates.
Tasks with missing classification are not cleanup candidates.
Tasks needed for active validation are not cleanup candidates unless replacement is planned.
Tasks containing secrets must not be printed and must not be cleaned by automated tooling.
Tasks in Replit queue must not be cleaned from WSL tooling.
Tasks in remote shared DB are out of scope.
```

---

## 13. Cleanup safety conditions

```
Cleanup Plan is not cleanup apply.
Cleanup dry-run is not cleanup apply.
Cleanup apply requires separate Owner approval.
Cleanup apply requires an explicit apply flag.
Cleanup apply requires a second confirmation flag.
Cleanup apply must be local-only in v0.7.4-F.
Cleanup apply must not touch Replit Preview.
Cleanup apply must not touch production DB.
Cleanup apply must not touch remote shared DB.
Cleanup apply must not call Worker.
Cleanup apply must not call OpenClaw.
Cleanup apply must not call Hermes.
Cleanup apply must not write Google Sheets.
Cleanup apply must not create webhook.
```

---

## 14. Dry-run cleanup report format

A future dry-run cleanup report (v0.7.4-F) carries at least these fields:

```
report_id
generated_at
execution_mode
dry_run
apply_requested
apply_allowed
candidate_count
blocked_count
candidates
blocked_items
reason
source_queue
target_environment
would_delete
would_archive
would_modify
external_side_effects
owner_approval_required
rollback_note
```

The report's fixed safety values are always:

```
dry_run = True
apply_requested = False
apply_allowed = False
external_side_effects = False
owner_approval_required = True
```

---

## 15. Owner approval gate

```
Owner approval for this plan does not approve cleanup apply.
Owner review of dry-run report does not approve cleanup apply.
Cleanup apply requires separate explicit Owner approval.
Cleanup apply requires exact command approval.
Cleanup apply requires local-only target confirmation.
Cleanup apply requires rollback note confirmation.
```

---

## 16. Plan vs dry-run vs apply

```
Plan = documentation and safety contract only.
Dry-run = local read-only candidate report only.
Apply = local data-changing cleanup action, prohibited until separately approved.
```

---

## 17. Local queue vs Replit queue boundary

```
Windows WSL local queue and Replit local queue are separate.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
WSL cleanup tooling must not clean Replit queue.
Replit Preview GET validation must not become POST or cleanup.
Remote shared DB is future-only.
```

---

## 18. QueueStore boundary

```
QueueStore runtime behavior is unchanged in v0.7.4-E.
v0.7.4-E does not modify app/queue_store.py.
v0.7.4-E does not add QueueStore methods.
v0.7.4-E does not delete tasks.
v0.7.4-E does not archive tasks.
v0.7.4-E does not modify payload persistence.
v0.7.4-E does not modify status persistence.
```

---

## 19. Route / POST boundary

```
v0.7.4-E does not add POST routes.
v0.7.4-E does not modify approval POST behavior.
v0.7.4-E does not modify reject POST behavior.
v0.7.4-E does not modify cancel POST behavior.
v0.7.4-E does not modify retry POST behavior.
v0.7.4-E does not modify archive POST behavior.
v0.7.4-E does not add cleanup route.
v0.7.4-E does not add cleanup button.
v0.7.4-E does not add cleanup form.
```

---

## 20. Runtime / external side-effect boundary

v0.7.4-E produces no runtime change and no external side effect: no Worker run, no
OpenClaw call, no Hermes call, no Google Sheets write, no webhook, no network write,
no queue write. It is documentation and a readiness check only.

---

## 21. Forbidden cleanup actions

The following are forbidden in v0.7.4-E and must remain forbidden until a future
segment is separately approved:

- Deleting any task.
- Archiving any task via tooling.
- Modifying any queue DB, local queue data, or Replit queue data.
- Running any cleanup apply command or `--apply`.
- Sending any POST to the Replit Preview or a real queue.
- Performing a live local queue write validation.

---

## 22. Future v0.7.4-F Safe Local Cleanup Tool boundary

```
v0.7.4-F must start with dry-run only.
v0.7.4-F apply must require separate Owner approval.
v0.7.4-F apply must require dual explicit flags.
v0.7.4-F must remain local-only.
v0.7.4-F must not touch Replit Preview.
v0.7.4-F must not touch production DB.
v0.7.4-F must not touch remote shared DB.
v0.7.4-F must not call Worker / OpenClaw / Hermes / Google Sheets.
```

---

## 23. Current safe system posture

```
Dashboard read-only / controlled local route behavior
Worker OFF
OpenClaw Not Connected
Hermes Not Connected
Google Sheets Disabled
No external side effects
No --apply
No demo task cleanup
No seed demo task
No secrets read
No webhook
No tag
```

---

## 24. Tests and readiness

- `scripts/check_hermes_openclaw_demo_task_cleanup_plan_v0_7_4_e.py` — static
  readiness check over the document's sections, markers, fixed dry-run safety
  values, Owner approval gate, and boundaries.

---

## 25. Non-goals

v0.7.4-E explicitly does not:

- Change any runtime code, template, static asset, existing doc, README, or test.
- Change QueueStore runtime behavior, `app/queue_store.py`, approval routes,
  dashboard auth, or any status transition.
- Add a cleanup tool runtime, a cleanup apply command, a cleanup route, button, or
  form.
- Delete, archive, or modify any task, queue DB, local queue data, or Replit queue
  data.
- Run `--apply`, start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external side effect.
- POST to the Replit Preview or a real queue, or perform a live local queue write
  validation.
- Commit, push, or create a release tag.

---

## 26. Acceptance criteria

v0.7.4-E is accepted when:

1. This planning document exists at the documented path and contains sections
   1–27.
2. The readiness script
   `scripts/check_hermes_openclaw_demo_task_cleanup_plan_v0_7_4_e.py` reports PASS.
3. The document records the current master, the v0.7.4-D-R / D / C / B / A
   completion markers, the demo task definition, the cleanup / non-cleanup
   candidate rules, the cleanup safety conditions, the dry-run report format with
   fixed safety values, the Owner approval gate, the plan / dry-run / apply
   distinction, and the boundaries.
4. The document carries no unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime file
   changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 27. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-F — Safe Local Cleanup Tool.**

> v0.7.4-F must start with dry-run only.
> v0.7.4-F apply must require separate Owner approval.
> v0.7.4-F apply must require dual explicit flags.
> v0.7.4-F must remain local-only.
> v0.7.4-F must not touch Replit Preview.
> v0.7.4-F must not touch production DB.
> v0.7.4-F must not touch remote shared DB.
> v0.7.4-F must not call Worker / OpenClaw / Hermes / Google Sheets.
