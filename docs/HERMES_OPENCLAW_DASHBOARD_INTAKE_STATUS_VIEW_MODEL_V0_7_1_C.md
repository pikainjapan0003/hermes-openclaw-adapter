# Hermes x OpenClaw — Dashboard Intake Status View Model v0.7.1-C

> 這一版只做**純 view-model + 唯讀 CLI/report + tests + readiness + 文件**。
> **不改 Web Dashboard**（不動 `app/main.py`、templates、static、不新增 route）。
> 只先建立「mock / local-only / executable=false」的**安全顯示模型**。

## 1. Purpose

v0.7.1-B 讓任務能以 `waiting_review` 寫入獨立的 local-only intake DB。
但這些任務目前在 Web Dashboard 上**看不到**（dashboard 只讀 production queue.db）。

v0.7.1-C 的目的：建立一個**純函式的顯示推導模型**（view-model），
能從一筆 Queue task row 安全地推導出「這是 mock / local-only / real？是否可被 worker 執行？
approval / risk 為何？」，並提供一支**唯讀 CLI** 來檢視 intake DB。
這一步**不改 Web Dashboard**，只先把顯示邏輯做對、做安全、可測試。

## 2. Relationship To v0.7.1-A And v0.7.1-B

- v0.7.1-A（plan-only）規劃了「mock / real 狀態可視性」與 Result Sink observation-only 邊界。
- v0.7.1-B 實作了 local-only intake bridge：任務以 `waiting_review` 寫入獨立 intake DB，標記 `local_only` / `executable_by_worker=false`。
- v0.7.1-C 在**不接觸執行路徑**的前提下，把 v0.7.1-B 已落地的標記，轉成**安全的唯讀顯示**。

## 3. Why This Version Does Not Modify Web Dashboard

Owner 裁定採**方案 A**：先做純 view-model 與唯讀 CLI，不動 Web Dashboard。
理由：

- `app/main.py` 在先前版本被列為**禁改**；先在獨立模組把顯示邏輯做對、可測試，風險最低。
- 顯示模型先穩定，未來若要接進 Web Dashboard（方案 B）只是「呼叫既有純函式」，改動更小、更可審查。

## 4. What v0.7.1-C Allows

- 新增 `app/dashboard_intake_view_v0_7.py`：純函式 `derive_intake_status_view(task)`。
- 新增 `scripts/show_intake_status_v0_7_1_c.py`：唯讀 CLI，讀指定 DB、套 view-model、印 console 摘要。
- 新增 tests / readiness / 本文件。

## 5. What v0.7.1-C Does Not Allow

明確安全聲明：

```text
No app/main.py modification.
No template modification.
No route addition.
No true Hermes webhook.
No true OpenClaw execution.
No true Worker start.
No Queue status mutation.
No production Queue DB write.
No automatic Google Sheets write.
No external side effect.
Result Sink is observation-only, not Queue source of truth.
```

## 6. View-model Fields

`derive_intake_status_view(task: dict) -> dict` 回傳：

```text
task_id
status
source_mode           # mock / local-only / real / unknown
intake_mode           # local-only / production / unknown
executable_by_worker  # true / false / unknown
approval_status       # pending / not_required / <explicit> / unknown
risk_level            # int 或 None
safety_level          # int 或 None
display_badges        # 人類可讀標籤清單（唯讀顯示用）
```

## 7. Source Mode Derivation

```text
metadata.intake_source == "mock-adapter-local" → local-only（最具體，優先）
metadata.mock == true                          → mock
metadata.mock == false（明確）                 → real
其他                                           → unknown
```

## 8. Intake Mode Derivation

```text
metadata.local_only == true   → local-only
metadata.local_only == false  → production
其他                          → unknown
```

## 9. Executable-by-worker Derivation

```text
metadata.executable_by_worker 為明確 bool → 採用該值
否則若 status == queued                   → true
否則若 status ∈ {waiting_review, rejected, cancelled, archived, completed, failed} → false
其他                                       → unknown

保守防線（最高優先）：
若任務為 local-only（intake_mode=local-only / source_mode=local-only / metadata.local_only=true），
且上面推得 true → 一律改回 false。
→ local-only 任務「永遠」不會被顯示成 executable_by_worker=true。
```

此推導與 `QueueStore.claim_next()`（只 claim `queued`）一致：`waiting_review` 任務 worker 不會 claim。

## 10. Approval / Risk Display Derivation

```text
approval_status：
  metadata.approval_status（非空字串）→ 採用
  否則 status == waiting_review        → pending
  否則 status == queued 且 safety_level <= 2 → not_required
  其他                                 → unknown

risk_level：
  優先 metadata.risk_level → 再 payload.risk_level → 再 task.safety_level → 否則 None
```

## 11. Local-only Intake DB Visibility

- intake 任務寫在獨立 DB（`INTAKE_QUEUE_DB_PATH`，預設 `data/intake_local_v0_7_1_b.db`），Web Dashboard 預設讀不到。
- v0.7.1-C 的 CLI 可指定 `--db-path` 或讀 `INTAKE_QUEUE_DB_PATH` 來**唯讀**檢視這些任務。
- CLI **只讀**：使用 `QueueStore` 的 SELECT 方法（`list_page` / `counts_by_status`），不寫入、不改狀態。

## 12. Read-only CLI Report

`scripts/show_intake_status_v0_7_1_c.py`：

```bash
python scripts/show_intake_status_v0_7_1_c.py --db-path /path/to/intake.db --limit 20
```

- 預設 DB 取 `INTAKE_QUEUE_DB_PATH`（再退回 `data/intake_local_v0_7_1_b.db`）。
- 只印 console 摘要，不建立任何檔案。
- 不 enqueue、不 claim_next、不 approve/reject、不啟動 worker、不呼叫 OpenClaw / Google Sheets。

## 13. Mock / Real Boundary

| 元件 | v0.7.1-C 邊界 |
|------|---------------|
| Hermes | mock only |
| Adapter / Bridge | v0.7.1-B 既有；本版不改 |
| Queue | 唯讀檢視（SELECT only）；不寫、不改狀態 |
| Worker | 不啟動、不 import；顯示層保守標示 executable_by_worker |
| OpenClaw | no true call |
| Google Sheets | no auto write；`GOOGLE_SHEETS_ENABLED=false` |
| Result Sink | observation-only, not Queue source of truth |

## 14. Result Sink Boundary

- 本版不觸發任何 Result Sink 寫入。
- **Result Sink is observation-only, not Queue source of truth.**

## 15. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`；view-model / CLI 不 import / 不呼叫任何 Google client。

## 16. Security / Secrets Rules

- view-model 為純函式，不讀環境、不讀 secrets。
- CLI 只讀本版相關的非敏感設定（`INTAKE_QUEUE_DB_PATH`、`--db-path`）。
- 不讀 / 不顯示任何 secret：refresh token、access token、client secret、private key、完整 spreadsheet ID、完整 Google Sheets URL、Owner 真實 secrets 路徑。
- 敏感檢查一律 regex / 格式比對。

## 17. Test Coverage

`scripts/test_dashboard_intake_view_v0_7_1_c.py` 至少涵蓋：

```text
- mock / local-only / real / unknown source_mode 推導
- intake_mode 推導
- executable_by_worker：explicit、queued、waiting_review、unknown
- local-only 任務永遠不會被推成 executable=true（含矛盾標記）
- risk_level / safety_level 多來源推導
- approval_status 推導
- view-model 不修改輸入（不寫 DB）
- payload 為 JSON 字串也能解析
- 不 import app.main / app.worker
```

## 18. Readiness Checks

`scripts/check_hermes_openclaw_dashboard_intake_status_view_model_v0_7_1_c_readiness.py`（純靜態）至少檢查：

```text
- doc / view module / CLI / test / readiness 檔存在
- doc 含必要標題與安全聲明
- view module 不 import app.main / app.worker
- view module 不呼叫 enqueue / claim_next / approve / reject / run_openclaw_cli / google client
- CLI 不寫 DB（無 enqueue / claim_next / mark_* / approve / reject）
- 未修改 app/main.py / templates/* / static/*
- 無新增 route / webhook / POST handler
- GOOGLE_SHEETS_ENABLED 無 true
- 無完整 spreadsheet URL / ID / token / secret / private key（格式比對）
```

## 19. Explicit Non-goals

- 不改 Web Dashboard（main.py / templates / static / route）。
- 不接真 Hermes / 真 OpenClaw / 不建 webhook / 不啟動 Worker。
- 不寫 production Queue DB、不改 Queue 狀態、不寫 Google Sheets。
- 不做任何外部 side effect、不讀 / 不顯示 secret。
- 不進 v0.7.1-D。

## 20. Final Recommendation

v0.7.1-C 提供穩定、可測試的唯讀顯示模型與 CLI，安全地把 local-only intake 任務的
「mock / local-only / 不可執行」狀態呈現出來。建議下一步（需 Owner 再批准）才評估：

- 是否把 `derive_intake_status_view` 接進 Web Dashboard（方案 B：改 main.py + templates，僅唯讀顯示）。
- 是否在 dashboard 以分頁/分區方式同時觀測 production queue 與 local-only intake DB。

本版到此收住——**不 push、不 tag、不進 v0.7.1-D，等待 Owner 檢視。**
