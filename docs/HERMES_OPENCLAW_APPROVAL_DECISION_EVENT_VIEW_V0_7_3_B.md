# Hermes × OpenClaw Adapter — Read-only Approval Event View (v0.7.3-B)

> **Status: READ-ONLY DISPLAY.** This version adds a read-only "Owner 決策紀錄 /
> Approval Decision Events" view: a pure view helper plus display-only wiring on
> the task detail and Owner Review surfaces. It records no event, writes nothing,
> changes no approval POST behavior, drives no status transition, and dispatches
> no Worker.
>
> Boundary declarations:
>
> - v0.7.3-B is read-only display only.
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

Add a read-only display of Owner approval decision events ("Owner 決策紀錄 /
Approval Decision Events") to the dashboard review surfaces, so an Owner can see
a task's decision history (or the empty state) without that view ever recording
an event, changing state, or dispatching the Worker. **approve is not execute.**

This is the **Read-only Approval Event View** segment of the v0.7.3 line. It
consumes the model defined by the v0.7.3-A **Approval Decision Event Plan**; it
does not implement a recorder.

---

## 2. Current master

```
current master = e3167601378739dae3ecc7d7fbd0dc5fd86f087d
docs: plan approval decision events
```

---

## 3. Scope

In scope (this segment only):

- Add a pure, read-only view helper
  (`app/approval_decision_events_v0_7.py`,
  `derive_approval_decision_event_view`).
- Read-only context wiring in `app/main.py` (attach the view to the task-detail
  and review-summary contexts) — no new route, no route path / method change, no
  approval POST behavior change.
- Display-only template + CSS on `templates/task_detail.html`,
  `templates/reviews.html`, `static/dashboard.css`.
- Add a readiness script and a read-only test script.

Explicitly out of scope: recording decision events, writing the queue, changing
approval wiring / status transitions, dispatching the Worker, schema migration,
or any external call.

---

## 4. Relationship to v0.7.3-A

v0.7.3-A (the **Approval Decision Event Plan**, commit `e316760`,
`docs: plan approval decision events`) defined the decision-event model: the
fields (`decision_id`, `task_id`, `decision_type`, `decided_by`, `decided_at`,
`decision_reason`, `previous_status`, `next_status`,
`approval_readiness_at_decision`, `execution_permission_at_decision`,
`dispatch_allowed_at_decision`, `safety_snapshot`, `annotation_snapshot`,
`audit_record`), the decision types, and the decision/execution separation.

v0.7.3-B implements only the **read-only view** of that model — it surfaces any
events that may exist in `payload.metadata.approval_decision_events` and renders
a safe empty state otherwise. It records nothing. The v0.7.3-A separation is
preserved verbatim: **Owner approval does not automatically imply Worker
execution. Decision and execution dispatch remain separate.**

---

## 5. Read-only view model

`derive_approval_decision_event_view(task)` is a pure function returning:

- `events` — normalized list of decision events (display-only).
- `event_count` — number of events.
- `has_events` — whether any events exist.
- `empty_state_message` / `empty_state_note` — the safe empty-state text.
- `safety_reminders` — the decision/execution separation reminders.
- `execution_permission` — always `False`.
- `dispatch_allowed` — always `False`.

Each normalized event carries `decision_id`, `task_id`, `decision_type`,
`decided_by`, `decided_at`, `decision_reason`, `previous_status`, `next_status`,
`approval_readiness_at_decision`, `execution_permission_at_decision` (always
`False`), `dispatch_allowed_at_decision` (always `False`), `safety_snapshot`,
`annotation_snapshot`, and `audit_record`.

---

## 6. Helper behavior

The helper reads `task.payload.metadata.approval_decision_events` safely
(`payload` may be a dict, a JSON string, or None; metadata or the field may be
missing or the wrong type — all handled without crashing) and returns the view.
It does **not** write the task, does **not** write QueueStore, does **not**
modify metadata, does **not** import app.main or QueueStore, does **not** start
the Worker, and does **not** call OpenClaw / Hermes / Google Sheets or read
secrets. The view never authorizes execution and never allows dispatch:
**approval decision event view is read-only.**

---

## 7. Task detail display

On `/dashboard/tasks/{task_id}` a read-only "Owner 決策紀錄 / Approval Decision
Events" card is shown. When events exist, it lists per-event:
`decision_type`, `decided_by`, `decided_at`, `decision_reason`,
`previous_status → next_status`, `approval_readiness_at_decision`,
`execution_permission_at_decision`, `dispatch_allowed_at_decision`. The card
always shows 只讀顯示, 執行權限：未授權 (`execution_permission = False`),
派工允許：未允許 (`dispatch_allowed = False`), and the reminders
**approve is not execute** / **Owner decision event is not Worker dispatch**.
No recorder is added and no event is written.

---

## 8. Owner review list display

On `/dashboard/reviews` each row gains a read-only decision event indicator —
決策紀錄：N, 只讀, 未派工 — that displays the per-task event count and reinforces
that the row is read-only and not dispatched. The indicator triggers no action.

---

## 9. Empty state behavior

When `payload.metadata.approval_decision_events` is absent or empty, the task
detail card shows:

```
尚無 Owner 決策事件紀錄
v0.7.3-B 只讀顯示；v0.7.3-C 才會規劃 local recorder
```

No traceback, no HTTP 500; the empty state is the default for every existing /
legacy task (none have events yet, because no recorder exists).

---

## 10. Event fields displayed

The fields displayed for each event (when present):

- `decision_type`
- `decided_by`
- `decided_at`
- `decision_reason`
- `previous_status` → `next_status`
- `approval_readiness_at_decision`
- `execution_permission_at_decision`
- `dispatch_allowed_at_decision`

All display-only; none grants execution or dispatch.

---

## 11. Execution permission boundary

The view and every event display execution permission as unauthorized:

```
execution_permission = False
```

This is hard-coded `False` by the helper and is display-only; it grants no
execution. No decision type, including approve, sets it to true.

---

## 12. Dispatch allowed boundary

The view and every event display dispatch as not allowed:

```
dispatch_allowed = False
```

This is hard-coded `False` by the helper and is display-only; it permits no
Worker dispatch. **Owner decision event is not Worker dispatch.**

---

## 13. Approval readiness boundary

`approval_readiness_at_decision` is a display-only snapshot. Even
`ready_for_owner_decision` only means enough information to decide; it grants
nothing. **Approval readiness is not execution permission.**

---

## 14. Runtime boundaries

- `app/main.py` change is read-only context wiring only: it attaches the view to
  the task-detail and review-summary render contexts.
- No new route; no route path or HTTP method change.
- No change to approve/reject/cancel/retry/archive POST behavior.
- No change to QueueStore status transitions.
- No Worker dispatch is added.

---

## 15. Safety boundaries

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
execution permission.** The view always reports `execution_permission = False`
and `dispatch_allowed = False`.

---

## 16. Non-goals

v0.7.3-B explicitly does not:

- Record a decision event or add a recorder (read-only view only).
- Write the queue or change QueueStore runtime behavior.
- Change approval wiring or any POST action behavior or status transition.
- Add a route or migrate schema.
- Dispatch the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any dependency.
- Seed (`--apply`) or clean up the demo task.
- Click approve/reject/cancel/retry/archive.
- Create a release tag.

---

## 17. Acceptance criteria

v0.7.3-B is accepted when:

1. The view helper and this document exist at the documented paths.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_event_view_v0_7_3_b.py`
   exists and reports PASS.
3. The read-only test script
   `scripts/test_approval_decision_event_view_readonly_v0_7_3_b.py`
   exists and passes (empty-state, immutability, execution_permission /
   dispatch_allowed `False`, no app.main / QueueStore import, template markers).
4. The task detail and Owner Review surfaces show the read-only decision-event
   view with the empty state and the decision/execution separation reminders.
5. No runtime behavior changes; no unsafe claim and no secret.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 18. Validation plan

- Run the readiness script and the read-only test script (both PASS).
- Run the prior v0.7.3-A and v0.7.2-F-line readiness checks (all PASS).
- Run the dashboard regression tests (`test_dashboard_readonly`,
  `test_dashboard_polish`) — both PASS, confirming no behavior regression.
- `compileall app scripts` PASS; `from app.main import app` imports cleanly.

---

## 19. Replit Preview requirement after push

Because this segment changes templates, CSS, and app render context (read-only
display), a Replit Preview validation is required after push: pull to the new
master, restart the preview server, and GET `/dashboard/reviews` and
`/dashboard/tasks/demo-ui-e-b-review-001` to confirm the read-only Owner 決策紀錄
view renders with the empty state and the unauthorized execution_permission /
dispatch_allowed markers — GET-only, no controls clicked.

---

## 20. Next recommended step

Recommended next step (each requires explicit Owner approval to start):

1. Owner-approved local commit of this segment, then push, then Replit Preview
   validation.
2. A future v0.7.3-C segment to plan a **local, append-only** decision-event
   recorder (still no execution wiring) — separately planned and approved.

Execution dispatch wiring remains explicitly **out** of this feature line.

---

## 21. Final statement

This segment adds only a read-only view of Owner approval decision events.

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
