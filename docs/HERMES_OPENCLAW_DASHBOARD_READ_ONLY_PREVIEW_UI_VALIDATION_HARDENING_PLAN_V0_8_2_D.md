# Hermes × OpenClaw v0.8.2-D
# Dashboard Read-only Preview UI Validation Hardening Plan

## 0. Status
- Phase: v0.8.2-D
- Type: plan-only
- Base commit: 1ee0bd597eb3d5f56028482389eb33a6cf9ccc97
- Previous phase: v0.8.2-C = DONE / PUSHED / CLOSED
- Implementation status: NOT IMPLEMENTED
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED

v0.8.2-D is a plan-only round. It does not modify Dashboard implementation. It does not modify
app/main.py. It does not modify templates/system.html. It does not modify static/dashboard.css. It
does not modify the v0.8.2-C validation script. It only plans future Dashboard read-only preview UI
validation hardening.

## 1. Purpose

v0.8.2-C added a read-only Dashboard preview UI refinement to the existing GET-only /dashboard/system
surface (section headers, an Owner Review notice, a badge block, a permission-flag meta-grid, and a
rows table with a caption and an empty state), all still sourced from
build_dashboard_preview_model(). v0.8.2-C's own validation script
(check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py) proved the refinement is
safe, but that script — like the v0.8.2-A script before its fixed-range follow-up fix — mixes two
different concerns in one check: (a) "is the required content and safety boundary present" and
(b) "is the effective changed-file scope exactly what this round is allowed to touch". Concern (b) is
inherently unstable once later, unrelated rounds add new untracked or committed files, because it was
written against a moving HEAD and a moving untracked-file set.

v0.8.2-D's purpose is to plan how a future v0.8.2-E hardening round would:
- separate "content/safety boundary is intact" checks from "this round's own changed-file scope"
  checks, so later rounds do not cause spurious failures in earlier rounds' validation scripts;
- give future validation a stable, explicit way to run in three phases — Owner Review (uncommitted),
  post-commit (committed, not yet pushed), and post-push (committed and pushed) — without needing a
  separate flag for each phase, following the same fixed-range pattern already proven in the
  v0.8.2-A fixed-range follow-up fix;
- keep validating that the Dashboard read-only preview UI never regresses toward exposing execution,
  dispatch, or other real-world side-effect controls;
- avoid ever importing app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/Hermes/Google
  Sheets integration, the P loader, or the V adapter from within a validation script.

This document does not implement any of the above. It only records the plan and the boundaries a
future v0.8.2-E would have to respect.

## 2. Current Safe Baseline

The following safety boundary is currently true and must remain true through v0.8.2-D and any future
v0.8.2-E:

- GET-only
- read-only
- synthetic local-only
- permission flags false
- disabled runtime badges visible
- no POST
- no button/form/action URL
- no Worker/OpenClaw/Hermes/Google Sheets
- no secrets
- no real queue DB
- no Remote Blackboard API runtime

## 3. What v0.8.2-C Changed

Summary of the already-completed and already-pushed v0.8.2-C round:

- templates/system.html: the v0.8.2-A display block was restructured into a single
  `<section class="local-mock-preview">` with a header, an Owner Review reminder notice, a badges
  block, a six-flag meta-grid, and a table-wrap (rows table with caption, or an empty-state block).
- static/dashboard.css: a new v0.8.2-C-marked CSS block defining the `.local-mock-preview` class
  family plus two responsive breakpoints. Pure layout/spacing/typography rules only.
- scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py: the v0.8.2-C
  validation script, committed and passing 37/37 both pre- and post-commit and post-push.
- No app/main.py route change.
- No data source change — Dashboard still consumes build_dashboard_preview_model() exactly as before.
- No fixture JSON, P loader, or V adapter change.

## 4. Validation Hardening Problems To Solve

At least the following problems should be solved by a future v0.8.2-E:

- v0.8.2-C's validation script is useful but mostly checks current content and changed scope in one
  pass; it does not yet separate "content is correct" from "this round's file scope is correct".
- Future validation should distinguish the Owner Review phase (uncommitted diff) from the committed
  phase (tracked, part of git history) so the same script gives a stable answer in both without a
  manual mode switch.
- Future validation should support a stable post-commit / post-push baseline, the same way the
  v0.8.2-A fixed-range follow-up fix pinned EXPECTED_BASE_HEAD..EXPECTED_V0_8_2_A_FINAL_HEAD instead of
  EXPECTED_BASE_HEAD..HEAD, so that later unrelated commits are never misclassified as this round's
  changed files.
- Future validation should avoid falsely failing merely because later plan docs or scripts (e.g. a
  future v0.8.2-F, v0.8.3, etc.) are added to the repository as new untracked or committed files.
- Future validation should continue to preserve strict safety boundaries: disabled runtime badges
  visible, permission flags false, no forbidden interactive controls added.
- Future validation should never import app runtime, Dashboard runtime, QueueStore, Worker/OpenClaw/
  Hermes/Google Sheets integration, the P loader, or the V adapter; it should never start a server; it
  should read no real queue DB, send no POST, make no network call, read no secrets, write no repo
  file, and modify no git index.

## 5. Proposed Future v0.8.2-E Scope

If Owner explicitly authorizes v0.8.2-E in the future, it would be allowed, at most, to:

- add a new v0.8.2-E hardening validation script;
- optionally add docs describing the validation hardening boundaries and design;
- optionally update v0.8.2-D / v0.8.2-E documentation only, and only if explicitly authorized.

v0.8.2-E must not modify:

- app/main.py
- templates/system.html
- static/dashboard.css
- the v0.8.2-C validation script, unless explicitly authorized
- the v0.8.2-B plan doc or readiness script
- the v0.8.2-A validation script
- the v0.8.1-P loader
- the v0.8.1-V adapter
- the fixture JSON
- any route, QueueStore, or other data source

## 6. Proposed v0.8.2-E Validation Requirements

A future v0.8.2-E validation script should check:

- current HEAD contains the v0.8.2-C base commit (1ee0bd597eb3d5f56028482389eb33a6cf9ccc97);
- v0.8.2-C's files (templates/system.html, static/dashboard.css, the C validation script) exist and
  are tracked;
- the v0.8.2-D plan doc exists and, once committed, is tracked;
- the v0.8.2-C validation script remains tracked and runnable (importable/executable as a
  subprocess, without importing it as a Python module into the same process);
- the required disabled runtime badges are still present in templates/system.html;
- the required permission flags (is_mock, local_only, read_only, execution_permission,
  dispatch_permission, external_side_effects_permission) are still present;
- no forbidden interactive control (`<form`, `<button`, `method="post"`, `action=`, `onclick=`,
  `action_url`, `post_url`, `webhook_url`, `endpoint_url`, `execute_url`, `dispatch_url`) is present in
  the relevant added/effective content;
- app/main.py is not modified by this round;
- the P loader, the V adapter, the fixture JSON, and the real queue DB are not touched;
- no POST, no network call, no secrets read, no Worker/OpenClaw/Hermes/Google Sheets call is made or
  claimed;
- `patches/` stays untracked and untouched;
- the script gives a stable, correct answer whether run during the Owner Review phase (uncommitted),
  the post-commit phase, or the post-push phase, without a manual mode flag — following the same
  fixed-range / union-of-committed-and-working-tree pattern already proven in the v0.8.2-A fixed-range
  follow-up fix.

## 7. Proposed v0.8.2-E Post-commit / Post-push Regression Boundary

A future v0.8.2-E should define its committed-diff range the same way the v0.8.2-A fixed-range fix
does: pin an `EXPECTED_V0_8_2_E_FINAL_HEAD` once v0.8.2-E's own commit exists, and compute the
committed diff as `EXPECTED_BASE_HEAD..EXPECTED_V0_8_2_E_FINAL_HEAD` (falling back to `HEAD` only while
v0.8.2-E's own commit does not yet exist in history), so that any later round (v0.8.2-F, v0.8.3, ...)
added on top never gets misclassified as v0.8.2-E's own changed-file scope. This is the same lesson
learned from the v0.8.2-B / v0.8.2-A untracked-file coupling incident documented in this project's
history.

## 8. How Future v0.8.2-E Avoids Touching Route / Data Source / Fixture / P Loader / V Adapter / Worker / OpenClaw / Hermes / Google Sheets

A future v0.8.2-E is scoped to validation-script-only changes (see Section 5), so by construction it
cannot:

- add or modify any `/dashboard/*` or other app route, because it does not touch app/main.py;
- change the Dashboard data source, because it does not touch app/main.py or templates/system.html,
  and Dashboard continues to consume build_dashboard_preview_model() unchanged;
- read the fixture JSON directly or call `load_local_mock_fixture_preview()` /
  `validate_local_mock_fixture_preview_object()`, because it does not touch the P loader or the V
  adapter and a validation script must not import them for execution (only path/existence/tracked
  checks via `pathlib`/`git`, never a Python import that runs their logic);
- start Worker, call OpenClaw, activate Hermes, or read/write Google Sheets, because a validation
  script is standard-library-only, imports no app runtime, and makes no network call;
- read secrets, because a validation script reads no `.env` and no credential file.

## 9. Exact Future v0.8.2-E Authorization Phrase

The following exact phrase, and only this exact phrase, may be used by Owner in the future to
authorize v0.8.2-E implementation. Paraphrases, general approval, readiness PASS, or Owner Review PASS
do not authorize v0.8.2-E. v0.8.2-E is not started by v0.8.2-D.

批准實作 v0.8.2-E — Dashboard Read-only Preview UI Validation Hardening Implementation，僅允許新增或調整 validation hardening artifacts，以更穩定驗證 v0.8.2-C 已完成的 /dashboard/system read-only preview UI；必須保持 GET-only、read-only、synthetic local-only、permission flags false、disabled runtime badges visible；不得修改 Dashboard route，不得修改資料來源，不得呼叫 P loader，不得直接讀 fixture JSON，不得讀 real queue DB，不得 POST，不得新增 button/form/action URL/webhook/endpoint/execute/dispatch/send controls，不得啟 Worker/OpenClaw/Hermes/Google Sheets，不得讀 secrets，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 10. Acceptance Criteria For D

v0.8.2-D is considered complete when:

- the v0.8.2-D plan doc exists;
- the v0.8.2-D readiness script exists;
- the v0.8.2-D readiness script PASSes;
- baseline checks (v0.8.2-C, v0.8.2-A, v0.8.2-B, V, W, Z, Y, X, compileall) PASS, or fail only because
  of the expected plan-only untracked-file exception (the D plan doc and D readiness script being
  untracked during Owner Review);
- no existing tracked file is modified;
- no commit, no push, no tag happens in this round;
- a full Owner Review diff is produced for Owner to review before any commit.

## 11. Non-goals

v0.8.2-D explicitly does NOT:

- implement anything;
- change the Dashboard UI;
- change any CSS;
- change any Dashboard route;
- start or connect Worker, OpenClaw, Hermes, or Google Sheets;
- perform any true execution, dispatch, or external side effect of any kind.
