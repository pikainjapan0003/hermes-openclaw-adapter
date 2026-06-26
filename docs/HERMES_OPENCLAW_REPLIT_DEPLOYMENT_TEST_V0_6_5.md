# Hermes x OpenClaw Replit Deployment Test v0.6.5

## 1. 本版目標

準備並驗證 Adapter 可從 GitHub 匯入 Replit，使用 **Replit Secrets** 開啟 Dashboard Auth Gate，
以「**假 OpenClaw / 安全沙盒**」完成基本部署測試。**本版不是正式上線**：不接真 OpenClaw、
不跑正式 Worker、不處理正式任務、不放真 token 到 repo。

## 2. 前置版本

- v0.6.0B GitHub Remote Backup、v0.6.1 Restore/Clone Test、v0.6.2 Deployment Assessment、
  v0.6.3 Replit Safe Sandbox Plan、**v0.6.4 Dashboard Auth Gate**（關鍵前置：`DASHBOARD_AUTH_ENABLED=true`
  即可保護所有 `/dashboard/*`，包含 approve/reject/cancel/retry/archive/comments 控制表單）。

## 3. Replit 匯入方式

Replit → Create App → **Import from GitHub** → 選 `pikainjapan0003/hermes-openclaw-adapter`。
匯入後 Replit 會讀到 repo 內既有的 `.replit`（已含 run command）。`.env` **不在 repo**（gitignored），
所以匯入後不會帶任何 secret，需在 Replit Secrets 自行設定（見第 5 節）。

## 4. Replit Access 建議

**Only you** 或 **Workspace only**，**不要 Public**。
原因：即使開了 Auth Gate，沙盒階段也沒必要對全世界開放；Published App 一旦 Public，
等於把登入頁暴露在公網，徒增暴力嘗試風險。沙盒測試用私有 access 最安全。

## 5. Replit Secrets 清單（只列 key 名，不放真值）

| 分類 | key | 沙盒建議值 |
|---|---|---|
| **v0.6.5 必要** | `DASHBOARD_AUTH_ENABLED` | `true`（Replit 必須開） |
| **v0.6.5 必要** | `DASHBOARD_TOKEN` | 一段隨機字串（只放 Replit Secrets，**不進 git**） |
| **可用 placeholder / 假值** | `EXECUTION_MODE` | `queue` |
| | `OPENCLAW_CLI_BIN` | `/nonexistent/openclaw`（**假**，確保不執行真 OpenClaw） |
| | `CALLBACK_ENABLED` | `false` |
| | `HERMES_ADAPTER_TOKEN` | 沙盒可留空或 dummy（API 才需要） |
| | `DATA_DIR` / `QUEUE_DB_PATH` | 預設即可（沙盒資料視為可丟） |
| **暫時不要在 Replit 放的高風險** | 真 `HERMES_ADAPTER_TOKEN`、真 `OPENCLAW_CLI_BIN`（指向真 openclaw）、真 `HERMES_CALLBACK_URL` / `HERMES_CALLBACK_SECRET` | 沙盒階段一律不放真值 |
| **未來才需要（Drive/Sheets，v0.6.6）** | 例如 Google service account JSON / OAuth client / sheet id | v0.6.5 不需要 |

原則：`.env` 永不 commit；Replit 用 Secrets；沙盒一律假值；token 不寫進任何 docs / .replit。

## 6. Run Command

repo 已含 `.replit`（**已 tracked，本版未修改**）：

```toml
run = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
[nix]
channel = "stable-24_05"
[deployment]
run = ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

- 沙盒 Run（webview）用 port 8000 即可。
- 若 Replit 的 Autoscale / Reserved VM 部署要求綁定 `$PORT`，可把 run 改為
  `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`（app 本身不讀 PORT，由 uvicorn 處理，兩種都相容）。
  本版**不改 `.replit`**，僅在此記錄此選項，等實際部署需要時再由 owner 調整。

## 7. 本版測試範圍

- `app.main` import OK。
- Dashboard Auth Gate：`DASHBOARD_AUTH_ENABLED=true` 時未登入被擋、登入後可進、控制 POST 被 gate 保護。
- `GET /health`（免 token、可當 Replit 健康檢查）。
- 假 OpenClaw smoke（`scripts/smoke_test_queue.sh`，內建 fake CLI，**不接真 OpenClaw**）。
- 既有離線測試。
- `scripts/check_replit_readiness.py`（readiness 檢查，不輸出 secret 值）。

## 8. 本版不做事項

不接真 OpenClaw、不跑正式 Worker、不放真 token、不處理正式任務、不接 Google Drive/Sheets、
不改 Queue 狀態機 / Worker 核心 / Hermes / MCP / Discord、不設 Public access。

## 9. Owner 需要在 Replit 網頁端手動做的事

1. 在 Replit **Create App → Import from GitHub** 匯入 `pikainjapan0003/hermes-openclaw-adapter`。
2. 到 **Secrets（🔒 Tools → Secrets）** 設定：`DASHBOARD_AUTH_ENABLED=true`、`DASHBOARD_TOKEN=<自取隨機字串>`，
   並依第 5 節補上沙盒假值（`OPENCLAW_CLI_BIN=/nonexistent/openclaw`、`CALLBACK_ENABLED=false` 等）。
3. 設定 App / Published access 為 **Only you** 或 **Workspace only**（不要 Public）。
4. 確認 Run command（已在 `.replit`；如需 `$PORT` 再依第 6 節調整）。
5. 按 **Run** 啟動，開 webview。
6. 測試 `/health` 回 `{"ok": true, ...}`；測試 `/dashboard` → 應被導到 `/dashboard/login`；
   用 `DASHBOARD_TOKEN` 登入後可進 Dashboard。
7. （可選）在 Replit Shell 跑 `python scripts/check_replit_readiness.py` 與離線測試。

> ⚠️ 這些是 Replit 帳號內的網頁操作，需 owner 親自完成；我無法代為登入 Replit 或設定 Secrets。

## 10. 測試清單

**本機（已可由我執行）**
- [ ] `python scripts/test_queue_store.py`
- [ ] `python scripts/test_system_health.py`
- [ ] `python scripts/test_dashboard_polish.py`
- [ ] `python scripts/test_dashboard_auth_gate.py`
- [ ] `python scripts/check_replit_readiness.py`
- [ ] `from app.main import app` import OK
- [ ] `bash scripts/smoke_test_queue.sh`（fake OpenClaw）

**Replit 上（owner 手動）**
- [ ] 匯入成功、Run 起得來
- [ ] `/health` 200
- [ ] 未登入 `/dashboard` → 導到 login
- [ ] 用 token 登入後 Dashboard 可進
- [ ] access = Only you / Workspace only

## 11. 風險與限制

- Replit filesystem **不可作正式資料來源**；`queue.db` / `*.jsonl` 在休眠 / 重啟可能消失 → 沙盒視為可丟。
- Worker **暫不正式常駐**（v0.6.5 只跑 Adapter / Dashboard / 假 smoke）。
- 真 OpenClaw / 真 Worker / 真 token 需另版（非沙盒）驗證。
- Auth Gate 是單 token 最小保護，非多使用者登入系統；token 外洩等於全開，請放 Secrets 並定期更換。

## 12. 下一步

**v0.6.6 Google Drive / Sheets 結果落地評估**（外部持久化，解決 Replit 資料不持久的問題）。
