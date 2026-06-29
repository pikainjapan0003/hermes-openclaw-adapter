# Hermes × OpenClaw Adapter — Read-only Approval Event View Replit Preview Closeout (v0.7.3-B-R)

> **Status: CLOSEOUT / VALIDATION RECORD ONLY.** This version adds a closeout
> document and a static readiness check that record the v0.7.3-B Replit Preview
> validation. It changes no application code, no templates, no static assets, no
> existing docs, no tests, and no seed script; it wires no route, migrates no
> schema, and creates no tag. It does not touch the Replit SQLite database and
> does not clean up the demo task.
>
> Boundary declarations:
>
> - v0.7.3-B-R is documentation / current-state only.
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
> - No approve/reject/cancel/retry/archive clicks.

---

## 1. Purpose

This is the **Read-only Approval Event View Replit Preview Closeout** for
v0.7.3-B. It records the **v0.7.3-B Replit Preview validation** into the repo:
the Replit pull to the F-3-B master, the preview server restart, the GET-only
HTTP smoke, and the GET-only visual validation of `/dashboard/reviews` and
`/dashboard/tasks/demo-ui-e-b-review-001`. This is a closeout / validation
record — not feature development. It performs no code change and recommends no
release tag.

---

## 2. Current master

```
HEAD = origin/master = 7fd09df4e6a6a5a26d73fc8e64f9f786dca1066f
feat: add read-only approval decision event view
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

## 4. Relationship to v0.7.3-B

v0.7.3-B (`7fd09df`, `feat: add read-only approval decision event view`) added a
read-only Owner approval decision event view: the pure helper
`derive_approval_decision_event_view`, read-only context wiring in `app/main.py`,
and display-only template + CSS on the task detail and Owner Review surfaces.
v0.7.3-B-R records that this view was validated on the Replit Preview server
after the push. The decision/execution separation is preserved verbatim:
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
`demo-ui-e-b-review-001` demo task (seeded earlier on Replit) exists there and
the Preview validation must run there.

---

## 6. Pull result

On Replit, a fast-forward pull to the F-3-B master succeeded:

```
pull before HEAD = 463f09d69dd9da26224a5b02a653c7dce20e2208
pull after HEAD  = 7fd09df4e6a6a5a26d73fc8e64f9f786dca1066f
fast-forward pull succeeded
```

The pull spanned the F-C-R, F-R, v0.7.3-A, and v0.7.3-B commits:

```
14 files changed
2562 insertions
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

On Replit, after pull, the read-only checks passed:

```
v0.7.3-B readiness PASS
v0.7.3-B readonly test PASS
dashboard regression PASS
compileall PASS
```

---

## 9. Preview server restart

Only the old `uvicorn app.main:app` process was stopped and a new one started:

```
old PID 1251
new PID 1458
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

## 11. /dashboard/reviews GET-only validation

`/dashboard/reviews` GET-only validation PASS.

```
/dashboard/reviews GET-only validation PASS
```

The Owner Review list rendered the read-only decision-event indicator:

- Owner 審核佇列 normal
- 決策紀錄 (decision events) column / indicator present
- 決策紀錄：0
- 只讀
- 未派工
- dispatch_allowed = False
- 審核準備狀態 still present
- 執行權限：未授權 / execution_permission = False still present

No approve/reject controls were clicked; no POST was sent.

---

## 12. /dashboard/tasks/demo-ui-e-b-review-001 GET-only validation

`/dashboard/tasks/demo-ui-e-b-review-001` GET-only validation PASS.

```
/dashboard/tasks/demo-ui-e-b-review-001 GET-only validation PASS
```

The task detail Owner 決策紀錄 card rendered the empty state and the separation
reminders:

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

The page was viewed read-only; no control was clicked.

---

## 13. Required v0.7.3-B markers confirmed

The following v0.7.3-B markers were confirmed on the Replit Preview:

- Owner 決策紀錄 / Approval Decision Events
- 決策紀錄 / 決策紀錄：0 / 只讀 / 未派工
- 尚無 Owner 決策事件紀錄
- v0.7.3-B 只讀顯示；v0.7.3-C 才會規劃 local recorder
- 執行權限：未授權 / execution_permission = False
- 派工允許：未允許 / dispatch_allowed = False
- approve is not execute. / Owner decision event is not Worker dispatch. /
  Decision and execution dispatch remain separate.

---

## 14. Safety confirmations

```
no commit
no push
no tag
no reset
no stash
no POST
no approve/reject/cancel/retry/archive clicks
No QueueStore runtime behavior changes
No approval wiring changes
No status transition changes
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

## 15. Non-goals

v0.7.3-B-R explicitly does not:

- Change any runtime code, template, or static asset.
- Change QueueStore runtime behavior, approval wiring, or any status transition.
- Add a route or migrate schema.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external dependency.
- Seed (`--apply`) or clean up the demo task.
- Click approve/reject/cancel/retry/archive or send any POST.
- Create a release tag.

---

## 16. Acceptance criteria

v0.7.3-B-R is accepted when:

1. This closeout / validation document exists at the documented path and
   contains sections 1–18.
2. The readiness script
   `scripts/check_hermes_openclaw_approval_decision_event_view_replit_validation_v0_7_3_b_r.py`
   exists and reports PASS.
3. The document records the Replit pull, the server restart, the HTTP smoke, and
   the GET-only validation of `/dashboard/reviews` and
   `/dashboard/tasks/demo-ui-e-b-review-001` with the v0.7.3-B markers.
4. The document states the safety confirmations and non-goals and carries no
   unsafe claim and no secret.
5. The segment adds only this document and the readiness script — no runtime
   file changed.
6. Nothing is committed, pushed, or tagged without Owner approval.

---

## 17. Final closeout statement

```
v0.7.3-B is complete after GitHub push and Replit Preview validation.
The read-only Owner decision event view renders correctly on both Owner Review list and task detail.
approve is not execute.
Owner decision event is not Worker dispatch.
execution_permission = False.
dispatch_allowed = False.
```

The system remains in its safe posture: Dashboard read-only, Worker OFF,
OpenClaw / Hermes not connected, Google Sheets disabled, no external side
effects.

---

## 18. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.3-C — Local Approval Event Recorder.**

> v0.7.3-C must remain local / append-only / no Worker dispatch / no OpenClaw /
> no Hermes / no Google Sheets write unless separately approved.

Execution dispatch wiring remains explicitly **out** of this feature line.
