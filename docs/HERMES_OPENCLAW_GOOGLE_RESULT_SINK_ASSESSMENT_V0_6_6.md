# Hermes x OpenClaw Google Result Sink Assessment v0.6.6

## 1. 本版目標

評估把任務**結果安全落地到 Google Drive / Google Sheets**，解決 Replit Safe Sandbox 的
filesystem 不持久問題（`queue.db` / `results.jsonl` 在 Replit 休眠 / 重啟可能消失）。

本版**只做評估 + 文件 + 唯讀 readiness 檢查**：不接真 Google 寫入、不放任何真 Google
credentials、不改任務執行核心邏輯。

## 2. 前置狀態

v0.6.0B GitHub Backup、v0.6.1 Restore Test、v0.6.2 Deployment Assessment、
v0.6.3 Replit Safe Sandbox Plan、v0.6.4 Dashboard Auth Gate、v0.6.5 Replit Deployment Test、
**v0.6.5B Replit Manual Smoke Test（已實測通過：/health、Auth Gate 登入、Dashboard 可瀏覽、
假 OpenClaw、Invite only）**。Replit Safe Sandbox 已可用，但缺「結果長期落地」。

## 3. 為什麼需要外部結果落地

- Replit filesystem **不持久**：休眠 / 重啟 / redeploy 後 `data/` 可能被重置。
- `queue.db` 是**runtime 狀態**（佇列狀態機），不是給人看的長期帳本。
- `results.jsonl` / `tasks.jsonl` 是 append-only ledger，放在 Replit 上同樣有遺失風險。
- → 需要一個**外部、持久、可被人查看**的結果落地點：Google Sheets / Drive 是低成本、新手友善的選擇。

## 4. 目前資料流盤點（實測 grep）

| 資料 | 位置 | 性質 |
|---|---|---|
| 任務佇列狀態 | `queue.db`（SQLite，`DATA_DIR/queue.db`） | runtime 狀態機（queued…archived）+ `result_ref` 路徑字串 |
| 任務結果全文 | `data/results.jsonl`（worker `append_jsonl(RESULTS_PATH, ...)`） | TaskResult schema v1：task_id / correlation_id / status / finished_at / title / goal / summary / **result_text** / error |
| 任務狀態 ledger | `data/tasks.jsonl` | 每次狀態變更 append 一列 |
| worker 心跳 | `worker_heartbeats` 表（同 db） | runtime 觀測 |
| 留言 | `task_comments` 表（同 db） | blackboard |

**應長期保存**：每個任務的最終結果（status / summary / result_text / error / 時間戳）。
**只是 runtime 暫存**：queue 狀態機、heartbeat、ledger 中間態。

## 5. 三種落地方案

### 方案 A：Google Sheets Result Ledger
- 任務完成後 append 一列到 Google Sheet（task_id / title / status / 時間 / safety_level / summary / result_uri / error）。
- 優點：新手易看、可篩選 / 審核 / 對帳、適合 MVP。
- 缺點：不適合存很大的結果全文、欄位需固定、要處理 API 配額與重試。

### 方案 B：Google Drive Result Files
- 任務完成後輸出一個 Markdown / JSON artifact 到 Drive；Sheet 只存索引 + 連結。
- 優點：適合長結果、每任務獨立 artifact、可回查。
- 缺點：Drive 權限 / 資料夾 / 命名要規劃、OAuth/SA 限制要清楚、檔案多要整理策略。

### 方案 C：Hybrid（Sheets ledger + Drive artifacts）
- Sheets 當 ledger（每列含 `result_file_url` / `drive_file_id`），Drive 當 artifact storage。
- 優點：最契合 Hermes x OpenClaw 長期方向；人看 Sheet、長結果放 Drive、Dashboard 只顯示摘要 + 連結。
- 缺點：實作較複雜、要錯誤處理 / 重試、要 credentials 管理。

**方案建議**：
- **v0.6.6 只評估**（本版）。
- **v0.6.7** 先做 **Google Sheets mock sink**（寫到本地 mock / 假 client，不連真 Google）。
- **v0.6.8** 再做 Drive artifact mock 或 OAuth/Secrets 設計。
- 真寫入要等安全設計完成後（v0.6.9+）才做。

## 6. 認證方式比較

### OAuth（使用者授權）
- 適合：個人 Gmail / 個人 My Drive / 個人 Sheets；使用者授權一次、保存 refresh token。
- 風險：**refresh token 高敏感**（要放 Replit Secrets、不可 commit）；consent / scopes 要控制。
- 建議：優先用**窄 scope**（例如只 `spreadsheets` 或 `drive.file`，避免一開始要完整 Drive 權限）。

### Service Account（server-to-server）
- 適合：寫入「已分享給 SA email」的特定 Sheet、或 Shared Drive / Workspace（可搭 domain-wide delegation）。
- 限制：**個人 Gmail 的 My Drive 不建議直接用 SA 正式寫入**（[[gdrive-service-account-write-limit]]：SA 在個人 My Drive 無儲存配額，無法建立 / 擁有檔案）；SA private key 高敏感；要寫某 Sheet 至少先把該 Sheet 分享給 SA email。

### Shared Drive
- 適合：Workspace / Team；讓 SA 寫入共用空間，比個人 My Drive 更適合自動化。
- 限制：個人帳號可能沒有 Shared Drive；需 Workspace 支援。

**認證結論**：
- **若 Owner 是個人 Gmail（目前情況）→ 優先 OAuth**（寫自己的 Sheets / Drive，窄 scope）。
- 若日後有 Workspace / Shared Drive → 可評估 **Service Account + Shared Drive**。
- **本版不實作，只記錄決策**。已知關鍵限制：SA 無法寫個人 My Drive（要 OAuth 或 Shared Drive）。

## 7. 推薦方向

- 個人 Gmail：**OAuth 優先**。
- Workspace / Shared Drive：可評估 Service Account。
- 長期：**Hybrid（Sheets ledger + Drive artifacts）**。
- 落地節奏：先 mock（v0.6.7），再設計 OAuth/Secrets（v0.6.8），再真寫 pilot（v0.6.9+）。

## 8. 建議環境變數（只列 key 名 / placeholder，不放真值）

| key | 用途 | 分類 |
|---|---|---|
| `RESULT_SINK_ENABLED` | 是否啟用結果落地 | v0.6.6 預設 `false`，不啟用 |
| `RESULT_SINK_TYPE` | `none` / `sheets` / `drive` / `hybrid` | 評估用 |
| `RESULT_SINK_MODE` | `mock` / `real` | 先 `mock` |
| `GOOGLE_AUTH_MODE` | `none` / `oauth` / `service_account` | 評估用 |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | 目標試算表 ID | 未來 mock 可用假值 |
| `GOOGLE_SHEETS_WORKSHEET_NAME` | 工作表名（預設 `tasks`） | 低敏感 |
| `GOOGLE_DRIVE_FOLDER_ID` | artifact 資料夾 ID | 未來 |
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth client id | 高敏感 → Secrets |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth client secret | **高敏感 → Secrets、不進 git** |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | OAuth refresh token | **最高敏感 → Secrets、不進 git** |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | SA 金鑰 JSON（inline） | **最高敏感 → Secrets、不進 git** |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | SA 金鑰檔路徑 | 檔案本身不進 git（gitignore） |

分類：
- **v0.6.6 只評估、不啟用**：全部（`RESULT_SINK_ENABLED=false`）。
- **未來 mock 可用**：`RESULT_SINK_TYPE` / `RESULT_SINK_MODE=mock` / `GOOGLE_SHEETS_WORKSHEET_NAME` / 假 spreadsheet id。
- **高敏感、必須放 Replit Secrets、不可進 git**：`GOOGLE_OAUTH_CLIENT_SECRET`、`GOOGLE_OAUTH_REFRESH_TOKEN`、`GOOGLE_SERVICE_ACCOUNT_JSON`、`GOOGLE_OAUTH_CLIENT_ID`。
- 另：credential JSON 檔（`*service_account*.json` / `*client_secret*.json` / `*token*.json`）建議加進 `.gitignore`（v0.6.7 接 mock 時一併處理）。

> 本版**未改 `.env.example`**（避免引入一堆尚未使用的 key）；上述僅為文件規劃，等 v0.6.7 真正用到再加 placeholder。

## 9. Google Sheets 欄位設計

| 欄位 | MVP 必要 | 說明 |
|---|---|---|
| `task_id` | ✅ | 主鍵 |
| `title` | ✅ | 任務標題 |
| `status` | ✅ | completed / failed / …（終態為主） |
| `safety_level` | ✅ | 0–4 |
| `requires_confirmation` | 後補 | 是否曾需審核 |
| `created_at` | ✅ | 建立時間 |
| `updated_at` | 後補 | 最後更新 |
| `completed_at` | ✅ | 完成時間 |
| `attempts` | 後補 | 嘗試次數 |
| `source` | 後補 | hermes / dashboard 等 |
| `result_summary` | ✅ | 結果摘要（短） |
| `result_uri` | 後補 | Drive 連結（Hybrid 用） |
| `drive_file_id` | 後補 | Drive 檔 id（Hybrid 用） |
| `error` | ✅ | 失敗原因 |
| `metadata_json` | 後補 | 其他 metadata（JSON 字串） |

原則：**長結果全文不直接塞 Sheet**（cell 有長度限制、難讀），改放 Drive 檔（方案 B/C），
Sheet 只存 `result_summary` + `result_uri` / `drive_file_id`。

## 10. 安全邊界

- 不 commit 任何 Google credentials JSON / token / client secret / SA private key。
- 不輸出任何 token / refresh token / private key 真值（readiness 腳本只回報 key 名與 PASS/FAIL）。
- 不直接真寫入 Google（本版零 Google API call）。
- credential 一律放 **Replit Secrets**；檔案型憑證放 gitignored 路徑。
- 真寫入前要先完成 OAuth/Secrets 安全設計（v0.6.8）。

## 11. 建議版本路線

- **v0.6.7**：Google Sheets Mock Sink（假 client / 本地 mock，驗證資料流與欄位，不連真 Google）
- **v0.6.8**：OAuth / Secrets Design（窄 scope、refresh token 管理、Replit Secrets 規劃）
- **v0.6.9**：Google Sheets Write Pilot（真寫入小規模試行，OAuth）
- **v0.7.x**：Drive Artifact Sink（長結果落 Drive，Hybrid）

## 12. 結論

本版只評估。建議**下一步先做 mock sink（v0.6.7），不直接真寫 Google**。
個人 Gmail 情境**優先 OAuth**（SA 無法寫個人 My Drive）；長期走 **Hybrid（Sheets + Drive）**。
所有 credential 一律放 Replit Secrets、永不進 git。
