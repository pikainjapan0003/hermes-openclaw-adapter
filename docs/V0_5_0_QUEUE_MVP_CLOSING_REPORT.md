# v0.5.0 Queue MVP — 封版報告

| 項目 | 內容 |
|---|---|
| **版本名稱** | `v0.5.0-local-queue-worker` |
| **完成日期** | 2026-06-15 |
| **功能完成 commit** | `0bd2a65 feat: add local queue worker MVP` |
| **狀態** | ✅ 已封版（測試全 PASS、tag 已固定、未 push） |
| **前一版** | `v0.4.1-discord-e2e-verified`（FastAPI BackgroundTasks 背景執行 + callback） |

---

## 1. 本版目標

把原本「Adapter 接到任務後直接用 FastAPI BackgroundTasks 執行 OpenClaw」的流程，
改成中間插入一層**持久化本地 Queue + 獨立 Worker**：

> 第一步只做「最小可用 Queue」，**不重構整個系統**、**不破壞 v0.4.1 既有流程**。

刻意限制：
- 第一版用 **SQLite / 本地檔案型 queue**，**不引入 Redis**（先驗證 Queue 架構，不一次增加外部依賴）。
- 不碰 token、不改安全等級邏輯、不改 OpenClaw CLI 呼叫方式、不改 MCP / Hermes / Discord。

---

## 2. 架構變更

```text
Hermes / MCP
  → Adapter  POST /tasks/dispatch        （只建立 task_id、寫 ledger、enqueue、立刻回 accepted）
  → Durable Local Queue (SQLite)          （app/queue_store.py）
  → OpenClaw Worker  python -m app.worker （輪詢 → claim → 執行 → 回寫狀態）
  → OpenClaw CLI (openclaw agent ...)
  → data/results.jsonl
  → GET /tasks/{task_id} / {task_id}/result （查詢結果）
```

任務狀態機：`queued → running → completed`
失敗時：`running → (可重試且未達上限) queued → … → (達上限或不可重試) failed`
可取消：仍在 `queued` 時 `cancelled`。

---

## 3. 與 v0.4.1 的差異

| 面向 | v0.4.1 | v0.5.0 |
|---|---|---|
| 執行方式 | FastAPI `BackgroundTasks`（與 request 同進程） | 持久化 Queue + 獨立 Worker 進程 |
| 持久性 | 重啟即遺失未跑完任務 | SQLite 落地，重啟後 Worker 可續跑 |
| 崩潰復原 | 無 | Worker 啟動時 `reset_stale_running()` 把卡在 `running` 的任務改回 `queued` |
| 重試 | 無 | `attempts` / `max_attempts`，可重試錯誤自動 requeue |
| 取消 | 無 | `POST /tasks/{id}/cancel`（僅限 `queued`） |
| 觀測 | `/tasks`、`/tasks/{id}` | 另加 `GET /queue`（counts + items）、查詢端點附 `queue` 欄位 |
| 向後相容 | — | `EXECUTION_MODE=background` 可一鍵退回 v0.4.1 行為 |

> **向後相容保證**：`EXECUTION_MODE` 預設 `queue`（v0.5），設為 `background` 即完全走回 v0.4.1 的 BackgroundTasks 路徑（已實測 PASS，`queue` 欄位為 `null`）。token / safety_level / MCP 呼叫格式 / OpenClaw CLI 呼叫方式 / results.jsonl / tasks.jsonl 機制皆未更動。

---

## 4. 新增檔案

| 檔案 | 說明 |
|---|---|
| `app/queue_store.py` | `QueueStore` 類別。純 stdlib `sqlite3`（WAL + `busy_timeout` + `BEGIN IMMEDIATE` 原子 claim）。狀態 `queued/running/completed/failed/cancelled`；欄位 `task_id, created_at, updated_at, status, title, task_text, safety_level, attempts, max_attempts, error, result_ref, correlation_id, payload`。 |
| `app/worker.py` | Queue Worker（`python -m app.worker`）。輪詢 → `claim_next`（→running、attempts+1）→ 重用 `app.main` 既有執行邏輯 → 回寫 `completed`/`failed`/requeue。啟動時崩潰復原。 |
| `scripts/test_queue_store.py` | QueueStore 純單元 smoke（不需 OpenClaw）。 |
| `scripts/smoke_test_queue.sh` | 端到端 PONG smoke（內建假 openclaw CLI；`USE_REAL_OPENCLAW=1` 改用真實 openclaw）。 |
| `scripts/start_worker.sh` | 背景常駐啟動 Worker 的輔助腳本。 |
| `docs/V0_5_0_QUEUE_MVP_CLOSING_REPORT.md` | 本封版報告。 |

## 5. 修改檔案

| 檔案 | 變更（最小） |
|---|---|
| `app/main.py` | 版本 → `0.5.0`；新增 `EXECUTION_MODE` / `QUEUE_DB_PATH` / `QUEUE_MAX_ATTEMPTS` 與懶初始化 `get_queue()`；`/tasks/dispatch` 在 queue 模式改為 enqueue（不在 request 內跑 OpenClaw）；`/tasks/{id}`、`/result` 附 additive `queue` 欄位；新增 `POST /tasks/{id}/cancel`、`GET /queue`；`/health` 顯示執行模式。 |
| `.env.example` | 新增 v0.5 Queue 區塊（`EXECUTION_MODE` / `QUEUE_DB_PATH` / `QUEUE_MAX_ATTEMPTS` / `WORKER_POLL_INTERVAL_SECONDS` / `WORKER_RETRY_BACKOFF_SECONDS`）。 |

---

## 6. 新增指令

```bash
# 啟動 Worker
python -m app.worker            # 或 ./scripts/start_worker.sh

# 測試
python scripts/test_queue_store.py          # QueueStore 單元 smoke
./scripts/smoke_test_queue.sh               # 端到端 PONG（假 openclaw）
USE_REAL_OPENCLAW=1 ./scripts/smoke_test_queue.sh   # 端到端 PONG（真實 openclaw）
EXECUTION_MODE=background ./scripts/smoke_test_queue.sh  # 驗證 v0.4 舊路徑

# 新 API
POST /tasks/{id}/cancel         # 取消仍在 queued 的任務
GET  /queue                     # queue 概況（counts + 最近 items）
```

---

## 7. 啟動方式

### 啟動 Adapter
```bash
cd ~/projects/hermes-openclaw-adapter
./scripts/start_adapter_v04.sh        # 沿用既有腳本，:8000
# 或手動： source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

### 啟動 Worker
```bash
source .venv/bin/activate
python -m app.worker                  # 或 ./scripts/start_worker.sh
```

> ⚠️ queue 模式（預設）下**一定要啟動 Worker**，否則任務會永遠停在 `queued`。
> 若暫時不想跑 Worker，可設 `EXECUTION_MODE=background` 退回 v0.4.1 行為。

### PONG smoke test
```bash
./scripts/smoke_test_queue.sh
```
流程：起 Adapter → 起 Worker → POST 一筆 PONG 任務 → 輪詢 status → 查 result → 確認 `results.jsonl` 有結果。

---

## 8. 測試結果摘要

| 測試 | 結果 |
|---|---|
| `python scripts/test_queue_store.py` | ✅ PASS — enqueue / claim / complete / requeue / failed / cancel / crash-recovery |
| `./scripts/smoke_test_queue.sh`（queue 模式） | ✅ PASS — `queued → running → completed`，`result_text=PONG`，`results.jsonl` 有結果 |
| `EXECUTION_MODE=background ./scripts/smoke_test_queue.sh` | ✅ PASS — v0.4 舊路徑保留，`queue:null`，completed / PONG |

衛生檢查：`.env` / `.venv/` / `data/`（含 `queue.db`）/ `*.log` 均被 `.gitignore` 排除，無敏感檔案被追蹤。

---

## 9. 第一版 Queue 的能力邊界

**做得到：**
- 任務落地持久化（SQLite），Adapter / Worker 重啟不遺失。
- 單一 Worker 順序消費；原子 claim 不重複領取。
- 失敗重試（可重試錯誤）+ 達上限標記 `failed` 並寫錯誤。
- 啟動崩潰復原（`running` → `queued`）。
- 取消 `queued` 任務、查詢 queue 概況。

**目前假設 / 限制：**
- **單一 Worker**。`reset_stale_running()` 與「卡住即視為崩潰」的邏輯，只有在單 Worker 下才安全。
- 無分散式鎖、無多 Worker 併發消費。
- 無死信佇列（DLQ）；達上限即 `failed`，不會自動搬移到獨立佇列。
- 無 approval flow；安全等級閘門沿用 v0.4（Level 0/1 自動跑，Level 2+ 拒絕）。
- 觀測僅 `GET /queue` 純 JSON，無 dashboard。
- callback 沿用 v0.4 的 `ledger_only` / `http`（HMAC），非事件流。

---

## 10. 尚未做的項目

- ❌ Redis（刻意先用 SQLite 驗架構）
- ❌ DLQ（死信佇列）
- ❌ Dashboard / 黑板（blackboard）
- ❌ Approval flow（人工審核高風險任務）
- ❌ 多 Worker / 併發消費
- ❌ 正式 callback event stream

---

## 11. 何時進入下一版

當出現以下訊號時，再投資下一階段：
- **任務變多**：單 Worker 順序消費跟不上 → 需要多 Worker / Redis。
- **需要更好觀測**：只看 JSON 不夠，要看吞吐 / 失敗率 / 等待時間。
- **需要黑板 dashboard**：要一個畫面看 queue 全貌與歷史。
- **需要 approval flow**：要把 Level 2+ 任務導入人工審核再放行。

---

## 12. 下一版建議（路線圖）

| 版本 | 主題 | 重點 |
|---|---|---|
| `v0.5.1` | queue observability | 指標 / 結構化日誌 / `/queue` 強化（吞吐、失敗率、等待時間） |
| `v0.5.2` | blackboard dashboard | 一個畫面看 queue 狀態與任務歷史 |
| `v0.5.3` | approval flow | 高風險（Level 2+）任務人工審核後放行 |
| `v0.6.0` | Redis / DLQ / multi-worker | 換上 Redis、加死信佇列、支援多 Worker 併發 |

---

> **封版聲明**：`v0.5.0-local-queue-worker` 功能已完成並通過全部測試，tag 固定指向 `0bd2a65`，本報告為結尾文件，不再加新功能、不改核心程式。
