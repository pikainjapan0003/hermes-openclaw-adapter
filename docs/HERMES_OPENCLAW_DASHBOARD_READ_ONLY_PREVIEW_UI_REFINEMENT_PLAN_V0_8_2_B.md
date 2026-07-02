# Hermes × OpenClaw — Dashboard Read-only Preview UI Refinement Plan (v0.8.2-B)

## 1. Purpose

v0.8.2-B is a plan-only round.
v0.8.2-B does not modify Dashboard implementation.
v0.8.2-B does not modify app/main.py.
v0.8.2-B does not modify templates/system.html.
v0.8.2-B does not modify static/dashboard.css.
v0.8.2-B does not modify adapter, loader, fixture JSON, QueueStore, Worker, OpenClaw, Hermes, or Google Sheets integration.
v0.8.2-B only plans future Dashboard read-only preview UI refinement.

It defines the future UI refinement categories, the future candidate files, the future forbidden UI
controls, the future validation requirements, the future rollback boundary, and the exact v0.8.2-C
phrase a future, separately approved implementation round must obtain before touching any candidate
file. It creates no Dashboard file, no route, no endpoint, no template change, no static asset change,
and modifies no existing file other than adding this doc and its readiness script.

## 2. Base

Base HEAD / origin/master:
7206afa7ed000fbaab761a1f0018524849cc8815

Base commits:
7206afa fix: make v0.8.2-a validation post-commit aware
f93cd51 feat: add dashboard read-only preview display

## 3. What v0.8.2-A already completed

v0.8.2-A added a read-only Dashboard preview display to the existing GET-only /dashboard/system surface.
Dashboard consumes build_dashboard_preview_model().
Dashboard does not call P loader.
Dashboard does not read fixture JSON directly.
Dashboard displays read-only rows.
Dashboard displays disabled runtime badges.
Dashboard displays false permission flags.
v0.8.2-A validation passes 30/30 after the post-commit-aware follow-up fix.

Read-only inspection of the current display block (`templates/system.html`, lines 84-141) confirmed:
- A "Local Mock Dashboard Preview" (本機模擬預覽) section gated by `{% if local_mock_preview_model %}`,
  placed after the existing "工單統計 / Queue Counts" table.
- A "Runtime Badges" card showing the five disabled badges as static text.
- A "Safety Flags" card showing is_mock/local_only/read_only/execution_permission/dispatch_permission/
  external_side_effects_permission as plain key-value rows.
- A `table.grid.hoverable` listing rows with display_index/display_title/display_summary/source_role/
  target_role/status columns.
- No form, no button, no POST attribute, no action/webhook/endpoint/execute/dispatch URL anywhere in
  the block.

Read-only inspection of `static/dashboard.css` confirmed reusable existing classes relevant to future
refinement: `.cards` / `.card` (card layout), `table.kv` (key-value tables), `table.grid.hoverable`
(sortable-looking data tables, already responsive — collapses to a stacked card view under the
existing `@media (max-width: 640px)` rule), `.badge` and its `.badge-*` status variants (including
prior-art local-only-style badges `.badge-local-only`, `.badge-source`, `.badge-executable-false` from
earlier v0.7 work), `.muted` / `.field-label` / `.field-code` / `.en-sub` text helpers, and existing
breakpoints at 900px and 640px. No new CSS mechanism is required to satisfy the refinement categories
below; future work is expected to reuse and extend these existing classes.

## 4. Current read-only display contract

The Dashboard preview display must remain GET-only.
The Dashboard preview display must remain read-only.
The Dashboard preview display must show synthetic local-only mock preview data only.
The Dashboard preview display must preserve:
- is_mock = True
- local_only = True
- read_only = True
- execution_permission = False
- dispatch_permission = False
- external_side_effects_permission = False

## 5. Disabled runtime badges

DISPATCH OFF
WORKER OFF
OPENCLAW NOT CONNECTED
HERMES NOT CONNECTED
GOOGLE SHEETS DISABLED

## 6. Future UI refinement categories, plan-only

1. Badge layout refinement
2. Safety flags layout refinement
3. Preview rows table refinement
4. Empty-state display
5. Error-state display
6. Owner Review reminder display
7. Local-only / read-only / synthetic data explanation
8. Mobile / small-screen readability
9. Visual separation from real queue / real task displays
10. Accessibility and semantic markup

## 7. Future UI requirements, plan-only

Future UI refinement may improve layout, spacing, grouping, labels, table readability, helper text, and CSS classes.
Future UI refinement must not add any state-changing control.
Future UI refinement must not add any POST form.
Future UI refinement must not add any button.
Future UI refinement must not add any action URL.
Future UI refinement must not add any endpoint URL.
Future UI refinement must not add any webhook URL.
Future UI refinement must not add any execute URL.
Future UI refinement must not add any dispatch URL.
Future UI refinement must not change the data source.
Future UI refinement must not call P loader.
Future UI refinement must not read fixture JSON directly.
Future UI refinement must not read real queue DB.

## 8. Future candidate files, plan-only

Future candidate display file:
- templates/system.html

Future candidate style file:
- static/dashboard.css

Future candidate validation file:
- scripts/check_hermes_openclaw_dashboard_read_only_preview_ui_refinement_v0_8_2_c.py

Files not expected to change for UI refinement:
- app/main.py
- templates/dashboard.html
- templates/task_detail.html
- templates/reviews.html
- templates/tasks.html
- templates/base.html

These candidate files are not modified by v0.8.2-B.
These candidate files are not authorized for modification by v0.8.2-B.
Future modification requires a separate Owner-approved implementation round.

## 9. Future forbidden UI controls, plan-only

No Run button.
No Execute button.
No Dispatch button.
No Approve and Dispatch button.
No Send button.
No POST form.
No webhook control.
No endpoint control.
No action_url.
No post_url.
No webhook_url.
No endpoint_url.
No execute_url.
No dispatch_url.
No external action control.

## 10. Future validation requirements, plan-only

Future UI refinement validation must confirm:
- templates/system.html remains display-only.
- static/dashboard.css changes, if any, are style-only.
- app/main.py is unchanged unless separately authorized.
- Dashboard still consumes build_dashboard_preview_model().
- Dashboard does not call P loader.
- Dashboard does not read fixture JSON directly.
- Dashboard does not read real queue DB.
- Dashboard does not define POST route.
- Dashboard does not expose action/execution/dispatch controls.
- Disabled runtime badges remain visible.
- Permission flags remain visible and false.
- v0.8.2-A validation passes.
- V/W/Z/Y/X checks pass.
- compileall passes.
- safety grep is benign.

## 11. Future rollback boundary, plan-only

Rollback of future UI refinement must remove only the future UI refinement changes.
Rollback must not remove v0.8.2-A Dashboard read-only display integration unless separately authorized.
Rollback must not modify P loader.
Rollback must not modify V adapter.
Rollback must not modify W/X/Y/Z artifacts.
Rollback must not modify fixture JSON.
Rollback must not clean patches/.

## 12. Future implementation authorization phrase for v0.8.2-C

Only the following exact phrase, verbatim, authorizes v0.8.2-C — Dashboard Read-only Preview UI
Refinement Implementation:

```
批准實作 v0.8.2-C — Dashboard Read-only Preview UI Refinement Implementation，僅允許改善 v0.8.2-A 已存在的 /dashboard/system read-only preview display 的版面、標籤、說明文字、表格可讀性與 CSS 樣式；必須保持 GET-only、read-only、synthetic local-only、permission flags false、disabled runtime badges visible；不得修改資料來源，不得呼叫 P loader，不得直接讀 fixture JSON，不得讀 real queue DB，不得 POST，不得新增 button/form/action URL/webhook/endpoint/execute/dispatch/send controls，不得啟 Worker/OpenClaw/Hermes/Google Sheets，不得讀 secrets，不得建立 production/shared DB 或 Remote Blackboard API runtime。
```

v0.8.2-C is not started by v0.8.2-B.
General approval does not authorize v0.8.2-C.
Commit approval does not authorize v0.8.2-C.
Push approval does not authorize v0.8.2-C.
Only the exact phrase above may authorize v0.8.2-C.

## 13. Known pre-commit coupling

During v0.8.2-B Owner Review, the v0.8.2-A / V / W / Z / Y / X readiness scripts may fail only because
the two new B files are untracked. This is the same strict-untracked-file coupling observed throughout
the v0.8.1/v0.8.2 line. This is acceptable only if the failure reason is exactly the two untracked B
files. No other regression failure is acceptable. After B files are committed in a separately approved
round, v0.8.2-A / V / W / Z / Y / X must recover to PASS.

## 14. Permission flags (plan-only)

execution_permission = false
dispatch_permission = false
external_side_effects_permission = false
dashboard_change_permission = false
css_change_permission = false
authorization_granted_for_v0_8_2_c = false

In v0.8.2-B execution_permission remains false.
In v0.8.2-B dispatch_permission remains false.
In v0.8.2-B external_side_effects_permission remains false.
In v0.8.2-B authorization_granted_for_v0_8_2_c remains false until the exact v0.8.2-C phrase in
Section 12 is given for a future separately approved round.

## 15. v0.8.2-B acceptance criteria

- B plan doc exists.
- B readiness script exists.
- B is plan-only.
- B documents v0.8.2-A's completed GET-only read-only display and its 30/30 validation status.
- B defines the current read-only display contract and disabled runtime badges.
- B defines the future UI refinement categories, requirements, candidate files, forbidden controls, validation requirements, and rollback boundary.
- B defines the exact v0.8.2-C future implementation authorization phrase.
- app/main.py remains unchanged.
- templates/system.html remains unchanged.
- static/dashboard.css remains unchanged.
- v0.8.2-A validation script remains unchanged.
- P loader, V adapter, W/X/Y/Z artifacts, and fixture JSON remain unchanged.
- No Dashboard route/endpoint/template/static is created or modified.
- No POST is sent, no network call is made, no Worker/OpenClaw/Hermes/Google Sheets/secrets integration is introduced.
- B does not commit / push / tag.

## 16. Non-goals

v0.8.2-B does not modify the Dashboard.
v0.8.2-B does not modify app/main.py.
v0.8.2-B does not modify templates/system.html.
v0.8.2-B does not modify static/dashboard.css.
v0.8.2-B does not modify the v0.8.1-P/V/W/X/Y/Z or v0.8.2-A artifacts.
v0.8.2-B does not start v0.8.2-C.

## 17. Next recommended step

Recommended next step:
v0.8.2-C — Dashboard Read-only Preview UI Refinement Implementation

v0.8.2-C is not started by v0.8.2-B.
v0.8.2-C requires the exact v0.8.2-C phrase defined in Section 12 of this doc.
