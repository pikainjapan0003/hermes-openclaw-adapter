# Hermes x OpenClaw Replit Safe Sandbox Plan v0.6.3

## 1. 本版目標

Owner 決策改為 **成本優先、Replit 優先**（不走 VPS 優先）。本版**只做安全規劃與文件**，
**不部署、不公開 Dashboard、不接真 token、不接真 OpenClaw、不改核心任務邏輯**。

## 2. 目前版本狀態

- ✅ v0.6.0B：GitHub Remote Backup（master + v0.5.x tags 已上 GitHub，SSH）
- ✅ v0.6.1：Restore / Clone Test（clone 重建 venv、全離線測試 + smoke PASS）
- ✅ v0.6.2：Deployment Assessment（Replit/VPS 評估，結論：Dashboard 不可裸露公開）
- 目前 master tip：`999e5ff`，與 origin 同步、working tree 乾淨。

## 3. 為什麼改走 Replit

- **成本優先**：Replit 入門方案約 US$5/月（促銷），比自管 VPS 便宜、無需自己維運主機。
- **新手操作容易**：網頁即可編輯 / 執行 / 看 log，不必處理 SSH、防火牆、systemd。
- 取捨：Replit 換來「便宜 + 易用」，但代價是**休眠、檔案系統不持久、預設 URL 公開**——
  所以必須以「安全沙箱」定位使用，不能當無保護正式生產。

## 4. Replit 使用定位

Replit 在本專案定位為 **Cloud Sandbox / Demo / 輕量測試**，**不是**無保護的正式生產環境。
- 可以：展示 UI、跑 import、用假 OpenClaw 跑 smoke、自己私下測試。
- 不可以：接真 token、跑真實任務、保存正式 queue 資料、把控制台公開給外人。

## 5. Dashboard 風險盤點（本版實測結果）

### 現有頁面（唯讀 GET）
`/dashboard`、`/dashboard/tasks`、`/dashboard/tasks/{task_id}`、`/dashboard/reviews`、`/dashboard/system`

### 會「改任務狀態」的控制路由（POST 表單）
`/dashboard/tasks/{task_id}/approve`、`/reject`、`/cancel`、`/retry`、`/archive`、`/comments`

### Token 保護現況（grep 實測）
| 類別 | 路由 | 是否有 token 保護 |
|---|---|---|
| JSON API | `/tasks/*`、`/queue/*`、`/system/health`、`/system/worker` | ✅ 有 `require_token`（`X-Adapter-Token`） |
| Dashboard 頁面 | `/dashboard`, `/dashboard/tasks`, `/dashboard/reviews`, `/dashboard/system`, `/dashboard/tasks/{id}` | ❌ **無** token 保護 |
| Dashboard 控制表單 | `/dashboard/tasks/{id}/approve\|reject\|cancel\|retry\|archive\|comments` | ❌ **無** token 保護 |

實測：`app/main.py` 中 Dashboard handler 區段（約 1318–1500 行）**完全沒有** `require_token` /
`x_adapter_token`；JSON `/tasks/*` 控制路由（約 693–760、1116、1135 行）**每個都有** `require_token`。

### 為什麼不能裸露公開
Dashboard 控制表單**無認證**，且 approve/reject/cancel/retry/archive 都會**改 queue 任務狀態**。
一旦放上 Replit 的公開 URL，任何知道網址的人都能直接 POST 這些表單去操控任務佇列。
→ **Dashboard 在加上 Auth Gate 之前，絕不可上 Replit 公開 URL。**

> ⚠️ 依本版規則第 10 條：此「控制路由未保護」**記錄為 v0.6.4 必做項**，本版**不直接修改**。

## 6. Replit 三種模式

### 模式 A：Replit Demo Only
- 用途：展示 Dashboard UI。
- 條件：不接真 token、不接真 OpenClaw、只用假資料 / mock queue（或空 queue）。
- 風險：最低；但仍**不建議**把含控制表單的頁面公開（至少要擋掉 POST 控制路由）。

### 模式 B：Replit Private Sandbox
- 用途：自己測試 Adapter / Dashboard。
- 條件：用 Replit Secrets 放**低風險 / 假**設定；只跑假 OpenClaw smoke；不處理正式任務。
- 風險：中；Repl 必須維持私有、不分享網址。

### 模式 C：Replit Controlled Pilot
- 用途：未來小規模實測。
- **前置條件（缺一不可）**：
  - 先完成 **Dashboard Auth Gate**（v0.6.4）。
  - 限制 `queue.db` 使用方式（視為暫時性、可丟，不放正式資料）。
  - 有備份與清理策略。
  - 確認控制路由**不會**公開裸露。

## 7. Replit Secrets 規劃（只列 key 名，不放真值）

依 `.env.example`（17 個 key）分類：

| 分類 | key |
|---|---|
| **可放 Replit Secrets（低風險設定值）** | `EXECUTION_MODE`、`DATA_DIR`、`QUEUE_DB_PATH`、`QUEUE_MAX_ATTEMPTS`、`WORKER_POLL_INTERVAL_SECONDS`、`WORKER_RETRY_BACKOFF_SECONDS`、`OPENCLAW_TIMEOUT_SECONDS`、`OPENCLAW_AGENT_ID`、`OPENCLAW_SESSION_KEY_PREFIX`、`CALLBACK_ENABLED`、`HERMES_CALLBACK_MODE`、`CALLBACK_MAX_RETRIES`、`CALLBACK_TIMEOUT_SECONDS` |
| **絕不能進 GitHub（只放 Secrets，且沙箱階段用假值）** | `HERMES_ADAPTER_TOKEN`、`HERMES_CALLBACK_SECRET` |
| **沙箱階段不應放真值的高風險 key** | `OPENCLAW_CLI_BIN`（Replit 無真 OpenClaw，指向不存在路徑即可）、`HERMES_CALLBACK_URL`（不要指向真 Hermes） |
| **目前可用 placeholder** | `HERMES_ADAPTER_TOKEN=<dummy>`、`HERMES_CALLBACK_SECRET=<dummy>`、`OPENCLAW_CLI_BIN=/nonexistent/openclaw`、`CALLBACK_ENABLED=false` |

原則：`.env` 永不 commit；Replit 上用 Replit Secrets，沙箱階段一律假值。

## 8. Replit 資料存放策略

- **`queue.db` 能不能當正式資料庫**：❌ 不能。Replit 檔案系統在休眠 / 重啟 / redeploy 可能不持久，
  正式佇列有遺失風險；沙箱階段視為「可丟的暫時資料」。
- **`tasks.jsonl` / `results.jsonl`**：❌ 不適合在 Replit 放正式 ledger（同樣持久性風險），且本來就是 gitignored。
- **休眠 / 重啟風險**：Repl 醒來後 `data/` 可能被重置 → 任務狀態 / 結果 / 心跳都可能消失。
- **是否改放外部**：正式落地建議改放**外部資料庫或 Google Sheets / Drive**（呼應 v0.6.6）。
- **v0.6.x 階段建議**：Replit 上只用**臨時 / 假 queue**，不存任何正式資料；正式資料留在本機，
  或等 v0.6.6 評估外部落地後再決定。

## 9. Worker 策略（保守）

- **Adapter 與 Worker 是否同 process**：Replit 通常只有一個 run command；Worker 需持續輪詢，
  與 Adapter 分開較乾淨，但 Replit 不利於穩定跑兩個常駐 process。
- **本版結論（保守）**：
  - **v0.6.3 不跑真 Worker**（Replit 上只跑 Adapter / Dashboard / 假 OpenClaw smoke）。
  - smoke test 只用 **fake OpenClaw**（內建假 CLI），不接真 OpenClaw CLI。
  - 真 OpenClaw CLI 暫時不接（Replit 無此環境）。
  - **v0.6.5** 才做正式 Replit Deployment Test；真 Worker / 真 OpenClaw 留待另外版本驗證。

## 10. v0.6.4 Dashboard Auth Gate 設計（只設計，不實作）

最小安全方案：

- 新增環境變數：
  - `DASHBOARD_AUTH_ENABLED=true|false`（本機開發可 `false`，**Replit 必須 `true`**）。
  - `DASHBOARD_TOKEN`（或 `DASHBOARD_PASSWORD`）：保護 Dashboard 用的密鑰，**不進 git**、放 Secrets。
- 保護範圍：**所有 `/dashboard/*`**（頁面 + 控制表單 approve/reject/cancel/retry/archive/comments）。
- 驗證方式（擇一最小可行）：
  - 簡易：Cookie / query token 或 HTTP Basic Auth（FastAPI dependency 統一套用到 dashboard router）。
  - 未通過 → 回 **401**（或 redirect 到登入頁）。
- 行為：
  - `DASHBOARD_AUTH_ENABLED=false` → 維持現狀（本機方便）。
  - `DASHBOARD_AUTH_ENABLED=true` → 未帶正確憑證一律擋下，控制表單也擋。
- 範圍限制：v0.6.4 只加「閘門」，**不改任務狀態機 / 不改控制行為本身**。

## 11. 建議版本路線

- **v0.6.4**：Dashboard Auth Gate（實作最小保護，必做，先於任何 Replit 公開）
- **v0.6.5**：Replit Deployment Test（私有 Repl、假 OpenClaw、開 Auth Gate）
- **v0.6.6**：Google Drive / Sheets 結果落地評估（外部持久化）

## 12. 結論

Replit 可以作為**第一個低成本雲端工作區**，但**必須先加 Dashboard 保護（v0.6.4），不能裸露公開**。
本版（v0.6.3）只完成安全規劃；目前最大風險是 **Dashboard 控制路由無 token 保護**，已列為 v0.6.4 必做項。
沙箱階段：不接真 token、不接真 OpenClaw、不跑真 Worker、不存正式資料、不公開控制台。
