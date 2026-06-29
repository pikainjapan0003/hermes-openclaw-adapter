# Hermes × OpenClaw Adapter — State Transition Guard Plan (v0.7.4-C)

> **Status: PLAN / CURRENT-STATE ONLY.** This version adds one planning document
> and one static readiness check. It changes no application code, no templates, no
> static assets, no `app/main.py`, no `app/queue_store.py`, no existing docs, no
> README, no tests, and no seed script; it wires no route, migrates no schema,
> builds no database, creates no connector, implements no runtime guard, and
> creates no tag. It does not touch the Replit SQLite database, does not change any
> existing transition result, and does not clean up or seed the demo task.
>
> Boundary declarations:
>
> - v0.7.4-C is documentation / planning only.
> - No QueueStore runtime behavior changes.
> - No approval routes changes.
> - No dashboard auth changes.
> - No status transition changes.
> - No runtime guard implementation.
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
> - No production DB.
> - No remote shared DB.
> - No Remote Blackboard API runtime.
> - No webhook receiver.

---

## 1. Purpose

This is the **State Transition Guard Plan** for the v0.7.4 line. It defines, as a
plan / current-state document, the legal state-transition rules and the safety
boundary for a future runtime guard: the guard's purpose, the unchanged current
state model, the planned lifecycle vocabulary, the proposed allowed and blocked
transitions, the Owner decision / dispatch candidate / Worker / OpenClaw / Hermes /
Dashboard / QueueStore boundaries, the runtime implementation boundary, the local-
vs-Replit queue boundary, and the Remote Blackboard future direction. It performs
no code change, enables no runtime behavior, implements no guard, and recommends no
release tag.

---

## 2. Current master

```
HEAD = origin/master = 0c3f80ce59bd44a180cbef7a7fff0070de85e61a
docs: plan queue blackboard lifecycle
```

---

## 3. Scope

In scope (this segment only):

- Add this planning document.
- Add one static readiness script that asserts the document exists, contains the
  required sections (1–24), the current-master marker, the v0.7.4-B / v0.7.4-A /
  v0.7.3-R completion markers, the guard purpose, the unchanged-status-model
  markers, the lifecycle vocabulary, the allowed / blocked transition rules, the
  boundary markers, the safe posture, and the next recommended step — and carries
  no unsafe claim and no secret.

Explicitly out of scope: any change to runtime code, templates, static assets,
`app/main.py`, `app/queue_store.py`, existing docs, README, tests, the seed
script, approval routes, dashboard auth, QueueStore, status transitions, the
Worker, or any external system. No runtime guard, no production DB, no remote
shared DB, no Remote Blackboard API runtime, no webhook receiver, and no new
connector are created.

---

## 4. Relationship to v0.7.4-B

v0.7.4-C builds directly on the v0.7.4-B lifecycle plan, which stays unchanged:

```
v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.
Task Message
Decision Message
Result Message
Advice Message
Queue lifecycle is a planning model in v0.7.4-B.
Queue lifecycle does not change runtime status transitions in v0.7.4-B.
Queue lifecycle prepares v0.7.4-C State Transition Guard.
```

v0.7.4-C translates the v0.7.4-B lifecycle vocabulary into proposed transition
rules; it does not change that lifecycle plan.

---

## 5. Relationship to v0.7.4-A

v0.7.4-C builds on the v0.7.4-A topology plan, which stays unchanged:

```
v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.
Replit is a remote observation station / Preview Dashboard.
Dashboard update means git pull plus Dashboard restart.
Dashboard update does not start Worker.
The core blackboard loop should not depend on whether Replit Dashboard is updated.
Current Windows WSL local queue and Replit local queue are separate.
Remote Blackboard API / shared DB is future planning only.
```

---

## 6. Relationship to v0.7.3-R

v0.7.4-C builds on the completed Approval Decision Layer, which stays unchanged:

```
v0.7.3 Approval Decision Layer is complete.
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records, not execution commands.
approve is not execute.
Owner decision event is not Worker dispatch.
```

---

## 7. Guard purpose

```
State Transition Guard defines allowed and blocked transitions before runtime enforcement.
State Transition Guard is a safety contract.
State Transition Guard is not Worker dispatch.
State Transition Guard is not OpenClaw execution.
State Transition Guard is not Hermes execution.
State Transition Guard is not Google Sheets write.
```

The guard is a written safety contract over which transitions are legal. Defining
it changes nothing at runtime.

---

## 8. Current state model

```
Current runtime status model remains unchanged in v0.7.4-C.
v0.7.4-C does not modify current status transitions.
v0.7.4-C does not enforce runtime guards.
v0.7.4-C only plans guard rules.
```

The existing runtime status model and its transitions are untouched. This document
plans guard rules on top of the v0.7.4-B planning vocabulary, not on top of the
runtime status column.

---

## 9. Planned lifecycle vocabulary

The v0.7.4-B planning vocabulary (plan-only; not runtime states):

```
draft_or_created
annotated
owner_review
owner_decided
dispatch_candidate
dry_run_claimed
dry_run_result_recorded
advice_recorded
archived_or_closed
```

---

## 10. Proposed allowed transitions

```
draft_or_created -> annotated
annotated -> owner_review
owner_review -> owner_decided
owner_decided -> dispatch_candidate
dispatch_candidate -> dry_run_claimed
dry_run_claimed -> dry_run_result_recorded
dry_run_result_recorded -> advice_recorded
advice_recorded -> owner_review
owner_review -> archived_or_closed
owner_decided -> archived_or_closed
```

```
Proposed allowed transitions are planning rules only in v0.7.4-C.
They are not runtime-enforced in v0.7.4-C.
```

---

## 11. Proposed blocked transitions

```
draft_or_created -> dry_run_claimed is blocked.
annotated -> dry_run_claimed is blocked.
owner_review -> dry_run_claimed is blocked.
owner_review -> dry_run_result_recorded is blocked.
owner_decided -> dry_run_result_recorded is blocked unless future Worker dry-run claim exists.
Decision Message -> Worker dispatch is blocked.
Advice Message -> Worker dispatch is blocked.
Dashboard display -> lifecycle mutation is blocked.
GitHub push -> queue mutation is blocked.
Replit pull -> queue mutation is blocked.
```

These blocked transitions are planning rules only; v0.7.4-C enforces none of them
at runtime.

---

## 12. Owner decision transition boundary

```
Owner decision may move a task toward owner_decided.
Owner decision may not directly move a task to dry_run_claimed.
Owner decision may not directly move a task to dry_run_result_recorded.
Owner decision may not directly dispatch Worker.
Owner decision may not call OpenClaw.
Owner decision may not call Hermes.
Owner decision may not write Google Sheets.
```

An Owner decision records a Decision Message and may move a task toward
`owner_decided`; it never crosses into a dry-run claim, a result record, or any
dispatch.

---

## 13. Dispatch candidate boundary

```
dispatch_candidate is future planning only in v0.7.4-C.
dispatch_candidate is not execution permission.
dispatch_candidate is not dispatch_allowed.
dispatch_candidate is not Worker claim.
dispatch_candidate is not OpenClaw command.
execution_permission = False
dispatch_allowed = False
```

`dispatch_candidate` is a planning label for a task an Owner has decided may, in
the future, be considered for a dry-run. It grants nothing.

---

## 14. Worker / OpenClaw boundary

```
Worker / OpenClaw boundary is future planning only in v0.7.4-C.
Worker must not run in v0.7.4-C.
OpenClaw must not be called in v0.7.4-C.
No task is claimed by Worker in v0.7.4-C.
No task is dispatched to OpenClaw in v0.7.4-C.
```

In the future model the Worker / OpenClaw may only read executable candidates; in
v0.7.4-C the Worker does not run and OpenClaw is not called at all.

---

## 15. Hermes advice boundary

```
Hermes advice boundary is future planning only in v0.7.4-C.
Hermes must not be called in v0.7.4-C.
Hermes Advice Message must not approve tasks.
Hermes Advice Message must not dispatch tasks.
Hermes Advice Message must not write external systems.
Owner remains the approval authority.
```

---

## 16. Dashboard display boundary

```
Dashboard may display planned lifecycle state.
Dashboard display does not change lifecycle state.
Dashboard display does not enforce guard.
Dashboard display does not grant execution permission.
Dashboard display does not dispatch Worker.
Dashboard display does not call OpenClaw.
Dashboard display does not call Hermes.
Dashboard display does not write Google Sheets.
```

The Dashboard is a read surface. Showing a planned lifecycle state never changes
it, never enforces the guard, and never causes any external side effect.

---

## 17. QueueStore boundary

```
QueueStore runtime behavior is unchanged in v0.7.4-C.
v0.7.4-C does not modify app/queue_store.py.
v0.7.4-C does not add QueueStore methods.
v0.7.4-C does not change status persistence.
v0.7.4-C does not change payload persistence.
```

---

## 18. Runtime implementation boundary

```
Runtime guard implementation is future work after v0.7.4-C.
v0.7.4-C does not implement runtime guard.
v0.7.4-C does not add route enforcement.
v0.7.4-C does not change approval behavior.
v0.7.4-C does not change archive behavior.
v0.7.4-C does not change retry behavior.
```

A runtime guard — code that enforces the allowed / blocked transitions — is future
work that requires separate Owner approval. v0.7.4-C only writes the contract.

---

## 19. Local queue vs Replit queue boundary

```
Current Windows WSL local queue and Replit local queue are separate.
They do not automatically sync.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
A shared blackboard requires a future Remote Blackboard API or shared DB.
```

---

## 20. Remote Blackboard future path

```
Remote Blackboard API / shared DB is future planning only in v0.7.4-C.
v0.7.4-C does not implement production DB.
v0.7.4-C does not migrate queues.
v0.7.4-C does not enable shared writes.
v0.7.4-C does not create webhooks.
v0.7.4-C does not start Worker.
```

---

## 21. Current safe system posture

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

## 22. Non-goals

v0.7.4-C explicitly does not:

- Change any runtime code, template, static asset, `app/main.py`, or
  `app/queue_store.py`.
- Change QueueStore runtime behavior, approval routes, dashboard auth, or any
  status transition.
- Implement a runtime guard, add route enforcement, or change approval / archive /
  retry behavior.
- Modify the seed script, existing docs, or the README.
- Add a route, migrate schema, or build a production DB / remote shared DB.
- Implement a Remote Blackboard API runtime, a webhook receiver, or any connector.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external side effect.
- Seed (`--apply`) or clean up the demo task.
- Perform a live local queue write validation.
- Commit, push, or create a release tag.

---

## 23. Acceptance criteria

v0.7.4-C is accepted when:

1. This planning document exists at the documented path and contains sections
   1–24.
2. The readiness script
   `scripts/check_hermes_openclaw_state_transition_guard_plan_v0_7_4_c.py`
   reports PASS.
3. The document records the current master, the v0.7.4-B / v0.7.4-A / v0.7.3-R
   completion markers, the guard purpose, the unchanged current state model, the
   lifecycle vocabulary, the proposed allowed and blocked transitions, the Owner
   decision / dispatch candidate / Worker / OpenClaw / Hermes / Dashboard /
   QueueStore / runtime boundaries, the local-vs-Replit queue boundary, the Remote
   Blackboard future-only direction, and the safe posture.
4. The document states the non-goals and carries no unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime file
   changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 24. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-D — Audit Trail Display.**

> v0.7.4-D should remain display-only unless separately approved.
> It should display lifecycle / audit trail information without changing state.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.

Runtime guard implementation, execution dispatch wiring, production DB, shared
writes, and any Remote Blackboard API runtime remain explicitly **out** of this
feature line.
