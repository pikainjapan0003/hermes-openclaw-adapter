# Hermes x OpenClaw — Google Sheets OAuth Live Pilot v0.6.9-C1 Closeout

## 1. 本文件目的

記錄並收尾 v0.6.9-C1：**第一次真寫 Google Sheets single-row pilot 已由 Owner 手動完成**。
本文件只做 closeout 與安全檢查，**不再真寫 Google Sheets**、不執行 live runner。

## 2. C1 是 Owner 手動真寫 closeout

- C1 的真寫由 **Owner 在受控下手動執行**（Replit Secrets 把 `GOOGLE_SHEETS_ENABLED` 暫時開為 true →
  跑 runner 寫一列 → 立即關回 `false`）。
- Claude / 自動化**未**、也**不得**代跑真寫；本版只負責文件收尾。

## 3. 實際結果摘要

- 第一次 single-row pilot append 成功。
- writer result status = **appended**。
- 目標 Google Sheet worksheet `pilot_result_sink` 新增了**正好一列** pilot row。
- 寫入後 `GOOGLE_SHEETS_ENABLED` 已由 Owner **改回 `false`**。

## 4. writer result status = appended

- runner 透過 `app/google_sheets_oauth_writer.py` 的 `append_single_pilot_row(..., allow_live_write=True)`
  完成一次 append，回報 `status = appended`、`appended_rows = 1`。

## 5. 寫入範圍

- append range = `pilot_result_sink!A:H`（固定）。

## 6. row columns = 8

- pilot row 固定 8 欄：`timestamp, source, environment, event_type, task_id, status, message, metadata_json`。

## 7. worksheet = pilot_result_sink

- 寫入只針對單一 worksheet `pilot_result_sink`，單一列（single row）。

## 8. spreadsheet id（masked）

- spreadsheet id masked: `1vzR1T...3u7E`
- **本文件不記錄完整 spreadsheet id**；完整 ID 只存在於 Replit Secrets，不進 repo / docs / log。

## 9. `GOOGLE_SHEETS_ENABLED` 已改回 false

- pilot 採「開一次 → 寫一列 → 立即關回」模式；目前 `GOOGLE_SHEETS_ENABLED=false`。
- 不長期保持開啟、不自動重試、不再真寫。

## 10. 沒有顯示 / commit token

- 全程**未**顯示、未 log、未寫檔、未 commit 任何 refresh token / access token。
- refresh token 僅存在於 Replit Secrets。

## 11. 沒有顯示 / commit client secret

- 全程**未**顯示、未 commit 任何 OAuth client secret；只存在於 Replit Secrets。

## 12. 沒有接 Queue / Worker / result_sink

- writer 與 runner 仍是**獨立**模組，**未**接 Queue / Worker / `app/result_sink.py` / `app/main.py`。
- `result_sink` 仍 mock-safe（不 import google）。

## 13. 目前 blast radius

- 僅單一 spreadsheet、單一 worksheet `pilot_result_sink`、單一 row。
- 不寫 Drive、不更新 / 刪除既有列、不碰其他分頁、不接自動化。
- 任何 writer 問題都不影響 Queue / Worker / Dashboard（writer 未接核心）。

## 14. 下一步建議

- **v0.6.9-D 或 v0.7.0 前不得自動化寫入**：在沒有明確設計與 Owner 批准前，
  不把 writer 接進 result_sink / Worker、不讓 `GOOGLE_SHEETS_ENABLED` 長期保持開啟、不自動 append。
- 後續若要常態化，需另立版本設計：批次 / 重試 / 去重 / 失敗不破壞 Queue / 權限最小化等。

## 15. rollback / revoke / rotate 注意事項

1. 立刻確認 `GOOGLE_SHEETS_ENABLED=false`（目前已是 false）。
2. 若 token 疑似外洩：Google Account → Security → Third-party access **撤銷**授權。
3. 刪除 / 重設對應 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`），重新產生 token。
4. 檢查 git history / logs 是否殘留 token 或完整 spreadsheet id。
5. 開一版 incident note，**不放真值**。

## 16. 最終狀態摘要

- C1 第一次真寫 single-row 已由 Owner 手動完成：`status = appended`、`pilot_result_sink` 新增一列。
- `GOOGLE_SHEETS_ENABLED=false` 已回復；未再真寫、未接核心、未顯示 / commit 任何 secret。
- writer / runner 仍獨立；`result_sink` 仍 mock-safe。
- 下一步：未經 Owner 明確批准與設計，不得自動化 Google Sheets 寫入。
