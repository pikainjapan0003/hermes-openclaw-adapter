# Hermes x OpenClaw — Web Dashboard Read-only Status Badges Plan v0.7.1-C2

> **v0.7.1-C2 is plan-only.** 這一版只做 plan / doc / readiness，
> **不改 `app/main.py`、不改 templates、不改 static、不新增 route、不實作**。
> 它規劃「未來如何把 v0.7.1-C 的 `derive_intake_status_view()` 推導結果，
> 安全地以**唯讀 badge** 顯示到 Web Dashboard」，但本版不動任何執行/顯示程式。

## 1. Purpose

v0.7.1-C 已建立純函式 view-model `app/dashboard_intake_view_v0_7.py`
（`derive_intake_status_view(task)`）與唯讀 CLI。但這些推導結果目前**只在 CLI 看得到**，
Web Dashboard 還沒有顯示。

本文件（v0.7.1-C2）規劃：**未來**如何在 Web Dashboard 以唯讀 badge 呈現
「mock / local-only / real」、「是否可被 worker 執行」、「approval / risk」等狀態——
**全程唯讀、不改 Queue 狀態、不觸發 worker、不寫任何外部系統**。本版**不實作**。

## 2. Relationship To v0.7.1-C

- v0.7.1-C：純 view-model + 唯讀 CLI（已 push）。view-model 為純函式，零副作用。
- v0.7.1-C2（本版）：規劃把該 view-model **接進 Web Dashboard 的唯讀顯示層**，但只出 plan + readiness。
- 真正改 `app/main.py` / templates 的實作，留待**未來**版本，且需 Owner 明確批准。

## 3. Why This Version Is Plan-only

- `app/main.py`、templates、static 在先前版本被列為**禁改**；改它們屬高風險。
- 先把「要顯示什麼、怎麼接、不能做什麼」規劃清楚、可被 readiness 靜態驗證，
  未來實作時改動才會小且可審查。
- 本版維持零程式風險：只新增文件與 readiness 檢查。

## 4. Existing Dashboard Routes

（盤點自 `app/main.py`，本版**不修改**，僅記錄現況）

```text
GET  /dashboard                      → dashboard.html（總覽，唯讀）
GET  /dashboard/tasks                → tasks.html（任務列表，唯讀；list_page）
GET  /dashboard/tasks/{task_id}      → task_detail.html（詳情，唯讀）
GET  /dashboard/reviews              → reviews.html（waiting_review 列表）
POST /dashboard/tasks/{id}/comments  → 既有：寫 blackboard 留言（不改 queue 狀態）
POST /dashboard/tasks/{id}/approve   → 既有：waiting_review → queued（QueueStore 狀態機）
POST /dashboard/tasks/{id}/reject    → 既有：waiting_review → rejected
GET  /dashboard/login, /logout       → auth gate
```

- 任務資料來自 `get_queue()`（`QueueStore(QUEUE_DB_PATH)`，production queue.db），全部 SELECT。
- view-model helper：`_obs_task_summary` / `_obs_task_detail` / `_review_summary` /
  `_parse_payload_metadata`（已能從 payload 取出 metadata）。

## 5. Existing Templates

（本版**不修改**，僅記錄）

```text
templates/base.html         共用版型
templates/dashboard.html    總覽
templates/tasks.html        任務列表
templates/task_detail.html  任務詳情（已顯示 metadata）
templates/reviews.html      pending reviews
templates/system.html       system health
templates/login.html        登入
static/dashboard.css        樣式
```

## 6. Proposed Read-only Badges

未來在列表 / 詳情頁，針對每筆任務顯示以下**唯讀 badge**（值由 view-model 推導）：

```text
source_mode:          mock / local-only / real / unknown
intake_mode:          local-only / production / unknown
executable_by_worker: false / true / unknown
approval_status:      pending / not_required / unknown
risk_level / safety_level
```

- badge 純為顯示，**不可**附帶任何會改變狀態的動作（無按鈕觸發 enqueue/approve→queued 等）。
- `unknown` 要明確顯示為 unknown，不可臆測成 true / executable。

## 7. Proposed View-model Reuse

- 直接重用 v0.7.1-C 的純函式 `derive_intake_status_view(task)`，**不重寫推導邏輯**。
- 未來只需在既有唯讀 helper（如 `_obs_task_summary` / `_obs_task_detail`）的回傳 dict 中，
  附加 `derive_intake_status_view(item)` 的輸出（或其中的 badge 欄位），交給 template 顯示。
- 推導為純函式、零副作用：不寫 DB、不改狀態、不連外。

## 8. Production Queue Visibility

- 既有 `/dashboard/tasks` 等讀的是 production `queue.db`。
- 對 production 任務套 view-model 時，多數 metadata 標記可能缺失 →
  badge 多為 `unknown`（保守），這是可接受且安全的顯示。

## 9. Local-only Intake DB Visibility

- local-only intake 任務寫在**獨立** DB（`INTAKE_QUEUE_DB_PATH`），Web Dashboard 預設讀不到。
- 若未來要在 dashboard 顯示 intake 任務，必須：
  - **分頁 / 分區**呈現，並**明確標示 DB source**（production vs local-only intake）。
  - 以**唯讀** `QueueStore(INTAKE_QUEUE_DB_PATH)` 的 SELECT 方法讀取，不寫入。
  - **絕不**提供 local-only 任務的 `approve → queued` 捷徑（見第 10 節）。

## 10. No Queue Status Mutation Guarantee

- 新增的顯示一律走 `GET` 唯讀 route，**不新增任何會改 queue 狀態的 route / 動作**。
- 既有 `approve`/`reject` 行為**維持不變**，且**不得**擴及 local-only intake 任務
  （local-only 任務不可被 approve 成 queued，避免變可執行）。
- badge 只反映狀態，不改狀態。**No Queue status mutation.**

## 11. No Worker Trigger Guarantee

- 顯示層**不呼叫** `claim_next`、不啟動 worker、不 import `app.worker`、不呼叫 `run_openclaw_cli`。
- `executable_by_worker` badge 只是**推導顯示**，local-only 任務一律顯示 `false`（沿用 view-model 保守規則）。**No Worker start. No OpenClaw execution.**

## 12. No Result Sink Write Guarantee

- 顯示層**不呼叫** `result_sink.emit_result`，不寫任何 Result Sink。
- **Result Sink is observation-only, not Queue source of truth.** **No Result Sink write.**

## 13. No Google Sheets Write Guarantee

- 顯示層**不** import / 呼叫任何 Google client，**不**自動寫 Google Sheets。
- 維持 `GOOGLE_SHEETS_ENABLED=false`。**No Google Sheets write.**

## 14. Proposed Minimal Future Implementation

未來（需 Owner 批准）最小、最安全的實作切法：

```text
1. app/main.py 只在既有唯讀 dashboard helper 中套用 derive_intake_status_view()
2. templates 只顯示 read-only badges（不加任何表單 / 動作按鈕）
3. 不新增 POST route
4. 不新增 approve / reject 行為（既有行為不擴及 local-only intake）
5. 不呼叫 enqueue / claim_next / worker / OpenClaw / Result Sink
6. local-only intake DB 若要顯示，必須分頁或明確標示 DB source
7. local-only 任務不得有 approve-to-queued 捷徑
```

## 15. Files That May Be Modified In Future Implementation

（**僅限未來、需 Owner 批准**；本版**不**碰）

```text
app/main.py        # 只在既有唯讀 helper 附加 badge 欄位；不新增 POST route
templates/tasks.html, templates/task_detail.html, templates/reviews.html  # 只加唯讀 badge 顯示
static/dashboard.css  # 只加 badge 樣式
（可能）一個唯讀 GET route 用於 local-only intake DB 觀測（分頁/標示 source）
```

## 16. Files That Must Not Be Modified

```text
app/worker.py            # 不改執行邏輯、不啟動
app/queue_store.py       # 不改狀態機 / schema
app/result_sink.py       # 維持 mock-safe，不真寫
app/queue_intake_bridge_v0_7.py   # v0.7.1-B 已收尾
app/dashboard_intake_view_v0_7.py # v0.7.1-C 純函式，維持不變
任何 Google Sheets writer / runner、OpenClaw / Hermes client
```

且本版（v0.7.1-C2）**完全不**修改任何既有檔案（含上方「未來可能改」的清單）。

## 17. Readiness Criteria For Future Web Dashboard Integration

未來真要動 Web Dashboard 前，須先滿足：

```text
[ ] Owner 批准修改 app/main.py / templates / static 的範圍
[ ] 只在既有 GET 唯讀 route / helper 顯示 badge，不新增 POST / 不新增改狀態動作
[ ] derive_intake_status_view 直接重用，不重寫推導
[ ] local-only intake 顯示須分頁 / 標示 DB source，且不可 approve→queued
[ ] 不呼叫 claim_next / worker / OpenClaw / Result Sink / Google Sheets
[ ] 維持 GOOGLE_SHEETS_ENABLED=false
[ ] 新增 readiness 靜態檢查（route 仍唯讀、無寫入呼叫、無 secret）
[ ] 既有 dashboard / queue / worker 測試全綠
```

## 18. Explicit Non-goals

本版**明確不做**：

- 不改 `app/main.py` / templates / static、不新增 route / webhook / POST handler。
- 不實作任何 badge 顯示（只規劃）。
- 不接真 Hermes / 真 OpenClaw、不啟動 Worker、不寫 production Queue DB、不改 Queue 狀態。
- 不寫 Google Sheets、不改 `GOOGLE_SHEETS_ENABLED`、不寫 Result Sink。
- 不做任何外部 side effect、不讀 / 不顯示 secret。
- 不進 v0.7.1-D。

## 19. Final Recommendation

建議下一步（需 Owner 批准）為 **v0.7.1-C3：Web Dashboard Read-only Badges（實作）**，
嚴守本文件第 14 節切法：只在既有唯讀 helper 套 view-model、template 只加唯讀 badge、
零新增 POST route、local-only 不可 approve→queued。

在 Owner 批准前，本版到此收住——**plan-only，不 commit、不 push、不 tag，不進 v0.7.1-D。**

安全聲明：

```text
v0.7.1-C2 is plan-only.
No app/main.py modification.
No template modification.
No static modification.
No route addition.
No Queue status mutation.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
No Result Sink write.
No production Queue DB write.
```
