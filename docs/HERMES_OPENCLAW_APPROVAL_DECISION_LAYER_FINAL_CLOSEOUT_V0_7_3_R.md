# Hermes × OpenClaw Adapter — Approval Decision Layer Full Closeout (v0.7.3-R)

> **Status: CLOSEOUT / CURRENT-STATE ONLY.** This version adds a final closeout
> document and a static readiness check for the whole v0.7.3 Approval Decision
> Layer (A → B → B-R → C → C-R). It changes no application code, no templates,
> no static assets, no existing docs, no tests, and no seed script; it wires no
> route, migrates no schema, and creates no tag. It does not touch the Replit
> SQLite database and does not clean up the demo task.
>
> Boundary declarations:
>
> - v0.7.3-R is documentation / current-state only.
> - No QueueStore runtime behavior changes.
> - No approval wiring changes.
> - No status transition changes.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No external side effects.
> - No --apply.
> - No demo task cleanup.
> - No seed demo task.
> - No secrets read.
> - No webhook.
> - No POST to Replit Preview or real queue.

---

## 1. Purpose

This is the **Approval Decision Layer Full Closeout** for the v0.7.3 line. It
consolidates the five segments — A (plan), B (read-only view), B-R (view
closeout), C (local recorder), C-R (recorder closeout) — into a single
current-state record and states the final boundary: the system now records and
displays Owner approval decision events as **local audit metadata**, while
execution remains entirely separate and disabled. It performs no code change and
recommends no release tag.

---

## 2. Current master

```
HEAD = origin/master = 329fcd836eeed2e02724eb78f4823ca378f9eb11
docs: close out approval decision recorder validation
```

---

## 3. Scope

In scope (this segment only):

- Add this final closeout / current-state document.
- Add one static readiness script that asserts the document exists, contains the
  required markers, sections 1–22, and the commit chain, and carries no unsafe
  claim.

Explicitly out of scope: any change to runtime code, templates, static assets,
existing docs, tests, the seed script, approval routes, QueueStore, the Worker,
or any external system.

---

## 4. v0.7.3 line summary

The v0.7.3 Approval Decision Layer commit chain:

```
e316760 docs: plan approval decision events
7fd09df feat: add read-only approval decision event view
3414456 docs: close out approval decision event view validation
c0417b4 feat: add local approval decision event recorder
329fcd8 docs: close out approval decision recorder validation
```

Completed segments:

```
v0.7.3-A Approval Decision Event Plan complete
v0.7.3-B Read-only Approval Event View complete
v0.7.3-B-R Replit Preview View Closeout complete
v0.7.3-C Local Approval Event Recorder complete
v0.7.3-C-R Replit GET-only Recorder Closeout complete
```

Each segment preserved the v0.7.x safety envelope: read-only / local-only,
Owner-gated, Worker OFF. Decision support and recording never crossed into
execution.

---

## 5. v0.7.3-A closeout

v0.7.3-A (`e316760`, Approval Decision Event Plan) planned the Owner approval
decision event model: the event fields (the contract in section 10), the decision
types (approve / reject / cancel / retry / archive / comment / request_more_info),
the decision lifecycle, and the snapshots — and established that **approve is not
execute** and **Owner approval does not automatically imply Worker execution**.

---

## 6. v0.7.3-B closeout

v0.7.3-B (`7fd09df`, Read-only Approval Event View) added the pure read-only view
helper `derive_approval_decision_event_view`, read-only context wiring, and the
display-only "Owner 決策紀錄 / Approval Decision Events" surfaces on task detail
and the Owner Review list — with the empty state and the decision/execution
separation reminders. It recorded nothing.

---

## 7. v0.7.3-B-R closeout

v0.7.3-B-R (`3414456`, Replit Preview View Closeout) recorded the Replit Preview
validation of the v0.7.3-B read-only view: after pulling and restarting the
preview server, `/dashboard/reviews` and `/dashboard/tasks/demo-ui-e-b-review-001`
rendered the read-only decision-event view (empty state, unauthorized
execution_permission / dispatch_allowed) — GET-only, no controls clicked.

---

## 8. v0.7.3-C closeout

v0.7.3-C (`c0417b4`, Local Approval Event Recorder) added a local, append-only
recorder (`build_approval_decision_event` /
`append_approval_decision_event_to_payload`) wired into the existing Owner
decision routes, plus one narrow QueueStore method
(`append_approval_decision_event`) that updates only the `payload` column. It
appends audit events to `payload.metadata.approval_decision_events` and never
changes a status transition, never dispatches the Worker, and never calls an
external system.

---

## 9. v0.7.3-C-R closeout

v0.7.3-C-R (`329fcd8`, Replit GET-only Recorder Closeout) recorded the Replit
Preview GET-only regression of the v0.7.3-C recorder:

```
v0.7.3-C pushed and passed Replit Preview GET-only regression.
Live local queue write validation not performed.
Live local queue write validation not required unless separately approved by Owner.
No POST to Replit Preview or real queue.
No approve/reject/cancel/retry/archive clicks.
```

The recorder's live append path was validated only locally (temp SQLite /
in-process TestClient in v0.7.3-C), never against the Replit Preview or a real
queue.

---

## 10. Approval decision event contract

Each approval decision event carries the v0.7.3-A contract fields:

```
decision_id
task_id
decision_type
decided_by
decided_at
decision_reason
previous_status
next_status
approval_readiness_at_decision
execution_permission_at_decision
dispatch_allowed_at_decision
safety_snapshot
annotation_snapshot
audit_record
```

`execution_permission_at_decision` and `dispatch_allowed_at_decision` are always
`False`.

---

## 11. Read-only view summary

The v0.7.3-B view (`derive_approval_decision_event_view`) reads
`payload.metadata.approval_decision_events` and renders, read-only: the event
list (or empty state) with decision_type, decided_by, decided_at, the status
transition, and the unauthorized execution_permission / dispatch_allowed markers.
It records nothing and grants nothing.

---

## 12. Local append-only recorder summary

The v0.7.3-C recorder appends Owner decision events to
`payload.metadata.approval_decision_events` (local audit metadata) after the
existing status transition. It is append-only (preserves and never modifies
existing events, never touches unrelated metadata, copy-on-write), local-only,
and never dispatches the Worker or calls an external system. Every appended event
has `execution_permission_at_decision = False` and
`dispatch_allowed_at_decision = False`.

---

## 13. Replit validation summary

Replit Preview validation is complete for both display (B-R) and recorder (C-R):
GET-only regressions of `/dashboard/reviews` and
`/dashboard/tasks/demo-ui-e-b-review-001` passed after restarts. No POST was sent
to the Replit Preview or a real queue; no approve/reject/cancel/retry/archive was
clicked; no live local queue write validation was performed.

---

## 14. Decision Message positioning

```
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records.
Decision Messages are not Worker commands.
Decision Messages are not OpenClaw commands.
Decision Messages are not Hermes instructions.
```

A Decision Message records that an Owner made a decision; it is an audit entry,
not an instruction to any executor.

---

## 15. Dispatch separation boundary

```
approve is not execute.
Owner decision event is not Worker dispatch.
Owner approval does not automatically imply Worker execution.
Decision and execution dispatch remain separate.
Approval readiness is not execution permission.
execution_permission_at_decision = False
dispatch_allowed_at_decision = False
execution_permission = False
dispatch_allowed = False
```

Recording or displaying a Decision Message never dispatches the Worker and never
grants execution.

---

## 16. QueueStore boundary

The only QueueStore change in the v0.7.3 line is the one narrow method
`append_approval_decision_event` (v0.7.3-C), which updates only the `payload`
column via the existing private `_update`. No schema migration, no status change,
no enqueue/dequeue/Worker-semantics change, and no existing method behavior was
modified.

---

## 17. External side-effect boundary

The v0.7.3 line produced no external side effect: no OpenClaw call, no Hermes
call, no Google Sheets write, no webhook, no network call, no secrets read. All
writes are local audit metadata in the local SQLite `payload` column.

---

## 18. Safety confirmations

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

## 19. Non-goals

v0.7.3-R explicitly does not:

- Change any runtime code, template, or static asset.
- Change QueueStore runtime behavior, approval routes, dashboard auth, or any
  status transition.
- Add a route or migrate schema.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external dependency.
- Seed (`--apply`) or clean up the demo task.
- POST to the Replit Preview or a real queue, or perform a live local queue write
  validation.
- Create a release tag.

---

## 20. Acceptance criteria

v0.7.3-R is accepted when:

1. This final closeout document exists at the documented path and contains
   sections 1–22.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_layer_final_closeout_v0_7_3_r.py`
   reports PASS.
3. The document records the commit chain, the A/B/B-R/C/C-R completion, the event
   contract, the Decision Message positioning, the dispatch separation, and the
   C-R GET-only state.
4. The document states the safety confirmations and non-goals and carries no
   unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime
   file changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 21. Final closeout statement

```
v0.7.3 Approval Decision Layer is complete.
The system now has an Owner approval decision event contract, a read-only display, and a local append-only recorder.
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records, not execution commands.
approve is not execute.
Owner decision event is not Worker dispatch.
No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.
```

The system remains in its safe posture: Dashboard read-only / controlled local
route behavior, Worker OFF, OpenClaw Not Connected, Hermes Not Connected, Google
Sheets Disabled, no external side effects.

---

## 22. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-A — Core Topology / Dashboard Update / Core Independence Plan.**

> v0.7.4-A must remain docs / readiness only.
> It should define Replit / GitHub / Windows WSL / Dashboard Update / Core Independence boundaries.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.

Execution dispatch wiring remains explicitly **out** of this feature line.
