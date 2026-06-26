# Hermes x OpenClaw Google Sheets Mock Sink v0.6.7

## 1. 本版目標

新增一個**可關閉、預設關閉**的「Google Sheets Mock Result Sink」雛形，用**假 client / 本地 mock**
驗證任務結果落地的資料流與欄位設計。**不連真 Google、不放真 credentials、不做正式寫入。**

## 2. 前置狀態

v0.6.6 評估結論：results 現存在 `data/results.jsonl`+`tasks.jsonl`+`queue.db`（Replit 上不持久），
需要外部結果落地；長期走 Hybrid（Sheets ledger + Drive artifacts），個人 Gmail 優先 OAuth。
Replit Safe Sandbox（v0.6.5B）已實測通過。本版做 mock，真寫入留待 v0.6.8+。

## 3. 新增環境變數（`.env.example` 只放 placeholder）

| key | 預設 | 說明 |
|---|---|---|
| `RESULT_SINK_ENABLED` | `false` | 總開關，**預設關閉** → emit 立刻回 `disabled`，零影響 |
| `RESULT_SINK_TYPE` | `none` | `none` / `google_sheets`（目前只實作 google_sheets 的 mock） |
| `RESULT_SINK_MODE` | `mock` | `mock` 才寫本地 JSONL；非 mock 在 v0.6.7 回 `skipped`（不做真寫入） |
| `MOCK_GOOGLE_SHEETS_ROWS_PATH` | `data/mock_google_sheets_rows.jsonl` | mock 落地路徑（在 `data/`，已 gitignore） |

## 4. Mock Sink 設計（`app/result_sink.py`）

- **不 import 任何 google client library**、不讀 credentials、零 API call。
- `is_result_sink_enabled()`：`RESULT_SINK_ENABLED=true` 且 `RESULT_SINK_TYPE != none` 才 True。
- `build_task_ledger_row(task, result, error)`：把 queue row(+TaskResult) 組成一列 ledger row；
  缺欄位補空值、不 crash；`result_summary` 截斷（≤500 字）。
- `emit_result(task, result, error)`：
  - 未啟用 → `{"status":"disabled"}`
  - `google_sheets` + `mock` → append 一列到 mock JSONL → `{"status":"mock_written", ...}`
  - 啟用但非 mock → `{"status":"skipped"}`（v0.6.7 不做真寫入）
  - **永不拋例外**：任何錯誤只回 `{"status":"error"}`，**絕不影響 queue / Worker**。

## 5. Sheets Ledger 欄位

`task_id` / `title` / `status` / `safety_level` / `requires_confirmation` / `created_at` /
`updated_at` / `completed_at` / `attempts` / `source` / `result_summary` / `result_uri` /
`drive_file_id` / `error` / `metadata_json`。

- MVP 必要：task_id / title / status / safety_level / created_at / completed_at / result_summary / error。
- 後補：requires_confirmation / updated_at / attempts / source / metadata_json。
- `result_uri` / `drive_file_id`：未來 Hybrid（Drive artifact）才填；本版恆 `None`。
- **長結果不塞整段**：`result_summary` 截斷 ≤500 字；長結果未來放 Drive。

## 6. Worker 接入策略

已在 `app/worker.py` 的**終態**（completed / 三個 failed 分支）後呼叫 `result_sink.emit_result(...)`：
- 成功 → `emit_result(item, result=result)`
- BAD_PAYLOAD / OpenClaw 最終失敗 / worker 內部錯誤 → `emit_result(item, result=result, error=...)`
- **retry-requeue（非終態）不 emit**。

安全邊界：
- `emit_result` 內部全 try/except、**預設 disabled**（`RESULT_SINK_ENABLED=false` 時是 no-op）。
- 未改 claim 邏輯、未改 Queue 狀態機、未改 retry / approval / dashboard control。
- sink 失敗只回 error，**不會讓任務變 failed、不影響 queue 狀態**。

## 7. 測試結果

新增 `scripts/test_google_sheets_mock_sink.py`（importlib.reload 多狀態），全數通過：
1. 預設 disabled → emit `disabled` 且不寫檔；enabled 但 type=none 仍 disabled。
2. mock 啟用 → 寫入 JSONL（含 `_mock=true` 標記）。
3. row 欄位完整（全部 15 欄）。
4. 長 `result_summary` 截斷 ≤500 + 省略號。
5. error case → `error` 欄位有值、status=failed。
6. mock log 在 `data/` 下且**未被 git tracked**。
7. emit 永不拋例外（空 task 不 crash）；`app.main` import OK。

既有測試全部仍通過（sink 預設 false）：queue_store / system_health / dashboard_polish /
dashboard_auth_gate / readiness + smoke（fake OpenClaw, PONG）。

## 8. 安全邊界

- 不連真 Google、不 import google library、零 API call。
- 不放 / 不輸出任何 credentials / token / client secret / SA private key。
- 不 commit `.env` / `data/` / `queue.db` / `*.jsonl` / mock log / credentials JSON。
- mock log 在 `data/`（已 gitignore），只是暫存、可丟。

## 9. Replit 使用方式

- 目前仍建議 **disabled**（`RESULT_SINK_ENABLED=false`）。
- 若要在 Replit 測 mock：Secrets 設 `RESULT_SINK_ENABLED=true`、`RESULT_SINK_TYPE=google_sheets`、
  `RESULT_SINK_MODE=mock`。**注意 mock log 寫在 Replit filesystem，不持久、只是暫存**，
  不是正式資料來源（這正是未來真 sink 要解的問題）。

## 10. 下一步

**v0.6.8 OAuth / Secrets Design**（個人 Gmail 走 OAuth，窄 scope、refresh token 放 Secrets），
之後 v0.6.9 Google Sheets Write Pilot（真寫入小規模試行）。
