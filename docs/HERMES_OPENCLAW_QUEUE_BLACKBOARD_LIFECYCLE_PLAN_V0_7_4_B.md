# Hermes × OpenClaw Adapter — Queue / Blackboard Lifecycle Plan (v0.7.4-B)

> **Status: PLAN / DOCS-ONLY.** This version adds one planning document and one
> static readiness check. It changes no application code, no templates, no static
> assets, no `app/main.py`, no `app/queue_store.py`, no existing docs, no README,
> no tests, and no seed script; it wires no route, migrates no schema, builds no
> database, creates no connector, and creates no tag. It does not touch the Replit
> SQLite database and does not clean up or seed the demo task.
>
> Boundary declarations:
>
> - v0.7.4-B is documentation / planning only.
> - No QueueStore runtime behavior changes.
> - No approval routes changes.
> - No dashboard auth changes.
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
> - No production DB.
> - No remote shared DB.
> - No Remote Blackboard API runtime.
> - No webhook receiver.

---

## 1. Purpose

This is the **Queue / Blackboard Lifecycle Plan** for the v0.7.4 line. It is a
planning document that formally defines the Blackboard / Queue lifecycle as a
plan-only model: the role of each Blackboard message kind (Task / Decision /
Result / Advice), the position of Owner Review and Decision Messages, the rule that
the Worker / OpenClaw may only read executable candidates and is never triggered
directly by an approval, the future direction for Result Messages written back to
the Blackboard and for Hermes Advice Messages, the relationship between the queue
lifecycle and the Dashboard display, and the preconditions for the v0.7.4-C State
Transition Guard. It performs no code change, enables no runtime behavior, and
recommends no release tag.

---

## 2. Current master

```
HEAD = origin/master = 1c507b995f44264bf973bd196e35d9ee8a88e983
docs: plan core topology and dashboard independence
```

---

## 3. Scope

In scope (this segment only):

- Add this planning document.
- Add one static readiness script that asserts the document exists, contains the
  required sections (1–24), the current-master marker, the v0.7.4-A and v0.7.3-R
  completion markers, the message-family / lifecycle / boundary / future markers,
  the safe posture, and the next recommended step — and carries no unsafe claim and
  no secret.

Explicitly out of scope: any change to runtime code, templates, static assets,
`app/main.py`, `app/queue_store.py`, existing docs, README, tests, the seed
script, approval routes, dashboard auth, QueueStore, status transitions, the
Worker, or any external system. No production DB, no remote shared DB, no Remote
Blackboard API runtime, no webhook receiver, and no new connector are created.

---

## 4. Relationship to v0.7.4-A

v0.7.4-B builds directly on the v0.7.4-A topology plan, which stays unchanged:

```
v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.
GitHub is the clean source of truth for code and docs.
Windows WSL is the primary local development environment.
Replit is a remote observation station / Preview Dashboard.
Dashboard update means git pull plus Dashboard restart.
Dashboard update does not start Worker.
Dashboard update does not call OpenClaw.
Dashboard update does not call Hermes.
Dashboard update does not write Google Sheets.
The core blackboard loop should not depend on whether Replit Dashboard is updated.
Current Windows WSL local queue and Replit local queue are separate.
Remote Blackboard API / shared DB is future planning only.
```

v0.7.4-B refines the lifecycle inside that topology; it does not change the
topology itself.

---

## 5. Relationship to v0.7.3-R

v0.7.4-B builds on the completed Approval Decision Layer, which stays unchanged:

```
v0.7.3 Approval Decision Layer is complete.
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records, not execution commands.
approve is not execute.
Owner decision event is not Worker dispatch.
No Worker / OpenClaw / Hermes / Google Sheets execution was enabled.
```

The Decision Message family member is already implemented (local append-only audit
metadata). v0.7.4-B positions it within the full lifecycle without altering it.

---

## 6. Blackboard lifecycle summary

The Blackboard is the shared record around which the system revolves. A task is
written as a Task Message, annotated, reviewed by the Owner, and recorded as a
Decision Message; in the future a Result Message records an outcome and an Advice
Message records Hermes guidance. Every kind is an additive record on the
Blackboard. The lifecycle below is a **planning model only** — it describes how the
records relate, not a runtime state machine that v0.7.4-B enforces.

---

## 7. Queue lifecycle summary

```
Queue lifecycle is a planning model in v0.7.4-B.
Queue lifecycle does not change runtime status transitions in v0.7.4-B.
Queue lifecycle does not enforce new state guards in v0.7.4-B.
Queue lifecycle prepares v0.7.4-C State Transition Guard.
```

The suggested lifecycle stages (plan-only; not runtime states in v0.7.4-B):

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

These names are a planning vocabulary for v0.7.4-C. v0.7.4-B does not add, rename,
or enforce any runtime status; the existing QueueStore behavior is untouched.

---

## 8. Message family overview

The Blackboard carries four message kinds:

```
Task Message
Decision Message
Result Message
Advice Message
```

- **Task Message** — proposed work (exists today as queue tasks + annotations).
- **Decision Message** — an Owner decision, recorded as audit metadata (exists
  today as `approval_decision_events`).
- **Result Message** — a future execution / dry-run outcome record.
- **Advice Message** — a future Hermes guidance record.

---

## 9. Task Message lifecycle

```
Task Message describes proposed work.
Task Message is not automatically executable.
Task Message requires Owner review before any future dispatch.
Task Message may carry annotation, approval_readiness, safety_snapshot, and audit metadata.
Task Message does not call Worker.
Task Message does not call OpenClaw.
Task Message does not call Hermes.
Task Message does not write Google Sheets.
```

A Task Message is a proposal on the Blackboard. It moves toward a possible future
dispatch only through Owner Review; it never executes itself.

---

## 10. Decision Message lifecycle

```
Decision Message records an Owner decision.
Decision Message is an audit record.
Decision Message is not a Worker command.
Decision Message is not an OpenClaw command.
Decision Message is not a Hermes instruction.
Decision Message does not grant execution permission.
Decision Message does not dispatch.
approval_decision_events are Decision Messages.
```

A Decision Message records that an Owner decided something. It is an audit entry on
the Blackboard, never an instruction to an executor.

---

## 11. Result Message lifecycle

```
Result Message records an execution result or dry-run result.
Result Message is future planning only in v0.7.4-B.
Result Message does not exist as a live Worker output yet.
Result Message must be append-only when implemented.
Result Message must not erase Task Message or Decision Message history.
Result Message must not contain secrets.
```

A Result Message is the future record of what an execution or dry-run produced. It
is described here only as direction; v0.7.4-B implements none of it.

---

## 12. Advice Message lifecycle

```
Advice Message records Hermes guidance.
Advice Message is future planning only in v0.7.4-B.
Advice Message is advisory, not approval.
Advice Message is not an Owner decision.
Advice Message is not Worker dispatch.
Advice Message must not bypass Owner Review.
```

An Advice Message is the future record of Hermes guidance derived from results. It
advises; it never approves or dispatches, and the Owner remains the authority.

---

## 13. Owner Review boundary

Owner Review sits between a Task Message and any possible future dispatch. The
Owner reviews proposed work and records a Decision Message. Owner Review is the
only path by which a task may ever become a dispatch candidate, and even then a
dispatch candidate is future planning only — recording a decision does not
dispatch anything.

---

## 14. Dispatch separation boundary

```
approve is not execute.
Owner decision event is not Worker dispatch.
Owner approval does not automatically imply Worker execution.
Decision and execution dispatch remain separate.
Approval readiness is not execution permission.
Decision Message is not dispatch permission.
dispatch_candidate is future planning only.
execution_permission = False
dispatch_allowed = False
execution_permission_at_decision = False
dispatch_allowed_at_decision = False
```

Decision and execution dispatch remain strictly separate. No Blackboard record
grants execution.

---

## 15. Worker / OpenClaw read boundary

```
Worker / OpenClaw read boundary is future planning only in v0.7.4-B.
Worker must not run in v0.7.4-B.
OpenClaw must not be called in v0.7.4-B.
No task is claimed by Worker in v0.7.4-B.
No task is dispatched to OpenClaw in v0.7.4-B.
```

In the future model, the Worker / OpenClaw may only **read** executable candidates
from the Blackboard; it is never triggered directly by an approval. In v0.7.4-B the
Worker does not run and OpenClaw is not called at all.

---

## 16. Hermes advice boundary

```
Hermes advice boundary is future planning only in v0.7.4-B.
Hermes must not be called in v0.7.4-B.
Hermes Advice Message must not approve tasks.
Hermes Advice Message must not dispatch tasks.
Hermes Advice Message must not write external systems.
Owner remains the approval authority.
```

Hermes, in the future model, contributes Advice Messages only. It never approves,
dispatches, or writes external systems, and in v0.7.4-B it is not called.

---

## 17. Dashboard display boundary

```
Dashboard may display lifecycle state.
Dashboard display does not change lifecycle state.
Dashboard display does not grant execution permission.
Dashboard display does not dispatch Worker.
Dashboard display does not call OpenClaw.
Dashboard display does not call Hermes.
Dashboard display does not write Google Sheets.
```

The Dashboard is a read surface over the lifecycle. Showing a state never changes
it and never causes any external side effect.

---

## 18. Local queue vs Replit queue boundary

```
Current Windows WSL local queue and Replit local queue are separate.
They do not automatically sync.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
A shared blackboard requires a future Remote Blackboard API or shared DB.
```

The lifecycle model applies independently to each local queue today. A shared
lifecycle across environments requires a future shared backend.

---

## 19. Remote Blackboard future path

```
Remote Blackboard API / shared DB is future planning only in v0.7.4-B.
v0.7.4-B does not implement production DB.
v0.7.4-B does not migrate queues.
v0.7.4-B does not enable shared writes.
v0.7.4-B does not create webhooks.
v0.7.4-B does not start Worker.
```

A Remote Blackboard API / shared DB is the eventual path to a single shared
lifecycle, described here only as direction. This segment implements none of it.

---

## 20. State Transition Guard preparation

v0.7.4-B is the planning groundwork for **v0.7.4-C — State Transition Guard**. The
lifecycle vocabulary (section 7), the message family (section 8), the dispatch
separation (section 14), and the read / advice / display boundaries (sections
15–17) are the inputs that v0.7.4-C will translate into guarded transition rules.
v0.7.4-B adds no guard, enforces no transition, and changes no runtime status.

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

v0.7.4-B explicitly does not:

- Change any runtime code, template, static asset, `app/main.py`, or
  `app/queue_store.py`.
- Change QueueStore runtime behavior, approval routes, dashboard auth, or any
  status transition.
- Add or enforce any new lifecycle state or state guard.
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

v0.7.4-B is accepted when:

1. This planning document exists at the documented path and contains sections
   1–24.
2. The readiness script
   `scripts/check_hermes_openclaw_queue_blackboard_lifecycle_plan_v0_7_4_b.py`
   reports PASS.
3. The document records the current master, the v0.7.4-A and v0.7.3-R completion
   markers, the message family, the Task / Decision / Result / Advice lifecycles,
   the dispatch separation, the Worker / OpenClaw read boundary, the Hermes advice
   boundary, the Dashboard display boundary, the local-vs-Replit queue boundary,
   the Remote Blackboard future-only direction, the State Transition Guard
   preparation, and the safe posture.
4. The document states the non-goals and carries no unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime file
   changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 24. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-C — State Transition Guard.**

> v0.7.4-C must remain Owner-approved.
> It should translate the v0.7.4-B lifecycle plan into guarded transition rules.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.

Execution dispatch wiring, production DB, shared writes, and any Remote Blackboard
API runtime remain explicitly **out** of this feature line.
