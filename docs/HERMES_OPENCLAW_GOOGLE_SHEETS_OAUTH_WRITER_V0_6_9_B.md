# Hermes x OpenClaw — Guarded Google Sheets OAuth Writer v0.6.9-B

## 1. 本版目的

新增一個**獨立、受保護、可測試**的 Google Sheets OAuth writer 模組
（`app/google_sheets_oauth_writer.py`），具備完整 guard，作為未來 v0.6.9-C 第一次真寫的基礎。
本版**仍不真寫 Google Sheets**，所有測試只走 fake env / mock transport。

## 2. v0.6.9-A 完成狀態摘要

- v0.6.9-A pilot plan + readiness 已完成並 push（遠端 master tip `1663728`）。
- `GOOGLE_OAUTH_REFRESH_TOKEN` 已由 Owner 放入 Replit Secrets；`GOOGLE_SHEETS_ENABLED=false`、
  `GOOGLE_SHEETS_WRITE_MODE=pilot`。

## 3. v0.6.9-B 是 guarded writer implementation，不是真寫

- 本版**只新增 writer 模組 + mock 測試 + readiness + 文件（+ 必要 dependency）**。
- 本版**不真寫 Google Sheets**、不連 Google API、不讀/不顯示 token、不改 Replit Secrets、
  不把 `GOOGLE_SHEETS_ENABLED` 改成 true、不接 Queue / Worker / result_sink / app.main、不接自動化。

## 4. writer blast radius

- 僅針對**單一** spreadsheet、**單一** worksheet（`pilot_result_sink`）、**單一** row（single row）。
- 一次只 append 一列；不更新、不刪除、不改格式、不碰其他分頁、不寫 Drive。
- writer 是獨立模組，**不被**核心引用，因此即使有 bug 也不影響 Queue / Worker / Dashboard。

## 5. 必要 env keys（只列 key 名，本版不要求 Owner 現在貼任何 secret）

```text
GOOGLE_OAUTH_REFRESH_TOKEN
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_SHEETS_ENABLED
GOOGLE_SHEETS_WRITE_MODE
GOOGLE_SHEETS_SPREADSHEET_ID
GOOGLE_SHEETS_WORKSHEET_NAME
```

token 類（refresh / client secret）只在真 live build 時從 env 讀取，**永不**印出 / log。

## 6. writer guard 條件

`append_single_pilot_row()` 依序 guard：

1. `GOOGLE_SHEETS_ENABLED` 必須明確等於 `true`，否則直接 `skipped`（不 import google、不讀 token）。
2. `GOOGLE_SHEETS_WRITE_MODE` 必須等於 `pilot`。
3. `GOOGLE_SHEETS_SPREADSHEET_ID` 必須存在且非空。
4. `GOOGLE_SHEETS_WORKSHEET_NAME` 必須等於 `pilot_result_sink`。
5. row 必須剛好 8 欄、純值（巢狀視為多列 → 拒絕）；一次只 append 一列。
6. 必須顯式 `allow_live_write=True`，否則 fail-safe 拒絕。
7. append range 固定 `pilot_result_sink!A:H`。

任何 guard 違反 → 丟出 `GoogleSheetsWriterGuardError` / `GoogleSheetsWriterConfigError`，不寫入。

## 7. pilot row schema（固定 8 欄）

```text
timestamp
source
environment
event_type
task_id
status
message
metadata_json
```

`build_pilot_row(...)` 回傳一列 8 欄字串。

## 8. fake / mock transport 測試策略

- `append_single_pilot_row(row, config, transport=None, allow_live_write=False)`：
  `transport` 可注入 fake/mock；測試只走 fake transport，**永不**連真 Google。
- 只有真要 live 且**未**注入 transport 時，才 lazy import google libs、用 refresh token 建 credentials、
  呼叫 Sheets API（`_build_live_transport`）。本版測試不會走到這條路徑。
- 測試使用純 fake 值（如 `fake-refresh-token-for-test` / `fake-spreadsheet-id`），不使用真 Replit Secrets。

## 9. 為什麼本版不接 Queue / Worker / result_sink

- 先把 writer 做成**獨立、可單測**的模組，確保 guard 正確、不誤寫，再談接入。
- 接入核心（result_sink emit → writer）屬於更後面的步驟，需另行批准；本版刻意**不接**，
  以維持 Queue / Worker / Dashboard 完全不受影響、result_sink 仍 mock-safe。

## 10. v0.6.9-C 第一次真寫 gate

v0.6.9-C 才會做第一次真寫，且只能在以下成立後：

- Owner 明確批准進入 v0.6.9-C。
- Owner 已建立 pilot spreadsheet + worksheet `pilot_result_sink`，並設好 `GOOGLE_SHEETS_SPREADSHEET_ID`。
- Owner 在受控下暫時把 `GOOGLE_SHEETS_ENABLED` 設為 `true`，以 `allow_live_write=True` 做**一次**
  single-row append 驗證，完成後立即關回 `false`。

## 11. token 安全規則

- refresh token / client secret **永不**印出 / log / 寫檔；只在 live build 時從 env 讀。
- 不把任何真 token / 真 spreadsheet ID 寫進 repo / docs / 測試。
- 測試一律用 fake 值。

## 12. rollback / revoke / rotate 流程

1. 立刻把 `GOOGLE_SHEETS_ENABLED` 設回 `false`（或關閉相關流程）。
2. 若 token 疑似外洩：Google Account → Security → Third-party access **撤銷**授權。
3. 刪除 / 重設對應 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`），重新產生 token。
4. 檢查 git history / logs 是否殘留 token 或 spreadsheet ID。
5. 開一版 incident note，**不放真值**。

## 13. 禁止事項

- 不真寫 Google Sheets、不連 Google API、不讀/顯示 token、不寫 token file、不改 Replit Secrets。
- 不把 `GOOGLE_SHEETS_ENABLED` 改成 true。
- 不接 Queue / Worker / result_sink、不改 `app/main.py`、不新增會真寫的 CLA / 自動化、不建 tag。

## 14. 最終狀態摘要

- 本版交付：guarded writer 模組 + mock 測試 + readiness + 文件（+ `google-api-python-client` dependency）。
- `GOOGLE_SHEETS_ENABLED=false` 維持；writer 未接核心；result_sink 仍 mock-safe（不 import google）。
- 未真寫 Google Sheets、未連 Google、未讀/顯示 token、未改 Replit Secrets。
- 下一步：Owner 明確批准後才進 v0.6.9-C（第一次真寫 single-row）。
