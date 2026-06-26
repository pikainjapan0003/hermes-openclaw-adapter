# Hermes x OpenClaw Replit Manual Smoke Test v0.6.5B

## 1. 本版目標

記錄 Owner 在 Replit 網頁端手動完成的 **Replit Safe Sandbox 實測**結果。
本版**只新增測試報告**：不改核心程式、不改 Replit 設定、不新增功能、不接真 OpenClaw、
不接 Google Drive / Sheets。

## 2. 測試前置

- GitHub repo（`pikainjapan0003/hermes-openclaw-adapter`）已從 GitHub 匯入 Replit
- v0.6.4 Dashboard Auth Gate 已完成（`DASHBOARD_AUTH_ENABLED` + `DASHBOARD_TOKEN`）
- v0.6.5 Replit Deployment Test Plan 已完成（`docs/HERMES_OPENCLAW_REPLIT_DEPLOYMENT_TEST_V0_6_5.md`）
- Replit Secrets 已設定
- Published access 設為 **Invite only**

## 3. Replit Secrets 驗證

> 只記錄「有設定 / 設定值類別」，**不列任何真值**（DASHBOARD_TOKEN 等真 secret 不記錄）。

- `DASHBOARD_AUTH_ENABLED=true`
- `DASHBOARD_TOKEN` 已設定（**真值不記錄**）
- `OPENCLAW_CLI_BIN=/nonexistent/openclaw`（假，確保不執行真 OpenClaw）
- `CALLBACK_ENABLED=false`
- `EXECUTION_MODE=queue`

## 4. 測試結果

**/health（免 token 健康檢查）**
- ✅ `/health` 成功
- `app = Hermes OpenClaw Adapter`
- `version = 0.5.6`
- `execution_mode = queue`
- `queue_db_path = data/queue.db`
- `openclaw_cli_bin = /nonexistent/openclaw`
- `callback_enabled = false`

**Dashboard Auth Gate**
- ✅ `/dashboard` 未登入會導向 `/dashboard/login`
- ✅ 使用 `DASHBOARD_TOKEN` 登入後可進 Dashboard
- ✅ `/dashboard/tasks` 可進
- ✅ `/dashboard/reviews` 可進
- ✅ `/dashboard/system` 可進

**狀態顯示（皆為本版預期）**
- Queue counts 全為 `0`（沙盒、無任務）→ 預期
- Worker `unknown`（本版不跑真 Worker）→ 預期
- OpenClaw CLI `missing`（`OPENCLAW_CLI_BIN=/nonexistent/openclaw`）→ 預期

## 5. 安全確認

- Replit access = **Invite only**
- ❌ 沒有 Public
- ❌ 沒有分享網址
- ❌ 沒有接真 OpenClaw
- ❌ 沒有跑真 Worker
- ❌ 沒有處理正式任務
- ❌ 沒有將 token 寫入 repo（DASHBOARD_TOKEN 只在 Replit Secrets）

## 6. 已知限制

- `queue.db` 仍在 Replit filesystem，**不作正式資料來源**（休眠 / 重啟可能消失）。
- Worker 未啟動。
- OpenClaw CLI 未接入。
- Google Drive / Sheets 未接入。
- 目前只適合 **Safe Sandbox**（展示 / 私有測試），非正式生產。

## 7. 結論

**Replit Safe Sandbox 手動測試通過**：可作為低成本雲端測試環境（私有、Auth Gate 保護、假 OpenClaw）。
下一步才是 **v0.6.6 Google Drive / Sheets 結果落地評估**（解決 Replit 資料不持久的問題）。
