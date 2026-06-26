# Hermes x OpenClaw Backup / GitHub Remote Push Plan

> 本文件是「push 前的計畫與檢查紀錄」。**本版（v0.5.9）不 push。**
> 真正的 push 必須等 **owner 明確批准** 後才執行。

---

## 1. 目前狀態

| 項目 | 值 |
|---|---|
| branch | `master` |
| latest commit | `d7dd5f6 docs: add operator guide` |
| latest tag | `v0.5.8-operator-guide` |
| unpushed commit count | **12**（`origin/master..master`） |
| unpushed tags | **9**：`v0.5.0-local-queue-worker` … `v0.5.8-operator-guide` |

未 push 的 commits（舊 → 新）：

```text
a3eb922 docs: add phase 2 callback closing report
0e06770 docs: record Google Drive / Sheets linkage
0bd2a65 feat: add local queue worker MVP
e6b5297 docs: add v0.5 queue MVP closing report
1e22e37 feat: add queue observability endpoints
41d1969 feat: add read-only queue dashboard
6c8ec45 feat: add blackboard task comments
8e7ade3 feat: add approval flow for reviewed tasks
0213e31 feat: add limited queue control actions
0edc7ed feat: add system health and worker heartbeat
1606012 style: polish dashboard ux
d7dd5f6 docs: add operator guide
```

未 push 的 tags（遠端目前只有到 `v0.4.2-service-helper-scripts`）：

```text
v0.5.0-local-queue-worker
v0.5.1-queue-observability
v0.5.2-read-only-dashboard
v0.5.3-blackboard-comments
v0.5.4-approval-flow
v0.5.5-limited-control-actions
v0.5.6-system-health-worker-heartbeat
v0.5.7-dashboard-polish
v0.5.8-operator-guide
```

---

## 2. Remote 檢查

| 項目 | 值 |
|---|---|
| remote name | `origin` |
| remote URL（遮蔽） | `https://github.com/pikainjapan0003/hermes-openclaw-adapter.git` |
| URL 是否含 token | 否（乾淨 HTTPS，無內嵌憑證可遮蔽） |
| 是否為 GitHub | 是 |
| credential helper | 無（`git config credential.helper` 為空） |

### ⚠️ Repo 可見性：看起來是 **PUBLIC**（需 owner 確認）

本機觀測：

- `git ls-remote`（停用 credential helper、`GIT_TERMINAL_PROMPT=0`）**仍可匿名讀到** `refs/heads/master`。
- 匿名打 `https://api.github.com/repos/pikainjapan0003/hermes-openclaw-adapter` 回 **HTTP 200**（GitHub 對「私有 repo 的匿名請求」會回 404）。

→ 綜合判斷：**這個 repo 目前極可能是 public。** 這與先前筆記提到的「private repo」不一致。

**這是一個需要 owner 先確認的重點：**
- 如果 owner 本來就要公開 → 沒問題（且我們的 secrets scan 乾淨，見第 3 節）。
- 如果 owner 原本以為是 private → 請先到 GitHub 把 repo 設成 private，**再** push；否則 v0.5.x 的程式碼一 push 就會公開。
- 注意：v0.1–v0.4.2 的歷史 commit/tag 其實**已經在這個 public repo 上**了。

---

## 3. Push 前安全檢查

### .gitignore 狀態
v0.5.9 已補強，現涵蓋：`.env`、`.venv/`（同時匹配 `mcp/.venv/`）、`venv/`、`__pycache__/`、`*.pyc`、
`data/`、`*.db`、`queue.db`、`results.jsonl`、`tasks.jsonl`、`node_modules/`、`*.log`、
`OPENCLAW_INTEGRATION_DIAGNOSIS.md`、`.DS_Store`。
（本版新增：`node_modules/`、`*.db`、`queue.db`、`results.jsonl`、`tasks.jsonl` 防呆。）

### tracked files 是否有 secrets / 執行期資料
- `git ls-files` 共 **62** 個 tracked 檔。
- 篩 `.env` / `data/` / `queue.db` / `*.jsonl` / `.venv/` / `mcp/.venv/` / `node_modules/`：**全部沒有被追蹤**。

| 檢查項 | 結果 |
|---|---|
| `.env` 是否未被追蹤 | ✅ 未追蹤（在 .gitignore） |
| `data/` 是否未被追蹤 | ✅ 未追蹤 |
| `queue.db` 是否未被追蹤 | ✅ 未追蹤 |
| `results.jsonl` / `tasks.jsonl` | ✅ 未追蹤 |
| `.venv/` / `mcp/.venv/` / `node_modules/` | ✅ 未追蹤 |

### secrets scan 結果
對 tracked 檔掃描高風險樣式：`sk-…`、`ghp_…`、`xox[baprs]-…`、`AIza…`、`-----BEGIN … PRIVATE KEY-----`
→ **零命中**。

關鍵字（`OPENAI_API_KEY` / `DISCORD_TOKEN` / `ADAPTER_TOKEN` / `GITHUB_TOKEN` / `Bearer` / `token=` / `password=`）
出現處皆為**程式識別字 / 環境變數名稱 / 函式參數**（例如 `require_token`、`x_adapter_token`、
mcp 錯誤訊息提到 `OPENCLAW_ADAPTER_TOKEN` 變數名），**沒有任何真實值**。

`.env.example` 只含 placeholder（`change-me`、`replace-me-long-random-secret`、預設數字、localhost URL），
**不含真實 secret**。

**結論：secrets scan 乾淨，沒有偵測到需要阻擋 push 的敏感內容。**

---

## 4. 測試結果（push 前穩定性）

| 測試 | 結果 |
|---|---|
| test_queue_store | ✅ |
| test_queue_observability | ✅ |
| test_dashboard_readonly | ✅ |
| test_blackboard_comments | ✅ |
| test_approval_flow | ✅ |
| test_limited_control_actions | ✅ |
| test_system_health | ✅ |
| test_dashboard_polish | ✅ |
| test_docs_operator_guide | ✅ |
| FastAPI import | ✅ OK |
| smoke_test_queue | ✅ PASS（PONG） |

---

## 5. Dry-run 結果

```bash
git push --dry-run origin master
git push --dry-run origin --tags
```

兩個 dry-run 都因為**缺少憑證**而停在認證階段：

```text
fatal: could not read Username for 'https://github.com': terminal prompts disabled
```

說明：

- 本機 remote 是 **HTTPS 且未設定 credential helper / 未快取憑證**；在非互動環境（停用 prompt）下，
  連 dry-run 都無法完成「會推什麼」的比對。
- 因此 **實際 push 必須由 owner 在可輸入憑證的環境** 執行（GitHub PAT，或把 remote 換成 SSH）。
- 這不是錯誤，只是代表：push 這一步天然需要 owner 的 GitHub 認證，無法在這個自動化環境內代為完成。

> 關於 `--tags`：遠端已有 v0.1–v0.4.2，`--tags` 會嘗試比對/推送**所有**本機 tag。
> 建議**不要無腦 `--tags`**，改用第 6 節的「逐一指定 v0.5.x tag」較安全、可控。

---

## 6. 建議正式 push 步驟（**等 owner 明確批准後才執行**）

> 前置：先確認第 2 節的 repo 可見性符合預期（若該 private 卻是 public，先改設定）。
> 並先設定好認證（GitHub PAT over HTTPS，或 `git remote set-url origin git@github.com:…` 走 SSH）。

**步驟 1 — 推 master：**

```bash
git push origin master
```

**步驟 2 — 逐一指定推 v0.5.x tags（不要用 `--tags`）：**

```bash
git push origin v0.5.0-local-queue-worker
git push origin v0.5.1-queue-observability
git push origin v0.5.2-read-only-dashboard
git push origin v0.5.3-blackboard-comments
git push origin v0.5.4-approval-flow
git push origin v0.5.5-limited-control-actions
git push origin v0.5.6-system-health-worker-heartbeat
git push origin v0.5.7-dashboard-polish
git push origin v0.5.8-operator-guide
```

> 若本機 tag 名稱與上面不同，以 `git tag` 實際輸出為準。
> （v0.5.9 封版後若也要備份，再補 `git push origin v0.5.9-backup-push-plan`。）

---

## 7. Rollback / 保守方案

- **push master 成功但 tag 失敗** → master 已是最新，安全；之後再單獨補推失敗的那個 tag
  （`git push origin <tag-name>`），不需 reset、不需 force。
- **remote 不是預期 repo**（URL / owner 不對）→ **停止**，先 `git remote set-url` 修正並重新確認。
- **repo 可見性不符預期**（該 private 卻 public）→ **停止**，先在 GitHub 改可見性再 push。
- **secrets scan 有疑慮** → **停止**，先處理掉敏感內容（並考慮歷史改寫）再 push。
- **dry-run / push 因認證失敗** → **停止**，先設定 PAT 或 SSH，不要把 token 寫進 remote URL 或文件。
- **owner 未明確批准** → **停止**，不 push。
- 全程**不要** `git push --force`、不要 `--force-with-lease`（本計畫是純新增推送，不需覆寫歷史）。

---

## 8. 不做事項（本版 v0.5.9）

- 本版**不 push**（不 `git push`、不 `git push --tags`）。
- **不部署**。
- **不用 Replit**。
- **不改功能**（不動 Hermes / OpenClaw / Discord / MCP / worker / Queue 狀態機 / Dashboard 功能）。
- **不改 `.env`**。
- **不清理外來 `HEAD` 檔**（維持不動，等 owner 確認）。
- 本版只做：盤點、安全檢查、secrets scan、dry-run、文件化。
