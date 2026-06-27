# Hermes x OpenClaw — Kill Switch / Audit Log / Per-tool Allowlist Plan v0.7.1-D

> **v0.7.1-D is plan-only.** 這一版只做 plan / doc / readiness，
> **不做 local-only implementation、不新增 Python security gate 模組、不改任何既有程式**。
> 它規劃三件未來的安全機制：kill switch、audit log、per-tool allowlist——但本版不實作。

## 1. Purpose

v0.7.1-A 已把「受控進 Queue」的安全模型寫成 plan；v0.7.1-B 實作 local-only intake bridge
（已有 `INTAKE_KILL_SWITCH` 與 task_type allowlist）；v0.7.1-C/C2/C3 完成唯讀顯示。

本文件（v0.7.1-D）的目的：**在不接任何真系統、不改既有程式的前提下**，
把以下三件事的規格定清楚，作為未來實作（v0.7.1-D2 起）的依據：

- **Kill switch**：分層、預設安全、可全域急停。
- **Audit log**：observation-only 的稽核紀錄，不影響任務狀態。
- **Per-tool allowlist**：強制 `denied_tools` / `allowed_tools`，denylist 優先、fail-closed。

## 2. Relationship To v0.7.1-A/B/C/C2/C3

- v0.7.1-A：Controlled Queue Intake Plan（plan-only）——首次規劃 kill switch / audit / allowlist。
- v0.7.1-B：Local-only Queue Intake Bridge——已實作 `INTAKE_KILL_SWITCH` + `INTAKE_ALLOWED_TASK_TYPES`（僅作用於 intake）。
- v0.7.1-C / C2 / C3：intake status view-model + 唯讀 dashboard badges。
- v0.7.1-D（本版）：把 kill switch / audit / allowlist 的**完整跨層規格**定清楚，plan-only。

## 3. Why This Version Is Plan-only

- kill switch / audit / allowlist 若實作不當，會碰到 `app/main.py`（approve/claim 路徑）、`worker.py`（執行）、`queue_store.py`（狀態機）——全是高風險區。
- 先把優先序、控制點、schema、邊界規格定清楚並可被 readiness 靜態驗證，未來實作改動才小、可審查、可逐層批准。
- 本版維持零程式風險：只新增文件與 readiness 檢查。

## 4. Current Safety Flags And Gates

（盤點現況，本版**不修改**）

| flag / gate | 位置 | 作用 |
|---|---|---|
| `QUEUE_INTAKE_ENABLED`（預設 false） | app/queue_intake_bridge_v0_7.py | intake 總開關，fail-closed |
| `INTAKE_KILL_SWITCH`（預設 false） | app/queue_intake_bridge_v0_7.py | 既有 kill switch（僅 local-only intake） |
| `INTAKE_ALLOWED_TASK_TYPES`（預設空） | app/queue_intake_bridge_v0_7.py | 既有 task_type allowlist（僅 intake） |
| `INTAKE_QUEUE_DB_PATH` | app/queue_intake_bridge_v0_7.py | 獨立 intake DB 路徑 |
| `DASHBOARD_AUTH_ENABLED` + `DASHBOARD_TOKEN` | app/main.py | dashboard 登入 gate |
| `RESULT_SINK_ENABLED` | app/result_sink.py | result sink 開關（mock-safe） |
| `CALLBACK_ENABLED` | app/main.py / app/worker.py | callback 開關 |
| `EXECUTION_MODE` / `QUEUE_DB_PATH` / `QUEUE_MAX_ATTEMPTS` | app/main.py | queue 模式 / 路徑 / 重試上限 |
| `HERMES_ADAPTER_TOKEN` | app/main.py | API token gate |
| `GOOGLE_SHEETS_ENABLED`（=false） | app/google_sheets_oauth_writer.py | Google 寫入開關 |
| `WORKER_AUTORUN_ENABLED` | （僅文件規劃，**尚無實作**） | 規劃中的 worker 啟動 gate |

## 5. Current Dashboard / API Actions

（盤點現況，本版**不修改**）

- API POST：`/tasks/{id}/cancel`、`/retry`、`/archive`、`/approve`、`/reject`。
- Dashboard POST：`/dashboard/tasks/{id}/{approve,reject,cancel,retry,archive,comments}`、`/dashboard/login`。
- 全部只走 `QueueStore` 狀態機；**沒有**任何 dashboard/API action 直接啟動 worker 或呼叫 OpenClaw。
- 真執行點唯一在 `app/worker.py`：`claim_next()` → `run_openclaw_cli()` → `result_sink.emit_result()`。

## 6. Current TaskEnvelope Tool Fields

- v0.7 schema 已有 `allowed_tools` / `denied_tools`（optional string arrays）；validator 會檢查型別；mock adapter 會原樣帶過。
- **目前這兩個欄位尚未被任何一層強制執行**（no enforcement yet）。
- 另有 `metadata.safety_level` / `requires_confirmation` 供既有 approval gate 使用。

## 7. Kill Switch Model

- **分層、預設安全（fail-closed）**：每一層各有獨立開關，且最上層有一個**全域** kill switch。
- 全域 kill switch（例如 `GLOBAL_KILL_SWITCH`）開啟時：同時否決 intake、approve→queued、worker claim、OpenClaw execution、Google Sheets live write。
- 任一 kill switch 狀態都必須易於檢查、預設為「安全（拒絕）」方向；無法判定一律視為 active（拒絕）。
- kill switch **優先於所有 allowlist 與 risk gate**。

## 8. Kill Switch Control Points

未來 kill switch 應可控制以下入口（本版只規劃，不實作）：

```text
1. Queue intake                         （已有 INTAKE_KILL_SWITCH）
2. Dashboard/API approve-to-queued      （阻止 waiting_review → queued）
3. Worker claim                         （worker 不 claim；配合 WORKER_AUTORUN_ENABLED 預設 false）
4. OpenClaw execution                   （真執行前最後一道，縱深防禦）
5. Google Sheets live write             （維持 GOOGLE_SHEETS_ENABLED=false）
```

## 9. Audit Log Model

- audit log 為 **observation-only** 的 append-only 紀錄；**不是** Queue 狀態來源。
- 對齊既有 `append_jsonl` / `tasks.jsonl` 風格：寫入為純附加、失敗不可影響主流程（best-effort、吞例外）。
- 未來最小落點建議：獨立、**git-ignored** 的 append-only JSONL（例如 `data/audit_v0_7_1_d.jsonl`）或獨立 sqlite 檔；**不得**動 production `queue.db` schema。
- audit 寫入失敗**不得**反轉或阻擋任務狀態轉移。

## 10. Audit Events

未來 audit event schema（欄位草案，本版只定義）：

```text
event_id
created_at
actor_type
actor_id_masked
action
task_id
correlation_id
from_status
to_status
decision
reason
risk_level
source_mode
intake_mode
tool_name
result
metadata_redacted
```

應記錄的事件（至少）：

```text
- intake 嘗試（accepted / rejected + reason：disabled / kill_switch / not_allowlisted / refuse_production_db）
- 狀態轉移（draft → pending_approval / queued / cancelled / rejected / archived / dead_letter）
- approve / reject（actor、time、task_id、from → to）
- kill switch / allowlist / denylist 命中決策
- worker claim / 執行開始 / 執行結果
```

## 11. Audit Log Boundary

```text
Audit log is observation-only, not Queue source of truth.
Queue SQLite remains the source of truth for task state.
```

- audit log 不改任務狀態、不影響 claim / 執行、不造成重複執行。
- audit log 不得記錄任何 secret / PII。

audit log **不可**記錄：

```text
Do not log refresh token.
Do not log client secret.
Do not log access token.
Do not log private key.
Do not log full spreadsheet ID.
Do not log full Google Sheets URL.
Do not log raw credentials.
```

## 12. Per-tool Allowlist Model

- `TaskEnvelope` 已有 `allowed_tools` / `denied_tools` 欄位；目前**尚未強制執行**。
- 未來應**分三層**強制（縱深防禦）：

```text
1. Adapter / intake layer        （最早、最安全）
2. Approval-to-queued layer      （approve 轉 queued 前再驗一次）
3. Worker execution layer        （claim 後、呼叫 OpenClaw 前最後一道）
```

未來規則建議：

```text
denied_tools 命中 → reject
allowed_tools 空 → fail-closed（拒絕）
tool 不在 allowed_tools → reject
unknown tool → reject
allowed_tools 通過仍需 risk / approval gate
```

## 13. Denylist / Allowlist Priority

```text
denylist 優先於 allowlist（同時命中 → 拒絕）
kill switch 優先於所有 allowlist
unknown tool / unknown source 預設拒絕
local-only 任務不得轉成 executable
audit log 不得影響任務狀態
```

## 14. Adapter / Intake / Approval / Worker Layering

未來 gate 的**完整優先順序**（由先到後、任一拒絕即停）：

```text
1. Global kill switch
2. Layer-specific kill switch
3. Denylist
4. Allowlist
5. Risk / approval gate
6. Queue status gate
7. Worker execution gate
```

- 每一層 fail-closed；越早拒絕越好（intake 層優先）。
- worker execution gate 為最內層縱深防禦；真執行版本另立、需逐層批准。

## 15. Queue Source-of-truth Boundary

- **Queue SQLite remains the source of truth for task state.**
- kill switch / allowlist / audit 都不得取代 Queue 作為狀態來源；它們只「准許 / 拒絕 / 記錄」，不「定義」狀態。

## 16. Result Sink Boundary

- 維持既有原則：**Result Sink is observation-only, not Queue source of truth.**
- 本版及未來 audit/allowlist/kill switch 都不得透過 Result Sink 反轉狀態。**No Result Sink write.**

## 17. Google Sheets Boundary

- 維持 `GOOGLE_SHEETS_ENABLED=false`；不自動寫 Google Sheets。**No Google Sheets write.**
- Google Sheets live write 也是 kill switch 控制點之一（第 8 節）。

## 18. Security / Secrets Rules

- 不讀 / 不顯示任何 secret：refresh token、access token、client secret、private key、完整 spreadsheet ID、完整 Google Sheets URL、Owner 真實 secrets 路徑。
- audit 欄位用 `actor_id_masked` / `metadata_redacted`，一律遮罩；不記原始 credential。
- 敏感檢查一律 regex / 格式比對，不逐字比對完整 spreadsheet ID。

## 19. Future v0.7.1-D2 Local-only Implementation Criteria

進入 v0.7.1-D2（local-only 實作）前須先滿足：

```text
[ ] Owner 批准做 local-only security gate 模組（純函式、不接 main.py / worker）
[ ] evaluate_tool_allowlist：denylist 優先、空 allowlist fail-closed、unknown 拒絕
[ ] kill_switch_active：預設安全（active 即拒絕），全域 + 分層
[ ] audit_record：observation-only、append-only、寫獨立 git-ignored 檔、不含 secret
[ ] 不改 queue 狀態、不寫 production queue.db、不啟動 worker、不接 OpenClaw
[ ] tempfile / 純函式測試 + 靜態 readiness（regex 敏感檢查）
[ ] 維持 GOOGLE_SHEETS_ENABLED=false
```

## 20. Future Worker / OpenClaw Integration Criteria

把 gate 真正接進 **worker claim / OpenClaw 執行** 前（屬最高風險）須先滿足：

```text
[ ] Owner 逐層明確批准（intake → approve → worker → execution）
[ ] WORKER_AUTORUN_ENABLED 設計確定，預設 false、fail-closed
[ ] worker claim 前檢查 global + worker kill switch
[ ] OpenClaw execution 前最後一道 allowlist + kill switch（縱深防禦）
[ ] 完整 audit（claim / 執行 / 結果），observation-only
[ ] 可回退、可急停（kill switch 立即生效）
```

## 21. Explicit Non-goals

本版**明確不做**：

```text
v0.7.1-D is plan-only.
No app/main.py modification.
No worker.py modification.
No queue_store.py modification.
No result_sink.py modification.
No DB schema change.
No new route.
No new POST handler.
No Worker start.
No OpenClaw execution.
No Hermes webhook.
No Google Sheets write.
No Result Sink write.
No Queue status mutation.
Audit log is observation-only, not Queue source of truth.
Queue SQLite remains the source of truth for task state.
```

- 不新增任何 Python security gate 實作模組。
- 不進 v0.7.1-D2、不進 v0.7.1-E。

## 22. Final Recommendation

建議下一步為 **v0.7.1-D2：Local-only Security Gates（純函式模組，不接 main.py / worker）**，
嚴守第 19 節 criteria：只做 `evaluate_tool_allowlist` / `kill_switch_active` / `audit_record` 純函式
+ tempfile 測試 + readiness，**不接** intake/approve/worker 真路徑。真正接線留待逐層批准的後續版本。

在 Owner 批准前，本版到此收住——**plan-only，不 commit（除非 Owner 批准）、不 push、不 tag、不進 v0.7.1-D2 / v0.7.1-E。**
