# Hermes x OpenClaw OAuth / Secrets Design v0.6.8

## 1. 本版目標

設計從 **Google Sheets Mock Sink（v0.6.7）** 過渡到**真 Google Sheets 寫入**時，需要的
**OAuth / Secrets 安全策略**。本版**只做設計 + 文件 + readiness 檢查**：
不連真 Google、不跑真 OAuth flow、不新增真 write client、不放任何真 credentials、
不改 Worker / Queue / mock sink 核心。

## 2. 前置狀態

- v0.6.6：評估結論——個人 Gmail 優先 OAuth；SA 無法寫個人 My Drive；長期走 Hybrid。
- v0.6.7：`app/result_sink.py` mock sink（預設關閉、不 import google、worker 終態 emit），
  寫 `data/mock_google_sheets_rows.jsonl`（gitignored）。
- 目前 `requirements.txt` **尚無 google library**（mock-safe）。

## 3. 為什麼需要 OAuth / Secrets Design

從 mock 過渡到真寫入前，**必須先把 token 安全設計清楚**：真寫入需要長期憑證
（OAuth refresh token 或 SA private key），這些一旦外洩等於別人能寫 Owner 的 Google 資料。
所以先設計「憑證放哪、怎麼換、怎麼撤銷、絕不進 git」，再動真寫入。

## 4. 推薦 Owner 個人 Gmail 方案：OAuth 使用者授權

- 代表 **Owner 本人**寫入 Owner 自己指定的 Google Sheet。
- 適合個人 Gmail / 個人 Drive / 個人 Sheets，**不依賴 Workspace Shared Drive**。
- 一次 consent 取得 **refresh token**，之後 server 端用 refresh token 換 access token 寫入。

## 5. OAuth Flow 草案（本版不實作）

1. Owner 在**本機或安全環境**跑一次 OAuth consent（local helper / 一次性腳本）。
2. 取得 **refresh token**（高敏感）。
3. 把 refresh token 放到 **Replit Secrets**（或 VPS secret manager）。
4. Replit app 啟動時用 `client_id` + `client_secret` + `refresh_token` 換 **access token**。
5. access token **只在 runtime 記憶體暫存**（不落地、不進 log）。
6. 用 access token append 一列到指定 Sheet。
7. **任何 token 都不寫入 repo / data / log。**

> v0.6.8 只畫流程；真正的 consent / 換 token / 寫 Sheet 留待 v0.6.9 pilot。

## 6. Scope 候選與最小權限原則

- **append Sheet 為主 → 優先 Sheets scope**（例如 `https://www.googleapis.com/auth/spreadsheets`，
  或更窄的唯該檔案存取）。
- **避免一開始就要完整 Drive 權限。**
- 若未來要 Drive artifact（Hybrid）→ 才考慮 Drive scope，且**優先窄權限**
  （例如 `drive.file`：只能存取 app 自己建立 / 開啟的檔案，而非整個 Drive）。
- **v0.6.8 不決定最終 scope，只列候選**；v0.6.9 pilot 前再確認**最小 scope**。

## 7. Refresh Token 安全規則

- refresh token 是**高敏感長期鑰匙**。
- **只能**放 Replit Secrets / VPS secret manager。
- **不得**放 `.env` 進 git、**不得**輸出到 log、**不得**出現在 docs 範例真值。
- 要有**撤銷**操作：到 Google Account → Security → Third-party access 移除授權，或用 API revoke。
- 若 token 洩漏 → 立即 **revoke + rotate**（重新跑 consent 取得新 token，舊的撤銷）。

## 8. Service Account / Shared Drive 補充

- **個人 Gmail My Drive 不優先用 Service Account**（SA 在個人 My Drive 無儲存配額，無法擁有檔案）。
- SA 適合 **server-to-server / Workspace / Shared Drive**。
- 若用 SA 寫指定 Sheet：**必須先把該 Sheet 分享給 service account email**（編輯權限）。
- 若用 Shared Drive：需要 **Workspace 支援**。
- SA private key JSON 也是**高敏感**，不得 commit。
- **本專案 Owner 目前優先 OAuth。**

## 9. Replit Secrets Inventory

| key | 用途 | 敏感等級 |
|---|---|---|
| `RESULT_SINK_ENABLED` / `RESULT_SINK_TYPE` / `RESULT_SINK_MODE` | sink 開關 / 型別 / 模式 | 非敏感（仍建議放 Secrets 統一管理） |
| `GOOGLE_AUTH_MODE` | `none` / `oauth` / `service_account` | 非敏感 |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | 目標試算表 ID | 低敏感（建議 Secrets） |
| `GOOGLE_SHEETS_WORKSHEET_NAME` | 工作表名（預設 `tasks`） | 非敏感 |
| `GOOGLE_DRIVE_FOLDER_ID` | artifact 資料夾 ID | 低敏感 |
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth client id | 可公開但**不建議硬編** → Secrets |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth client secret | **高敏感 → Secrets、不進 git** |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | OAuth refresh token | **最高敏感 → Secrets、不進 git** |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | SA 金鑰 JSON（inline） | **最高敏感 → Secrets、不進 git** |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | SA 金鑰檔路徑 | 檔案本身 gitignore，不進 git |

## 10. .env.example Placeholder

`.env.example` 只放上述 key 名的**空值 / `none` / 預設**（例如 `GOOGLE_AUTH_MODE=none`、
`GOOGLE_SHEETS_WORKSHEET_NAME=tasks`，其餘留空）。**不填任何真值、不新增 credentials 檔案。**
真值一律放 Replit Secrets。

## 11. Readiness 檢查

- `scripts/check_google_sink_readiness.py`：已擴充——檢查 result_sink 仍不 import google、
  `.env.example` 含 OAuth placeholder key、v0.6.8 文件存在、credential/token/mock-log 未 tracked。
- `scripts/check_oauth_secrets_design.py`（v0.6.8 新增）：靜態檢查——credential/token 未 tracked、
  `.env.example` 含必要 OAuth key 且**高敏感 key 為空值**、result_sink 不 import google、
  v0.6.8 文件存在、requirements google 現況（只回報）。**不讀 .env、不印 secret。**

## 12. 不做事項

- 不連真 Google、不跑真 OAuth consent flow、不寫真 Sheet。
- 不新增真 Google write client、不安裝 google library。
- 不放 / 不輸出任何 credentials / token / client secret / SA private key。
- 不改 Worker / Queue / mock sink 核心；mock sink 維持預設關閉。

## 13. 下一步

**v0.6.9 Google Sheets OAuth Write Pilot**（或先做 OAuth local helper draft：一次性 consent
取得 refresh token 的安全腳本）。pilot 前先：確認最小 scope、建立 OAuth client、在安全環境跑
consent、把 refresh token 放 Replit Secrets，再小規模真寫入試行。
