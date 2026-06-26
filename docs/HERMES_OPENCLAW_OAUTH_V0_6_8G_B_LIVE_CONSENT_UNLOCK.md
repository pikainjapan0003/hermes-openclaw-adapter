# Hermes x OpenClaw OAuth — v0.6.8G-B Live Consent Unlock

## 1. 本版目的

把 helper 從「`LIVE_CONSENT_ENABLED=False` 永久 kill-switch」改成**更精準的 explicit-flag gate**：
預設仍不跑 live，只有在 **Owner 本機**且明確帶齊完整風險旗標時，才允許進入 live consent flow。

## 2. 本版做了什麼

- helper（`scripts/oauth_local_consent_helper.py`）：
  - live 不再靠永久 kill-switch，而靠 **explicit Owner flags + local-only + file validation +
    token display acknowledgement**。
  - 取得憑證集中在 `_obtain_credentials()`（唯一連 Google / 延遲 import 的地方；測試 monkeypatch 它）。
  - 新增 `--show-refresh-token-once` 與 `--i-understand-token-will-be-visible`。
  - 預設只回報 `refresh token present: YES/NO` + `access token present: YES/NO` + `scopes`，**不顯示真 token**。
- 新增 readiness：`scripts/check_oauth_v0_6_8g_b_live_unlock_readiness.py`（靜態 + fake-flow，永不連真 Google）。
- 同步調整既有 OAuth readiness 的舊斷言（原本斷言 `LIVE_CONSENT_ENABLED = False`）為新語意。

## 3. 本版仍不跑真 OAuth

- 本版**不**跑真 OAuth、**不**讀 Owner 真 OAuth JSON、**不**取得真 token、**不**放 Replit Secrets、**不**進 v0.6.9。
- 所有測試以 **fake flow（monkeypatch）** 驗證，永不連真 Google、永不開瀏覽器。
- 真正執行只能由 Owner 在本機按第 4 節操作（v0.6.8G-C）。

## 4. Owner 未來 G-C 手動執行方式

在 **Owner 本機**（非 Replit / 非 CI）：

```bash
pip install google-auth-oauthlib   # 只在本機安裝
# 預設安全模式：只看到 present: YES/NO，不顯示真 token
python scripts/oauth_local_consent_helper.py \
  --live \
  --i-understand-local-only \
  --client-secret-file /path/outside/repo/oauth-client.json
```

需要把 refresh token 取出時，再加兩個風險旗標（見第 5、6 節）。

## 5. `--show-refresh-token-once` 的風險

```bash
python scripts/oauth_local_consent_helper.py \
  --live \
  --i-understand-local-only \
  --client-secret-file /path/outside/repo/oauth-client.json \
  --show-refresh-token-once \
  --i-understand-token-will-be-visible
```

- 只顯示 **refresh token**，**不**顯示 access token。
- 顯示前有明確警告與 countdown；**只顯示一次**。
- 風險：refresh token 會出現在**終端機畫面 / 歷史 / 螢幕截圖**；Owner 須自行控管。
- 顯示後立即：不要貼到聊天工具、不要 commit、立刻放入 Replit Secrets、外洩即 revoke / rotate。

## 6. `--i-understand-token-will-be-visible` 的必要性

- `--show-refresh-token-once` **必須**再加 `--i-understand-token-will-be-visible`，否則拒絕（exit 2）。
- 這是「雙重明確同意」：避免 Owner 不小心把 token 顯示在畫面上。

## 7. 不寫 token file 的原因

- token 落地成檔案會增加外洩面（被同步、被備份、被誤 commit）。
- 因此 helper **永不**寫 token 檔；refresh token 只在 show-once 模式短暫顯示，由 Owner 手動貼入 Secrets。

## 8. Replit / CI 禁止 live 的原因

- Replit / production / CI 屬公開或共享環境，不應接觸 client secret、不應產出 / 保存 token。
- helper 偵測 `REPL_ID` / `REPLIT_DB_URL` / `CI` / `GITHUB_ACTIONS` 等，命中即拒絕（exit 2）。

## 9. token 外洩 revoke / rotate 流程

1. 立刻停止 Replit app，或關閉相關 result sink。
2. Google Account → Security → Third-party access **撤銷**該授權。
3. 刪除對應的 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`）。
4. 重新產生 token（重跑本機 consent）。
5. 檢查 git history / logs 是否殘留 token。
6. 開一版 incident note，**不放真 token**。

## 10. v0.6.8G-C 開工 gate

v0.6.8G-C（Owner 本機真跑 consent）只能在以下成立後開始：

- Owner 明確批准進入 v0.6.8G-C，且確認在本機（非 Replit / CI）。
- Owner 本機安裝 `google-auth-oauthlib`。
- 使用 repo 外 client secret（placeholder：`/path/outside/repo/oauth-client.json`）。

## 11. v0.6.8G-D Replit Secrets gate

- 只有 v0.6.8G-D 才把取得的 refresh token **手動**放進 Replit Secrets。
- 放入後仍維持 `GOOGLE_SHEETS_ENABLED=false`，**不立刻真寫 Sheets**。

## 12. v0.6.9 仍不得開始

- v0.6.9 需要已安全就位的 refresh token，且通過 G-C / G-D gate 與 Owner 明確批准。
- v0.6.9 仍須先做 single-sheet / single-row / guarded pilot，且不寫 Drive artifacts。
