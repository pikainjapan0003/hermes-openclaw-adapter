# Hermes × OpenClaw Adapter — Local Approval Event Recorder (v0.7.3-C)

> **Status: LOCAL / APPEND-ONLY RECORDER.** This version adds a local,
> append-only Owner approval decision event recorder wired into the existing
> Owner decision routes. It appends an audit event to
> `payload.metadata.approval_decision_events`; it adds no route, changes no route
> path / method, changes no status transition result, dispatches no Worker, and
> calls no external system.
>
> Boundary declarations:
>
> - v0.7.3-C is a local append-only recorder of audit metadata.
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

---

## 1. Purpose

Record each Owner decision (approve / reject / cancel / retry / archive) as a
local, append-only **approval decision event** in the task's
`payload.metadata.approval_decision_events`, so the v0.7.3-B read-only view can
display a real decision history. The recorder is a **local audit record, not a
dispatch command**: **approve is not execute. Owner decision event is not Worker
dispatch.**

---

## 2. Current master

```
current master = 341445656090bc104a96fa60007c3ed1aec8a781
docs: close out approval decision event view validation
```

---

## 3. Relationship to v0.7.3-A / v0.7.3-B / v0.7.3-B-R

- **v0.7.3-A** (`e316760`) planned the decision event model and contract.
- **v0.7.3-B** (`7fd09df`) added the read-only view
  (`derive_approval_decision_event_view`) and its display.
- **v0.7.3-B-R** (`3414456`) recorded the Replit Preview validation of that view.
- **v0.7.3-C** (this segment) adds the **local append-only recorder** that
  actually writes the events the v0.7.3-B view reads. The decision/execution
  separation is preserved verbatim: **Owner approval does not automatically imply
  Worker execution. Decision and execution dispatch remain separate.**

---

## 4. Scope

In scope:

- Add a pure recorder helper (`app/approval_decision_event_recorder_v0_7.py`):
  `build_approval_decision_event` and `append_approval_decision_event_to_payload`.
- Wire the recorder into the existing Owner decision routes in `app/main.py`
  (read-only-to-everything-else; only appends local audit metadata).
- Add one narrow QueueStore method
  (`QueueStore.append_approval_decision_event`) to persist the appended payload.
- Add a readiness script and a local append-only test script.

Out of scope: new routes, route path/method changes, dashboard auth changes,
template form/button changes, status transition changes, schema migration, the
Worker, or any external system.

---

## 5. Local append-only recorder model

The recorder is local and append-only. It writes only local metadata (the
`payload.metadata.approval_decision_events` list inside the local SQLite payload):

- It only appends to `payload.metadata.approval_decision_events`.
- It preserves existing events and appends the new event at the tail.
- It never overwrites, deletes, or modifies existing events.
- It never modifies unrelated metadata (copy-on-write; it does not mutate the
  input payload).
- It records local audit metadata only; it produces no external side effect.

---

## 6. Event contract

Each event follows the v0.7.3-A contract:

`decision_id`, `task_id`, `decision_type`, `decided_by`, `decided_at`,
`decision_reason`, `previous_status`, `next_status`,
`approval_readiness_at_decision`, `execution_permission_at_decision`,
`dispatch_allowed_at_decision`, `safety_snapshot`, `annotation_snapshot`,
`audit_record`.

Fixed safety values (always):

```
execution_permission_at_decision = False
dispatch_allowed_at_decision = False
```

`decision_id` is a local UUID. `decided_at` is a UTC ISO-8601 timestamp.
`decided_by` defaults to `"owner"`. `decision_reason` is the route's existing
reason, or `"not_provided"` when none is supplied (no new form field is added).
`safety_snapshot` and `annotation_snapshot` are derived from the existing task /
annotation metadata (no secrets). `audit_record` holds local audit info only — no
token, secret, spreadsheet ID, or private key.

---

## 7. app/main.py integration

The recorder is wired into the existing Owner decision routes only:

- `/dashboard/tasks/{task_id}/approve`
- `/dashboard/tasks/{task_id}/reject`
- `/dashboard/tasks/{task_id}/cancel`
- `/dashboard/tasks/{task_id}/retry`
- `/dashboard/tasks/{task_id}/archive`

After the existing QueueStore status transition succeeds (and after the existing
`append_task_status` / system comment), a helper `_record_owner_decision`
appends the event. It adds no route, changes no path/method, changes no dashboard
auth, changes no template form/button, and changes no status transition result.
Recording is best-effort and isolated: if it fails it is swallowed and **no
external fallback is performed** — recording never affects the approval state
machine. The recorder triggers no Worker and calls no OpenClaw / Hermes / Google
Sheets.

> approval decision event is an audit record, not a dispatch command.
> Owner approval does not automatically imply Worker execution.

---

## 8. QueueStore boundary

One narrow method was added: `QueueStore.append_approval_decision_event(task_id,
event)`. It reads the task, computes the appended payload via the pure
`append_approval_decision_event_to_payload`, and updates **only** the `payload`
column (plus `updated_at`) via the existing private `_update`. It does not change
the schema, does not migrate, does not change status, and does not change
enqueue/dequeue semantics or the Worker's read logic. No existing method's
behavior was modified.

---

## 9. Status transition boundary

Status transitions are unchanged: approve still does waiting_review → queued,
reject → rejected, cancel/retry/archive via the existing QueueStore methods. The
recorder runs **after** the transition and only appends audit metadata; it never
alters the transition result.

---

## 10. Execution permission boundary

Every recorded event carries `execution_permission_at_decision = False`. The
recorder never sets it true; recording a decision grants no execution.

---

## 11. Dispatch boundary

Every recorded event carries `dispatch_allowed_at_decision = False`. The recorder
never dispatches the Worker; **Owner decision event is not Worker dispatch.**

---

## 12. External side-effect boundary

The recorder produces no external side effect: no OpenClaw call, no Hermes call,
no Google Sheets write, no webhook, no network call, no secrets read. It only
writes local audit metadata into the local SQLite `payload` column.

---

## 13. Test strategy

`scripts/test_approval_decision_event_recorder_local_appendonly_v0_7_3_c.py`
covers: empty-metadata append, append-only accumulation, copy-on-write
immutability, unrelated-metadata preservation, fixed `False` safety values,
`decision_id` / `decided_at` shape, snapshot/audit dict types, and the import
boundary (no app.main / QueueStore / Worker). It also uses a FastAPI TestClient
against a **temp SQLite** DATA_DIR / QUEUE_DB_PATH to verify the existing decision
routes append an event, that status transition results are unchanged, that no
`results.jsonl` is produced, and that no worker thread exists. The TestClient
POST happens only against the local temp queue — never against Replit Preview or
a real queue, never seeding the Replit queue, never `--apply`, never cleaning up
the demo task.

---

## 14. Safety confirmations

```
approve is not execute.
Owner decision event is not Worker dispatch.
Owner approval does not automatically imply Worker execution.
Decision and execution dispatch remain separate.
Approval readiness is not execution permission.
execution_permission_at_decision = False
dispatch_allowed_at_decision = False
No Worker execution
No OpenClaw call
No Hermes call
No Google Sheets write
No external side effects
No --apply
No demo task cleanup
No seed demo task
No secrets read
No webhook
```

---

## 15. Non-goals

v0.7.3-C explicitly does not:

- Dispatch the Worker or run any task.
- Call OpenClaw / Hermes or write Google Sheets.
- Add a route, change a route path/method, or change dashboard auth.
- Change template forms/buttons or any status transition result.
- Migrate the schema or change enqueue/dequeue/Worker semantics.
- Read secrets, create a webhook, or add any external dependency.
- Seed the Replit queue, `--apply`, or clean up the demo task.
- Create a release tag.

---

## 16. Acceptance criteria

v0.7.3-C is accepted when:

1. The recorder helper, this document, the readiness script, and the test script
   exist at their documented paths.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_event_recorder_v0_7_3_c.py`
   reports PASS.
3. The local append-only test script passes (pure append-only + local route
   append, status transitions unchanged, no worker thread, no results.jsonl).
4. The recorder is local / append-only with fixed
   `execution_permission_at_decision = False` /
   `dispatch_allowed_at_decision = False`, and carries no unsafe claim and no
   secret.
5. Existing routes and status transitions are preserved.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 17. Replit Preview requirement after push

Because v0.7.3-C modifies `app/main.py` route-side local recorder behavior, a
Replit Preview GET-only regression is required after push (pull, restart, GET
`/dashboard/reviews` and `/dashboard/tasks/demo-ui-e-b-review-001`). However, no
approve/reject/cancel/retry/archive must be clicked on the Replit Preview unless
the Owner separately approves a live local queue write validation.

---

## 18. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.3-C-R — Local Approval Event Recorder Closeout.**

Execution dispatch wiring remains explicitly **out** of this feature line:
approve is not execute, and Owner approval does not automatically imply Worker
execution.
