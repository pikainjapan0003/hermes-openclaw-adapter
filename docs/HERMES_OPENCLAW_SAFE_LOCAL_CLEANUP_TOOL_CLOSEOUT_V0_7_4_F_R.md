# HERMES ↔ OpenClaw Adapter — Safe Local Cleanup Tool Closeout (v0.7.4-F-R)

> Closeout / current-state document. This is **docs / closeout only**. It records the
> completed, dry-run-only state of the v0.7.4-F Safe Local Cleanup Tool. It changes no
> runtime, performs no cleanup, performs no apply, and introduces no external side effect.

## 1. Purpose

This document formally closes out **v0.7.4-F — Safe Local Cleanup Tool** and records the
current safe state of the adapter after that feature landed on `origin/master`.

It exists so that the dry-run-only nature of the cleanup tool is captured as an explicit,
reviewable, current-state record: what was added, what was validated, and — most
importantly — which boundaries remain in force (no cleanup apply, no task deletion, no
task archive, no queue-data change, no external side effect).

This closeout adds **only** documentation and a readiness verification script. It does not
modify `app/`, `templates/`, `static/`, seed scripts, existing docs, or the README.

## 2. Current master

```
HEAD = origin/master = dce39f871f0119f72d24f8cf2ea6a54ef0bf6de0
feat: add dry-run demo task cleanup tool
```

The v0.7.4-F commit `dce39f8` is fully synced to `origin/master`. The working tree is
clean apart from the accepted untracked `patches/` overlay.

## 3. Scope

In scope for v0.7.4-F-R:

- Add this closeout / current-state document.
- Add a readiness script that statically verifies this document.

Out of scope for v0.7.4-F-R (and explicitly forbidden this round):

- Any runtime change, any cleanup, any apply, any commit, any push, any tag.
- Any change to `app/`, `app/main.py`, `app/queue_store.py`, `templates/`, `static/`,
  seed scripts, existing docs, or the README.

## 4. Relationship to v0.7.4-F

v0.7.4-F delivered the dry-run-only Safe Local Cleanup Tool. The following facts are
recorded as the closed state of that feature:

```
v0.7.4-F Safe Local Cleanup Tool is complete.
v0.7.4-F is dry-run-only.
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

## 5. Relationship to v0.7.4-E

v0.7.4-E established the Demo Task Cleanup **Plan** (plan-first). v0.7.4-F implemented the
dry-run tool consistent with that plan's safety contract:

```
Cleanup Plan is not cleanup apply.
Cleanup dry-run is not cleanup apply.
Cleanup apply requires separate Owner approval.
```

v0.7.4-F is the dry-run realization of the v0.7.4-E plan. It does not advance to an apply
phase, and the apply phase remains gated behind separate Owner approval.

## 6. Files added in v0.7.4-F

```
app/demo_task_cleanup_v0_7.py
scripts/demo_task_cleanup_dry_run_v0_7_4_f.py
docs/HERMES_OPENCLAW_SAFE_LOCAL_CLEANUP_TOOL_V0_7_4_F.md
scripts/check_hermes_openclaw_safe_local_cleanup_tool_v0_7_4_f.py
scripts/test_demo_task_cleanup_dry_run_v0_7_4_f.py
```

These five files are the entire v0.7.4-F surface: a pure dry-run helper, a stdout-only
CLI, the safety-boundary document, a static readiness check, and a synthetic test.

## 7. Dry-run-only helper validation

The helper exposes a single pure classifier and obeys strict dry-run boundaries:

```
derive_demo_task_cleanup_dry_run_report exists.
Helper is pure dry-run classifier.
Helper does not import app.main.
Helper does not import QueueStore.
Helper does not read real queue DB.
Helper does not mutate input.
Helper does not delete tasks.
Helper does not archive tasks.
Helper does not modify queue data.
```

The report it returns carries fixed safety values that can never indicate an apply or an
external side effect:

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

## 8. CLI validation

The CLI is dry-run-only and provides no apply path:

```
CLI requires explicit JSON input.
CLI writes JSON report to stdout only.
CLI rejects --apply.
CLI rejects --confirm-apply.
CLI rejects apply-like arguments.
CLI provides no apply path.
CLI does not read real queue DB.
CLI does not POST.
```

Any argument containing the token `apply` is rejected before any file read or report
derivation, so there is no code path that could escalate from dry-run to apply.

## 9. Synthetic test validation

The test uses only synthetic, in-memory / temp-JSON fixtures. It never touches a real
queue DB and sends no network request.

```
v0.7.4-F dry-run tool test: ALL PASS.
```

One synthetic fixture deliberately includes a fake secret-like value to verify that the
helper blocks / redacts such fields rather than emitting them. The value is not real.

## 10. Readiness validation

The static readiness check for the tool passes in full:

```
v0.7.4-F readiness: ALL PASS.
```

## 11. Prior regression checks

All prior readiness / test / check suites continue to pass:

```
v0.7.4-F readiness: ALL PASS.
v0.7.4-F dry-run tool test: ALL PASS.
v0.7.4-E check: ALL PASS.
v0.7.4-D-R check: ALL PASS.
v0.7.4-D readiness and helper test: ALL PASS.
v0.7.4-C / B / A checks: ALL PASS.
v0.7.3 checks: ALL PASS.
prior F-line checks: ALL PASS.
compileall app + scripts: PASS.
```

## 12. Safety grep summary

A safety grep over the v0.7.4-F surface and over this closeout round found no real unsafe
claim and no real secret:

```
No real unsafe claim was found.
No real secret was found.
Helper secret-like key names are defensive markers, not secret values.
Synthetic test fixture secret-like value is fake and used only to verify blocking/redaction behavior.
Readiness forbidden-pattern matches are benign.
```

The only grep hits are: (a) defensive key-name markers in the helper used to decide what
to block / redact, (b) one fake fixture value in the synthetic test, and (c) the forbidden
pattern lists inside the readiness scripts themselves. All are benign by construction.

## 13. No Replit POST validation required

```
No Replit POST validation is required for v0.7.4-F.
No Replit queue cleanup is allowed.
No Replit Preview POST was sent.
No Replit queue data was modified.
```

Because the tool is dry-run-only and stdout-only, there is nothing to validate against a
live Replit Preview or a real queue. No POST-based validation was performed.

## 14. No cleanup / apply boundary

```
No cleanup demo task.
No cleanup apply.
No --apply.
No task deletion.
No task archive.
No cleanup route.
No cleanup button.
No cleanup form.
```

There is no apply path, no state-changing route, no state-changing button, and no
state-changing form. The apply phase stays gated behind separate Owner approval.

## 15. QueueStore / queue data boundary

```
No queue DB change.
No local queue data change.
No Replit queue data change.
No real queue DB read.
No QueueStore runtime behavior change.
No app/queue_store.py change.
```

The helper never imports `QueueStore`, never reads a real queue DB, and never writes any
queue data. `app/queue_store.py` is unchanged.

## 16. Runtime / external side-effect boundary

```
No POST.
No live local queue write validation.
No Worker execution.
No OpenClaw call.
No Hermes call.
No Google Sheets write.
No secrets read.
No webhook.
No external side effects.
No production DB.
No remote shared DB.
No Remote Blackboard API runtime.
No connector.
No approval routes change.
No dashboard auth change.
No status transition change.
No runtime guard.
No existing transition result change.
```

## 17. Current safe system posture

After v0.7.4-F, the adapter remains in a read-only / dry-run-safe posture:

- The cleanup capability that exists is dry-run-only and stdout-only.
- No code path deletes, archives, or modifies tasks or queue data.
- No code path performs an external side effect.
- Apply remains a separate, Owner-approval-gated future step.

The fixed safety values (`execution_mode = "dry_run_only"`, `dry_run = True`,
`apply_allowed = False`, `would_delete = False`, `would_archive = False`,
`would_modify = False`, `external_side_effects = False`, `owner_approval_required = True`)
encode this posture directly in every report the tool produces.

## 18. Non-goals

- Not implementing or enabling a cleanup apply path.
- Not deleting, archiving, or modifying any task.
- Not changing any queue DB / local queue data / Replit queue data.
- Not reading a real queue DB.
- Not sending any POST or performing live queue-write validation.
- Not starting the Worker; not calling OpenClaw / Hermes; not writing Google Sheets.
- Not changing `app/main.py`, `app/queue_store.py`, approval routes, dashboard auth, or
  status transitions.
- Not adding a webhook, connector, production DB, remote shared DB, or Remote Blackboard
  API runtime.

## 19. Acceptance criteria

- This closeout document exists and contains sections 1–20.
- The current-master marker records `dce39f8` on `origin/master`.
- The v0.7.4-F completion markers are present.
- The five v0.7.4-F file markers are present.
- The helper validation markers and fixed safety values are present.
- The CLI validation markers are present.
- The test / check PASS markers are present.
- The safety grep summary, No-Replit-POST, cleanup/apply, QueueStore/queue-data, and
  runtime/external side-effect boundary markers are present.
- The next recommended step is present.
- No real unsafe claim and no real secret appear in this document.
- The readiness script `check_hermes_openclaw_safe_local_cleanup_tool_closeout_v0_7_4_f_r.py`
  passes ALL.

## 20. Next recommended step

```
v0.7.4-R — Topology + Queue + Audit Display Closeout
```

with the constraints:

```
v0.7.4-R must remain closeout / docs-only unless separately approved.
v0.7.4-R must not perform cleanup apply.
v0.7.4-R must not start Worker / OpenClaw / Hermes / Google Sheets.
```
