# Hermes x OpenClaw OAuth — v0.6.8F Checkpoint

## 1. 本 checkpoint 目的

凍結並記錄 **v0.6.8F（guarded local OAuth live helper — prepare only）** 的完成狀態，
作為進入 v0.6.8G 前的單一事實對照點：說明本版實際做了什麼、刻意不做什麼、目前安全狀態、
已 push 的 commit、未建 tag 的原因，以及後續 gate。本文件**不含任何 secret / token / 真路徑**。

## 2. v0.6.8F 實際完成內容

- helper（`scripts/oauth_local_consent_helper.py`）補齊 **guarded live scaffolding**：
  - 新增 `--client-secret-file` 參數。
  - client secret 檔**安全驗證**（只看結構，不輸出任何欄位值）：拒絕 repo 內路徑、拒絕
    service account JSON、拒絕 `my-openclaw*` 檔名、拒絕 `web` client、缺檔/不存在拒絕；
    僅接受 Desktop App（`installed`）client。
  - **token non-disclosure 設計**（Plan A）：未來真執行只回報 token 是否存在（YES/NO）+ scopes，
    永不印真 token、永不寫 token 檔。
  - **environment guard**：live 分支偵測 Replit / CI（`REPL_ID` / `REPLIT_DB_URL` / `CI` 等）即拒絕。
  - google library 只在 live 真執行路徑**延遲 import**；dry-run 不 import。
- 新增 readiness：`scripts/check_oauth_live_enablement_readiness.py`（靜態 + fake-fixture 驗證）。
- 新增文件：`docs/HERMES_OPENCLAW_OAUTH_LIVE_HELPER_ENABLEMENT_V0_6_8F.md`（已 retitle 為 Guarded Prepare）。
- `requirements.txt` 新增 `google-auth-oauthlib`（註明僅本機 live helper 用；dry-run / result_sink 不 import）。
- 命名修正：commit message 由誤導性的 "feat: enable..." amend 為 **"chore: prepare guarded local oauth live helper"**。

## 3. v0.6.8F 沒有做什麼

- **沒有**跑真 OAuth、**沒有**連 Google、**沒有**開瀏覽器。
- **沒有**取得 refresh token、**沒有**顯示 / 寫入任何 token。
- **沒有**讀取 Owner 真 OAuth client secret JSON。
- **沒有**真寫 Google Sheets。
- **沒有**翻開 `LIVE_CONSENT_ENABLED`（維持 `False`）。
- **沒有**修改 Worker / Queue / `app/result_sink.py` / `app/main.py`。
- **沒有**進入 v0.6.9。

## 4. 安全狀態

- `LIVE_CONSENT_ENABLED = False` 仍保留為最終 kill-switch：即使帶齊
  `--live --i-understand-local-only --client-secret-file <repo 外路徑>`，
  驗證通過後仍會被擋下（exit 3），不會啟動 Google OAuth flow。
- 高敏感檔（client secret JSON / token）一律放 **repo 外**；helper 會拒絕 repo 內路徑。
- 任何真值（client secret / refresh token）只屬 Replit Secrets / 本機安全處，**永不進 git / log / docs**。
- 全套 readiness + 測試通過；敏感掃描未發現任何真值或 Owner 真路徑被 tracked。

## 5. 已 push commit 資訊

- commit：`db4770ab3d23bea72eebee7b180ca26232e6b0a5`（短碼 `db4770a`）。
- commit message：`chore: prepare guarded local oauth live helper`。
- 本機 HEAD = 遠端 `origin/master` tip = `db4770a`，working tree clean，已同步。

## 6. 未建立 tag 的原因

- v0.6.8F 是 v0.6.8 OAuth / Secrets Design 線的**補充實作（prepare only）**，不是真 OAuth、
  不是真 token 取得完成、不是真 Google 寫入里程碑。
- 為保持 tag 線乾淨，與 v0.6.8B / v0.6.8C / v0.6.8D 一致，**不另建 tag**。

## 7. v0.6.8G 開工前 gate

v0.6.8G（token extraction / Replit Secrets placement runbook）只能在以下成立後開始：

- Owner **明確批准**進入 v0.6.8G。
- 確認在 **Owner 本機**（非 Replit / 非 CI）進行。
- Owner 自行於本機安裝 `google-auth-oauthlib`。
- Owner 明確同意翻開 `LIVE_CONSENT_ENABLED`（只在本機，不 commit 真值）。
- 取得的 refresh token **不經 console、不落 repo / log / file**，只手動放進 Replit Secrets。
- v0.6.8G 需同步調整兩支斷言 `LIVE_CONSENT_ENABLED = False` 的 readiness。

## 8. v0.6.9 仍不得開始的原因

- v0.6.9（Google Sheets OAuth Write Pilot）需要一個**已安全就位的 refresh token**，
  而目前**尚未取得任何 token**。
- 必須先完成 v0.6.8G：Owner 本機 live consent → 安全取得 token → 放入 Replit Secrets →
  驗證 token 不在 repo / log / file，並由 Owner 明確批准，才可進 v0.6.9。
- v0.6.9 仍須先做 single-sheet / single-row / guarded pilot，且不寫 Drive artifacts。

## 9. Owner 真 OAuth JSON 路徑不得寫入文件

- 本文件與本專案任何 docs **不得**記錄 Owner 本機 client secret JSON 的真實路徑。
- 涉及路徑時一律用 placeholder：`/path/outside/repo/oauth-client.json`。

## 10. 不包含任何 secret / token / credential 真值

- 本 checkpoint **不含**任何 client_id / client_secret / refresh token / access token /
  service account private key / dashboard token 等真值。
- 出現的皆為 **key 名 / placeholder / 說明文字**，非真值。
