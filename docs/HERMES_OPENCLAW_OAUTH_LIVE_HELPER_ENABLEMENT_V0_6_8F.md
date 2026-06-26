# Hermes x OpenClaw OAuth Live Helper — Guarded Prepare (v0.6.8F)

> 命名澄清：本版是 **prepare only**，不是「真正 enable live」。
> v0.6.8F 完成 **guarded live helper scaffolding**，但**不會真正啟動 Google OAuth flow**。
> 真正打開 live consent（翻開 kill-switch、跑本機 consent、處理 token extraction）
> 放到 **v0.6.8G**，且需 **Owner 明確批准**。

## 1. 本版目標

把 OAuth local consent helper 從「live 結構存在但封住」**補齊 guarded live scaffolding**：
新增 `--client-secret-file`、client secret 檔安全驗證、token 不揭露（non-disclosure）設計、
environment guard（Replit / CI 拒絕）、google library 延遲 import。

本版**只做 prepare，不跑真 OAuth**：

- 預設仍 dry-run。
- 不在 Replit / CI 執行 live。
- 不顯示 refresh token / access token。
- 不寫 token file。
- 不真寫 Google Sheets。
- **本版仍保留 `LIVE_CONSENT_ENABLED = False` kill-switch**；即使帶齊旗標與合法 client secret，
  驗證通過後仍會被 kill-switch 擋下（exit 3），**不會**真正啟動 Google OAuth flow、**不會**取得 refresh token。

### 版本分工

- **v0.6.8F：prepare only** — 只完成 client secret path validation / environment guard /
  token non-disclosure design / guarded scaffolding；不跑真 OAuth、不取得 token。
- **v0.6.8G：由 Owner 明確批准後**，才翻開 kill-switch（`LIVE_CONSENT_ENABLED`）、
  跑本機 consent、處理 token extraction，並把 refresh token 手動放進 Replit Secrets。

## 2. 前置狀態

- v0.6.8 / v0.6.8B / v0.6.8C / v0.6.8D 已完成（設計 → 草案 → 本機 helper 結構 → Owner runbook）。
- Owner 已在 Google Cloud 建立 **Desktop App OAuth Client**，並把 client_secret JSON 移到
  **本機 repo 外的安全位置**（未讀內容、未顯示 client_id / client_secret、未 commit、未上傳）。
- 尚未取得 refresh token，尚未真寫 Google Sheets，尚未進 v0.6.9。

## 3. credential JSON 必須放 repo 外

- client_secret JSON 是高敏感檔，**必須放在 repo 目錄之外**。
- helper 的驗證會**拒絕**位於 repo 內的 client secret 路徑（避免被 commit）。
- 也**拒絕** service account JSON、檔名為 `my-openclaw*` 的檔、以及非 Desktop App（installed）格式。
- 範例（placeholder，非真實路徑）：`/path/outside/repo/oauth-client.json`。

## 4. 本版不跑真 OAuth

- 本版**不**連 Google、**不**跑真 consent、**不**換 token、**不**寫 Google Sheets。
- 即使 Owner 下 `--live --i-understand-local-only --client-secret-file <repo 外路徑>`，
  在通過所有 guard 與檔案驗證後，仍會因 `LIVE_CONSENT_ENABLED = False` 停在最終 kill-switch
  並 exit 3（印「結構就緒但本版停用」），**不會**真的開瀏覽器或連 Google。

## 5. 本版不顯示 refresh token / 不寫 token file

- Plan A：未來真執行成功後，helper **只回報**：
  - refresh token 是否存在：YES / NO
  - access token 是否存在：YES / NO
  - scopes
  - 下一步提醒 Owner 依 v0.6.8G 安全取 token
- **永不**印出真 refresh / access token，**永不**寫 `token*.json` 等 token 檔。
- 禁止存在的旗標：`--write-token-file`、`--print-secret-to-clipboard`、`--show-refresh-token-once`。

## 6. 本版只補齊 helper 的 guarded live scaffolding（不真正啟動）

helper 模式與守門：

```bash
python scripts/oauth_local_consent_helper.py                         # dry-run（exit 0）
python scripts/oauth_local_consent_helper.py --dry-run               # dry-run（exit 0）
python scripts/oauth_local_consent_helper.py --explain               # dry-run + 說明（exit 0）
python scripts/oauth_local_consent_helper.py --live                  # 拒絕：缺安全旗標（exit 2）
python scripts/oauth_local_consent_helper.py --live --i-understand-local-only            # 拒絕：缺 --client-secret-file（exit 2）
python scripts/oauth_local_consent_helper.py --live --i-understand-local-only \
    --client-secret-file /path/outside/repo/oauth-client.json        # 驗證通過後仍停在 kill-switch（exit 3）
```

client secret 檔驗證（只看結構，**不輸出任何欄位值**）：

- 必須存在；不得位於 repo 內；檔名不得是 `my-openclaw*`。
- 是 service account（`type=service_account` 或含 `private_key`）→ 拒絕。
- 是 Desktop App（頂層 `installed`）→ 接受；是 `web` client → 拒絕。

## 7. Replit / CI 永遠拒絕 live

- helper 在 live 分支會偵測 `REPL_ID` / `REPL_SLUG` / `REPLIT_DB_URL` / `CI` / `GITHUB_ACTIONS` 等
  環境變數，命中即拒絕（exit 2）。
- OAuth consent 只能在 **Owner 本機**進行。

## 8. Dependency 策略

- 本版在 `requirements.txt` **新增 `google-auth-oauthlib`**，但：
  - 只供**本機 live helper**未來使用。
  - dry-run **不** import；google library 只在 live 真執行路徑延遲 import。
  - `app/result_sink.py` 仍**不** import google（mock-safe 不變）。
  - Replit / CI 不會跑 live，故不受影響。

## 9. v0.6.9 尚未開始

- v0.6.9（Google Sheets OAuth Write Pilot）**尚未開始**。
- 前提仍是：Owner 本機完成 live consent、安全取得 refresh token、放入 Replit Secrets、
  確認 token 不在 repo / log / file，再明確批准。

## 10. 下一步：v0.6.8G

**v0.6.8G token extraction / Replit Secrets placement runbook**：
說明 Owner 如何在本機真正翻開 `LIVE_CONSENT_ENABLED`、跑一次 consent、**安全地**取得 refresh token
（不經 console / 不落 repo），並手動放進 Replit Secrets `GOOGLE_OAUTH_REFRESH_TOKEN`，
最後通過 token 就位驗證。完成後才評估 v0.6.9。

## 11. 本版不做事項

- 不連真 Google、不跑真 OAuth、不換 / 不顯示 / 不寫 token、不真寫 Google Sheets。
- 不翻開 `LIVE_CONSENT_ENABLED`（維持 False）。
- 不讀 Owner 真 client secret JSON、不顯示 client_id / client_secret。
- 不改 Worker / Queue / `app/result_sink.py` / `app/main.py`。
- 不進 v0.6.9。
