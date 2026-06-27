# Hermes x OpenClaw — Local-only Queue Intake Bridge v0.7.1-B

> 這一版做一個**受控、fail-closed、不可執行落地**的 local-only intake bridge：
> 讓 mock Adapter 產生的 TaskEnvelope，在嚴格條件下寫入**獨立的 local-only intake DB**，
> 且**一律以 `waiting_review` 落地**——worker 結構上不會 claim、不會執行。

## 1. Purpose

v0.7.1-A 規劃了「受控進 Queue」的安全模型。v0.7.1-B 是這套模型的**第一步最小實作**：
只做「把任務安全地放進一個獨立的、不可被執行的 local intake 暫存區」，
**不**呼叫真 OpenClaw、**不**接真 Hermes、**不**啟動 Worker、**不**寫 production queue.db。

可以把它想成：一個「收件匣」，東西只能進來、被標記成「待審、不可執行」，
等之後（更後面的版本、且經 Owner 批准）才談是否要真正進入執行路徑。

## 2. Relationship To v0.7.1-A

- v0.7.1-A（plan-only）定義了 flags、kill switch、allowlist、waiting_review 保證、Result Sink 邊界。
- v0.7.1-B 把其中**最小、最安全的一塊**落地：local-only intake 寫入 + fail-closed gate。
- v0.7.1-A 列出的其他項目（真 Queue 寫入、worker 啟動、真執行）**仍不**在本版。

## 3. What v0.7.1-B Allows

- 新增 `app/queue_intake_bridge_v0_7.py`（受控 intake 函式）。
- 在 `QUEUE_INTAKE_ENABLED=true`、未觸發 kill switch、task_type 在 allowlist 內時，
  把 TaskEnvelope 寫入**獨立 intake DB**，狀態一律 `waiting_review`。
- 用 tempfile DB 做完整測試；提供靜態 readiness 檢查。

## 4. What v0.7.1-B Does Not Allow

明確安全聲明：

```text
No true Hermes webhook.
No true OpenClaw execution.
No true Worker start.
No production Queue DB write.
No automatic Google Sheets write.
No external side effect.
No queued status from intake bridge.
All persisted intake tasks must be waiting_review.
Result Sink is observation-only, not Queue source of truth.
```

- 不修改 `app/main.py`、`app/worker.py`、`app/queue_store.py`、`app/result_sink.py`。
- 不新增 API route / webhook / worker launcher / background task / scheduler。
- 不 import `app.worker`、不 import `app.main`、不呼叫 `run_openclaw_cli`、不呼叫 Google client。

## 5. Local-only Intake DB Boundary

- intake 只寫入**獨立** DB：`INTAKE_QUEUE_DB_PATH`（預設 `data/intake_local_v0_7_1_b.db`）。
- 預設路徑**不等於** production `QUEUE_DB_PATH`（`data/queue.db`）。
- 若解析後的 intake DB 路徑**撞到** production queue DB，bridge **拒絕寫入**（reason=`refuse_production_db`），保護真 queue。
- 測試一律使用 tempfile DB，**絕不**碰 `data/queue.db`。

## 6. Fail-closed Flag Model

| flag | 預設 | 行為 |
|------|------|------|
| `QUEUE_INTAKE_ENABLED` | `false` | **預設不寫任何 DB**；非 true 一律拒絕（reason=`intake_disabled`） |
| `INTAKE_KILL_SWITCH` | `false` | true 時拒絕所有 intake（最優先） |
| `INTAKE_ALLOWED_TASK_TYPES` | 空 | 逗號分隔；空集合 → 全部拒絕 |
| `INTAKE_QUEUE_DB_PATH` | `data/intake_local_v0_7_1_b.db` | 獨立 intake DB 路徑 |
| `WORKER_AUTORUN_ENABLED` | `false` | 規劃用；本版不啟動 worker |
| `GOOGLE_SHEETS_ENABLED` | `false` | 維持 false，不得改 true |

預設情況（什麼 flag 都不設）：bridge **不寫 DB**。這是 fail-closed。

## 7. Kill Switch Behavior

- `INTAKE_KILL_SWITCH=true` 時，**在所有其他判斷之前**直接拒絕 intake（reason=`kill_switch_active`）。
- kill switch 優先於 `QUEUE_INTAKE_ENABLED`：即使 enabled=true，kill switch 開啟仍拒絕。

## 8. Task Type Allowlist Behavior

- `INTAKE_ALLOWED_TASK_TYPES` 為逗號分隔白名單，預設**空集合**。
- 任務的 `task_type` 必須**明確在白名單內**才可能寫入；否則拒絕（reason=`task_type_not_allowlisted`）。
- 空 allowlist = 全部拒絕（fail-closed）。

## 9. Waiting Review Status Guarantee

- 任何實際寫入 intake DB 的任務，`initial_status` **一律為 `waiting_review`**。
- **絕不**以 `queued` 寫入。連 payload 內的 TaskEnvelope `status` 也被改為 `pending_approval`（schema 合法、非可執行），確保任何地方都不是 `queued`。
- `QueueStore.claim_next()` 只 `SELECT ... WHERE status='queued'`，因此 worker **結構上無法 claim** `waiting_review` 任務。

## 10. Worker Auto-run Prevention

- bridge **不 import** `app.worker`、**不**啟動任何 worker、**不** spawn 程序、**不**呼叫 `run_openclaw_cli`。
- 即使環境中剛好有 worker 在跑，因為任務狀態是 `waiting_review`（非 `queued`），worker 也不會 claim/執行。
- 三層防線：fail-closed flag + 獨立 intake DB + `waiting_review` 狀態。

## 11. Mock / Real Boundary

| 元件 | v0.7.1-B 邊界 |
|------|---------------|
| Hermes | mock only（輸入為 mock TaskEnvelope，無真 webhook） |
| Adapter | mock adapter 產生 envelope；bridge 受控落地 |
| Queue | 只寫**獨立 local-only intake DB**；不寫 production queue.db |
| Worker | 不啟動、不 import；任務 waiting_review 不可被 claim |
| OpenClaw | no true call |
| Google Sheets | no auto write；`GOOGLE_SHEETS_ENABLED=false` |
| Result Sink | observation-only, not Queue source of truth |

## 12. Metadata Marking

寫入的 payload 在 `metadata` 標示：

```text
local_only = true
mock = true
intake_source = "mock-adapter-local"
executable_by_worker = false
```

並將 payload TaskEnvelope 的 `status` 設為 `pending_approval`、`approval_status` 設為 `pending`。

## 13. Result Sink Boundary

- 本版**不觸發**任何 Result Sink 寫入。
- **Result Sink is observation-only, not Queue source of truth.**
- Result Sink 不得反轉任務狀態、不得造成重複執行。

## 14. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`。
- bridge 不 import / 不呼叫任何 Google client，不自動寫 Google Sheets。

## 15. Security / Secrets Rules

- bridge 只讀本版定義的**非敏感 flag**（`QUEUE_INTAKE_ENABLED` / `INTAKE_KILL_SWITCH` /
  `INTAKE_ALLOWED_TASK_TYPES` / `INTAKE_QUEUE_DB_PATH` / `QUEUE_DB_PATH` 比對）。
- 不讀 / 不顯示任何 secret：refresh token、access token、client secret、private key、
  完整 spreadsheet ID、完整 Google Sheets URL、Owner 真實 secrets 路徑。
- 回傳的 `db_path` 僅為本機路徑（非 secret）。
- 敏感檢查一律 regex / 格式比對，不逐字比對完整 spreadsheet ID。

## 16. Test Coverage

`scripts/test_queue_intake_bridge_v0_7_1_b.py`（tempfile DB，不碰 data/queue.db）至少涵蓋：

```text
- 預設 QUEUE_INTAKE_ENABLED=false → 不寫 DB
- INTAKE_KILL_SWITCH=true → 拒絕
- allowlist 空 → 拒絕
- allowlist 含 task_type 且 enabled=true → 寫入 tempfile DB
- 寫入狀態為 waiting_review
- 沒有 queued 任務
- claim_next 不 claim waiting_review
- metadata local_only=true / executable_by_worker=false
- 未 import app.worker / app.main
- 未呼叫 OpenClaw / Google client
```

## 17. Readiness Checks

`scripts/check_hermes_openclaw_local_only_queue_intake_bridge_v0_7_1_b_readiness.py`（純靜態）至少檢查：

```text
- doc / bridge / test 檔存在
- 文件含必要標題與安全聲明
- bridge 預設 QUEUE_INTAKE_ENABLED=false、含 kill switch / allowlist / intake DB 路徑
- bridge 不 import app.worker / app.main、不呼叫 run_openclaw_cli / Google client
- bridge 不寫 queued、寫入狀態只能 waiting_review
- app/main.py / worker.py / queue_store.py / result_sink.py 未被接入新流程
- 無新增 webhook / route / background worker
- GOOGLE_SHEETS_ENABLED 無 true
- 無完整 spreadsheet URL / ID / token / secret / private key（格式比對）
```

## 18. Explicit Non-goals

本版**明確不做**：

- 不寫 production Queue DB、不把任務寫成 `queued`。
- 不啟動 Worker、不 import 真 worker / app.main。
- 不接真 Hermes / 真 OpenClaw / 不建 webhook / 不新增 API route。
- 不寫 Google Sheets、不改 `GOOGLE_SHEETS_ENABLED`。
- 不做任何外部 side effect、不讀 / 不顯示任何 secret。
- 不進 v0.7.1-C。

## 19. Final Recommendation

v0.7.1-B 提供「安全收件匣」：任務只能以 `waiting_review` 進到獨立 local DB，
worker 結構上無法執行，且預設 fail-closed。建議下一步（需 Owner 再批准）才討論：

- 是否要在 dashboard 觀測 intake DB（唯讀）。
- 是否、以及在什麼批准流程下，才允許把 `waiting_review` 任務轉為可執行——
  那會涉及 worker 與真執行，屬更後面的獨立版本。

本版到此收住——**不 push、不 tag、不進 v0.7.1-C，等待 Owner 檢視。**
