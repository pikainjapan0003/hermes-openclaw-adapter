# Hermes x OpenClaw Deployment Assessment v0.6.2

## 1. 本版目標

本版**只評估** Replit / VPS 部署可行性，**不做**正式公開部署、不暴露 Dashboard、
不新增高風險功能、不改核心任務邏輯。產出僅一份評估文件。

## 2. 目前本機系統能力

| 元件 | 說明 |
|---|---|
| **Adapter** | FastAPI（`app/main.py`），收任務 / 發狀態 / 提供 Dashboard 與 observability API |
| **Worker** | `python -m app.worker`，單一 worker 輪詢 SQLite queue，呼叫 OpenClaw CLI 執行 |
| **Queue** | 本地 SQLite（`data/queue.db`，WAL + `BEGIN IMMEDIATE` claim），狀態機 queued/running/completed/failed/cancelled/waiting_review/rejected/archived |
| **Dashboard** | server-side render（FastAPI + Jinja2 + CSS，無 React/Vite），Overview / Tasks / Reviews / System |
| **Blackboard** | 每任務留言（`data` 的 `task_comments` 表），純記錄、不反向控制 queue |
| **Approval Flow** | safety_level ≥ 3 或 requires_confirmation → waiting_review，人工 approve/reject |
| **Limited Control** | Cancel / Retry / Archive（只走 queue 狀態機，不 kill worker、不 force run） |
| **System Health** | worker heartbeat（`worker_heartbeats` 表）+ OpenClaw CLI 路徑檢查（只檢查、不執行） |

技術堆疊：`fastapi 0.115.6` / `uvicorn[standard] 0.32.1` / `httpx` / `pydantic 2.10.4` /
`python-dotenv` / `jinja2 3.1.4` / `python-multipart`。資料庫只用 stdlib `sqlite3`，**無 Redis、單 worker**。

## 3. 本機啟動方式

- **Adapter**：`uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env`
- **Worker**（另一個終端）：`python -m app.worker`
- **Dashboard URL**：`http://localhost:8000/dashboard`（另有 `/dashboard/tasks`、`/dashboard/tasks/{id}`、`/dashboard/reviews`、`/dashboard/system`）
- **環境變數**（`.env.example` 共 17 項；含兩個敏感值 `HERMES_ADAPTER_TOKEN`、`HERMES_CALLBACK_SECRET`，其餘為 OpenClaw CLI 路徑 / queue / callback 設定）

### 關鍵可攜性阻礙：OpenClaw CLI 依賴
Worker 真正執行任務時是 **shell out 到 WSL 的 `openclaw` CLI**（`asyncio.create_subprocess_exec`）。
任何沒有安裝 OpenClaw CLI / 連到 OpenClaw Gateway 的環境（Replit、未配置的 VPS），
**無法執行真實任務**——只能跑「假 OpenClaw」的 smoke、Dashboard UI、與離線測試。

## 4. Replit 評估

| 項目 | 評估 |
|---|---|
| 跑 FastAPI Adapter | △ 可跑 uvicorn，但 Replit 會休眠；穩定常駐需付費 Always-On / Reserved VM |
| 長時間跑 Worker | ✗ 不適合：Replit 單一主程序 + 休眠模型，與「持續輪詢的常駐 worker」衝突，任務會卡住 |
| 保存 SQLite `queue.db` | ✗ 不適合：Replit 檔案系統在 redeploy / 重啟可能不持久，正式 queue 有遺失風險 |
| 放 Dashboard | ✗✗ **不適合公開**：Replit 預設 URL 是公開的，會把**未認證的控制路由**暴露出去（見第 6 節） |
| Secrets | 可用 Replit Secrets 放環境變數，但**只放假 token**；不要放真 `HERMES_ADAPTER_TOKEN` / `HERMES_CALLBACK_SECRET` |
| OpenClaw CLI | ✗ Replit 上沒有 OpenClaw CLI / Gateway，無法跑真實任務 |

**Replit 結論**
- **適合**：展示 Dashboard UI、`from app.main import app` import 測試、用內建假 OpenClaw 跑 smoke、跑離線測試。
- **不適合**：真 Worker 長期任務、保存正式 `queue.db`、接真 token、公開控制台。
- **最低安全做法**：只當 demo/測試；不接真 token、不存正式資料、**若放 Dashboard 必須加認證且不放控制路由**（或乾脆不放 Dashboard，只展示靜態截圖 / 唯讀頁）。

## 5. VPS 評估

| 項目 | 評估 |
|---|---|
| 跑 Adapter + Worker | ✓ 適合：完整控制，可用 systemd 常駐、崩潰自動重啟 |
| 保存 SQLite `queue.db` | ✓ 適合：VPS 磁碟可持久；WAL 適合單寫者；需搭配備份策略 |
| 未來接 OpenClaw CLI / Gateway | ✓ 適合：VPS 可安裝 OpenClaw（與目前 WSL 環境對等），是真實執行能長期落腳的環境 |
| systemd / tmux / docker | 建議 **systemd** 各一個 unit 跑 Adapter 與 Worker（**仍只一個 worker**，不要水平擴充）；docker 可選；tmux 僅臨時用 |
| 風險 | 防火牆、Dashboard 不可裸露、secrets 管理、備份、log rotation、SSH 安全 |

**VPS 結論**
- **適合**：長期私有常駐 Adapter+Worker、私有 Dashboard、未來接 Google Drive/Sheets、Discord/Hermes。
- **不適合**：未做安全強化前直接對公網開 8000 / 開放 Dashboard。
- **最低安全做法**：
  - 防火牆只開 SSH；Adapter 綁 `127.0.0.1` 或內網，**不要**對公網開 8000。
  - Dashboard 走 **SSH tunnel / VPN / 反向代理 + 認證**，永不裸露公開。
  - `.env` 放 root-only（`chmod 600`），**不進 git**；secrets 用環境或 secret manager。
  - 設定 `queue.db` / `data/` 定期備份（rsync / 快照），log rotation。
  - SSH 強化：key-only 登入、禁 root 密碼登入、改 port / fail2ban。

## 6. Dashboard 安全邊界（重要）

**目前 `/dashboard/*` 頁面與表單路由沒有 token 驗證**（為本機單機使用而設計）：
- 唯讀頁：`GET /dashboard`、`/dashboard/tasks`、`/dashboard/tasks/{id}`、`/dashboard/reviews`、`/dashboard/system`
- **控制表單（會改 queue 狀態，且無 `require_token`）**：
  `POST /dashboard/tasks/{id}/approve | reject | cancel | retry | archive | comments`

相對地，JSON API（`/tasks/*`、`/queue/*`、`/system/health`、`/system/worker`）**有** `require_token`
（`X-Adapter-Token`）保護。

→ 結論：**Dashboard 只能本機 / 私有網路使用，絕不可裸露公開**。一旦公開，任何人都能打
`approve / reject / cancel / retry / archive` 改任務狀態。approve/reject/retry/cancel/archive
全是**控制功能**，公開前必須先加登入 / 權限 / 網路層保護。
（本版**不**新增登入系統，只在文件中記錄此邊界。）

## 7. 建議結論

三種方案：

### 方案 A：保持本機（短期主力）
- 用途：開發、測試、安全控制。
- 優點：最安全、不公開 Dashboard、不碰網路暴露。
- 缺點：需手動啟動、不能雲端常駐。

### 方案 B：Replit 輕量展示 / 測試
- 用途：展示 Dashboard UI、Adapter import、假 OpenClaw smoke。
- 限制：不跑真 Worker 長期任務、不存正式 `queue.db`、不接真 token、不公開控制台。

### 方案 C：VPS 私有常駐（未來首選）
- 用途：長期跑 Adapter + Worker、私有 Dashboard、未來接 Drive/Sheets、Discord/Hermes。
- 限制：需安全設定、防火牆、登入 / VPN / tunnel、備份策略。

**整體建議**：
- **短期：本機（A）** 繼續作為主要開發與控制環境。
- **Replit（B）**：只做展示 / 輕量測試，**不放真 token、不存正式資料、不公開控制台**。
- **VPS（C）**：作為未來私有常駐首選。
- **正式公開前必須先做**：登入 / 權限、防火牆、secrets 管理、備份、log rotation、Dashboard 不裸露。

## 8. 下一步

**v0.6.3 Google Drive / Sheets 結果落地評估**。
（部署實作本身留待 owner 決定方案後，再開獨立版本；本版不上線、不公開。）
