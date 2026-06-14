# Hermes MCP 串接設定指南

> 讓真實 Hermes Agent 透過一個 MCP 工具 `dispatch_to_openclaw`，把任務交給 Adapter，再由 Adapter 呼叫真實 OpenClaw。
> 本指南對應已實測成功的設定（PONG 端到端通過）。

---

## 1. 目前最終架構

```text
真實 Hermes Agent
   │  呼叫 MCP 工具 dispatch_to_openclaw（typed tool）
   ▼
MCP server  (mcp/openclaw_mcp.py，stdio，跑在 mcp/.venv)
   │  HTTP POST /tasks/dispatch（帶 X-Adapter-Token）
   ▼
Adapter  (FastAPI, app/main.py, port 8000, 跑在 .venv)
   │  asyncio.create_subprocess_exec → openclaw agent --message ... --json
   ▼
真實 OpenClaw  (MiniMax-M3) → 回覆結果
   │
   └─ 結果一路回傳：OpenClaw → Adapter → MCP → Hermes → 使用者
```

## 2. 為什麼用 MCP，而不是直接用 HTTP tool

- Hermes **沒有**「任意 URL + 自訂 header 的通用 HTTP POST 工具」（內建 `web` 只做搜尋/抓網頁）。
- MCP 是 Hermes 官方「給 agent 一個自訂工具」的標準機制。工具有明確輸入欄位（title/goal/task_text…），呼叫穩定、typed、可控，不必每次叫 agent 自己拼 curl。
- 不需要開放 terminal 任意執行，安全性較好。
- 可用 `hermes tools` 開關、`hermes mcp test` 驗證。

## 3. 檔案位置

| 路徑 | 說明 |
|---|---|
| `mcp/openclaw_mcp.py` | MCP server（stdio），提供工具 `dispatch_to_openclaw` |
| `mcp/requirements.txt` | MCP server 依賴（`mcp[cli]`, `httpx`） |
| `mcp/.venv/` | MCP server 專用虛擬環境（**已被 .gitignore 忽略**） |

### ⚠️ 重要：為什麼 MCP 用「獨立 venv」

`mcp` 套件會把 `starlette` / `pydantic` 升到較新版本，而 Adapter 釘死的 `fastapi==0.115.6` 需要舊版 `starlette`。兩者**裝在同一個 venv 會讓 Adapter 壞掉**（實測會出現 `Router.__init__() got an unexpected keyword argument 'on_startup'`）。

因此：
- **Adapter 用 `.venv`**（fastapi/uvicorn/pydantic 2.10.4/starlette 0.41.3）。
- **MCP server 用 `mcp/.venv`**（mcp/httpx，獨立）。
- 兩個 process 各自獨立，互不干擾。

> 如果你曾經 `pip install "mcp[cli]"` 到 Adapter 的 `.venv` 而把它弄壞，修復方式：
> `\.venv/bin/python -m pip install -r requirements.txt`（把 starlette/pydantic 還原到釘住的版本）。

## 4. 安裝（MCP server 的獨立 venv）

```bash
cd ~/projects/hermes-openclaw-adapter
python3 -m venv mcp/.venv
mcp/.venv/bin/pip install -r mcp/requirements.txt
```

## 5. 啟動 Adapter

MCP server 只負責呼叫 Adapter，所以 Adapter 必須先在跑：

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

確認活著：`curl http://127.0.0.1:8000/health`

## 6. 在 Hermes 註冊 MCP server

```bash
hermes mcp add openclaw \
  --command /home/lnovo/projects/hermes-openclaw-adapter/mcp/.venv/bin/python \
  --args   /home/lnovo/projects/hermes-openclaw-adapter/mcp/openclaw_mcp.py \
  --env OPENCLAW_ADAPTER_URL=http://127.0.0.1:8000/tasks/dispatch \
        OPENCLAW_ADAPTER_TOKEN=change-me \
        OPENCLAW_ADAPTER_TIMEOUT_SECONDS=900
```

- 過程會連線、列出工具，然後問 **`Enable all 1 tools? [Y/n/select]:`** → 輸入 **`Y`**。
  （非互動腳本可用 `printf 'y\n' | hermes mcp add ...`。）
- 成功會看到：`Saved 'openclaw' to ~/.hermes/config.yaml (1/1 tools enabled)`。
- 設定寫在 `~/.hermes/config.yaml` 的 `mcp_servers.openclaw`（**不要手改，用 CLI 管理**）。

確認：

```bash
hermes mcp list          # 應看到 openclaw / stdio / all / ✓ enabled
hermes mcp test openclaw # 應看到 ✓ Connected、Tools discovered: 1
```

> 提示：Hermes 若有正在跑的 gateway（tmux `hermes`），新工具通常要**開新 session**才會載入。
> `hermes mcp add` 也會提示「Start a new session to use these tools.」。
> 重啟 gateway：`tmux kill-session -t hermes ; tmux new -d -s hermes hermes gateway run`

## 7. PONG 安全測試

最安全的測試：只要 OpenClaw 回 PONG，不碰檔案、不執行外部動作。

**(a) 只測 MCP server 連線：**
```bash
hermes mcp test openclaw
```

**(b) 端到端（先確定 Adapter 在跑）：** 在 `hermes chat` 或一次性 `hermes -z` 裡叫它呼叫工具：

```bash
hermes -z '請呼叫 dispatch_to_openclaw 工具：title="PONG 安全測試"；goal="連線測試"；task_text="請只回覆 PONG，不要操作任何檔案、不要執行外部動作。"；priority="low"；metadata={"source":"hermes_mcp_test","workflow":"connectivity_test"}。把工具回傳的 ok/adapter_status/transport/task_id 與 openclaw_response 最終文字回報給我。' --yolo
```

> `--yolo` 是為了讓非互動（無 TTY）情況下自動通過工具審批；正式互動使用時可省略，由你手動核准。
> 本測試任務只回 PONG，無副作用。

## 8. 成功時應該看到什麼

- Hermes 回報：`ok: true`、`adapter_status: "sent"`、`transport: "cli"`、`task_id: task-xxxx`、`openclaw_response` 最終文字 = **`PONG`**。
- Adapter log：`POST /tasks/dispatch HTTP/1.1 200 OK`。
- `data/tasks.jsonl` 最後一筆：同一個 `task_id`、`adapter_status: sent`、openclaw 文字 `PONG`。
- **三處的 task_id 一致 = 整條鏈真的通了**（不是 Hermes 自己亂回）。

## 9. 常見錯誤排查

| 症狀 | 原因 | 解法 |
|---|---|---|
| `hermes mcp add` 連到一半就結束、`mcp list` 仍空 | 卡在 `Enable all tools?` 互動提示（無 TTY → EOF） | 互動輸入 `Y`，或 `printf 'y\n' | hermes mcp add ...` |
| 工具回 `error: 無法連線到 Adapter` | Adapter 沒啟動 | 先啟動 uvicorn（第 5 節） |
| 工具回 `HTTP 401/403` | token 不一致 | `OPENCLAW_ADAPTER_TOKEN`（MCP）要等於 `HERMES_ADAPTER_TOKEN`（Adapter `.env`） |
| 工具回 `HTTP 422` | 缺必填欄位 `task_text` | 呼叫工具時一定要給 `task_text` |
| 工具回逾時 | 任務太重 / OpenClaw 卡住 | 調大 `OPENCLAW_ADAPTER_TIMEOUT_SECONDS`；確認 `openclaw status` |
| Adapter 啟動就壞（`on_startup` TypeError） | 不小心把 `mcp` 裝進 Adapter `.venv` 升級了 starlette | `\.venv/bin/python -m pip install -r requirements.txt` 還原 |
| Hermes 看不到工具 | 舊 session 沒載入新 MCP | 開新 session / 重啟 gateway |
| `mcp test` 連不上 | server 路徑或 venv 有誤 | 確認 `mcp/.venv/bin/python` 與 `mcp/openclaw_mcp.py` 存在 |

## 10. 如何移除 MCP 註冊

```bash
hermes mcp remove openclaw      # 或 hermes mcp rm openclaw
hermes mcp list                 # 確認已移除
```

（移除只是把 `mcp_servers.openclaw` 從 `~/.hermes/config.yaml` 拿掉；`mcp/openclaw_mcp.py` 與 `mcp/.venv` 仍在專案內。）

## 11. 安全提醒

- 這個工具會讓 OpenClaw **真的執行**任務（並消耗模型額度），請只送清楚、可驗證的任務。
- 高風險動作（改檔 / 刪資料 / 登入 / 操作平台 / 對外發送訊息）**先問使用者確認**。
- **不要**把密碼、API key、token、cookie、個資寫進 `task_text` 或 `metadata`。
- 測試一律先用 PONG。
