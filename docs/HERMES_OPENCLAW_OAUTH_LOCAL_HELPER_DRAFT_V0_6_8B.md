# Hermes x OpenClaw OAuth Local Helper Draft v0.6.8B

## 1. 本版目標

在 **OAuth / Secrets Design（v0.6.8）** 與 **真寫入 Pilot（v0.6.9）** 之間，補上一個缺口：
Owner 要怎麼**安全地、在本機**跑一次 OAuth consent，取得 **refresh token**，再放進 Replit Secrets。

本版**只做 helper 草案 + 文件 + readiness 檢查**：
不連真 Google、不開 browser、不跑真 OAuth consent、不產生 / 不輸出 / 不寫入任何 token、
不新增真 Google client、不改 Worker / Queue / result_sink 核心。

## 2. 前置狀態

- v0.6.7：`app/result_sink.py` mock sink（預設關閉、不 import google、worker 終態 emit）。
- v0.6.8：OAuth / Secrets 設計完成——個人 Gmail 優先 OAuth；refresh token 只放 Replit Secrets；
  高敏感 key 不進 git；SA 不優先寫個人 My Drive。
- 目前 `requirements.txt` **尚無 google library**（mock-safe）。
- `.env.example` 已有 OAuth / Sheets placeholder key（高敏感 key 為空值）。

## 3. 為什麼需要 Local Helper

- 真寫入（v0.6.9）需要一個長期 **refresh token**。
- refresh token 只能透過一次 **OAuth consent** 取得，而 consent 過程會短暫接觸 **client secret**。
- 這個敏感過程**不可**在 Replit / 公開環境裸跑，也**不可**讓 token 落到 repo / log。
- 因此需要一個**只在 Owner 本機執行一次**的 helper：產出 refresh token → 人工貼進 Replit Secrets →
  之後 server 端只用 `client_id + client_secret + refresh_token` 換 access token，**不再跑 consent**。

## 4. Helper 安全設計原則

1. **預設 dry-run**：直接跑只會印出「未來流程、需要的參數 key 名、安全檢查清單」，不做任何真事。
2. **不在 repo 內跑真 OAuth**：v0.6.8B 的 `scripts/oauth_local_helper_draft.py` 是**草案**，
   即使帶 `--live` 也會**明確拒絕**並 exit 非 0（真實作留待 v0.6.9，且只在本機）。
3. **不 import 任何 google library**：草案不依賴 google-auth / googleapiclient / gspread。
4. **不讀 `.env` 真值**：草案不載入 `.env`，不存取任何真 client secret / token。
5. **不開 browser**：草案不呼叫 `webbrowser.open`，不啟動 local redirect server。
6. **不印 token、不寫 token 檔**：草案不輸出任何 token 值，不建立 `token*.json`。
7. **最小 scope**：未來真實作優先 `spreadsheets`（或更窄），避免一開始要完整 Drive 權限。

## 5. 未來真實作的 OAuth 流程（本版只描述，不執行）

> 以下為 **v0.6.9 真實作**時，helper 在 **Owner 本機**該做的事；v0.6.8B 一律不執行。

1. Owner 在 Google Cloud Console 建立 **OAuth 2.0 Client ID**（Desktop app 類型）。
2. 把 `client_id` / `client_secret` 放在**本機環境變數或本機檔案**（不進 repo）。
3. 在本機跑 helper（live 模式）：
   - 以 **Installed App / Loopback** 流程啟動，開啟瀏覽器到 Google consent 頁。
   - Owner 登入並同意**最小 scope**（優先 `https://www.googleapis.com/auth/spreadsheets`）。
   - helper 收到 authorization code，向 token endpoint 換 **refresh token + access token**。
4. helper **只把 refresh token 顯示給 Owner**（或寫到本機受保護路徑），**絕不寫進 repo**。
5. Owner 手動把 refresh token 貼進 **Replit Secrets**（`GOOGLE_OAUTH_REFRESH_TOKEN`）。
6. 本機刪除暫存 token；client secret 仍只放 Replit Secrets / 本機安全處。
7. server 端（Replit）日後啟動時只用 `client_id + client_secret + refresh_token` 換 access token。

## 6. 未來真實作需要的參數（key 名，非真值）

| 參數 | 來源 | 敏感等級 | 備註 |
|---|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | Google Cloud Console | 可公開但建議 Secrets | Desktop app client |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google Cloud Console | **高敏感** | 僅本機 consent 時用 |
| OAuth scope | helper 參數 | 非敏感 | 優先 `spreadsheets`，最小化 |
| redirect / loopback port | helper 參數 | 非敏感 | Installed App loopback |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | consent 產出 | **最高敏感** | 產出後貼 Replit Secrets |

> 真值一律**不**放 repo / `.env` / docs；高敏感者**只**放 Replit Secrets 或本機安全處。

## 7. Helper 草案行為（`scripts/oauth_local_helper_draft.py`）

- **預設（無參數）**：dry-run，印出第 5 / 6 節流程與參數 key 名、以及安全自我檢查結果，exit 0。
- **`--explain`**：等同 dry-run，額外列出未來真實作的步驟清單。
- **`--live`**：**明確拒絕**，印出「v0.6.8B 為草案，不在 repo 內跑真 OAuth」，exit 非 0。
- 全程：不 import google、不讀 `.env`、不開 browser、不連網路、不印 / 不寫任何 token。

## 8. Readiness 檢查（`scripts/check_oauth_local_helper_readiness.py`）

靜態檢查（不連 Google、不讀 `.env`、不印 secret）：

1. helper 草案存在，且**預設 dry-run**（原始碼可見 dry-run 預設、`--live` 會拒絕）。
2. helper **不 import** 任何 google client library。
3. helper **不呼叫** `webbrowser.open`（不開瀏覽器）。
4. helper 原始碼**無真 client secret / refresh token**樣式（無硬編憑證）。
5. **無 token 檔被 git tracked**（`*token*.json` 等）。
6. `.env.example` 高敏感 key（client secret / refresh token / SA JSON）仍為**空值**。
7. `app/result_sink.py` 仍**不 import google**（維持 mock-safe）。
8. `requirements.txt` 是否新增 google library（**只回報**，不阻擋）。
9. v0.6.8B 文件存在。

## 9. 不做事項

- 不連真 Google、不開 browser、不跑真 OAuth consent、不換 token。
- 不產生 / 不輸出 / 不寫入任何 refresh token 或 access token。
- 不新增真 Google client、不安裝 google library。
- 不放 / 不讀 / 不印任何 client secret / token / SA private key。
- 不讀 `.env` 真值。
- 不改 Worker / Queue / result_sink 核心；mock sink 維持預設關閉。

## 10. 下一步

**v0.6.9 Google Sheets OAuth Write Pilot**。進入 pilot 前先：
1. 確認**最小 scope**（優先 `spreadsheets`）。
2. 在 Google Cloud Console 建 OAuth client。
3. 在 **Owner 本機**把本草案升級為真 helper（live 模式），跑一次 consent 取得 refresh token。
4. 把 refresh token 放 **Replit Secrets**，本機刪除暫存。
5. 再小規模真寫入試行（仍預設關閉、可隨時 disable）。
