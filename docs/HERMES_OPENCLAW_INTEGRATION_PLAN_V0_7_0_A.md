# Hermes x OpenClaw — Integration Plan v0.7.0-A

## 1. 本文件目的

把開發方向從 **Google Sheets pilot 線**校正回 **Hermes ↔ OpenClaw 協同主線**，
定義 Adapter / Queue / Callback 的契約、schema 草案、approval 模型與安全邊界。
本版**只做 plan / contract / schema 草案 / readiness**：
不呼叫真 OpenClaw、不接真 Hermes、不改 Worker 執行邏輯、不自動寫 Google Sheets、
不把 `GOOGLE_SHEETS_ENABLED` 改成 true。

## 2. 為什麼 v0.7.0 要回到 Hermes ↔ OpenClaw 主線

- v0.6.8/0.6.9 把大量精力放在 OAuth + Google Sheets pilot；那是**觀測 / 結果落地**能力，不是主線。
- 專案核心價值在於：**Hermes 下任務 → Adapter 驗證 → Queue 排程 → OpenClaw 執行 → callback 回寫 →
  Dashboard 監控 / Owner 批准**。v0.7.0 起回到這條主線。

## 3. v0.6.9 Google Sheets pilot 完成狀態摘要

- pilot 線 A→B→C0→C1 已完成並 push；single-row 真寫成功（`status=appended`）。
- `GOOGLE_SHEETS_ENABLED=false` 已回復；writer / runner 仍**獨立**，未接核心；`result_sink` 仍 mock-safe。

## 4. 校正結論：Google Sheets 是觀測層，不是主線

- Google Sheets 是 **pilot-proven 的 result sink（觀測 / 紀錄層）**，不是任務執行主線。
- 它只能作為**終態摘要**的落地選項之一，受 `GOOGLE_SHEETS_ENABLED` gate 控制；
  **不可**直接常態化、不可成為 Queue 狀態來源、不可破壞任務狀態。

## 5. 目標架構

```text
Owner / Dashboard
        ↓
Hermes Agent
        ↓
Adapter API / MCP Tool
        ↓
Queue TaskEnvelope
        ↓
OpenClaw Worker
        ↓
OpenClaw Gateway / Webhooks / Tools
        ↓
Callback Event
        ↓
Queue State Update
        ↓
Result Sink / Dashboard / Hermes Summary
```

## 6. 固定角色分工

```text
Owner          = 監控者 / 最終批准
Hermes         = 主腦 / 任務拆解 / 記憶 / 技能 / 決策
Adapter        = 契約層 / 驗證層 / 安全 gate（唯一操作入口）
Queue          = 任務唯一事實來源（single source of truth）
OpenClaw Worker= 執行層（從 Queue claim 任務並執行）
Callback       = 執行結果回報
Result Sink    = 觀測與紀錄，不可破壞 Queue 狀態
Dashboard      = 人類監控與批准介面
```

核心原則：**Queue 是任務唯一事實來源；Adapter 是唯一操作入口；OpenClaw 是執行網關（execution gateway）；
Hermes 是主腦；Result Sink 不可破壞 Queue 狀態；Level 3+ 需 Owner 批准。**

## 7. TaskEnvelope v0.7 草案

Adapter 收到 Hermes 任務後，正規化為 Queue 中的 TaskEnvelope。建議欄位：

```text
task_id              # 唯一 id（adapter 產生）
created_at           # ISO8601 UTC
created_by           # hermes / owner / system
source               # 來源（discord / dashboard / hermes-agent ...）
requested_by         # 實際請求者識別（非 secret）
risk_level           # 0..4（見第 10 節 approval model）
approval_required    # bool
approval_status      # none / pending / approved / rejected
intent               # 高層意圖（人類可讀）
goal                 # 目標描述
task_type            # 類別（query / action / pipeline ...）
priority             # low / normal / high
input_summary        # 摘要（不含 secret）
input_payload_ref    # 指向 payload 的參考（不內嵌 secret）
allowed_tools        # 允許工具白名單
denied_tools         # 禁用工具黑名單
target_runtime       # openclaw / mock ...
target_workspace     # 目標工作區（非 secret）
idempotency_key      # 去重鍵（見第 11 節）
max_retries          # 上限
retry_count          # 目前重試次數
status               # 見下方狀態機
result_policy        # 結果落地策略（none / ledger / sink ...）
callback_policy      # callback 策略（ledger_only / http ...）
metadata             # 其他非敏感中繼資料
```

### TaskEnvelope 狀態機

```text
draft → pending_approval → queued → dispatching → running
      → callback_received → completed
                          → failed → (retry → queued) | dead_letter
任意非終態 → cancelled
```

狀態值：`draft, pending_approval, queued, dispatching, running, callback_received,
completed, failed, cancelled, dead_letter`。

## 8. CallbackEvent v0.7 草案

OpenClaw 執行端回報事件，Adapter 驗證後據以更新 Queue。建議欄位：

```text
event_id       # 事件唯一 id
task_id        # 對應 TaskEnvelope
flow_id        # 執行流程 id（可選）
source         # openclaw-worker / gateway ...
created_at     # ISO8601 UTC
event_type     # 見下方
status         # 對應結果狀態
summary        # 人類可讀摘要（不含 secret）
result_ref     # 結果參考（不內嵌 secret）
error_code     # 失敗代碼
error_message  # 失敗訊息（不含 secret）
retryable      # bool
duration_ms    # 執行耗時
artifacts      # 產出參考清單（非 secret）
metadata       # 其他非敏感中繼資料
```

`event_type`：`accepted, started, progress, completed, failed, cancelled,
artifact_ready, approval_required`。

## 9. Queue state machine（治理）

- Queue 是**唯一事實來源**；只有 Adapter（依 callback / approval）可改狀態。
- Dashboard **不**直接呼叫 OpenClaw CLI、**不**直接改 Queue 狀態（只透過 Adapter 的受控動作）。
- 終態為 `completed / failed / cancelled / dead_letter`；終態後不得被 result sink 反轉。

## 10. Approval model（本版只定義契約，不實作）

```text
Level 0：純讀 / 無副作用            → 可自動
Level 1：低風險單步操作              → 可自動或半自動
Level 2：外部系統寫入 / 可逆操作    → 需要 guard
Level 3：不可逆 / 金流 / 刪除 / 發送 / 跨平台 → 需要 Owner 批准
Level 4：高風險 / credential / 法律金融醫療 / 大量自動化 → 禁止自動執行
```

- `risk_level >= 2` → `approval_required` 視策略而定；`>= 3` → **必須** Owner 批准（`approval_status=approved`）。
- v0.7.0-A **不實作** approval 流程，只定義等級與契約。

## 11. Retry / DLQ / idempotency 草案

- **idempotency**：每個任務帶 `idempotency_key`；Adapter / Worker 以此**避免重複執行 / 重複寫入**。
- **retry**：`failed` 且 `retryable` 且 `retry_count < max_retries` → 退避後重新 `queued`；
  retry-requeue **不** emit result sink（沿用 v0.6.7 規則，只在終態 emit）。
- **DLQ / dead_letter**：超過 `max_retries` 或不可重試 → `dead_letter`，待人工檢視，不再自動重試。

## 12. Result Sink integration 原則

```text
Result Sink 不是 Queue 狀態來源。
Result Sink 失敗不得讓 completed task 變 failed。
Result Sink 不得造成任務重複執行。
Result Sink 只可寫終態摘要。
Google Sheets 寫入必須受 GOOGLE_SHEETS_ENABLED gate 控制。
Google Sheets 常態寫入需 v0.7 後續版本另行批准。
```

## 13. Google Sheets 目前定位

- Google Sheets 目前只能作為 **pilot-proven sink**，**不可**直接常態化。
- 維持 `GOOGLE_SHEETS_ENABLED=false`；writer / runner 仍獨立，未接 result_sink / Worker。
- 要常態化必須另立版本，設計批次 / 重試 / 去重 / 失敗隔離 / 最小權限，並經 Owner 批准。

## 14. v0.7.0-B / C / D 建議路線

- **v0.7.0-B**：TaskEnvelope / CallbackEvent 的**正式 schema 檔 + 純驗證器**（mock，不接真系統）。
- **v0.7.0-C**：Adapter 契約層**驗證 + approval gate**（mock callback，不呼叫真 OpenClaw / Hermes）。
- **v0.7.0-D**：以 mock OpenClaw / mock Hermes 做 end-to-end dry-run；真接線再另立版本與批准。

## 15. 禁止事項

- 不呼叫真 OpenClaw Gateway、不呼叫真 Hermes API、不建立真 webhook。
- 不開啟 Google Sheets 自動寫入、不執行 live runner、不把 `GOOGLE_SHEETS_ENABLED` 改成 true。
- 不讀 / 顯示任何 secret / refresh token / client secret、不改 Replit Secrets。
- 不改 `app/main.py` 自動接新流程、不把 `result_sink` 改成真寫、不建 tag。

## 16. 最終狀態摘要

- 本版交付：整合計畫 + 契約 / schema 草案 + approval 模型 + readiness + 安全邊界文件。
- 方向已校正回 Hermes ↔ OpenClaw 主線；Google Sheets 定位為觀測層、維持 `GOOGLE_SHEETS_ENABLED=false`。
- 未呼叫真 OpenClaw / 真 Hermes、未自動寫 Sheets、未改 Worker / app.main / result_sink。
- 下一步：Owner 批准後進 v0.7.0-B（正式 schema + 純驗證器，mock）。
