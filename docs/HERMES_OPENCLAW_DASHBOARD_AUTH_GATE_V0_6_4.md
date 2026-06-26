# Hermes x OpenClaw Dashboard Auth Gate v0.6.4

## 1. 本版目標

為所有 Dashboard 頁面與控制表單加上**最小認證關卡**，作為把 Dashboard 放上 Replit
（公開 URL）之前的安全前置。本版只加閘門，**不改任務狀態機 / Worker / OpenClaw / Hermes / MCP**。

## 2. 為什麼需要 Auth Gate

Dashboard 的控制表單（`approve` / `reject` / `cancel` / `retry` / `archive` / `comments`）
會**改 queue 任務狀態**，且 v0.6.3 實測這些 `/dashboard/*` 路由**原本完全沒有 token 驗證**
（只有 JSON `/tasks`、`/queue`、`/system/*` 有 `X-Adapter-Token`）。一旦放上 Replit 公開 URL，
任何人都能操控任務佇列。因此公開前必須先擋住 Dashboard。

## 3. 新增環境變數

| 變數 | 預設 | 說明 |
|---|---|---|
| `DASHBOARD_AUTH_ENABLED` | `false` | 是否啟用 Dashboard 認證。本機可 `false`；公開環境必須 `true`。 |
| `DASHBOARD_TOKEN` | （空） | Dashboard 登入用 token。放 Replit Secrets，**不進 git、不寫死、不記 log、docs 不放真值**。 |

- `DASHBOARD_AUTH_ENABLED=false`：完全維持 v0.6.3 舊行為（Dashboard 直接可進、不需登入）。
- `DASHBOARD_AUTH_ENABLED=true` 但 `DASHBOARD_TOKEN` 為空：**fail-closed**（一律擋下），
  避免「以為有保護、其實沒設 token」。

## 4. 保護範圍

由一個 HTTP middleware 集中保護**所有以 `/dashboard` 開頭**的路由（唯一豁免：`/dashboard/login`、
`/dashboard/logout`）：

- 頁面：`/dashboard`、`/dashboard/tasks`、`/dashboard/tasks/{task_id}`、`/dashboard/reviews`、`/dashboard/system`
- 控制表單：`/dashboard/tasks/{task_id}/approve | reject | cancel | retry | archive | comments`

行為（auth 開啟且未通過時）：
- **GET** → `303` redirect 到 `/dashboard/login`
- **POST**（控制表單）→ `401 {"detail": "Dashboard auth required"}`（任務狀態不被改動）

**未更動**：JSON API（`/tasks`、`/queue`、`/system/health`、`/system/worker`）原有的
`X-Adapter-Token` 保護、`/health` 公開性、Queue 狀態轉換規則、Worker heartbeat、OpenClaw CLI 路徑檢查。

### 認證方式（最小）
登入後設一個 **httpOnly cookie**（`dashboard_auth`）；middleware 也接受
`X-Dashboard-Token` header 或 `?dashboard_token=` query 作為替代。token 比對用
`hmac.compare_digest`（避免時序側信道），token 不寫進 log。

登入流程：
- `GET /dashboard/login`：顯示簡單登入頁（auth 關閉時直接 redirect 回 `/dashboard`）。
- `POST /dashboard/login`：驗證 `DASHBOARD_TOKEN` 正確 → 設 httpOnly cookie → redirect `/dashboard`；錯誤 → 回登入頁帶 `?error=1`。
- `GET /dashboard/logout`：清除 cookie → redirect 登入頁。

## 5. 本機與 Replit 設定

- **本機開發**：`DASHBOARD_AUTH_ENABLED=false`（方便，不需登入）。
- **Replit / 任何公開環境**：`DASHBOARD_AUTH_ENABLED=true` + `DASHBOARD_TOKEN=<放 Replit Secrets>`。
- `.env` 永不 commit；`.env.example` 只有 placeholder（`replace-with-dashboard-token`）。

## 6. 測試結果

新增 `scripts/test_dashboard_auth_gate.py`，三情境全數通過：

1. **auth=false**：`/dashboard`、`/dashboard/tasks`、`/dashboard/system` 皆 200；控制 `cancel` 可用（303 + cancelled）；`/dashboard/login` 直接 redirect 回 dashboard。→ 舊行為不變。
2. **auth=true 無憑證**：5 個 GET 頁面全 `303 → /dashboard/login`；6 個控制 POST 全 `401`；被擋的 POST 沒改任務狀態；錯誤 header token 仍被擋；`/dashboard/login` 豁免可開（200）。
3. **auth=true + 正確 token**：header token 直接 200；登入設 cookie 後頁面 200；控制 `cancel` 通過 gate 且 `queued→cancelled`；`running` 仍被狀態機擋（維持 running，**gate 沒破壞既有規則**）；logout 後又被擋。

既有測試全部仍通過（auth 預設 false）：test_queue_store / test_dashboard_readonly /
test_blackboard_comments / test_approval_flow / test_limited_control_actions /
test_system_health / test_dashboard_polish + `import app.main` + smoke（PONG）。

## 7. 安全邊界

- 這是**最小單 token gate**，**不是**完整多使用者登入系統（無帳號、無角色、無密碼雜湊存儲）。
- token 是單一共享密鑰；外洩等於全開，請只放 Replit Secrets 並定期更換。
- gate 只擋「誰能開 Dashboard」；**不改變**任務狀態機 / approve/reject/cancel/retry/archive 的既有規則。
- 仍建議搭配網路層保護（私有 Repl、必要時再加反向代理 / IP 限制）。

## 8. 下一步

**v0.6.5 Replit Deployment Test**（私有 Repl、`DASHBOARD_AUTH_ENABLED=true`、假 OpenClaw、不跑真 Worker）。
