# Hermes x OpenClaw — Mock Adapter + Approval Gate v0.7.0-C

## 1. 這一版在做什麼（一句話）

v0.7.0-C 做的是一個**純 mock 的 Adapter + Approval Gate**：
模擬「Hermes 把任務送進來 → Adapter 在進 Queue 之前做格式轉換與批准判斷」這一段，
**完全不接任何真系統**。可以把它想成「進 Queue 前的安全櫃台」。

## 2. 為什麼需要「安全櫃台」

主線流程是：

```text
Hermes（主腦）→ Adapter（櫃台 / 驗證 / 安全 gate）→ Queue → OpenClaw Worker → Callback → Result Sink / Dashboard
```

任務在進 Queue（任務唯一事實來源）之前，必須先：

1. 被整理成統一格式（**TaskEnvelope**，見 v0.7.0-B schema）。
2. 通過格式驗證（v0.7.0-B validator）。
3. 依風險決定是「可直接排隊」還是「要先給 Owner 批准」。

v0.7.0-C 就只負責這個櫃台，**還沒有**真的把任務放進 Queue。

## 3. 這一版「只做」與「不做」

只做：

- 把一個 **mock request**（假裝是 Hermes 送來的）轉成 TaskEnvelope。
- 用 v0.7.0-B 的 `validate_task_envelope` 檢查格式。
- 依 `risk_level` / `approval_required` 套用 approval gate，產生 `queued` 或 `pending_approval` 的 TaskEnvelope。

不做（本版明確不碰）：

- **不接真 Hermes**（輸入只是手寫的 mock dict）。
- **不接真 OpenClaw**、**不建立真 webhook**。
- **不寫 Queue DB**（只回傳一個「queue candidate」，不落地）。
- **不啟動 Worker**。
- **不寫 Google Sheets**、維持 `GOOGLE_SHEETS_ENABLED=false`。
- **不讀任何 secret**（refresh token / client secret / 完整 spreadsheet ID 一律不碰）。
- **不改** `app/main.py`、`app/result_sink.py`、Google Sheets writer/runner、Queue/Worker 執行邏輯。

## 4. 程式碼結構

新增檔案：`app/mock_adapter_v0_7.py`

公開 API：

```text
class MockAdapterError(Exception)
build_task_envelope_from_mock_request(request: dict) -> dict
apply_approval_gate(task_envelope: dict) -> dict
prepare_queue_candidate_from_mock_request(request: dict) -> dict
```

### 4.1 build_task_envelope_from_mock_request

輸入一個 mock request（假裝 Hermes 送來），例如：

```python
{
    "request_id": "mock-001",
    "requested_by": "owner",
    "intent": "summarize",
    "goal": "Summarize a mock document",
    "task_type": "mock.summarize",
    "risk_level": 0,
    "approval_required": False,
    "input_summary": "Mock input only",
    "target_runtime": "mock",
    "target_workspace": "local",
    "priority": "normal",
    "metadata": {"mock": True}
}
```

輸出一個符合 v0.7.0-B TaskEnvelope schema 的 dict，並由 adapter 自動補齊：

- `task_id`（adapter 產生，唯一）
- `created_at`（ISO8601 UTC）
- `idempotency_key`（由 request 內容衍生，相同 request → 相同 key）
- `result_policy` / `callback_policy`（預設值）
- `max_retries` / `retry_count`
- 初始 `status = draft`

最後會用 `validate_task_envelope` 檢查；缺 mock 必要欄位會 raise `MockAdapterError`，
欄位值不合法（例如 `risk_level` 超出 0–4）會由 validator raise `ContractValidationError`。

### 4.2 apply_approval_gate（批准判斷規則）

```text
risk_level 3 或 4：
  status = pending_approval
  approval_required = true
  approval_status = pending

approval_required = true：
  status = pending_approval
  approval_status = pending

risk_level 0,1,2 且 approval_required = false：
  status = queued
  approval_status = not_required
```

注意：這裡只是產生 **queue candidate**，**不寫 Queue DB**、**不呼叫現有 Queue store**、**不啟動 Worker**。

### 4.3 prepare_queue_candidate_from_mock_request（完整流程）

```text
mock request
  → build_task_envelope_from_mock_request
  → validate_task_envelope
  → apply_approval_gate
  → validate_task_envelope
  → 回傳最終 TaskEnvelope（queue candidate）
```

## 5. 與 Result Sink 的關係

Result Sink（含 Google Sheets）仍是**觀測層 / 紀錄層**，
**不是** Queue 狀態來源，也不是這個櫃台的一部分。本版完全不觸發任何 Result Sink 寫入。

## 6. 安全邊界

- 維持 `GOOGLE_SHEETS_ENABLED=false`。
- 不呼叫真 OpenClaw / 真 Hermes、不建立真 webhook、不寫 Queue DB、不啟動 Worker。
- 不讀 / 不顯示任何 secret，包含 refresh token、client secret、完整 spreadsheet ID、完整 Google Sheets URL。
- 不改 `app/main.py`、`app/result_sink.py`、Google Sheets writer/runner、Queue/Worker 執行邏輯。

## 7. 下一步（不在本版）

- **v0.7.0-D**：以 mock OpenClaw / mock Hermes 做 end-to-end dry-run；真接線再另立版本與 Owner 批准。
- 本版到此收住，**不進 v0.7.0-D**。
