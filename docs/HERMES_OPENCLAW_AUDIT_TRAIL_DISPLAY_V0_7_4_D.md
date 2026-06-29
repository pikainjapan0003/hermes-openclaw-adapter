# Hermes × OpenClaw Adapter — Audit Trail Display (v0.7.4-D)

> **Status: READ-ONLY DISPLAY.** This version adds a pure read-only audit-trail
> display helper, wires it into the GET display paths, and adds a read-only panel
> on task detail plus a read-only summary on the reviews list. It adds no POST
> route, no state-changing button, and no state-changing form; it changes no
> approval / reject / cancel / retry / archive behavior, no dashboard auth, no
> status transition, no QueueStore runtime behavior, and `app/queue_store.py` is
> untouched. It implements no runtime guard, does not touch the Replit SQLite
> database, and does not clean up or seed the demo task.
>
> Boundary declarations:
>
> - v0.7.4-D is a read-only display addition.
> - No QueueStore runtime behavior changes.
> - No `app/queue_store.py` change.
> - No approval routes method / path / redirect / status result change.
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

This is the **Audit Trail Display** for the v0.7.4 line. It lets the Dashboard show
read-only information about a task's lifecycle, its Blackboard message family, and
the Owner Decision audit trail — without changing any state. It performs no queue
write, no POST, no dispatch, no runtime guard, and no external side effect.

---

## 2. Current master

```
HEAD = origin/master = 33476de2c65438ca10627657f94afaf1955b0660
docs: plan state transition guard
```

---

## 3. Scope

In scope (this segment only):

- Add a pure read-only helper `app/audit_trail_display_v0_7.py`
  (`derive_audit_trail_display_view`).
- Wire the helper into the existing GET display context builders in `app/main.py`.
- Add a read-only "Audit Trail / Blackboard Messages" panel to
  `templates/task_detail.html` and a read-only audit summary to
  `templates/reviews.html`, plus supporting classes in `static/dashboard.css`.
- Add this document, a readiness script, and a read-only helper test.

Explicitly out of scope: any change to `app/queue_store.py`, QueueStore runtime
behavior, approval routes, dashboard auth, status transitions, the seed script,
existing docs, the README, the Worker, or any external system. No POST route, no
state-changing button, no state-changing form, no runtime guard.

---

## 4. Relationship to v0.7.4-C

v0.7.4-D builds on the completed State Transition Guard Plan, which stays unchanged:

```
v0.7.4-C State Transition Guard Plan is complete.
State Transition Guard is a safety contract.
v0.7.4-C does not modify current status transitions.
v0.7.4-C does not enforce runtime guards.
Allowed and blocked transitions are planning rules only.
```

The displayed lifecycle state is a read-only derivation over the v0.7.4-B / v0.7.4-C
planning vocabulary; it enforces none of the guard rules.

---

## 5. Relationship to v0.7.4-B

```
v0.7.4-B Queue / Blackboard Lifecycle Plan is complete.
Task Message
Decision Message
Result Message
Advice Message
Result Message is future planning only.
Advice Message is future planning only.
```

---

## 6. Relationship to v0.7.4-A

```
v0.7.4-A Core Topology / Dashboard Update / Core Independence Plan is complete.
Replit is a remote observation station / Preview Dashboard.
Dashboard update means git pull plus Dashboard restart.
Current Windows WSL local queue and Replit local queue are separate.
```

---

## 7. Relationship to v0.7.3-R

```
v0.7.3 Approval Decision Layer is complete.
approval_decision_events are Decision Messages.
Decision Messages are blackboard audit records, not execution commands.
approve is not execute.
Owner decision event is not Worker dispatch.
```

---

## 8. Read-only display contract

```
Audit Trail Display is read-only.
Audit Trail Display does not change lifecycle state.
Audit Trail Display does not enforce guard.
Audit Trail Display does not grant execution permission.
Audit Trail Display does not dispatch Worker.
Audit Trail Display does not call OpenClaw.
Audit Trail Display does not call Hermes.
Audit Trail Display does not write Google Sheets.
Audit Trail Display does not write queue data.
```

---

## 9. Audit trail helper

`derive_audit_trail_display_view(task) -> dict` is a pure function. It reads only
the task / payload / metadata, never writes, never calls QueueStore, never imports
`app.main`, and uses only the standard library (`json` / `typing`). It returns a
dict containing `lifecycle_state`, `lifecycle_state_label`, `message_family_counts`,
`timeline_items`, `decision_message_count`, `result_message_count`,
`advice_message_count`, `task_message_present`, and the fixed safety flags. The
fixed flags are always:

```
execution_permission = False
dispatch_allowed = False
worker_dispatch_enabled = False
openclaw_call_enabled = False
hermes_call_enabled = False
google_sheets_write_enabled = False
read_only = True
```

---

## 10. Dashboard task detail display

The task detail page gains a read-only **Audit Trail / Blackboard Messages** panel.
It shows the derived lifecycle state, Task Message present, Decision Message count,
Result / Advice Message future-only counts, a read-only timeline, and the fixed
safety badges (execution permission False, dispatch allowed False, Worker dispatch
Disabled, OpenClaw Not Called, Hermes Not Called, Google Sheets Disabled, read-only
display only). The panel contains no button and no form.

---

## 11. Dashboard reviews display

The reviews list gains a short read-only audit summary per row:

```
Audit：Task 1 / Decision N / Result 0 / Advice 0
Lifecycle：<derived state>
```

These are read-only text / badge only — no button and no form are added.

---

## 12. Blackboard message family display

```
Task Message = 1 when task exists
Decision Message = len(payload.metadata.approval_decision_events)
Result Message = 0 in v0.7.4-D
Advice Message = 0 in v0.7.4-D
```

---

## 13. Lifecycle state display

The displayed lifecycle state is conservatively derived read-only:

```
archived_or_closed：若 task.status 看起來是 archived / closed / cancelled 類型
owner_decided：若 approval_decision_events 數量 > 0
owner_review：若有 approval_readiness 或 task.status 顯示待審
annotated：若有 annotation / safety_snapshot / approval_readiness 類資訊
draft_or_created：其他狀況
```

```
Displayed lifecycle state is derived read-only.
Displayed lifecycle state does not change task status.
Displayed lifecycle state does not enforce guard.
Displayed lifecycle state does not grant execution permission.
Displayed lifecycle state does not dispatch Worker.
```

---

## 14. Decision Message display

Decision Messages are counted read-only from
`payload.metadata.approval_decision_events`. The display shows the count only; it
records no event, changes no status, and dispatches nothing. The v0.7.3 contract
holds: approve is not execute; Owner decision event is not Worker dispatch.

---

## 15. Result Message future-only display

```
Result Message display is future-only in v0.7.4-D.
```

Result Message count is fixed at 0 in v0.7.4-D; no live Worker output exists.

---

## 16. Advice Message future-only display

```
Advice Message display is future-only in v0.7.4-D.
```

Advice Message count is fixed at 0 in v0.7.4-D; Hermes is not called.

---

## 17. Dispatch separation boundary

```
approve is not execute.
Owner decision event is not Worker dispatch.
execution_permission = False
dispatch_allowed = False
```

The display surfaces these fixed-False flags; it never grants execution and never
dispatches.

---

## 18. QueueStore boundary

```
QueueStore runtime behavior is unchanged in v0.7.4-D.
v0.7.4-D does not modify app/queue_store.py.
v0.7.4-D does not add QueueStore methods.
v0.7.4-D does not change status persistence.
v0.7.4-D does not change payload persistence.
```

---

## 19. Route / POST boundary

```
v0.7.4-D does not add POST routes.
v0.7.4-D does not modify approval POST behavior.
v0.7.4-D does not modify reject POST behavior.
v0.7.4-D does not modify cancel POST behavior.
v0.7.4-D does not modify retry POST behavior.
v0.7.4-D does not modify archive POST behavior.
v0.7.4-D does not add state-changing buttons.
v0.7.4-D does not add state-changing forms.
```

The helper is wired only into the existing GET display context builders; no POST
route, method, path, redirect, or status result was changed.

---

## 20. Local queue vs Replit queue boundary

```
Current Windows WSL local queue and Replit local queue are separate.
They do not automatically sync.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
A shared blackboard requires a future Remote Blackboard API or shared DB.
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

## 22. Tests and readiness

- `scripts/check_hermes_openclaw_audit_trail_display_v0_7_4_d.py` — static readiness
  check over the helper, doc, templates, css, and markers.
- `scripts/test_audit_trail_display_readonly_v0_7_4_d.py` — pure in-memory read-only
  tests of the helper (no real queue, no POST, no TestClient POST).

---

## 23. Non-goals

v0.7.4-D explicitly does not:

- Change `app/queue_store.py`, QueueStore runtime behavior, approval routes,
  dashboard auth, or any status transition.
- Add a POST route, a state-changing button, or a state-changing form.
- Implement a runtime guard or change any existing transition result.
- Modify the seed script, existing docs, or the README.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external side effect.
- Seed (`--apply`) or clean up the demo task.
- Perform a live local queue write validation.
- Commit, push, or create a release tag.

---

## 24. Acceptance criteria

v0.7.4-D is accepted when:

1. The helper, document, readiness script, and read-only test exist at the
   documented paths; this document contains sections 1–25.
2. The readiness script
   `scripts/check_hermes_openclaw_audit_trail_display_v0_7_4_d.py` reports PASS and
   the read-only test passes.
3. The helper returns the fixed-False safety flags and `read_only = True`, with
   Result / Advice Message counts fixed at 0.
4. The document records the current master, the v0.7.4-C / v0.7.4-B / v0.7.4-A /
   v0.7.3-R completion markers, the read-only display contract, the QueueStore
   boundary, and the Route / POST boundary, and carries no unsafe claim and no
   secret.
5. Only the allowed files are added / modified; `app/queue_store.py` is untouched.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 25. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-D-R — Audit Trail Display Replit GET-only Validation.**

> v0.7.4-D-R must be GET-only.
> No POST to Replit Preview.
> No approve/reject/cancel/retry/archive clicks.
> No live local queue write validation.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.
