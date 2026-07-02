# Hermes × OpenClaw v0.8.2-F
# Dashboard Read-only Preview Validation Closeout / Handoff Plan

## 0. Status
- Phase: v0.8.2-F
- Type: plan-only / closeout / handoff
- Base commit: 98cf8115ee7389742a9763dc3660911ea220115a
- Previous phase: v0.8.2-E = DONE / PUSHED / CLOSED
- Implementation status: NOT IMPLEMENTED
- Commit status: NOT COMMITTED
- Tag status: NOT TAGGED
- v0.8.3 status: NOT STARTED

v0.8.2-F is a plan-only closeout / handoff round. It does not modify Dashboard implementation. It does
not modify app/main.py. It does not modify templates/system.html. It does not modify
static/dashboard.css. It does not modify the v0.8.2-E validation script. It only collects, summarizes,
and hands off the state of the v0.8.2 Dashboard read-only preview validation series for Owner decision
on whether/how to proceed toward v0.8.3.

## 1. Purpose

The v0.8.2 series (A through E) built and hardened a read-only Dashboard preview UI at the existing
GET-only `/dashboard/system` surface, plus a stable validation gate for it. v0.8.2-F's purpose is to:

- close out the v0.8.2 series with a single reference document Owner can consult without re-reading
  five separate rounds' worth of Owner Review transcripts;
- record which validation scripts are safe to treat as permanent regression gates versus which are
  scoped to a specific round's Owner Review phase and should not be relied on afterward;
- restate the current safety boundary in one place;
- hand off a recommendation for what a future v0.8.3 would need to plan first, without starting any of
  it.

This document implements nothing. It only summarizes prior work and proposes a boundary for future
work, pending explicit Owner authorization.

## 2. v0.8.2 Series Summary

- **A — Dashboard Preview Adapter Read-only Display Integration**: wired app/main.py's existing
  GET-only `/dashboard/system` route to call `build_dashboard_preview_model()` from the v0.8.1-V
  read-only preview adapter, and added the first version of the local mock preview display block to
  templates/system.html. No new route, no data-source change beyond the read-only adapter call.
- **B — Dashboard Read-only Preview UI Refinement Plan**: plan-only round that reviewed A's completed
  display block and planned a future UI refinement (layout, labels, captions, empty-state, Owner
  Review reminder) without touching any code. Defined the exact v0.8.2-C authorization phrase.
- **C — Dashboard Read-only Preview UI Refinement Implementation**: implemented the plan from B —
  restructured the display block into `<section class="local-mock-preview">` with header, Owner
  Review notice, badges, a six-flag meta-grid, and a table-wrap (rows table with caption, or an
  empty-state). Added the matching `.local-mock-preview` CSS class family to static/dashboard.css. No
  new interactive control was added.
- **D — Dashboard Read-only Preview UI Validation Hardening Plan**: plan-only round that identified a
  structural problem in C's validation script (it conflates "content is correct" with "this round's
  changed-file scope is correct" against a moving HEAD, which breaks once later rounds add new files)
  and proposed a fixed pattern for a future hardening implementation. Defined the exact v0.8.2-E
  authorization phrase.
- **E — Dashboard Read-only Preview UI Validation Hardening Implementation**: implemented the plan from
  D — added a new validation script that (1) detects its own phase (`owner_review` /
  `post_commit_or_ahead` / `post_push_or_synced`) purely from its own tracked/untracked status and
  HEAD-vs-origin/master comparison, never from a historical committed-diff range, and (2) checks
  Dashboard read-only preview UI safety-boundary content directly from the current file content rather
  than from a diff against a historical base. Verified stable across Owner Review, post-commit, and
  post-push phases with zero script modification in between.

Each of A/B/C/D/E is DONE / PUSHED / CLOSED as of the base commit above.

## 3. Current Latest Baseline

- HEAD = origin/master = 98cf8115ee7389742a9763dc3660911ea220115a
- latest commit = test: add dashboard read-only preview validation hardening
- status expected = clean except patches/
- tag = NOT TAGGED
- Worker OFF
- OpenClaw NOT CONNECTED
- Hermes NOT CONNECTED
- Google Sheets DISABLED

## 4. Stable Validation Gates

The following are safe to treat as standing regression gates going forward, because they either check
tracked/committed state that does not depend on a moving HEAD, or (in E's case) were specifically
designed to remain stable across all three phases:

- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_v0_8_2_e.py` — the
  v0.8.2-E script. E is the preferred content/safety-boundary gate. E is stable post-commit/post-push:
  it supports `owner_review` / `post_commit_or_ahead` / `post_push_or_synced` phases automatically for
  its own lifecycle, and its content/safety-boundary checks (required text markers, disabled badges,
  permission flags, rows-table columns, forbidden interactive controls, CSS class family, forbidden CSS
  patterns) read current file content directly rather than a historical diff, so those checks stay
  stable no matter how many later rounds land on top. However, E is
  not fully immune to later Owner Review untracked artifacts — see the nuance below.

  **Important nuance for the E gate:** the v0.8.2-E script is the preferred Dashboard read-only preview
  UI content/safety-boundary gate and is confirmed stable across its own Owner Review, post-commit, and
  post-push lifecycle. However, its untracked-file allowlist check is still intentionally strict.
  During later Owner Review rounds, new untracked later-round artifacts may cause E check [E] to fail.
  If that happens and the only failure is unexpected untracked later-round Owner Review files, treat it
  as a scope/phase warning, not as a Dashboard content or safety-boundary failure. The content markers,
  disabled badges, permission flags, forbidden controls, and CSS safety checks remain the important
  safety signal.
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py` — the v0.8.2-C
  script. Still valid as a fixed-range historical regression check (its own round is long since
  committed and pushed), though it carries the same untracked-file-coupling characteristic D identified
  — it will show spurious failures on later rounds' new untracked files during their Owner Review
  phase, same as it always has.
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_read_only_display_integration_v0_8_2_a.py` (A)
- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_plan_v0_8_2_b.py` (B)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_v0_8_1_v.py` (V)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_runtime_check_v0_8_1_w.py` (W)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_implementation_plan_v0_8_1_z.py` (Z)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_authorization_plan_v0_8_1_y.py` (Y)
- `scripts/check_hermes_openclaw_local_mock_fixture_dashboard_preview_adapter_integration_boundary_plan_v0_8_1_x.py` (X)
- `python -m compileall scripts`

All of the above are confirmed PASS at the base commit in Section 3.

## 5. Owner Review-only / Phase-limited Gates

- `scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_validation_hardening_plan_v0_8_2_d.py`
  (the v0.8.2-D readiness script) is Owner Review phase-only. It was written to confirm the D doc/
  script were untracked during D's own Owner Review round; once D was committed, those files became
  tracked and this script began failing on checks [D]/[E] by design. This is expected and is NOT a
  safety failure — it is not a regression gate and should not be treated as one post-commit or
  post-push.
- Do not "fix" the D readiness script to pass post-commit unless a future Owner explicitly authorizes a
  new hardening round for it (the same way E was authorized to harden C's equivalent limitation).

## 6. Current Safety Boundary

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

## 7. What Is Not Done

- no Worker dry-run implementation
- no OpenClaw mock execution boundary implementation
- no true OpenClaw connection
- no true Hermes readback
- no Google Sheets runtime
- no production/shared DB
- no Remote Blackboard API runtime
- v0.8.3 has not been started

## 8. Recommended Next Step After F

If Owner chooses to proceed, the recommended next step is:

- v0.8.3-A — Worker Dry-run Preview Boundary Plan
- plan-only first
- no Worker implementation yet
- no OpenClaw call
- no Hermes activation
- no Google Sheets
- no execution / dispatch

This mirrors the same plan-then-implement-then-harden-then-closeout cadence the v0.8.2 series used
(B→C, D→E, this document as F), applied to the next surface (Worker dry-run) rather than to the
Dashboard read-only preview UI.

## 9. Exact Future v0.8.3-A Authorization Phrase

The following exact phrase, and only this exact phrase, may be used by Owner in the future to authorize
v0.8.3-A planning. Paraphrases, general approval, readiness PASS, or Owner Review PASS do not authorize
v0.8.3-A. v0.8.3-A is not started by v0.8.2-F.

批准規劃 v0.8.3-A — Worker Dry-run Preview Boundary Plan，僅允許建立 Worker dry-run preview 的邊界計畫與 readiness 檢查設計；不得啟動 Worker，不得呼叫 OpenClaw，不得啟動或連接 Hermes，不得讀寫 Google Sheets，不得讀 real queue DB，不得 POST，不得新增 execute/dispatch/send controls，不得讀 secrets，不得建立 production/shared DB 或 Remote Blackboard API runtime。

## 10. Acceptance Criteria For F

v0.8.2-F is considered complete when:

- the v0.8.2-F closeout / handoff doc exists;
- the v0.8.2-F readiness script exists;
- the v0.8.2-F readiness script PASSes;
- baseline checks (E, C, A, B, V, W, Z, Y, X, compileall) PASS, or fail only because of the expected
  F-untracked exception during Owner Review;
- no existing tracked file is modified;
- no commit, no push, no tag happens in this round;
- a full Owner Review diff is produced for Owner to review before any commit.

## 11. Non-goals

v0.8.2-F explicitly does NOT:

- implement anything;
- change the Dashboard UI;
- change any CSS;
- change any Dashboard route;
- start or connect Worker;
- call OpenClaw;
- activate or connect Hermes;
- read or write Google Sheets;
- perform any true execution, dispatch, or external side effect of any kind;
- start v0.8.3 work of any kind.
