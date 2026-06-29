# Hermes × OpenClaw Adapter — Local Approval Event Recorder Replit GET-only Closeout (v0.7.3-C-R)

> **Status: CLOSEOUT / VALIDATION RECORD ONLY.** This version adds a closeout
> document and a static readiness check that record the v0.7.3-C Replit Preview
> GET-only regression. It changes no application code, no templates, no static
> assets, no existing docs, no tests, and no seed script; it wires no route,
> migrates no schema, and creates no tag. It does not touch the Replit SQLite
> database and does not clean up the demo task.
>
> Boundary declarations:
>
> - v0.7.3-C-R is documentation / current-state only.
> - No QueueStore runtime behavior changes during validation.
> - No approval route path/method changes during validation.
> - No dashboard auth changes during validation.
> - No status transition changes during validation.
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
> - No approve/reject/cancel/retry/archive clicks.

---

## 1. Purpose

This is the **Local Approval Event Recorder Replit GET-only Closeout** for
v0.7.3-C. It records the **v0.7.3-C Replit Preview GET-only regression** into the
repo: the Replit pull to the F-3-C master, the preview server restart, the
GET-only HTTP smoke, and the GET-only regression of `/dashboard/reviews` and
`/dashboard/tasks/demo-ui-e-b-review-001`. The regression was GET-only and did
**not** exercise live approval writes. This is a closeout / validation record —
not feature development. It performs no code change and recommends no release tag.

---

## 2. Current master

```
HEAD = origin/master = c0417b46c81528ffd8997978bd8190edb636c101
feat: add local approval decision event recorder
```

---

## 3. Scope

In scope (this segment only):

- Add this closeout / validation-record document.
- Add one static readiness script that asserts the document exists and contains
  the required validation markers, and that the segment adds nothing else.

Explicitly out of scope: any change to runtime code, templates, static assets,
existing docs, tests, the seed script, approval routes, QueueStore, the Worker,
or any external system.

---

## 4. Relationship to v0.7.3-C

v0.7.3-C (`c0417b4`, `feat: add local approval decision event recorder`) added a
local, append-only Owner approval decision event recorder wired into the existing
Owner decision routes, plus one narrow QueueStore append method. v0.7.3-C-R
records that this change passed a Replit Preview GET-only regression after the
push. The decision/execution separation is preserved verbatim:
**approve is not execute. Owner decision event is not Worker dispatch.**

---

## 5. Replit environment confirmation

The validation was performed in the Replit workspace.

```
Replit environment confirmed
not Windows WSL
```

The WSL development clone that produced and pushed the commit is a separate
machine; the Replit Preview is a distinct cloud environment, which is why the
`demo-ui-e-b-review-001` demo task exists there and the Preview regression must
run there.

---

## 6. Pull result

On Replit, a fast-forward pull to the F-3-C master succeeded:

```
pull before HEAD = 7fd09df4e6a6a5a26d73fc8e64f9f786dca1066f
pull after HEAD = c0417b46c81528ffd8997978bd8190edb636c101
fast-forward pull succeeded
```

The pull spanned the v0.7.3-B-R and v0.7.3-C commits:

```
8 files changed
1452 insertions
```

No reset, no stash, no overlay checkout was performed.

---

## 7. Replit overlay status

Only the expected Replit / local overlay appeared; it was left untouched:

```
M .replit
?? .claude/
?? patches/
```

`patches/` was not added, `.replit` was not added, `.claude/` was not added; no
overlay file was reset, checked out, or deleted.

---

## 8. Local checks on Replit

On Replit, after pull, the checks passed:

```
v0.7.3-C readiness PASS
77/77
v0.7.3-C local append-only test PASS
33/33
local append-only test used temp SQLite / in-process TestClient only
no POST to Replit Preview or real queue
v0.7.3-B readiness PASS
76/76
v0.7.3-B readonly test PASS
42/42
v0.7.3-B-R readiness PASS
112/112
dashboard regression PASS
compileall PASS
```

The v0.7.3-C local append-only test exercises decision routes only against a
temporary in-process SQLite queue (temp DATA_DIR / QUEUE_DB_PATH); it sent no
POST to the Replit Preview or the real queue.

---

## 9. Preview server restart

Only the old `uvicorn app.main:app` process was stopped and a new one started:

```
old PID 1458
new PID 3720
Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

The restart was a process reload only; it started no Worker, opened no external
connection, and triggered no approve/reject/cancel/retry/archive action.

---

## 10. HTTP smoke results

GET-only HTTP smoke after restart:

```
GET / -> 303 /dashboard
GET /dashboard -> 303 /dashboard/login
GET /dashboard/login -> 200
GET /dashbord -> 404
```

All GET-only; no POST was sent, so no queue state changed.

---

## 11. /dashboard/reviews GET-only regression

`/dashboard/reviews` GET-only regression PASS.

```
/dashboard/reviews GET-only regression PASS
```

The Owner Review list still rendered the read-only decision-event indicator:

- Owner 審核佇列 normal
- 決策紀錄 (decision events) indicator present
- 決策紀錄：0
- 只讀
- 未派工
- dispatch_allowed = False
- 審核準備狀態 still present
- 執行權限：未授權 / execution_permission = False still present

No approve/reject controls were clicked; no POST was sent.

---

## 12. /dashboard/tasks/demo-ui-e-b-review-001 GET-only regression

`/dashboard/tasks/demo-ui-e-b-review-001` GET-only regression PASS.

```
/dashboard/tasks/demo-ui-e-b-review-001 GET-only regression PASS
```

The task detail Owner 決策紀錄 card still rendered the empty state and the
separation reminders:

- Owner 決策紀錄
- Approval Decision Events
- 只讀顯示
- 尚無 Owner 決策事件紀錄
- v0.7.3-B 只讀顯示；v0.7.3-C 才會規劃 local recorder
- 執行權限：未授權
- execution_permission = False
- 派工允許：未允許
- dispatch_allowed = False
- approve is not execute.
- Owner decision event is not Worker dispatch.
- Decision and execution dispatch remain separate.

The page was viewed read-only; no control was clicked. (The empty state remains
because no approval POST was clicked on the Preview during this GET-only
regression.)

---

## 13. Required v0.7.3-C safety confirmations

The v0.7.3-C recorder remains local / append-only, and every event carries the
fixed safety values:

```
execution_permission_at_decision = False
dispatch_allowed_at_decision = False
approve is not execute.
Owner decision event is not Worker dispatch.
Decision and execution dispatch remain separate.
```

---

## 14. No live queue write validation

This segment did not perform a live local queue write on the Replit Preview:

```
Live local queue write validation not performed
Live local queue write validation not required unless separately approved by Owner
```

No approve/reject/cancel/retry/archive was clicked on the Preview; the recorder's
live append path was validated only locally (temp SQLite / in-process TestClient
in v0.7.3-C), never against the Replit Preview or a real queue.

---

## 15. Safety confirmations

```
no commit
no push
no tag
no reset
no stash
no POST to Replit Preview or real queue
no approve/reject/cancel/retry/archive clicks
No QueueStore runtime behavior changes during validation
No approval route path/method changes during validation
No dashboard auth changes during validation
No status transition changes during validation
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
Owner visual confirmation not required
```

---

## 16. Non-goals

v0.7.3-C-R explicitly does not:

- Change any runtime code, template, or static asset.
- Change QueueStore runtime behavior, approval routes, dashboard auth, or any
  status transition.
- Add a route or migrate schema.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external dependency.
- Seed (`--apply`) or clean up the demo task.
- Click approve/reject/cancel/retry/archive or send any POST to the Preview or a
  real queue.
- Create a release tag.

---

## 17. Acceptance criteria

v0.7.3-C-R is accepted when:

1. This closeout / validation document exists at the documented path and
   contains sections 1–19.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_event_recorder_replit_validation_v0_7_3_c_r.py`
   exists and reports PASS.
3. The document records the Replit pull, the restart, the HTTP smoke, the
   GET-only regression of `/dashboard/reviews` and
   `/dashboard/tasks/demo-ui-e-b-review-001`, and the "no live queue write
   validation" stance.
4. The document states the safety confirmations and non-goals and carries no
   unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime
   file changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 18. Final closeout statement

```
v0.7.3-C is pushed and has passed Replit Preview GET-only regression.
The Local Approval Event Recorder remains local / append-only.
The Replit Preview validation did not exercise live approval writes.
approve is not execute.
Owner decision event is not Worker dispatch.
execution_permission_at_decision = False.
dispatch_allowed_at_decision = False.
```

The system remains in its safe posture: Dashboard read-only, Worker OFF,
OpenClaw / Hermes not connected, Google Sheets disabled, no external side
effects.

---

## 19. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.3-R — Approval Decision Layer Full Closeout.**

> v0.7.3-R must remain docs / readiness only.
> No runtime changes.
> No Worker dispatch.
> No OpenClaw / Hermes / Google Sheets.
> No external side effects.

Execution dispatch wiring remains explicitly **out** of this feature line.
