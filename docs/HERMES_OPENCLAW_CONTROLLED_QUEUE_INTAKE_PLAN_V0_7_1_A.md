# Hermes x OpenClaw — Controlled Queue Intake Plan v0.7.1-A

> **v0.7.1-A is plan-only.** 這一版只做 plan / doc / readiness，**不寫任何程式邏輯、不接任何真系統**。
> 它規劃「mock Adapter 未來在什麼受控條件下，才能把任務寫進真 Queue DB」，但本版**不實作**。

## 1. Purpose

v0.7.0 A–E 已經完成一條**純 mock** 的 Hermes ↔ OpenClaw dry-run 主線
（mock Adapter → TaskEnvelope 驗證 → approval gate → in-memory mock queue → mock worker → mock callback）。

本文件（v0.7.1-A）的目的：**在不接真系統的前提下**，規劃下一步——
也就是「Controlled Queue Intake（受控的進 Queue）」：
讓 mock Adapter 在嚴格、可回退、可稽核的條件下，**未來**能把任務寫入真 Queue DB，
但**仍不**呼叫真 OpenClaw、**仍不**啟動自動外部操作、**仍需** Owner 批准所有高風險任務。

本版只談「進 Queue 之前與當下的安全設計」，不談「真執行」。

## 2. Current State From v0.7.0-E

來自 v0.7.0-E closeout 的固定狀態：

- 一條 **mock-only** dry-run 主線已可運作並通過驗證。
- `No true Hermes integration`、`No true OpenClaw execution`。
- `No true Queue DB write from mock E2E`、`No true Worker start`。
- `No automatic Google Sheets write`，`GOOGLE_SHEETS_ENABLED remains false`。
- Result Sink 為觀測層，不是 Queue 狀態來源。
- 無 v0.7 tag。

## 3. What v0.7.1-A Allows

本版**只允許**：

- 新增本規劃文件與其 readiness 檢查腳本。
- 用文字**描述**未來受控 Queue intake 的模型、政策、邊界與安全條件。
- 定義進入 v0.7.1-B（實作階段）前必須先滿足的 readiness criteria。

## 4. What v0.7.1-A Does Not Allow

本版**明確不允許**（plan-only 安全聲明）：

```text
v0.7.1-A is plan-only.
No true Hermes webhook.
No true OpenClaw execution.
No true Queue DB write.
No true Worker start.
No automatic Google Sheets write.
No external side effect.
No automatic approval for high-risk tasks.
Result Sink is observation-only, not Queue source of truth.
```

- 不修改 `app/main.py`、`app/queue_store.py`、`app/worker.py`、`app/result_sink.py`。
- 不建立 webhook 實作、不啟動 Worker、不寫 Queue DB、不寫 Google Sheets。
- 不讀 / 不顯示任何 secret。

## 5. Controlled Queue Intake Model

未來（v0.7.1-B 起）受控 intake 的目標流程（**本版僅為規劃**）：

```text
mock Hermes request
  → mock Adapter（prepare_queue_candidate_from_mock_request）
  → TaskEnvelope validation（validate_task_envelope）
  → approval gate（risk / approval_required 判斷）
  → Intake Guard（受控閘門：mode / flags / allowlist / kill switch 檢查）
        ├─ 不通過 → 拒絕或維持 pending_approval（不寫 Queue）
        └─ 通過   → 寫入真 Queue DB，狀態標為 queued（mock=false）
  → （仍不自動進 Worker；Worker 啟動為獨立、需明確啟用的後續版本）
```

設計原則：

- **單向閘門**：只有 Intake Guard 通過才寫 Queue；任何不確定一律 fail-closed（不寫）。
- **預設關閉**：受控寫入由一個明確的 flag（例如 `QUEUE_INTAKE_ENABLED`，預設 false）控制；本版不建立此 flag，只規劃。
- **可回退**：寫入 Queue 的任務必須可被標記 cancelled / dead_letter，不可被 Result Sink 反轉。
- **進 Queue ≠ 執行**：寫入 Queue 只代表「排隊」，不代表「執行」；Worker 啟動是另一道獨立關卡。

## 6. Mock / Real Boundary

| 元件 | v0.7.1-A 規劃後的邊界（本版仍為 mock-only） |
|------|--------------------------------------------|
| Hermes | mock only（仍無真 webhook） |
| Adapter | mock adapter exists；未來受控寫 Queue 仍由 flag gate |
| Queue | v0.7.1-A 仍只有 in-memory mock queue；真 Queue DB 寫入留待 v0.7.1-B 且預設關閉 |
| Worker | mock worker only；真 Worker 不啟動、不 import |
| Callback | mock callback event only |
| OpenClaw | no true call |
| Google Sheets | no auto write；`GOOGLE_SHEETS_ENABLED=false` |
| Result Sink | observation-only, not Queue source of truth |

每筆任務都必須帶明確的 `mock` 標記（例如 `metadata.mock`），
真實寫入 Queue 的任務需可清楚與 mock dry-run 任務區分。

## 7. Task Type Intake Policy

規劃哪些 `task_type` 未來可被受控寫入 Queue：

| 類別 | 範例 | Intake 政策（規劃） |
|------|------|---------------------|
| 純讀 / 無副作用 | `mock.summarize`、`query.*` | 可進 Queue（仍不自動執行） |
| 本機可逆操作 | `local.*`（local-only intake） | 可進 Queue，但需標記、需稽核 |
| 外部寫入 / 不可逆 | `action.external.*`、刪除 / 發送 / 金流 | **不可**自動進 Queue；一律 pending_approval |
| 未知 / 未列入 allowlist | 任何未明列者 | fail-closed：拒絕進 Queue |

只有出現在 per-tool allowlist（見第 13 節）的 `task_type` 才可被考慮 intake。

## 8. Risk Level Policy

沿用 v0.7.0 approval model，明確化 intake 對應：

```text
risk_level 0–2 且 approval_required=false → 可進 Queue（queued），仍不自動執行
risk_level 3–4                            → 必須停在 pending_approval，不寫 Queue 為 queued
approval_required=true                    → 必須停在 pending_approval
```

- `risk_level >= 3`：**必須** Owner 批准（`approval_status=approved`）後，才可由後續版本轉為 queued。
- 任何高風險任務**不得**自動批准、不得自動進 Queue 執行路徑。

## 9. Approval Gate Requirements

- approval gate 必須在「寫 Queue 之前」執行；`pending_approval` 任務**不得**被寫成 queued。
- 批准狀態只能由 Owner / 受控管理動作改變，不能由 callback 或 Result Sink 改變。
- 批准與否的判斷必須可稽核（記錄誰、何時、對哪個 task_id、改成什麼狀態）。
- 本版不實作批准流程，只定義要求。

## 10. Worker Auto-run Prevention

- 進 Queue **不等於**執行。Worker 啟動必須是獨立、預設關閉、需明確啟用的關卡。
- 規劃一個獨立 flag（例如 `WORKER_AUTORUN_ENABLED`，預設 false）；本版不建立。
- 受控 intake 階段（v0.7.1-B）**仍不**啟動 Worker、**仍不** import 真 worker 執行邏輯。
- 真實執行（呼叫真 OpenClaw）需另立版本與 Owner 批准。

## 11. Kill Switch Plan

- 規劃一個**全域急停**機制（例如 `INTAKE_KILL_SWITCH`），開啟時：
  - 立即停止任何新的 Queue 寫入（fail-closed）。
  - 不影響既有任務的可檢視性，但不再接受新 intake。
- Kill switch 狀態必須易於檢查、預設為「安全（不寫入）」方向。
- 本版只規劃，不實作。

## 12. Audit Log Plan

- 規劃對以下事件留下**稽核紀錄**（append-only，不含 secret）：
  - intake 嘗試（接受 / 拒絕 / 原因）。
  - 狀態轉移（draft → pending_approval / queued / cancelled / dead_letter）。
  - 批准動作（誰、何時、對哪個 task_id）。
- audit log **不得**記錄任何 secret、token、完整 spreadsheet ID 或 PII。
- audit log 是觀測紀錄，**不是** Queue 狀態來源。
- 本版只規劃 schema 與欄位方向，不實作寫入。

## 13. Per-tool Allowlist Plan

- 規劃一份**逐工具 / 逐 task_type 白名單**：只有列入者才可被考慮 intake。
- allowlist 預設為空 / 最小集合；新增項目需 Owner 明確批准。
- 與 denied_tools 搭配：denylist 優先於 allowlist（同時命中時拒絕）。
- 本版只規劃結構，不建立實際 allowlist 檔案、不接任何工具。

## 14. Result Sink Boundary

- Result Sink（含未來可能的 Google Sheets）為**觀測 / 紀錄層**。
- **Result Sink is observation-only, not Queue source of truth.**
- Result Sink 失敗不得讓任務狀態反轉；終態（completed / failed / cancelled / dead_letter）不可被 Result Sink 覆寫。
- Result Sink 不得造成任務重複執行或重複寫入。

## 15. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`。
- 不自動寫 Google Sheets；writer / runner 仍獨立，不接 intake / Queue / Worker。
- Google Sheets 常態化需另立版本，設計批次 / 重試 / 去重 / 失敗隔離 / 最小權限，並經 Owner 批准。

## 16. Security / Secrets Rules

- 不讀 / 不顯示任何 secret：refresh token、access token、client secret、private key、完整 spreadsheet ID、完整 Google Sheets URL、Owner 真實 secrets 路徑。
- 文件與腳本只可出現 key 名稱、placeholder、遮罩形式、readiness 偵測樣式。
- 敏感檢查一律使用 regex / 格式比對，不逐字比對完整 spreadsheet ID。
- 不修改 Replit Secrets。

## 17. Readiness Criteria For v0.7.1-B

進入 v0.7.1-B（受控 intake **實作**）前，必須先滿足：

```text
[ ] Owner 已批准「允許寫真 Queue DB」的範圍與條件
[ ] 已決定是否先做 local-only intake
[ ] QUEUE_INTAKE_ENABLED flag 設計確定，預設 false、fail-closed
[ ] WORKER_AUTORUN_ENABLED 維持 false，且 v0.7.1-B 不啟動 Worker
[ ] Kill switch 設計與檢查方式確定
[ ] Audit log 欄位與 append-only 寫法確定（不含 secret）
[ ] Per-tool allowlist 結構確定，預設最小、denylist 優先
[ ] approval gate 必在寫 Queue 前、pending_approval 不得轉 queued
[ ] Result Sink observation-only 邊界在實作中被保證
[ ] 仍維持 GOOGLE_SHEETS_ENABLED=false、no true OpenClaw execution
```

## 18. Explicit Non-goals

本版**明確不做**：

- 不實作真 Queue DB 寫入。
- 不接真 Hermes / 真 OpenClaw / 不建 webhook。
- 不啟動 Worker、不 import 真 worker / queue_store / sqlite3。
- 不寫 Google Sheets、不改 `GOOGLE_SHEETS_ENABLED`。
- 不建立 allowlist / kill switch / audit log 的實際實作（只規劃）。
- 不做任何外部 side effect。

## 19. Final Recommendation

建議下一步為 **v0.7.1-B：Controlled Queue Intake（實作，預設關閉）**，且：

- 先以 `QUEUE_INTAKE_ENABLED=false` fail-closed 起步，僅在 Owner 明確啟用下、且僅對 allowlist 內低風險 task_type 寫入真 Queue DB。
- 仍**不**啟動 Worker、仍**不**呼叫真 OpenClaw。
- 所有高風險任務仍停在 `pending_approval`，需 Owner 批准。
- 在 v0.7.1-B 之前，本版到此收住——**plan-only，不 push、不 tag，等待 Owner 批准**。
