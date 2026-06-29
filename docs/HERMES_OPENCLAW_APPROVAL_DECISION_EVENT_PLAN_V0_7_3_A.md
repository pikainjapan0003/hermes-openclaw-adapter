# Hermes × OpenClaw Adapter — Approval Decision Event Plan (v0.7.3-A)

> **Status: PLAN / DOCS ONLY.** This document plans an Owner approval decision
> event model. It implements nothing, wires nothing, commits nothing, pushes
> nothing, and migrates no schema. It changes no application code, no templates,
> no static assets, no existing docs, no tests, and no seed script. It does not
> touch the Replit SQLite database and does not clean up the demo task.
>
> Boundary declarations:
>
> - v0.7.3-A is planning / documentation only.
> - No QueueStore runtime behavior changes.
> - No approval wiring changes.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No secrets read.
> - No webhook.
> - No external side effects.
> - No --apply.
> - No demo task cleanup.
> - No approve/reject/cancel/retry/archive clicks.

---

## 1. Purpose

Plan an explicit, auditable **Owner decision event** model so that each Owner
action on a task (approve, reject, cancel, retry, archive, comment,
request_more_info) is recorded as a structured **approval decision event** —
capturing who decided, when, why, the status transition, and a snapshot of the
read-only annotation / approval-readiness context at decision time. This is
design planning; no code changes here.

Crucially, this plan keeps decision strictly separate from execution:
**approve is not execute.** An Owner decision event is a record of a human
decision; it is **not** a Worker dispatch.

---

## 2. Current master

```
current master = 888967cbf2ff644df7c89c20226d0d9a2f5d164c
docs: close out queue task annotation line
```

This plan builds conceptually on the completed v0.7.2-F annotation line.

---

## 3. Scope

In scope (this segment only):

- Add this plan document.
- Add one static readiness script that asserts the document exists, contains the
  required markers and sections 1–21, and carries no unsafe claim.

Explicitly out of scope: any change to runtime code, templates, static assets,
existing docs, tests, the seed script, approval routes, QueueStore, the Worker,
or any external system. No implementation, no schema migration, no wiring.

---

## 4. Relationship to v0.7.2-F annotation line

The v0.7.2-F line (F-A plan, F-B deriver, F-C display, F-C-R / F-R closeouts)
delivered a read-only annotation and `approval_readiness` signal:
**Approval readiness is not execution permission**, and the deriver always
returns `execution_permission = False` and `dispatch_allowed = False`.

v0.7.3-A extends the *record-keeping* story — not the execution story. It plans
how an Owner's decision is captured as an event, alongside a snapshot of the
F-line annotation. It does not change the annotation, the deriver, or the
display, and it does not connect decisions to execution. The decision/execution
separation from the F-line is preserved verbatim:
**Owner approval does not automatically imply Worker execution. Decision and
execution dispatch remain separate.**

---

## 5. Why approval decision events are needed

Today the dashboard drives the QueueStore state machine (waiting_review →
queued / rejected, etc.) and writes a blackboard comment, but there is no single,
structured, auditable record of *the Owner decision itself*: the decision type,
the deciding identity, the timestamp, the reason, the exact status transition,
and the safety/annotation context at that moment. An explicit decision event:

- gives the Owner and any reviewer a clear audit trail of human decisions;
- captures the read-only approval-readiness / annotation snapshot at decision
  time (so later metadata drift cannot rewrite history);
- makes the decision/execution boundary explicit and inspectable — every event
  records `execution_permission = False` and `dispatch_allowed = False`.

It is a record, not a trigger. Recording a decision must never cause execution.

---

## 6. Decision event definition

An **approval decision event** is an immutable, append-only record that an Owner
made a decision about a task at a point in time. It is descriptive metadata for
audit and display; it has no executable effect. Recording the event does not
change runtime behavior, does not dispatch the Worker, and does not call any
external system.

> approve only records an Owner decision event.
> approve does not dispatch Worker.
> approve does not call OpenClaw.
> approve does not call Hermes.
> approve does not write Google Sheets.
> retry does not call external systems.
> archive does not delete external state.

---

## 7. Decision event fields

Planned fields of an approval decision event (future; not added in this segment):

| Field | Meaning |
| --- | --- |
| `decision_id` | Unique id for the decision event (audit key). |
| `task_id` | The task the decision is about. |
| `decision_type` | The decision (see section 8). |
| `decided_by` | Identity label of who decided (not a secret). |
| `decided_at` | Timestamp of the decision (UTC ISO-8601). |
| `decision_reason` | Plain-language reason the Owner gave. |
| `previous_status` | Task status before the decision. |
| `next_status` | Task status after the decision (state-machine only). |
| `approval_readiness_at_decision` | Snapshot of `approval_readiness` at decision time. |
| `execution_permission_at_decision` | Snapshot of execution permission (always `False`). |
| `dispatch_allowed_at_decision` | Snapshot of dispatch allowed (always `False`). |
| `safety_snapshot` | Snapshot of safety_level / requires_confirmation / boundaries. |
| `annotation_snapshot` | Snapshot of the read-only F-line annotation. |
| `audit_record` | The serialized, append-only audit entry for this event. |

All fields are descriptive metadata only — display, audit, and decision-support.
They do not, by themselves, grant execution.

---

## 8. Decision types

Planned decision types:

| Type | Meaning |
| --- | --- |
| `approve` | Owner approves; status moves toward queued (state-machine only). |
| `reject` | Owner rejects; task is recorded as rejected. |
| `cancel` | Owner cancels a queued / waiting task. |
| `retry` | Owner requests retry of a failed task (no external call). |
| `archive` | Owner archives a terminal task (no external delete). |
| `comment` | Owner records a note; no status change. |
| `request_more_info` | Owner asks for more information before deciding. |

For every type, the event is a record only. In particular:

> approve only records an Owner decision event.
> approve does not dispatch Worker.
> approve does not call OpenClaw.
> approve does not call Hermes.
> approve does not write Google Sheets.
> retry does not call external systems.
> archive does not delete external state.

---

## 9. Decision lifecycle

Planned lifecycle of a decision event:

1. Owner views the task (read-only annotation + approval_readiness).
2. Owner makes a decision (one of section 8) via the existing dashboard control.
3. A decision event is recorded (append-only) with the section 7 fields,
   including the `execution_permission = False` / `dispatch_allowed = False`
   snapshots.
4. The existing QueueStore state machine performs only its current transition
   (e.g. waiting_review → queued for approve) — unchanged by this plan.
5. The event is available for audit and future read-only display.

No step in this lifecycle dispatches the Worker or calls an external system. An
**Owner decision event is not Worker dispatch.**

---

## 10. Approval readiness snapshot

`approval_readiness_at_decision` captures the conservative F-line
`approval_readiness` value (not_ready / owner_review_required /
ready_for_owner_decision / blocked_by_policy / prohibited) as it was at decision
time. This is a snapshot for audit; it is descriptive and does not grant
anything. **Approval readiness is not execution permission.**

---

## 11. Execution permission snapshot

`execution_permission_at_decision` records the execution permission at decision
time, which is always unauthorized:

```
execution_permission = False
```

This snapshot is display/audit only and never grants execution. No decision
type, including approve, sets it to true.

---

## 12. Dispatch allowed snapshot

`dispatch_allowed_at_decision` records the dispatch flag at decision time, which
is always not allowed:

```
dispatch_allowed = False
```

This snapshot is display/audit only and never permits Worker dispatch. Recording
an approve decision does not dispatch the Worker.

---

## 13. Safety snapshot

`safety_snapshot` captures the task's safety context at decision time
(safety_level, requires_confirmation, the current safe posture: Worker OFF,
OpenClaw Not Connected, Hermes Not Connected, Google Sheets Disabled). It is a
read-only record; it changes no setting and enables nothing.

---

## 14. Audit trail requirement

Decision events must form an **append-only audit trail**: each `audit_record` is
written once and never mutated, keyed by `decision_id`, ordered by `decided_at`.
The trail must contain no secrets (identities are labels, never tokens or keys).
The audit trail is for accountability and review; it has no executable effect.

---

## 15. Dashboard future display

When implemented (a future, separately-approved segment), the dashboard would
show a read-only decision history per task: decision_type, decided_by,
decided_at, decision_reason, the status transition, and the
approval_readiness / execution_permission / dispatch_allowed snapshots — all
read-only, Chinese-first with English/code sublabels, reusing existing styles.
No new route is required for display, and display grants no execution.

---

## 16. Queue metadata future storage

Decision events would be stored as append-only audit metadata (e.g. a decision
log alongside the existing blackboard / audit mechanisms, or inside
`payload.metadata` history), **without** changing the SQLite schema. No new
columns and no `QueueStore` runtime behavior change are required by this plan;
any indexed-column storage would be a separate, explicitly-approved migration —
out of scope here.

---

## 17. Boundaries

- No QueueStore runtime behavior changes.
- No approval wiring changes.
- No Worker execution.
- No OpenClaw call.
- No Hermes call.
- No Google Sheets write.
- No external side effects.
- No secrets read.
- No webhook.
- No --apply.
- No demo task cleanup.
- No approve/reject/cancel/retry/archive clicks.

Core separation restated: **approve is not execute. Owner decision event is not
Worker dispatch. Owner approval does not automatically imply Worker execution.
Decision and execution dispatch remain separate. Approval readiness is not
execution permission.** Every decision event records `execution_permission =
False` and `dispatch_allowed = False`.

---

## 18. Non-goals

v0.7.3-A explicitly does not:

- Implement decision events, fields, storage, or display (plan only).
- Change approval wiring or any POST action behavior.
- Change QueueStore runtime behavior, add routes, or migrate schema.
- Make approve (or any decision) dispatch the Worker or call OpenClaw / Hermes /
  Google Sheets.
- Start the Worker, read secrets, create a webhook, or add any dependency.
- Seed (`--apply`) or clean up the demo task.
- Click approve/reject/cancel/retry/archive.
- Create a release tag.

---

## 19. Acceptance criteria

v0.7.3-A is accepted when:

1. This plan document exists at the documented path and contains sections 1–21.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_event_plan_v0_7_3_a.py`
   exists and reports PASS.
3. The plan defines the decision event (sections 6–9), its fields, decision
   types, and the approval-readiness / execution-permission / dispatch-allowed /
   safety snapshots, and restates the decision/execution separation.
4. The plan states the boundaries and non-goals and carries no unsafe claim and
   no secret.
5. The segment adds only this document and the readiness script — no runtime
   file changed.
6. Nothing is committed, pushed, or tagged in this segment without Owner
   approval.

---

## 20. Next recommended step

Recommended next step (each requires explicit Owner approval to start):

1. Owner-approved local commit of this plan, then push only after Owner approval.
2. A future v0.7.3-B segment to implement a **read-only** decision-event recorder
   (pure / append-only audit, no wiring to execution), with unit tests and a
   readiness script — separately planned and approved.

Execution dispatch wiring remains explicitly **out** of this feature line.

---

## 21. Final planning statement

This document plans the Owner approval decision event model only. It implements
nothing and connects no decision to execution.

```
approve is not execute.
Owner decision event is not Worker dispatch.
Owner approval does not automatically imply Worker execution.
Decision and execution dispatch remain separate.
Approval readiness is not execution permission.
execution_permission = False.
dispatch_allowed = False.
```

The system remains in its safe posture: Dashboard read-only, Worker OFF,
OpenClaw / Hermes not connected, Google Sheets disabled, no external side
effects.
