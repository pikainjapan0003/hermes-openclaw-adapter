# Hermes x OpenClaw — Mock E2E Dry-run v0.7.0-D

## 1. 這一版在做什麼（一句話）

v0.7.0-D 把前面 A/B/C 的零件**串起來跑一圈**，做一條**純 mock 的 End-to-End dry-run**：
讓一個假任務從 mock Adapter 進來，經過 mock Queue、mock Worker、mock Callback，
最後產生一份**可驗證的 dry-run 結果**。全程**不接任何真系統**。

可以把它想成「彩排」：流程走一遍給你看，但沒有真的對外做任何事。

## 2. 一圈長什麼樣子

```text
mock Hermes request
   → mock Adapter（v0.7.0-C：prepare_queue_candidate_from_mock_request）
   → approval gate 判斷
        ├─ status = pending_approval → 停在 approval gate（不進 worker、不產生 completed callback）
        └─ status = queued          → 繼續往下
   → InMemoryMockQueue（純記憶體，不是真 Queue DB）
   → mock Worker（假 Worker，不做真事）
   → mock CallbackEvent（completed 或 failed，符合 v0.7.0-B schema）
   → 更新 task 狀態（只改 dict 的 copy）
   → 回傳 dry_run_result
```

## 3. 只做 / 不做

只做：

- 用 v0.7.0-C 的 mock Adapter 把 request 轉成 TaskEnvelope 並套 approval gate。
- 用一個**純記憶體**的 `InMemoryMockQueue`（list / dict）模擬排隊。
- 用一個**假 Worker** 產生 CallbackEvent（用 v0.7.0-B `validate_callback_event` 驗證）。
- 把 callback 套回 task（用 `validate_task_envelope` 驗證），回傳 dry-run 結果。

不做（本版明確不碰）：

- **不接真 Hermes**（輸入只是手寫 mock dict）。
- **不接真 OpenClaw**、**不建立真 webhook**。
- **不寫真 Queue DB**、**不 import `queue_store` / `sqlite3`**、**不用真 `QueueStore`**。
- **不啟動真 Worker**、**不 import 真 worker 執行邏輯**。
- **不寫 Google Sheets**、維持 `GOOGLE_SHEETS_ENABLED=false`。
- **不寫 Result Sink**、**不讀任何 secret**、**不做 network call**。
- **不改** `app/main.py`、`app/result_sink.py`、Google Sheets writer/runner、現有 Queue/Worker 執行邏輯。

## 4. 程式碼結構

新增檔案：`app/mock_e2e_v0_7.py`

公開 API：

```text
class MockE2EError(Exception)
class InMemoryMockQueue
mock_worker_process_task(task_envelope: dict) -> dict
apply_callback_to_mock_task(task_envelope: dict, callback_event: dict) -> dict
run_mock_e2e_dry_run(request: dict) -> dict
```

### 4.1 InMemoryMockQueue（假 Queue）

- 只用 Python **記憶體結構**（`dict` 存任務、`list` 存順序）。
- `enqueue` / `claim_next` / `mark_completed` / `mark_failed` / `get_task`。
- **不是真 Queue DB**：沒有 sqlite、沒有檔案寫入、沒有資料庫寫入、沒有 `QueueStore`。

### 4.2 mock_worker_process_task（假 Worker）

- `task_type = mock.fail` → 產生 **failed** CallbackEvent
  （`status=failed`、`retryable=true`、`error_code=MOCK_FAILURE`、`error_message=Mock failure requested`）。
- 其他任務 → 產生 **completed** CallbackEvent（`status=completed`、`retryable=false`）。
- 產出的 CallbackEvent 必須符合 v0.7.0-B schema，會用 `validate_callback_event` 檢查。

### 4.3 apply_callback_to_mock_task

只更新傳入 task 的 **copy**（不寫 DB、不改原物件）：

```text
completed callback → task status = completed
failed callback    → task status = failed
cancelled callback → task status = cancelled
其他 callback      → task status = callback_received
```

### 4.4 run_mock_e2e_dry_run

回傳的 `dry_run_result` 至少包含：

```text
dry_run            # true
task_id
initial_status
final_status
approval_required
approval_status
callback_event     # pending_approval 時為 None
events             # 流程事件清單（list）
stopped_at         # pending_approval 時為 "approval_gate"，否則 None
summary
metadata
```

行為重點：

- `pending_approval` 任務會**停在 approval gate**：`stopped_at = approval_gate`、
  **不進 mock worker**、**不產生 completed callback**。
- `queued` 任務才會進 mock worker，最終 `final_status` 為 `completed`（一般 mock 任務）
  或 `failed`（`task_type = mock.fail`）。

## 5. 與 Result Sink 的關係

Result Sink（含 Google Sheets）仍是**觀測層 / 紀錄層**，**不是** Queue 狀態來源，
也不是這條 dry-run 的一部分。本版完全不觸發任何 Result Sink 寫入。

## 6. 安全邊界

- 維持 `GOOGLE_SHEETS_ENABLED=false`。
- 不呼叫真 OpenClaw / 真 Hermes、不建立真 webhook。
- 不寫真 Queue DB、不 import `queue_store` / `sqlite3`、不啟動真 Worker、不 import 真 worker。
- 不寫 Google Sheets、不寫 Result Sink、不做 network call。
- 不讀 / 不顯示任何 secret，包含 refresh token、client secret、完整 spreadsheet ID、完整 Google Sheets URL。
- 不改 `app/main.py`、`app/result_sink.py`、Google Sheets writer/runner、現有 Queue/Worker 執行邏輯。

## 7. 下一步（不在本版）

- 真接線（真 Hermes / 真 OpenClaw / 真 Queue / 真 Worker / Result Sink 常態化）必須另立版本，
  設計安全、批准、重試、去重、失敗隔離、最小權限，並經 Owner 批准。
- 本版到此收住，**不進 v0.7.1**。
