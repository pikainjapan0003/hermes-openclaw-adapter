# Hermes × OpenClaw Adapter — Safe Local Cleanup Tool (v0.7.4-F)

> **Status: DRY-RUN-ONLY TOOL.** This version adds a pure helper and a dry-run-only
> CLI that read an explicit synthetic JSON input and emit a demo task cleanup
> candidate report to stdout. It implements no apply path: it deletes no task,
> archives no task, modifies no queue DB, modifies no local queue data, modifies no
> Replit queue data, and reads no real queue DB. It changes no existing runtime
> route, no QueueStore, no template, no static asset, no existing doc, and no
> README; it creates no tag.
>
> Boundary declarations:
>
> - v0.7.4-F is a dry-run-only tool.
> - No cleanup apply.
> - No --apply.
> - No task deletion.
> - No task archive.
> - No queue DB change.
> - No local queue data change.
> - No Replit queue data change.
> - No real queue DB read.
> - No POST.
> - No live local queue write validation.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No secrets read.
> - No webhook.
> - No external side effects.

---

## 1. Purpose

This is the **Safe Local Cleanup Tool** for the v0.7.4 line, in its dry-run-only
form. It classifies tasks from an explicit synthetic JSON input and produces a
cleanup candidate report — candidates and blocked items — to stdout. It performs no
cleanup, no apply, no deletion, no archive, no queue write, and no external side
effect.

---

## 2. Current master

```
HEAD = origin/master = 110285ba7f243f0e75f1a5208f95ad0d8f46c655
docs: plan demo task cleanup safety
```

---

## 3. Scope

In scope (this segment only):

- Add a pure helper `app/demo_task_cleanup_v0_7.py`
  (`derive_demo_task_cleanup_dry_run_report`).
- Add a dry-run-only CLI `scripts/demo_task_cleanup_dry_run_v0_7_4_f.py`.
- Add this document, a readiness script, and a synthetic test.

Explicitly out of scope: any change to `app/main.py`, `app/queue_store.py`,
QueueStore runtime behavior, approval routes, dashboard auth, status transitions,
templates, static assets, the seed script, existing docs, the README, the Worker,
or any external system. No apply path, no task deletion, no task archive, and no
queue data change.

---

## 4. Relationship to v0.7.4-E

```
v0.7.4-E Demo Task Cleanup Plan is complete.
Cleanup Plan is not cleanup apply.
Cleanup dry-run is not cleanup apply.
Cleanup apply requires separate Owner approval.
Cleanup apply requires an explicit apply flag.
Cleanup apply requires a second confirmation flag.
WSL cleanup tooling must not clean Replit queue.
```

v0.7.4-F implements the dry-run side of the v0.7.4-E plan only; it implements none
of the apply side.

---

## 5. Tool boundary

```
v0.7.4-F Safe Local Cleanup Tool is dry-run-only.
v0.7.4-F does not implement cleanup apply.
v0.7.4-F does not delete tasks.
v0.7.4-F does not archive tasks.
v0.7.4-F does not modify queue DB.
v0.7.4-F does not modify local queue data.
v0.7.4-F does not modify Replit queue data.
v0.7.4-F does not read real queue DB.
v0.7.4-F requires explicit JSON input.
v0.7.4-F writes report to stdout only.
```

---

## 6. Helper contract

`derive_demo_task_cleanup_dry_run_report(tasks, *, source_queue="synthetic",
target_environment="local") -> dict` is a pure function. It reads only the task
list passed in, never writes, never mutates its input, never reads a real queue DB,
and uses only the standard library (`json` / `uuid` / `datetime` / `typing`). It
imports no `app.main` and no QueueStore. It deletes, archives, and modifies
nothing; it only classifies tasks into candidates and blocked items.

---

## 7. CLI contract

`scripts/demo_task_cleanup_dry_run_v0_7_4_f.py` is a dry-run-only CLI. It requires
`--input`, reads only that explicit JSON file, builds the report via the helper,
and prints the JSON report to stdout. It writes no output file, reads no real
queue, scans no queue by default, modifies no data, and provides no apply path.

---

## 8. Explicit input requirement

The CLI requires an explicit `--input` JSON file (a list of tasks or
`{"tasks": [...]}`). Without `--input` the CLI fails. It never scans a default
queue and never reads a real queue DB; only the synthetic file the user explicitly
passes is read.

---

## 9. Candidate classifier

A task becomes a candidate only via an explicit metadata marker — never by
`task_id`, `title`, or `summary` name alone. Accepted markers:

```
metadata.demo_task = true
metadata.sample_task = true
metadata.preview_task = true
metadata.test_task = true
metadata.cleanup_classification = demo/sample/preview/test
metadata.task_classification = demo/sample/preview/test
```

---

## 10. Blocked item rules

```
A task with no explicit demo marker is blocked.
A target_environment that is not local or preview blocks every task.
A task with a production marker is blocked.
A task with an external side effect marker is blocked.
A task with a secret-like marker is blocked.
A task with unknown origin is blocked.
A task needed for active validation is blocked unless metadata.owner_approved_replacement = true.
```

Secret-like tasks are never printed; only a blocked reason is recorded.

---

## 11. Dry-run report format

The report carries at least these fields:

```
report_id
generated_at
execution_mode
dry_run
apply_requested
apply_allowed
candidate_count
blocked_count
candidates
blocked_items
source_queue
target_environment
would_delete
would_archive
would_modify
external_side_effects
owner_approval_required
rollback_note
safety_notes
```

---

## 12. Fixed safety values

The report's fixed safety values are always:

```
execution_mode = "dry_run_only"
dry_run = True
apply_requested = False
apply_allowed = False
would_delete = False
would_archive = False
would_modify = False
external_side_effects = False
owner_approval_required = True
```

---

## 13. Apply prohibition in v0.7.4-F

```
No apply path exists in v0.7.4-F.
The CLI must reject --apply.
The CLI must reject --confirm-apply.
The CLI must reject apply-like arguments.
Owner approval of v0.7.4-F does not approve cleanup apply.
A future apply path requires a separate version, separate Owner approval, and dual explicit flags.
```

If any apply-like argument is present, the CLI exits non-zero and shows a blocked
message before reading any file or producing any report.

---

## 14. Owner approval boundary

Owner approval of this dry-run tool does not approve cleanup apply. Reviewing a
dry-run candidate report does not approve cleanup apply. Any future apply path
requires a separate version, separate explicit Owner approval, and dual explicit
flags.

---

## 15. Local queue vs Replit queue boundary

```
Windows WSL local queue and Replit local queue are separate.
WSL cleanup tooling must not clean Replit queue.
Replit pull updates code, not queue data.
GitHub push updates code, not queue data.
Remote shared DB is future-only.
```

---

## 16. QueueStore boundary

```
QueueStore runtime behavior is unchanged in v0.7.4-F.
v0.7.4-F does not modify app/queue_store.py.
v0.7.4-F does not add QueueStore methods.
v0.7.4-F does not delete tasks.
v0.7.4-F does not archive tasks.
v0.7.4-F does not modify payload persistence.
v0.7.4-F does not modify status persistence.
```

---

## 17. Route / POST boundary

```
v0.7.4-F does not add POST routes.
v0.7.4-F does not modify approval POST behavior.
v0.7.4-F does not modify reject POST behavior.
v0.7.4-F does not modify cancel POST behavior.
v0.7.4-F does not modify retry POST behavior.
v0.7.4-F does not modify archive POST behavior.
v0.7.4-F does not add cleanup route.
v0.7.4-F does not add cleanup button.
v0.7.4-F does not add cleanup form.
```

---

## 18. Runtime / external side-effect boundary

v0.7.4-F produces no runtime route change and no external side effect: no Worker
run, no OpenClaw call, no Hermes call, no Google Sheets write, no webhook, no
network write, no real queue read, no queue write. It only reads an explicit
synthetic JSON input and writes a JSON report to stdout.

---

## 19. Tests and readiness

- `scripts/check_hermes_openclaw_safe_local_cleanup_tool_v0_7_4_f.py` — static
  readiness check over the five files, the doc sections, markers, fixed safety
  values, apply-rejection, classifier, and boundaries.
- `scripts/test_demo_task_cleanup_dry_run_v0_7_4_f.py` — pure synthetic tests of the
  helper and CLI (no real queue, no POST, no apply, no queue data change).

---

## 20. Non-goals

v0.7.4-F explicitly does not:

- Change `app/main.py`, `app/queue_store.py`, QueueStore runtime behavior, approval
  routes, dashboard auth, status transitions, templates, static assets, the seed
  script, existing docs, or the README.
- Implement an apply path, a cleanup route, button, or form.
- Delete, archive, or modify any task, queue DB, local queue data, or Replit queue
  data.
- Read a real queue DB, POST to the Replit Preview or a real queue, or perform a
  live local queue write validation.
- Start the Worker, call OpenClaw / Hermes, or write Google Sheets.
- Read secrets, create a webhook, or add any external side effect.
- Commit, push, or create a release tag.

---

## 21. Acceptance criteria

v0.7.4-F is accepted when:

1. The helper, CLI, document, readiness script, and synthetic test exist at the
   documented paths; this document contains sections 1–22.
2. The readiness script
   `scripts/check_hermes_openclaw_safe_local_cleanup_tool_v0_7_4_f.py` reports PASS
   and the synthetic test passes.
3. The helper returns the fixed safety values (`dry_run = True`,
   `apply_allowed = False`, `would_delete = False`, `would_archive = False`,
   `would_modify = False`, `external_side_effects = False`) and classifies
   candidates only by explicit metadata markers.
4. The CLI requires explicit input and rejects apply-like arguments.
5. The document carries no unsafe claim and no secret.
6. Only the five allowed files are added; no existing file changed.
7. Nothing is committed, pushed, or tagged without Owner approval.

---

## 22. Next recommended step

Recommended next step (requires explicit Owner approval to start):

- **v0.7.4-F-R — Safe Local Cleanup Tool Closeout.**

> No Replit POST validation is required for v0.7.4-F.
> No Replit queue cleanup is allowed.
> v0.7.4-F-R must remain dry-run / current-state only.
> A future apply path requires a separate version, separate Owner approval, and dual explicit flags.
