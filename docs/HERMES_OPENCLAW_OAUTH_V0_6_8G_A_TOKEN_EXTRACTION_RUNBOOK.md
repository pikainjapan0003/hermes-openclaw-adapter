# Hermes x OpenClaw OAuth — v0.6.8G-A Token Extraction / Replit Secrets Placement Runbook

## 1. 本文件目的

規劃「未來如何安全地把 refresh token 從本機 OAuth consent 取出、放進 Replit Secrets」的
完整流程與守則，作為 v0.6.8G 子階段的唯一事實對照點。
本文件**不含任何 secret / token / credential 真值**，**不含任何 Owner 本機真路徑**。

## 2. v0.6.8G-A 是文件階段，不執行 OAuth

- v0.6.8G-A **只新增文件與 readiness gate**，**不執行 OAuth**、**不跑真 OAuth**。
- 本階段**不翻開 kill-switch**、**不顯示 token**、**不寫 token file**、**不放 Replit Secrets**。
- 本階段不連 Google、不讀 Owner 真 OAuth JSON、不寫 Google Sheets、不進 v0.6.9。

## 3. v0.6.8F 目前狀態摘要

- v0.6.8F helper prepare 已完成並 push；checkpoint 已完成並 push；遠端 master tip：`7708379`；未 tag。
- `LIVE_CONSENT_ENABLED = False` 仍保留（最終 kill-switch）。
- 尚未跑真 OAuth、尚未取得 refresh token、尚未顯示 / 寫入 token、尚未真寫 Google Sheets。
- helper 已具備 guarded scaffolding：`--client-secret-file`、檔案驗證、environment guard、
  token non-disclosure 設計；但真正網路 consent 仍被 kill-switch 擋住。

## 4. v0.6.8G-B 才能翻開 `LIVE_CONSENT_ENABLED`

- 只有 v0.6.8G-B（需 Owner 明確批准）才會把 `LIVE_CONSENT_ENABLED` 由 False 翻開。
- 翻開只在 **Owner 本機**進行，且**不得 commit** 任何真值或被翻開的本機設定。
- v0.6.8G-B 同時需調整兩支斷言 `LIVE_CONSENT_ENABLED = False` 的 readiness。

## 5. v0.6.8G-C 才能由 Owner 本機手動跑 OAuth

- 只有 v0.6.8G-C 才會由 **Owner 本機**手動跑一次 OAuth consent。
- 一律 **local only**：偵測到 Replit / CI 必須拒絕。
- consent 使用 Owner 本機、**repo 外**的 Desktop App client secret（路徑用 placeholder：
  `/path/outside/repo/oauth-client.json`，本文件不寫真路徑）。

## 6. v0.6.8G-D 才能把 refresh token 放入 Replit Secrets

- 只有 v0.6.8G-D 才會把取得的 refresh token **手動**放進 Replit Secrets。
- refresh token **不經 console log、不落 repo / file**；只由 Owner 以最小暴露方式手動貼上。
- 放入後仍**不能立刻真寫 Sheets**（見第 8 節 `GOOGLE_SHEETS_ENABLED` 初期維持 false）。

## 7. refresh token 顯示策略建議（本版不實作，只比較）

### 方案 A：Manual copy once（建議優先）

- v0.6.8G-B 才新增 `--show-refresh-token-once`，且**必須**再加
  `--i-understand-token-will-be-visible`。
- 必須 **local only**（Replit / CI 拒絕）。
- 顯示前 **countdown**；**只顯示一次**；**不寫檔**；**不 log**。
- 顯示後立即提醒 Owner 馬上貼到 Replit Secrets。
- Owner 需自行注意**終端機歷史**與**螢幕截圖**風險。

### 方案 B：Local clipboard（不建議優先）

- 風險：clipboard 可能被其他工具讀到。
- 若採用，必須加強警告並**自動清空 clipboard**。
- **本專案暫不採用。**

### 結論

> v0.6.8G-B 優先採 **方案 A**：show refresh token once with explicit Owner risk acknowledgement。

## 8. Replit Secrets 預計欄位（只列 key 名，不寫真值）

```text
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_OAUTH_REFRESH_TOKEN
GOOGLE_SHEETS_SPREADSHEET_ID
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_WRITE_MODE=pilot
```

- `GOOGLE_SHEETS_ENABLED` 初期仍為 **false**。
- 只有 v0.6.9 pilot 才能開為 true。
- refresh token 放入 Replit Secrets 後，**也不能立刻真寫 Sheets**；需經 v0.6.9 gate。

## 9. token 外洩時 revoke / rotate 流程

1. 立刻停止 Replit app，或關閉相關 result sink。
2. 到 Google Account → Security → Third-party access **撤銷**該授權。
3. 刪除對應的 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN` 等）。
4. 重新產生 token（重跑本機 consent）。
5. 檢查 git history / logs 是否殘留 token。
6. 開一版 incident note 記錄，**不放真 token**。

## 10. v0.6.9 開工 gate

v0.6.9（Google Sheets OAuth Write Pilot）**不得開始**，除非以下全部成立：

- v0.6.8G-B / C / D 全部完成（kill-switch 翻開 → 本機 consent → token 放入 Replit Secrets）。
- Owner 明確說「refresh token 已安全放進 Replit Secrets」。
- Owner 明確說「repo / log / file 沒有 token」。
- Owner 明確批准真 Google Sheets write pilot。
- v0.6.9 仍須先做 single-sheet / single-row / guarded pilot，且不寫 Drive artifacts。

## 11. 絕對不可 commit 的項目

- `.env`、`data/`、`queue.db`、`tasks.jsonl`、`results.jsonl`、`mock_google_sheets_rows.jsonl`。
- 任何 credential JSON / `client_secret*.json` / `token*.json` / `service_account*.json` /
  `my-openclaw*.json`。
- 任何 client_id / client_secret / refresh token / access token 真值。
- 任何 Owner 本機真路徑。

## 12. Owner 操作清單（未來各子階段）

1. （v0.6.8G-B）在本機明確翻開 `LIVE_CONSENT_ENABLED`，不 commit 真值。
2. （v0.6.8G-C）在本機 `pip install google-auth-oauthlib`，跑一次本機 consent。
3. （v0.6.8G-D）用方案 A 顯示一次 refresh token，立即手動貼進 Replit Secrets。
4. 確認 token 不在 repo / log / file；確認 `GOOGLE_SHEETS_ENABLED=false`。
5. 明確回報「token 已就位、repo 乾淨」，再決定是否進 v0.6.9。

## 13. Claude / Codex 不可做的事項

- 不可代 Owner 跑真 OAuth、不可翻開 `LIVE_CONSENT_ENABLED`。
- 不可讀 / 顯示 Owner 真 OAuth JSON、不可顯示 client_id / client_secret。
- 不可顯示 / 寫入任何 refresh token / access token、不可寫 token file。
- 不可寫 Owner 本機真路徑進任何文件。
- 不可在 Replit / CI 跑 live、不可真寫 Google Sheets、不可自行進 v0.6.9。

## 14. 安全檢查命令

```bash
git status --short

grep -R "private_key\|client_email\|client_secret\|refresh_token\|GOOGLE_OAUTH_REFRESH_TOKEN\|GOOGLE_SERVICE_ACCOUNT_JSON\|DASHBOARD_TOKEN" -n \
  docs/HERMES_OPENCLAW_OAUTH_V0_6_8G_A_TOKEN_EXTRACTION_RUNBOOK.md \
  scripts/check_oauth_v0_6_8g_a_runbook_readiness.py || true

git ls-files | grep -E '(^\.env$|^data/|queue\.db|tasks\.jsonl|results\.jsonl|credentials.*\.json|token.*\.json|my-openclaw.*\.json)' || true
```

> 若 grep 只命中 key 名稱、placeholder、說明文字，視為安全；命中真值或真路徑則停止，不要 commit。
