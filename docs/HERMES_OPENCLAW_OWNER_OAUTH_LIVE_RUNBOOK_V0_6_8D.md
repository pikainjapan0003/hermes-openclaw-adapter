# Hermes x OpenClaw Owner OAuth Live Runbook v0.6.8D

## 1. 本版目標

本版**只建立 Owner OAuth Live Runbook**（操作手冊 + checklist + 靜態 readiness）。
**不執行真 OAuth、不連真 Google、不取得 refresh token、不真寫 Google Sheets、不改 helper live flag。**
這份文件是給 **Owner 本人**看的：未來要在自己本機安全地跑一次 OAuth consent、取得 refresh token、
手動放進 Replit Secrets，並確認 token 沒有進 repo / log / file。

## 2. 前置狀態

- v0.6.8 OAuth / Secrets Design 已完成（個人 Gmail 優先 OAuth；refresh token 只放 Replit Secrets）。
- v0.6.8B OAuth Local Helper Draft 已完成（草案、預設 dry-run、`--live` 直接拒絕）。
- v0.6.8C OAuth Local Consent Helper 已完成（本機 helper 結構，live 分支已寫但封住）。
- helper live 結構**已存在但封住**：`LIVE_CONSENT_ENABLED = False`。
- **尚未取得 refresh token。**
- **尚未真寫 Google Sheets。**
- `requirements.txt` 尚無 google library（mock-safe）。

## 3. Owner 需要理解的概念（白話）

- **Google OAuth** = 讓 Owner「授權」這支程式，可以用 Owner 的身分操作 Google Sheets。
- **refresh token** = 長期鑰匙。拿到它，程式日後可長期換短期鑰匙，不用每次重新登入。**最高敏感。**
- **access token** = 短期鑰匙。用 refresh token 換來，幾十分鐘就過期，只放在執行時記憶體。
- **Replit Secrets** = 放鑰匙的保險箱。真值放這裡，不會進 git。
- **GitHub / repo** = 公開倉庫，**絕對不能**放任何鑰匙（client secret / refresh token）。

## 4. 絕對不能做的事

- **不**把 refresh token 貼給 Claude / ChatGPT / Discord / Slack 或任何 AI / 聊天工具。
- **不**截圖 token。
- **不**把 token 寫進 `.env` 之後 commit。
- **不**把 `client_secret*.json` commit。
- **不**把 `token*.json` commit。
- **不**在 Replit 跑 OAuth live consent。
- **不**把 token 印到 log / console。
- **不**分享 Replit Secrets 畫面中可見的真值（截圖 / 投影 / 錄影都不行）。

## 5. v0.6.9 前置條件總表

> 注意：本節版本號一律寫成完整的 **v0.6.9**，不可簡寫或漏掉中間的 `.6`。

進入 **v0.6.9 Google Sheets OAuth Write Pilot** 前，Owner 必須**全部**完成：

1. Owner 在本機準備 OAuth client（Google Cloud Console，Desktop App）。
2. Owner 確認 helper live branch 安全（已偵測 Replit / CI、不印 token、不寫 token 檔）。
3. Owner 在本機安裝 `google-auth-oauthlib`（只在本機，不入 repo / requirements）。
4. Owner 在本機**明確**啟用 `LIVE_CONSENT_ENABLED`（只在本機改，不 commit）。
5. Owner 在本機跑 live consent。
6. Owner 取得 refresh token。
7. Owner 手動把 refresh token 放入 Replit Secrets：`GOOGLE_OAUTH_REFRESH_TOKEN`。
8. Owner 確認 token 沒有出現在 repo / log / file。
9. Owner 確認 Replit Secrets 有必要 key。
10. Owner 再明確批准 v0.6.9。

## 6. Google Cloud / OAuth Client 準備清單（只寫概念，不放真值）

- 建立或選擇一個 Google Cloud project。
- 啟用 **Google Sheets API**。
- 設定 **OAuth consent screen**（個人 Gmail；測試 / 內部使用即可）。
- 建立 **Desktop App** 類型的 OAuth client。
- 把 `client_secret` JSON 下載到 **Owner 本機安全位置**。
- **不要**放進 repo。
- **不要**放進 Replit（client secret 改用 Replit Secrets 的環境變數值，不放整個 JSON 檔進 repo）。
- **不要**貼給任何 AI。
- 用完後妥善保存或刪除本機 JSON。

## 7. 本機執行 live helper 的未來流程（本版不執行）

> 以下指令**只有 Owner 本機、未來版本**才可執行；本版 / Replit / CI 一律不可執行。

```bash
# 僅 Owner 本機，未來版本才可做
pip install google-auth-oauthlib
python scripts/oauth_local_consent_helper.py --live --i-understand-local-only
```

強調：

- 本版**不得**執行上述 `--live --i-understand-local-only` 真 consent。
- **Replit 不得**執行。
- **CI 不得**執行。
- 只有 **Owner 本機**可執行。
- token **不可**印出。
- token **不可**寫入 repo。

## 8. Replit Secrets 設定清單（只列 key 名，不放真值）

- `RESULT_SINK_ENABLED`
- `RESULT_SINK_TYPE`
- `RESULT_SINK_MODE`
- `GOOGLE_AUTH_MODE`
- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_SHEETS_WORKSHEET_NAME`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REFRESH_TOKEN`

敏感度標示：

- `GOOGLE_OAUTH_CLIENT_SECRET` = **高敏感**。
- `GOOGLE_OAUTH_REFRESH_TOKEN` = **最高敏感**。
- `GOOGLE_SHEETS_SPREADSHEET_ID` = 非密碼，但**不建議硬編**進 repo。
- **任何真值都不得進 git。**

## 9. Token 就位後的驗證清單

Owner 把 token 放入 Replit Secrets 後，逐項檢查：

- GitHub repo **無** token。
- local repo **無** token 檔。
- terminal history **沒有** token。
- Claude / ChatGPT 對話**沒有** token。
- 截圖**沒有** token。
- Replit App 仍為 **Invite only**。
- Dashboard 仍需要 **login**（Auth Gate 開著）。
- result sink 仍**預設 disabled**，除非 Owner 明確打開 pilot。

## 10. Revoke / Rotate 緊急處理

若懷疑 token 外洩：

1. 立刻停止 Replit app，或關閉相關 result sink。
2. 到 Google Account → Security → Third-party access **撤銷**該授權。
3. 刪除對應的 Replit Secret。
4. 重新產生 token（重跑本機 consent）。
5. 檢查 git history / logs 是否殘留 token。
6. 開一版 incident note 記錄處理，**不放真 token**。

## 11. v0.6.9 開工前 Gate

v0.6.9 只能在以下條件**全部**成立後開始：

- Owner 明確說「refresh token 已安全放進 Replit Secrets」。
- Owner 明確說「repo / log / file 沒有 token」。
- Owner 明確批准真 Google Sheets write pilot。
- v0.6.9 仍必須先做 **single-sheet / single-row / guarded** pilot。
- 仍**不得**寫 Drive artifacts。

## 12. 本版不做事項

- 不連真 Google。
- 不跑 OAuth。
- 不取得 refresh token。
- 不改 helper live flag（`LIVE_CONSENT_ENABLED` 維持 False）。
- 不寫 Google Sheets。
- 不改 Worker / Queue / result_sink。
- 不改 requirements。

## 13. 結論

本版是 **Owner 操作手冊**，讓下一步 live OAuth 可以**安全、可控、可撤銷**。
真正的 live consent 與 token 取得，全部交由 Owner 在本機按本 runbook 執行；
完成並通過第 9 / 11 節檢查後，才進入 v0.6.9。
