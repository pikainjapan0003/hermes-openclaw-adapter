# Hermes x OpenClaw — Google Sheets OAuth Live Pilot v0.6.9-C0 (Runner + Preflight)

## 1. 本版目的

新增 Google Sheets OAuth single-row **live pilot runner** 與 **preflight**，先在
`GOOGLE_SHEETS_ENABLED=false` 下確認所有 guard 正常運作。第一次真寫留待 C1。

## 2. C0 是 live pilot runner + preflight，不是真寫

- 本版**不真寫 Google Sheets**、不把 `GOOGLE_SHEETS_ENABLED` 改成 true、不改 Replit Secrets。
- 因 `GOOGLE_SHEETS_ENABLED=false`，runner 會得到 writer 的 `skipped`，**不連 Google、不 append**。
- 本版不讀/不顯示 refresh token / client secret、不 log token、不寫 token file、不自動重試。

## 3. 已完成的 A / B 狀態摘要

- v0.6.9-A pilot plan + readiness 已完成並 push。
- v0.6.9-B guarded writer（`app/google_sheets_oauth_writer.py`）已完成並 push；獨立、未接核心、
  google libs 延遲 import、預設關閉。
- Owner 已建立 Google Sheet + worksheet `pilot_result_sink`（header 8 欄），並把相關 key 放 Replit Secrets。

## 4. Google Sheet 目標合約

- 單一 spreadsheet、單一 worksheet `pilot_result_sink`、單一 row（single row）append。
- 固定 8 欄：`timestamp, source, environment, event_type, task_id, status, message, metadata_json`。
- append range 固定 `pilot_result_sink!A:H`；`event_type=oauth_sheets_write_pilot`、
  `task_id=manual-pilot-001`、`status=ok`、`metadata_json` 含 `version=v0.6.9 / phase=C / mode=pilot / single_row=true`。

## 5. 必要 Replit Secrets（只列 key 名，不放真值）

```text
GOOGLE_OAUTH_REFRESH_TOKEN
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_SHEETS_SPREADSHEET_ID
GOOGLE_SHEETS_WORKSHEET_NAME=pilot_result_sink
GOOGLE_SHEETS_ENABLED=false
GOOGLE_SHEETS_WRITE_MODE=pilot
```

## 6. 為什麼本版仍要求 `GOOGLE_SHEETS_ENABLED=false`

- C0 只驗證 runner 的 guard 路徑與安全摘要輸出，不需要也不應該真寫。
- 維持 `GOOGLE_SHEETS_ENABLED=false` 可確保即使 runner 帶了所有正確 env 與 ack 旗標，
  writer 仍只回 `skipped`，**不連 Google**，把第一次真寫的決定權完整留給 C1 / Owner。

## 7. live runner 的 guard

- **雙重 live guard**：runner 必須帶 `--i-understand-this-writes-one-row`，否則拒絕（exit 2）。
- 只有帶該旗標時，runner 才對 writer 傳 `allow_live_write=True`。
- 仍受 writer 全部 guard 約束：ENABLED=true、write_mode=pilot、spreadsheet_id 非空、
  worksheet=`pilot_result_sink`、row 8 欄、single row、append range `pilot_result_sink!A:H`。
- runner 只印**安全摘要**：status / worksheet / row 欄數 / append range / **masked** spreadsheet id
  （前 6 + 後 4）/ ENABLED / write_mode；**永不**印 token / client secret / 完整 env。

## 8. 第一次真寫 C1 的條件

- Owner 明確批准進入 C1。
- Owner 在受控下把 `GOOGLE_SHEETS_ENABLED` 暫時設為 `true`（見第 9 節）。
- 以 `--i-understand-this-writes-one-row` 跑 runner，做**一次** single-row append。
- 確認 Google Sheet `pilot_result_sink` 新增了正好一列、內容正確、無多寫。

## 9. Owner 手動 toggle 流程（C1 時）

1. 在 Replit Secrets 把 `GOOGLE_SHEETS_ENABLED` 由 `false` 暫時改為 `true`。
2. 跑：`python scripts/run_google_sheets_oauth_single_row_pilot_v0_6_9_c.py --i-understand-this-writes-one-row`。
3. 確認 Sheet 只新增一列、append range 正確。
4. **立即**把 `GOOGLE_SHEETS_ENABLED` 改回 `false`（見第 10 節）。

## 10. 寫入後必須立刻關回 false

- C1 真寫完成後，**必須立刻**把 `GOOGLE_SHEETS_ENABLED` 設回 `false`，避免後續任何意外寫入。
- pilot 採「開一次 → 寫一列 → 關回」模式；不得長期保持 `true`、不得自動重試。

## 11. 禁止事項

- 不真寫 Google Sheets（本版）、不連 Google API、不讀/顯示 token / client secret、不 log token、不寫 token file。
- 不把 `GOOGLE_SHEETS_ENABLED` 改成 true（本版）、不改 Replit Secrets。
- 不接 Queue / Worker / result_sink、不改 `app/main.py`、不自動重試 live write、不建 tag。

## 12. rollback / revoke / rotate

1. 立刻把 `GOOGLE_SHEETS_ENABLED` 設回 `false`（或關閉相關流程）。
2. 若 token 疑似外洩：Google Account → Security → Third-party access **撤銷**授權。
3. 刪除 / 重設對應 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`），重新產生 token。
4. 檢查 git history / logs 是否殘留 token 或 spreadsheet ID。
5. 開一版 incident note，**不放真值**。

## 13. 最終狀態摘要

- 本版交付：live pilot runner + preflight readiness + 文件。
- `GOOGLE_SHEETS_ENABLED=false` 維持；runner 在 disabled 下為 `skipped`，未連 Google、未 append。
- 未真寫 Google Sheets、未讀/顯示 token、未改 Replit Secrets、未接核心。
- 下一步：Owner 明確批准後才進 C1（第一次真寫 single-row，開一次 → 寫一列 → 立即關回 false）。
