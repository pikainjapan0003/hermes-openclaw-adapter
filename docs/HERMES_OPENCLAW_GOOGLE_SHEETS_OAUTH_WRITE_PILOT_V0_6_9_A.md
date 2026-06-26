# Hermes x OpenClaw — Google Sheets OAuth Write Pilot Plan v0.6.9-A

## 1. 本文件目的

定義 v0.6.9 Google Sheets OAuth Write Pilot 的**安全邊界、合約與 readiness gate**。
規劃「未來如何安全地做第一次 OAuth Google Sheets 真寫入」，但本版**不執行任何寫入**。

## 2. v0.6.9-A 是 plan / readiness，不是真寫

- 本版**只新增 plan 文件與 readiness check**。
- 本版**不真寫 Google Sheets**、不連 Google、不讀/不顯示 refresh token、不修改 Replit Secrets、
  不把 `GOOGLE_SHEETS_ENABLED` 改成 true、不實作 writer、不接自動化。
- 真正寫入留待 v0.6.9-C，且需 Owner 明確批准。

## 3. v0.6.8G 完成狀態摘要

- G-A runbook ✅、G-B live consent unlock ✅、G-C Owner 本機 OAuth consent ✅、
  G-D Replit Secrets confirmation ✅。
- `GOOGLE_OAUTH_REFRESH_TOKEN` 已由 Owner 放入 Replit Secrets（值不顯示、不入 repo）。
- `GOOGLE_SHEETS_ENABLED=false`、`GOOGLE_SHEETS_WRITE_MODE=pilot`：Sheets 真寫入仍關閉。

## 4. Google Sheets pilot 的 blast radius（影響範圍）

- 僅限**單一** spreadsheet、**單一** worksheet、**單一** row（single spreadsheet / single worksheet / single row）。
- 只 append 一列；不更新既有列、不刪除、不改格式、不碰其他分頁。
- 不寫 Drive artifacts、不建立新檔、不分享、不改權限。
- 任何錯誤都不得影響 Queue 狀態機（沿用 result_sink 的 fail-safe：emit 失敗不破壞 Queue）。

## 5. Pilot spreadsheet / worksheet 合約

- 目標 spreadsheet 由 Owner 在 v0.6.9-B/C 前自行建立並設定 `GOOGLE_SHEETS_SPREADSHEET_ID`（放 Replit Secrets）。
- worksheet 名稱固定為 `pilot_result_sink`。
- **本版不建立、不寫入任何 Google Sheet，也不把真 spreadsheet ID 寫進 repo**；
  路徑 / ID 一律 placeholder。

## 6. Pilot row schema

第一筆 pilot row 的欄位（本版只定義，不寫入）：

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

未來 v0.6.9-C 第一次真寫的建議內容（single row）：

```text
source=hermes-openclaw-adapter
environment=pilot
event_type=oauth_sheets_write_pilot
task_id=manual-pilot-001
status=ok
message=Google Sheets OAuth pilot write succeeded
metadata_json={"version":"v0.6.9","mode":"pilot","single_row":true}
```

## 7. 必要 env keys（只列 key 名，不放真值）

```text
GOOGLE_OAUTH_REFRESH_TOKEN          # 只檢查 SET / MISSING，值不顯示
GOOGLE_SHEETS_ENABLED=false         # 本版必須仍為 false
GOOGLE_SHEETS_WRITE_MODE=pilot      # 必須為 pilot
GOOGLE_SHEETS_SPREADSHEET_ID        # v0.6.9-B/C 前由 Owner 設定；不寫死在 repo
GOOGLE_SHEETS_WORKSHEET_NAME=pilot_result_sink
```

## 8. 安全 gate

- `GOOGLE_OAUTH_REFRESH_TOKEN`：只回報 SET / MISSING，**永不**顯示值。
- `GOOGLE_SHEETS_ENABLED`：本版**必須**為 `false`；被設成 `true` 即 readiness 失敗。
- `GOOGLE_SHEETS_WRITE_MODE`：必須為 `pilot`。
- 真 spreadsheet ID / refresh token / client secret 一律只放 Replit Secrets，不進 git / log / docs。
- `app/result_sink.py` 仍**不** import google（mock-safe）；本版不實作真 writer。

## 9. v0.6.9-B 開工條件（實作 guarded writer）

v0.6.9-B（實作 guarded Google Sheets writer，但仍預設關閉）只能在以下成立後開始：

- Owner 明確批准進入 v0.6.9-B。
- readiness 確認 `GOOGLE_OAUTH_REFRESH_TOKEN: SET`、`GOOGLE_SHEETS_ENABLED=false`、`WRITE_MODE=pilot`。
- writer 必須：預設關閉、single-row append、fail-safe（不破壞 Queue）、不寫 Drive、
  延遲 import google（dry-run / 關閉時不 import）、不 log token。
- v0.6.9-B 仍**不**真寫（除非 Owner 在受控下臨時開 `GOOGLE_SHEETS_ENABLED`）。

## 10. v0.6.9-C 才能做第一次真寫

- v0.6.9-C 才會由 Owner 在受控下，把 `GOOGLE_SHEETS_ENABLED` 暫時開為 true，
  做**一次** single-row append 驗證，完成後立即關回 false。
- 需 Owner 明確批准，且確認 spreadsheet / worksheet 已就位、refresh token 有效。

## 11. 禁止事項

- 不真寫 Google Sheets、不連 Google、不實作真 writer（本版）。
- 不讀出 / 不顯示 refresh token、不印任何 secret、不寫 token file、不改 Replit Secrets。
- 不把 `GOOGLE_SHEETS_ENABLED` 改成 true。
- 不寫真 spreadsheet ID、不寫 Owner 真路徑進 repo。
- 不修改 Worker / Queue / `app/result_sink.py` / `app/main.py`、不接自動化、不建 tag。

## 12. rollback / revoke / rotate 流程

1. 立刻把 `GOOGLE_SHEETS_ENABLED` 設回 `false`（或關閉 Replit app / result sink）。
2. 若 token 疑似外洩：Google Account → Security → Third-party access **撤銷**授權。
3. 刪除 / 重設對應 Replit Secret（`GOOGLE_OAUTH_REFRESH_TOKEN`），重新產生 token。
4. 檢查 git history / logs 是否殘留 token 或 spreadsheet ID。
5. 開一版 incident note，**不放真值**。

## 13. Owner 手動操作清單（未來各子階段）

1. （v0.6.9-B 前）建立 pilot spreadsheet，新增 worksheet `pilot_result_sink`，
   把 `GOOGLE_SHEETS_SPREADSHEET_ID` 放 Replit Secrets。
2. （v0.6.9-B）批准實作 guarded writer（仍預設關閉）。
3. （v0.6.9-C）在受控下暫時開 `GOOGLE_SHEETS_ENABLED=true`，做一次 single-row 驗證，立即關回 false。
4. 確認寫入正確、無多寫、無 Drive 影響、token / ID 未外洩。
5. 明確回報結果，再決定後續。

## 14. 最終狀態摘要

- 本版只交付：v0.6.9-A pilot plan 文件 + readiness check。
- `GOOGLE_SHEETS_ENABLED=false` 維持；`GOOGLE_SHEETS_WRITE_MODE=pilot`。
- 未真寫 Google Sheets、未讀/顯示 token、未改 Replit Secrets、未改 app 核心。
- 下一步：Owner 明確批准後才進 v0.6.9-B（實作 guarded writer，仍預設關閉）。
