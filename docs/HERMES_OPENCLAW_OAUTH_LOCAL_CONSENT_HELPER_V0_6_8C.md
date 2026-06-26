# Hermes x OpenClaw OAuth Local Consent Helper v0.6.8C

## 1. 本版目標

把 OAuth helper 從 **草案（v0.6.8B）** 升級為 **本機可用的 consent helper 程式結構**，
但本版**仍不執行真 OAuth**：不連真 Google、不取得真 refresh token、不寫 / 不印任何 token。

本版交付：`scripts/oauth_local_consent_helper.py`（live 結構就緒但封住）、
`scripts/check_oauth_local_consent_helper_readiness.py`、本文件。

## 2. 前置狀態

- v0.6.8：OAuth / Secrets 設計完成（個人 Gmail 優先 OAuth；refresh token 只放 Replit Secrets）。
- v0.6.8B：`scripts/oauth_local_helper_draft.py` 草案（預設 dry-run、`--live` 直接拒絕）。
- `requirements.txt` **尚無 google library**（mock-safe），本版**不新增**。
- `.env.example` 已有 OAuth / Sheets placeholder key（高敏感 key 為空值）。

## 3. Helper 使用模式

```bash
python scripts/oauth_local_consent_helper.py                       # 預設 dry-run（exit 0）
python scripts/oauth_local_consent_helper.py --dry-run             # 同上（exit 0）
python scripts/oauth_local_consent_helper.py --explain             # dry-run + 流程/安全說明（exit 0）
python scripts/oauth_local_consent_helper.py --live                # 拒絕：缺安全旗標（exit 2）
python scripts/oauth_local_consent_helper.py --live --i-understand-local-only  # 進 live 分支
```

- **dry-run / explain**：只印未來流程、需要的環境變數 key 名、安全規則；不讀 credentials、不連 Google。
- **`--live` 無 `--i-understand-local-only`**：明確拒絕，exit 2。
- **`--live --i-understand-local-only`（本版）**：先偵測 Replit / CI（命中即拒絕 exit 2），
  再因 `LIVE_CONSENT_ENABLED = False` 印「結構就緒但本版停用」後 exit 3。**本版不連 Google。**

## 4. 為什麼只能本機跑

- OAuth consent 會短暫接觸 **client secret**，並產出長期 **refresh token**。
- Replit / production 屬公開或共享執行環境，**不應**在其上跑 consent、**不應**保存 client secret /
  token 檔案。
- 因此 consent 只能在 **Owner 自己受控的本機**完成；helper 會偵測 `REPL_ID` / `REPLIT_DB_URL` /
  `CI` 等環境變數，命中即拒絕。

## 5. Live guard 設計

- `--live` 必須搭配 `--i-understand-local-only`，否則 exit 2。
- live 分支第一步偵測「非本機」環境（Replit / CI）→ 命中即 exit 2。
- 模組層常數 `LIVE_CONSENT_ENABLED = False`（本版）：真正 consent / 換 token 一律停用，exit 3。
- 真執行的程式結構（延遲 import `google-auth-oauthlib`、`InstalledAppFlow.run_local_server`）
  已寫在 live 函式內，但本版因旗標為 False **不可達**；未來啟用只能由 Owner 在本機手動開啟。
- **本版測試不執行 `--live --i-understand-local-only` 的真 consent。**

## 6. Token 安全規則

- refresh token：**不印 console、不寫檔、不進 repo**。
- 本版**不產生任何 token 檔案**（無 `token.json` / `credentials.json` 寫入）。
- 未來 live 真執行取得 token 後，Owner 必須**手動**把它放進 Replit Secrets：
  `GOOGLE_OAUTH_REFRESH_TOKEN`。helper 不替 Owner 自動搬運 token。
- client secret 只放 Replit Secrets / 本機安全處，**不進 git、不輸出**。

## 7. Dependency 策略

- 本版**不新增** google library 到 `requirements.txt`。
- helper 在 dry-run **不 import** google；google library 只在 live 真執行路徑做**延遲 import**。
- 未來 Owner 本機要跑真 consent 時，再自行安裝 `google-auth-oauthlib`（本機，不入 repo）。
- 若日後判斷必須把 google library 加入 `requirements.txt`，需 **Owner 另行批准**後才改。

## 8. Replit Secrets 對應

| key | 用途 | 敏感等級 |
|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth client id | 可公開但建議 Secrets |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth client secret | **高敏感 → Secrets、不進 git** |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | consent 產出的 refresh token | **最高敏感 → Secrets、不進 git** |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | 目標試算表 ID | 低敏感（建議 Secrets） |

## 9. 不做事項

- 不連真 Google、不跑真 OAuth consent、不換 token、不寫 Google Sheets。
- 不取得 / 不輸出 / 不寫入任何 refresh token 或 access token。
- 不新增 google library 到 requirements（未經 Owner 批准）。
- 不讀 `.env` 真值、不輸出 client secret / token。
- 不改 Worker / Queue / `app/result_sink.py` / `app/main.py`。

## 10. 下一步

由 **Owner 本機**決定是否真正啟用 live helper（把 `LIVE_CONSENT_ENABLED` 開啟、在本機安裝
`google-auth-oauthlib`、跑一次 consent）。完成並確認 refresh token 已安全放入 Replit Secrets、
**不在 repo / log / file** 之後，才評估進入 **v0.6.9 Google Sheets OAuth Write Pilot**。
