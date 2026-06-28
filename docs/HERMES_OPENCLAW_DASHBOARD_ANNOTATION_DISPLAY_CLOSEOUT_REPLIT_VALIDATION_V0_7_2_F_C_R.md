# Hermes × OpenClaw Adapter — Dashboard Annotation Display Closeout & Replit Preview Validation (v0.7.2-F-C-R)

> **Status: CLOSEOUT / VALIDATION RECORD ONLY.** This version adds a closeout
> document and a static readiness check. It changes no application code, no
> templates, no static assets, no existing docs, no tests, and no seed script;
> it wires no route and creates no tag. It does not touch the Replit SQLite
> database and does not clean up the demo task.
>
> Boundary declarations:
>
> - v0.7.2-F-C-R is documentation / current-state only.
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

This document is the **Dashboard Annotation Display Closeout** for the v0.7.2-F-C
segment, plus a **Replit Preview Validation** record. It formally captures into
the repo that the read-only annotation display shipped in F-C renders correctly
on the Replit Preview server, on both the Owner Review Queue (`/dashboard/reviews`)
and the task detail Owner Review Panel
(`/dashboard/tasks/demo-ui-e-b-review-001`). This is a closeout / validation
record — not feature development. It performs no code change and recommends no
release tag.

---

## 2. Current master

```
current master = 463f09d69dd9da26224a5b02a653c7dce20e2208
feat: display queue task annotations
```

This is the F-C commit whose display behavior this record validates.

---

## 3. Scope

In scope (this segment only):

- Add this closeout / validation-record document.
- Add one static readiness script that asserts the document exists and contains
  the required markers, and that the segment adds nothing else.

Explicitly out of scope: any change to runtime code, templates, static assets,
existing docs, tests, the seed script, approval routes, QueueStore, the Worker,
or any external system.

---

## 4. Relationship to F-A / F-B / F-C

The v0.7.2-F (annotation / approval-readiness) line:

| Segment | Commit | What it delivered |
| --- | --- | --- |
| F-A | `7c6c265` | Plan: Queue Task Annotation / Approval Readiness model (doc + readiness). |
| F-B | `b9013fb` | Pure, read-only annotation deriver (`derive_queue_task_annotation`) + unit tests + readiness. |
| F-C | `463f09d` | Read-only display of the annotation in the Owner Review Panel / review surfaces. |
| **F-C-R** | *(this record)* | Closeout + Replit Preview validation of the F-C display. |

F-A defined the fields and the `approval_readiness` enum and the
decision/execution separation. F-B implemented the conservative read-only
deriver (with `execution_permission`/`dispatch_allowed` always `False`). F-C
wired the deriver into the dashboard context and rendered it. F-C-R records that
the rendering was validated on Replit Preview. Each segment preserved the
v0.7.x safety envelope: read-only, local-only, Owner-gated, Worker OFF.

---

## 5. What F-C delivered

F-C (`463f09d`, `feat: display queue task annotations`) delivered read-only
display only:

- `app/main.py`: read-only context wiring — imports `derive_queue_task_annotation`
  and attaches an `annotation` dict to the task-detail and review-summary
  contexts. No route path / HTTP method change; no QueueStore write; no Worker
  dispatch; approve/reject/cancel/retry/archive route behavior unchanged.
- `templates/task_detail.html`: an "審核準備狀態 / Annotation / Approval
  Readiness" card displaying the annotation fields.
- `templates/reviews.html`: decision/execution separation reminders plus a
  per-row `approval_readiness` badge column.
- `static/dashboard.css`: display-only styling (no JS, no CDN, no external asset).
- New read-only test + readiness scripts for the display.

---

## 6. Replit pull result

On the Replit Preview environment the repository was pulled to the F-C master
commit `463f09d69dd9da26224a5b02a653c7dce20e2208`
(`feat: display queue task annotations`). The pull succeeded and the working
tree on Replit matched the pushed master for the F-C display surfaces
(`app/main.py`, `templates/task_detail.html`, `templates/reviews.html`,
`static/dashboard.css`). No local runtime change was made on Replit beyond
pulling.

---

## 7. Server restart reason

The Replit Preview server was restarted so the updated Jinja2 templates
(`task_detail.html`, `reviews.html`) and the updated `static/dashboard.css`
were reloaded into the running process. The restart was a process reload only;
it started no Worker, opened no external connection, and triggered no
approve/reject/cancel/retry/archive action.

---

## 8. HTTP smoke validation

After restart, an authenticated read-only HTTP smoke check confirmed:

- `GET /dashboard/reviews` returned HTTP 200 and rendered the Owner Review Queue.
- `GET /dashboard/tasks/demo-ui-e-b-review-001` returned HTTP 200 and rendered
  the task detail Owner Review Panel with the annotation card.

The smoke check was GET-only; no POST action was issued, so no queue state
changed.

---

## 9. /dashboard/reviews visual validation

On `/dashboard/reviews` the Owner Review Queue showed, for the demo
`waiting_review` task:

- The decision/execution separation safety reminders.
- An `approval_readiness` badge column ("審核準備狀態").
- The explicit unauthorized markers — 執行權限：未授權 and 派工允許：未允許 —
  i.e. `execution_permission = False` and `dispatch_allowed = False`.

The page remained read-only; no approve/reject controls were clicked.

---

## 10. /dashboard/tasks/demo-ui-e-b-review-001 visual validation

On `/dashboard/tasks/demo-ui-e-b-review-001` the task detail Owner Review Panel
rendered the full annotation card ("審核準備狀態 / Annotation / Approval
Readiness") with the human-readable summary, the readiness state, the owner
reason, risk/side-effect summaries, the next step, the execution mode and
dry-run/mock/touchpoint markers, the rollback note, the explicit unauthorized
permission/dispatch badges, and the decision/execution separation reminders.
The page was viewed read-only; no control was clicked.

---

## 11. Annotation fields validated

The following annotation fields rendered correctly (Chinese-first labels with
English / code sublabels):

- 任務摘要 (`human_readable_summary`)
- 審核準備狀態 (`approval_readiness`)
- 需要 Owner 的原因 (`owner_reason`)
- 風險摘要 (`risk_summary`)
- 外部影響 (`side_effect_summary`)
- 核准後下一步 (`next_step_if_approved`)
- 執行模式 (`execution_mode`)
- 可否 dry-run (`dry_run_available`)
- 可否 mock (`mock_available`)
- 外部接觸點 (`external_touchpoints`)
- Rollback 說明 (`rollback_note`)

---

## 12. Execution permission display

The Owner Review Panel and the review queue both displayed the execution
permission as unauthorized:

```
執行權限：未授權
execution_permission = False
```

This is hard-coded `False` by the F-B deriver and is display-only; it grants no
execution.

---

## 13. Dispatch allowed display

The Owner Review Panel and the review queue both displayed dispatch as not
allowed:

```
派工允許：未允許
dispatch_allowed = False
```

This is hard-coded `False` by the F-B deriver and is display-only; it permits no
Worker dispatch.

---

## 14. Safety reminders validated

The decision/execution separation reminders rendered on both surfaces:

- 審核準備狀態不是執行權限。 (Approval readiness is not execution permission.)
- Owner 核准不等於 Worker 執行。 (Owner approval does not imply Worker execution.)
- Decision 與 dispatch 仍然分離。 (Decision and dispatch remain separate.)

---

## 15. Legacy / fallback behavior

Tasks without annotation metadata rendered safely (no traceback, no HTTP 500):

- A `waiting_review` legacy task conservatively derived
  `approval_readiness = owner_review_required` while still showing the fallback
  text (`owner_reason`, `risk_summary`, etc.).
- A non-review legacy task (e.g. `queued`) conservatively derived
  `approval_readiness = not_ready`.
- In all cases 執行權限：未授權 / 派工允許：未允許
  (`execution_permission = False` / `dispatch_allowed = False`) were shown.

---

## 16. Replit overlay note

The Replit / local overlay files (`.replit`, `.claude/`, `patches/`) are
environment-specific and are intentionally left untouched. This segment does not
reset, checkout, or delete any overlay file; `patches/` remains untracked and
preserved.

---

## 17. Safety boundaries

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

Current safe posture (display-only): Dashboard read-only; Worker OFF / not
running; OpenClaw Not Connected; Hermes Not Connected; Google Sheets Disabled.

---

## 18. Non-goals

v0.7.2-F-C-R explicitly does not:

- Change any runtime code, template, or static asset.
- Change QueueStore runtime behavior, approval wiring, or any POST action.
- Add a route or migrate schema.
- Start the Worker, call OpenClaw, call Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external dependency.
- Seed (`--apply`) or clean up the demo task.
- Click approve/reject/cancel/retry/archive.
- Create a release tag (no tag unless the Owner explicitly approves).

---

## 19. Acceptance criteria

v0.7.2-F-C-R is accepted when:

1. This closeout / validation document exists at the documented path and
   contains sections 1–21.
2. The readiness script
   `scripts/check_hermes_openclaw_dashboard_annotation_display_closeout_replit_validation_v0_7_2_f_c_r.py`
   exists and reports PASS.
3. The document records the Replit Preview validation of `/dashboard/reviews`
   and `/dashboard/tasks/demo-ui-e-b-review-001`, the validated annotation
   fields, the execution_permission / dispatch_allowed unauthorized display, and
   the decision/execution separation reminders.
4. The document states the safety boundaries and non-goals.
5. The segment adds only this document and the readiness script — no runtime
   file changed.
6. Nothing is committed, pushed, or tagged in this segment without Owner
   approval.

---

## 20. Current state

- master = `463f09d69dd9da26224a5b02a653c7dce20e2208` (`feat: display queue task
  annotations`).
- F-A / F-B / F-C are merged and pushed; the annotation deriver and its display
  are live read-only.
- Replit Preview validated `/dashboard/reviews` and
  `/dashboard/tasks/demo-ui-e-b-review-001` after a process restart.
- Worker OFF; OpenClaw Not Connected; Hermes Not Connected; Google Sheets
  Disabled; no external side effects.
- The demo task `demo-ui-e-b-review-001` remains in the Replit queue; it was not
  cleaned up.

---

## 21. Next recommended step

Recommended next step (each requires explicit Owner approval to start):

1. Commit this closeout record (Owner-approved local commit), then push only
   after Owner approval.
2. Optionally proceed to a future F-D segment (annotation authoring at intake
   time via `payload.metadata`, no schema change) — separately planned and
   approved.

Execution dispatch wiring remains explicitly **out** of this feature line:
approval readiness is not execution permission, and Owner approval does not
imply Worker execution — decision and dispatch remain separate.
