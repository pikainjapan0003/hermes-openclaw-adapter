# Hermes x OpenClaw — Web Dashboard Read-only Status Badges v0.7.1-C3

> 把 v0.7.1-C 的 `derive_intake_status_view()` 推導結果，以**唯讀 badge** 顯示到現有 Web Dashboard。
> 只做顯示：**不改 Queue 狀態、不啟動 Worker、不接 Hermes/OpenClaw、不寫 Google Sheets、不新增 route、不新增 POST handler。**

## 1. Purpose

讓 Owner 在現有 dashboard 任務列表與詳情頁，直接看到每筆任務的
「mock / local-only / real」、「是否可被 worker 執行」、「approval / risk」狀態，
全部為**唯讀顯示**，不附帶任何會改變狀態的動作。

## 2. Relationship To v0.7.1-C And v0.7.1-C2

- v0.7.1-C：純函式 view-model `derive_intake_status_view()` + 唯讀 CLI（已 push）。
- v0.7.1-C2：規劃如何把 view-model 顯示到 Web Dashboard（plan-only，已 push）。
- v0.7.1-C3（本版）：依 C2 規劃**實作唯讀 badge 顯示**，直接重用 C 的純函式，零推導重寫。

## 3. What Was Implemented

- 在 `app/main.py` 既有唯讀 dashboard helper（`_obs_task_summary` / `_obs_task_detail`）中，
  附加 `derive_intake_status_view(item)` 的輸出為 `intake_status`（`_review_summary` 透過 `_obs_task_summary` 自動繼承）。
- 在 `templates/tasks.html` 任務列表新增「intake (read-only)」欄位，顯示 badges。
- 在 `templates/task_detail.html` 新增「Intake Status (read-only)」卡片。
- 在 `static/dashboard.css` 新增 badge 樣式（無 JS、無外部 CDN）。

## 4. Files Changed

修改（最小）：

```text
app/main.py                 # import derive_intake_status_view；2 個唯讀 helper 各加 intake_status 欄位
templates/tasks.html        # 新增 intake badges 欄位（唯讀）
templates/task_detail.html  # 新增 Intake Status 唯讀卡片
static/dashboard.css        # 新增 badge 樣式
```

新增：

```text
docs/HERMES_OPENCLAW_WEB_DASHBOARD_READ_ONLY_STATUS_BADGES_V0_7_1_C3.md
scripts/test_web_dashboard_status_badges_v0_7_1_c3.py
scripts/check_hermes_openclaw_web_dashboard_read_only_status_badges_v0_7_1_c3_readiness.py
```

未修改：`app/worker.py`、`app/queue_store.py`、`app/result_sink.py`、`app/queue_intake_bridge_v0_7.py`、
`app/dashboard_intake_view_v0_7.py`、任何 Google Sheets / OpenClaw / Hermes client。
`templates/reviews.html` / `templates/dashboard.html` 本版未改（非必要）。

## 5. Read-only Badge Fields

```text
source_mode:          mock / local-only / real / unknown
intake_mode:          local-only / production / unknown
executable_by_worker: false / true / unknown
approval_status:      pending / not_required / unknown
risk_level / safety_level
```

## 6. View-model Reuse

- 直接呼叫 v0.7.1-C 的純函式 `derive_intake_status_view(task)`，**不重寫**任何推導邏輯。
- 只在唯讀 helper 的回傳 dict 加 `intake_status` 欄位，交給 template 顯示。

## 7. No Queue Status Mutation Guarantee

- 只在既有 `GET` 唯讀 helper 加顯示欄位，**未新增任何 route / POST handler**。
- 既有 approve/reject/cancel/retry/archive 行為**完全未改**。
- badge 只反映狀態，不改狀態。**No Queue status mutation.**

## 8. No Worker Trigger Guarantee

- 未呼叫 `claim_next`、未啟動 worker、未 import `app.worker`、未呼叫 `run_openclaw_cli`。
- `executable_by_worker` 只是唯讀推導；local-only 一律顯示 `false`。**No Worker start. No OpenClaw execution.**

## 9. No Result Sink Write Guarantee

- 未呼叫 `result_sink.emit_result`、未寫任何 Result Sink。
- **Result Sink is observation-only, not Queue source of truth.** **No Result Sink write.**

## 10. No Google Sheets Write Guarantee

- 未 import / 呼叫任何 Google client、未自動寫 Google Sheets。維持 `GOOGLE_SHEETS_ENABLED=false`。
  **No Google Sheets write.**

## 11. Mock / Local-only / Real Boundary

- 顯示值由既有 task row 的 `status` + `payload.metadata` 推導；production 任務多半標示 `unknown`（保守）。
- local-only intake 任務寫在獨立 DB；本版 dashboard 仍讀 production queue.db，
  顯示層只是把「若有」的標記安全呈現，不改變任何讀取來源或狀態。

## 12. Local-only Safety Behavior

- local-only 任務**永遠**顯示 `executable_by_worker=false`（沿用 view-model 保守規則）。
- **未**對 local-only 任務提供任何 `approve → queued` 捷徑或新按鈕。
- `unknown` 一律顯示為 unknown，**不**臆測成 true / executable。

## 13. Test Coverage

`scripts/test_web_dashboard_status_badges_v0_7_1_c3.py`（純 helper / dict 測試，不啟動 server）：

```text
- _obs_task_summary / _obs_task_detail 含 intake_status view 欄位
- local-only task → executable_by_worker=false
- mock task → source_mode=mock
- queued production-like task → executable_by_worker=true
- unknown metadata → 保守 unknown
- app.main 可 import、未啟動 worker、未寫 DB
```

## 14. Readiness Checks

`scripts/check_hermes_openclaw_web_dashboard_read_only_status_badges_v0_7_1_c3_readiness.py`（純靜態）：

```text
- doc / test / readiness 存在
- app/main.py import derive_intake_status_view，且只在 dashboard helper 使用
- 無新增 route / webhook / POST handler、無 enqueue / claim_next / worker / OpenClaw / Result Sink / google
- templates 只顯示 badge、未新增表單 / POST；static 只加 badge 樣式
- app/worker.py / queue_store.py / result_sink.py 未被接入新流程
- GOOGLE_SHEETS_ENABLED 無 true；無完整 spreadsheet URL / ID / token / secret / private key
```

## 15. Explicit Non-goals

```text
No new route.
No new POST handler.
No Queue status mutation.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
No Result Sink write.
No production Queue DB write.
Badges are read-only display only.
```

- 不接真 Hermes / 真 OpenClaw、不啟動 Worker、不寫 production Queue DB、不改 Queue 狀態。
- 不進 v0.7.1-D。

## 16. Final Recommendation

唯讀 badge 已安全顯示 intake / mock / executable 狀態，且不觸及任何執行/狀態路徑。
建議下一步（需 Owner 批准）才評估：

- 是否在 dashboard 以分頁/分區方式**唯讀觀測 local-only intake DB**（需明確標示 DB source、仍不可 approve→queued）。

本版到此收住——**不 commit（除非 Owner 批准）、不 push、不 tag、不進 v0.7.1-D。**
