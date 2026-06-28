# Hermes × OpenClaw Adapter — Owner Review Panel Layout Plan (v0.7.2-UI-E-A)

> **Status: PLAN ONLY.** This document is a UI layout plan. v0.7.2-UI-E-A
> implements nothing, commits nothing, and pushes nothing. It describes a future
> layout for the Owner Review Panel / Pending Actions surface so the Owner can
> review and decide faster. It is layout polish, **not** approval wiring.
>
> Boundary declarations:
>
> - This is UI layout planning only.
> - No approval wiring changes.
> - No QueueStore behavior changes.
> - No Worker execution.
> - No OpenClaw call.
> - No Hermes call.
> - No Google Sheets write.
> - No external side effects.

---

## 1. Purpose

Plan a clearer **Owner Review Panel** for the already-Chinese-first Jarvis
Dashboard so the Owner can see, at a glance, what needs human attention (pending
reviews, recent errors, items requiring confirmation) and act on them with
unambiguous Chinese-first controls. This is a layout/visual plan; it changes no
routes and no behavior.

---

## 2. Current UI baseline

Current master is `1eb83a2409488a29014ff04867fcf99ee13d780c`. State:

- Dashboard is a Jarvis visual shell (dark cockpit, neon, glass, HUD), Read-only.
- Dashboard is Chinese-first with small English auxiliary labels.
- Replit Preview visual validation passed.
- Worker OFF; OpenClaw is Not Connected; Hermes is Not Connected; Google Sheets
  is Disabled; no external side effects.

Existing dashboard pages and routes (read-only / unchanged this segment):

| Page | Route(s) |
| --- | --- |
| Overview | `GET /dashboard` — status ribbon + System Health / Queue Counts / Quick Links (中文) |
| Tasks | `GET /dashboard/tasks` — Chinese-first list + filters |
| Task Detail | `GET /dashboard/tasks/{id}` — Summary / Intake / Review / Safe Controls (中文) |
| Reviews | `GET /dashboard/reviews` — 待審核項目 list |
| System | `GET /dashboard/system` — 系統健康 (中文) |

Existing POST action routes that **already exist** and are **not changed** in
this segment: `POST /dashboard/tasks/{id}/approve`, `/reject`, `/cancel`,
`/retry`, `/archive`, `/comments`. The layout plan reuses these routes as-is; it
does not alter their behavior, method, action, or input names.

The Read-only posture and the `_dashboard_auth_middleware` auth gate are
preserved exactly; this plan adds no new route and no auth change.

---

## 3. Owner Review Panel goal

Give the Owner one obvious place — "Owner 待處理" — that answers: *what needs me
right now?* and lets the Owner open the relevant task to 核准 / 拒絕. The panel
groups pending reviews, recent errors, and items requiring confirmation, with a
suggested next step for each.

---

## 4. User problem

Today the signals are spread across the overview cards, the 待審核項目 page, and
each 任務詳情 page. The Owner has to hunt for what needs action. There is no
single "pending actions" focus, and read-only links look similar to
action-capable buttons, which is ambiguous.

---

## 5. Proposed dashboard overview changes

- Add a primary **「Owner 待處理」** block near the top of `GET /dashboard`
  (below the status ribbon), as a glass HUD panel.
- Contents: 待審核任務 count + link, 最近錯誤 count + link, 需要人工確認 count,
  and a short 下一步建議 line per group.
- Distinguish **read-only links** from **action-capable buttons**: anything whose
  behavior is not being wired in this segment is labeled **「查看」** (view), not
  「執行」 (execute). Only the existing approve/reject/cancel/retry/archive
  controls remain action-capable, and only on the task pages.
- No new data source: counts derive from the same read-only `/queue/*` context
  already used by the overview.

---

## 6. Proposed reviews page layout

`GET /dashboard/reviews` (中文主標 **「待審核項目」**):

- Render each review as a clearer row/glass card showing: 任務 ID (task id), 標題
  (title), 風險等級 (safety_level / risk), 請求動作 (requested action), 建立時間
  (created at), 目前狀態 (current status).
- Action buttons clearly labeled **「核准」** (Approve) and **「拒絕」** (Reject),
  visually separated from read-only links.
- These buttons keep using the existing `POST .../approve` and `.../reject`
  routes. **This stage does not change route behavior** — only labels/layout.
- Keep the existing empty state ("目前沒有待審核任務").

---

## 7. Proposed task detail review panel layout

`GET /dashboard/tasks/{id}` (中文主標 **「任務詳情」**):

- Add an **「Owner 審核面板」** panel (top or right column) summarizing: 目前任務
  狀態, 是否可核准 (can-approve), 為什麼需要 Owner (why owner is required),
  風險提示 (risk note), and the 安全邊界 labels.
- Keep the existing 安全控制 (Safe Controls) and 人工審核 (Human Review) sections;
  buttons stay 核准 / 拒絕 / 取消 / 重試 / 封存 with clearer Chinese-first
  wording and the same routes/behavior.
- The panel is descriptive (read-only summary); it adds no new action.

---

## 8. Pending actions model

A display-only grouping (no new persistence, no QueueStore change):

| Group | Source signal | Suggested next step | Control |
| --- | --- | --- | --- |
| 待審核 (pending review) | status == waiting_review | 開啟任務 → 核准 / 拒絕 | 查看 + existing approve/reject |
| 最近錯誤 (recent errors) | status == failed | 檢視錯誤 → 重試 / 封存 | 查看 + existing retry/archive |
| 需要人工確認 | safety_level ≥ 3 或 requires_confirmation | 人工確認 | 查看 |

The model is derived at render time from existing read-only counts/lists; it is
not stored and triggers nothing.

---

## 9. Safety boundary labels

Every action-capable area shows the same calm safety labels already used on the
overview ribbon: Read-only (where applicable), Worker OFF, OpenClaw is Not
Connected, Hermes is Not Connected, Google Sheets is Disabled, Approval Gate:
Owner Required, Kill Switch visible. These are display-only assertions.

---

## 10. Chinese-first wording plan

Chinese-first throughout, English kept only as small auxiliary labels /
machine-code values (consistent with UI-D-C):

| Concept | 中文主字 | English sub |
| --- | --- | --- |
| Owner pending | Owner 待處理 | Owner Pending |
| Pending reviews | 待審核項目 | Pending Reviews |
| Task detail | 任務詳情 | Task Detail |
| Approve | 核准 | Approve |
| Reject | 拒絕 | Reject |
| Cancel | 取消 | Cancel |
| Retry | 重試 | Retry |
| Archive | 封存 | Archive |
| View (read-only) | 查看 | View |

---

## 11. Read-only vs action-capable distinction

- **Read-only links** ("查看"): styled as links/neutral chips; navigate only.
- **Action-capable buttons** ("核准/拒絕/取消/重試/封存"): styled as the existing
  colored buttons; submit to the existing POST routes; appear only where they
  already appear today.
- The plan makes this distinction visual and lexical so the Owner never confuses
  a navigation link with an action.

---

## 12. Visual hierarchy

1. Top: status ribbon (existing).
2. Then: 「Owner 待處理」 focus panel (new layout).
3. Then: existing overview cards (System Health / Queue Counts / Quick Links).
4. On task pages: 「Owner 審核面板」 above/beside the detail sections.

Maintains Jarvis style: dark field, neon cyan accent, glass panels, HUD borders,
restrained motion, readable first.

---

## 13. Empty states

- No pending reviews: 「目前沒有待審核任務」 (keep existing).
- No recent errors: 「目前沒有最近錯誤」.
- No items requiring confirmation: 「目前沒有需要人工確認的項目」.
- The 「Owner 待處理」 panel as a whole shows 「目前沒有待處理項目」 when all groups
  are empty.

---

## 14. Error states

- If counts/context are unavailable, show a calm inline note 「暫時無法讀取狀態」
  (read-only) rather than failing the page.
- Existing per-action error display (e.g. comment_error / approve failure) is
  reused unchanged; this plan does not add new error-producing actions.

---

## 15. Replit Preview smoke criteria

**Replit Preview smoke criteria** for the *eventual* implementation (not part of
UI-E-A itself):

1. `/dashboard` renders the 「Owner 待處理」 panel with correct group counts.
2. Read-only links show 「查看」; action buttons show 核准/拒絕/取消/重試/封存.
3. `/dashboard/reviews` shows 待審核項目 with 任務 ID / 標題 / 風險等級 / 請求動作
   / 建立時間 / 目前狀態 and clear 核准 / 拒絕 buttons.
4. `/dashboard/tasks/{id}` shows the 「Owner 審核面板」 summary; Safe Controls
   intact.
5. No console errors; readable contrast; no aggressive flashing.
6. No network calls to external hosts.

---

## 16. Allowed future implementation files

When the Owner approves implementation (a later segment, not UI-E-A), changes
should be limited to:

- `templates/dashboard.html` — 「Owner 待處理」 panel.
- `templates/reviews.html` — clearer review rows/cards.
- `templates/task_detail.html` — 「Owner 審核面板」 summary.
- `static/dashboard.css` — panel/label styles (no new dependency, no CDN, no JS).
- (Optional) a readiness/regression script under `scripts/`.

No `app/` route change, no QueueStore change, and no auth change are needed for
this layout work.

---

## 17. Non-goals

UI-E-A explicitly does **not**:

- Implement any UI (plan only).
- Change approval wiring or any POST action behavior (No approval wiring changes).
- Change QueueStore (No QueueStore behavior changes).
- Add or change routes, auth, or Jinja variables.
- Start the Worker (No Worker execution), call OpenClaw (No OpenClaw call), call
  Hermes (No Hermes call), or write Google Sheets (No Google Sheets write).
- Read secrets, create webhooks, or add any external dependency (No external side
  effects).

---

## 18. Risks

- **Action vs view confusion** — mitigated by section 11's visual+lexical split.
- **Scope creep into wiring** — mitigated by the boundary block, section 17, and
  the readiness script's forbidden-pattern checks.
- **Dark-theme contrast** on the new panel — mitigated by reusing UI-D color
  tokens and the Preview smoke criteria.
- **Overview density** — the new focus panel must not crowd out existing cards;
  keep it compact and collapsible-friendly.

---

## 19. Acceptance criteria

UI-E-A (this plan) is accepted when:

1. This plan exists at the documented path and contains sections 1–19.
2. The readiness script
   `scripts/check_hermes_openclaw_dashboard_owner_review_panel_layout_plan_v0_7_2_ui_e_a.py`
   exists and reports ALL PASS.
3. The plan defines the 「Owner 待處理」 overview panel, the 待審核項目 reviews
   layout, and the 「Owner 審核面板」 task-detail panel, all Chinese-first.
4. The plan states Non-goals, Allowed future implementation files, Replit Preview
   smoke criteria, and Acceptance criteria.
5. The plan asserts Read-only and the safety boundaries and carries no external
   side effects and no secrets.
6. Nothing is implemented, committed, pushed, or tagged in this segment without
   Owner approval.
