# Hermes x OpenClaw OAuth — v0.6.8G-D Replit Secrets Placement Confirmation

## 1. 本版目的

確認 Owner 已把 OAuth refresh token 與相關開關放進 **Replit Secrets**，並驗證：
key 是否存在、是否非空、Google Sheets 真寫入是否仍關閉。
本版**只做確認**：不顯示任何 secret 真值、不跑 OAuth、不真寫 Google Sheets、不進 v0.6.9。

## 2. G-C 已由 Owner 完成

- v0.6.8G-C（Owner 本機跑 OAuth consent、取得 refresh token）**已由 Owner 完成**。
- 取得的 refresh token 由 Owner **手動**放入 Replit Secrets，未經 repo / log / file、未貼給任何 AI。

## 3. Replit Secrets 應包含哪些 key（只列 key 名，不列真值）

```text
GOOGLE_OAUTH_REFRESH_TOKEN     # 最高敏感；存在且非空即可，值不得顯示
GOOGLE_SHEETS_ENABLED=false    # Sheets 真寫入仍關閉
GOOGLE_SHEETS_WRITE_MODE=pilot # 之後 pilot 用
```

（其餘相關 key 如 `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` /
`GOOGLE_SHEETS_SPREADSHEET_ID` 視 pilot 需要另行設定，一律只放 Replit Secrets、不進 git。）

## 4. 不得顯示 token 真值

- 任何流程 / 腳本 **不得** print / log / 寫檔 `GOOGLE_OAUTH_REFRESH_TOKEN` 的值。
- readiness 只回報 `GOOGLE_OAUTH_REFRESH_TOKEN: SET` 或 `MISSING`，**永不**顯示值。
- 不得把 token 貼進 Claude / ChatGPT / Discord / Slack、不得截圖、不得 commit。

## 5. `GOOGLE_SHEETS_ENABLED=false` 的原因

- refresh token 就位**不等於**可以開始真寫 Sheets。
- 為避免誤寫，Sheets 真寫入預設 **關閉**（`false`）；只有通過 v0.6.9 gate 後才會考慮開啟。

## 6. `GOOGLE_SHEETS_WRITE_MODE=pilot` 的原因

- 之後真寫入第一步只能是 **pilot**：single-sheet / single-row / guarded，小規模可隨時關閉。
- `pilot` 模式標記讓未來 v0.6.9 一開始就受限，不會一次大量寫入。

## 7. v0.6.9 開工 gate

v0.6.9（Google Sheets OAuth Write Pilot）只能在以下全部成立後開始：

- readiness 確認 `GOOGLE_OAUTH_REFRESH_TOKEN: SET`、`GOOGLE_SHEETS_ENABLED=false`、`GOOGLE_SHEETS_WRITE_MODE=pilot`。
- Owner 明確說「refresh token 已安全放進 Replit Secrets」「repo / log / file 沒有 token」。
- Owner 明確批准真 Google Sheets write pilot。
- v0.6.9 仍須先做 single-sheet / single-row / guarded pilot，且不寫 Drive artifacts。

## 8. 若 token 外洩如何 revoke / rotate

1. 立刻停止 Replit app，或關閉相關 result sink。
2. Google Account → Security → Third-party access **撤銷**該授權。
3. 刪除對應的 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`）。
4. 重新產生 token（Owner 本機重跑 consent）。
5. 檢查 git history / logs 是否殘留 token。
6. 開一版 incident note，**不放真 token**。

## 9. 不得 commit 的項目

- `.env`、`data/`、`queue.db`、`tasks.jsonl`、`results.jsonl`、`mock_google_sheets_rows.jsonl`。
- 任何 credential JSON / `client_secret*.json` / `token*.json` / `service_account*.json` / `my-openclaw*.json`。
- 任何 refresh token / access token / client_id / client_secret 真值。
- 任何 Owner 本機真路徑。

## 10. 最終狀態摘要

- refresh token 已由 Owner 放入 Replit Secrets（值不顯示、不入 repo）。
- `GOOGLE_SHEETS_ENABLED=false`、`GOOGLE_SHEETS_WRITE_MODE=pilot`：Sheets 真寫入仍關閉。
- 未跑本版 OAuth、未讀 Owner 真 OAuth JSON、未真寫 Google Sheets、未進 v0.6.9。
- 下一步：由 Owner 明確批准後，才評估 v0.6.9 guarded pilot。
