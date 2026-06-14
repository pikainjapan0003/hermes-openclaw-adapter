# Hermes → Adapter → OpenClaw

把任務從 **Hermes 主腦**送到 **OpenClaw 執行端**的中間轉接層（Adapter）。
Hermes 透過 MCP 工具呼叫 Adapter，Adapter 在背景用 **OpenClaw CLI** 執行，完成後把結果寫進 `results.jsonl`，Hermes 再查回結果。

```text
Discord / Hermes 聊天
        ↓
Hermes 主腦  ──(MCP: dispatch_to_openclaw / get_openclaw_task_result)──┐
        ↓                                                              │
Adapter (FastAPI, :8000)  POST /tasks/dispatch → 背景執行             │
        ↓                                                              │
OpenClaw CLI (openclaw agent ...)                                     │
        ↓                                                              │
data/results.jsonl  ──(GET /tasks/{id}/result)───────────────────────┘
```

---

## 目前版本

**`v0.4.1-discord-e2e-verified`**（async background + callback，已完成 Discord 端到端驗證）

> 完整驗收報告：[`docs/V0.4_DISCORD_E2E_VERIFICATION.md`](docs/V0.4_DISCORD_E2E_VERIFICATION.md)

### 已完成

- ✅ **Hermes MCP 串接** —— stdio MCP server（`mcp/openclaw_mcp.py`），暴露兩個工具
- ✅ **Adapter v0.4 async background + callback** —— `POST /tasks/dispatch` 立刻回 `accepted` + `task_id`，任務在背景執行
- ✅ **OpenClaw CLI 背景執行** —— `openclaw agent --message ... --json`（不經 shell）
- ✅ **`results.jsonl`** —— 每筆任務結果寫入 `data/results.jsonl`（TaskResult schema v1：`completed` / `failed`）
- ✅ **`get_openclaw_task_result`** —— 用 `task_id` 查 `completed` / `result_text`
- ✅ **Discord E2E 驗證** —— Discord → Hermes → MCP → Adapter v0.4 → OpenClaw → `results.jsonl`，實測 `completed` / `PONG`（`task-b7c8c2dd81d9`）
- ✅ **GitHub 備份** —— `master` 與全部 tags（`v0.1` ～ `v0.4.1`）已推上 GitHub private repo

### 目前限制

- ⛔ **還沒有 Queue**（目前用 FastAPI BackgroundTasks，單機背景執行）
- ⛔ **還沒有 DLQ**（失敗任務沒有死信佇列 / 自動重試編排）
- ⚠️ **Adapter / Hermes Gateway 目前不是開機自動啟動** —— WSL/機器重啟後要手動拉起
- ⚠️ **新增 MCP tool 後需要重啟 Hermes Gateway** —— 長駐 Gateway 只在啟動時載入一次 MCP 工具清單；新註冊的工具要重啟才看得到（細節見驗收報告第 8、9 節）

---

## 新手小白操作

> 前提：在 **WSL Ubuntu**、用跟 OpenClaw 同一個使用者執行（才讀得到 `~/.openclaw` 與 gateway token），且 `openclaw` 指令在 PATH 內。專案位置：`~/projects/hermes-openclaw-adapter`。

### 1. 啟動 Adapter v0.4

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

要常駐在背景（關掉終端機也不中斷）可以：

```bash
setsid nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env \
  > /tmp/adapter_v04.log 2>&1 < /dev/null &
```

> 第一次安裝套件：`python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`，
> 並 `cp .env.example .env`（`.env` 不會進 git）。

### 2. Health check（確認是 v0.4）

```bash
curl http://127.0.0.1:8000/health
```

應看到 `"version":"0.4.0"`：

```json
{"ok":true,"app":"Hermes OpenClaw Adapter","version":"0.4.0",
 "mode":"async-background+callback","callback_enabled":true,
 "callback_mode":"ledger_only","token_required":true}
```

### 3. 跑一次 PONG 測試（最安全的連線驗證）

```bash
./scripts/test_callback_pong.sh
```

會立刻回 `accepted` 與一個 `task_id`：

```json
{"status":"accepted","task_id":"task-xxxxxxxxxxxx",
 "message":"任務已送出，OpenClaw 會在背景執行，完成後 callback Hermes。"}
```

> 這個任務內容是「請只回覆 PONG，不要操作任何檔案、不要登入、不要下單、不要發訊息」（安全等級 Level 0），不會產生任何副作用。

### 4. 查任務結果

把上一步拿到的 `task_id` 帶進去：

```bash
./scripts/check_task_result.sh task-xxxxxxxxxxxx
```

成功時會看到 `completed` 與 `PONG`：

```json
{"task_id":"task-xxxxxxxxxxxx",
 "task":{"status":"completed", ...},
 "result":{"status":"completed","result_text":"PONG","error":null}}
```

> 背景任務需要幾十秒跑完；剛送出馬上查可能是 `running`，稍等再查即可。

### 5. 看完整驗收報告

```bash
less docs/V0.4_DISCORD_E2E_VERIFICATION.md
```

裡面有這次正式切換 + Discord 端到端驗證的所有佐證（health、gateway 重啟、MCP 載入、task_id、`tasks.jsonl` / `results.jsonl` 紀錄、根因分析）。

---

## 專案結構（重點）

```text
hermes-openclaw-adapter/
├── app/main.py                       # Adapter 主程式（dispatch / result / 背景執行 / callback）
├── mcp/openclaw_mcp.py               # Hermes 端 stdio MCP server（dispatch_to_openclaw / get_openclaw_task_result）
├── scripts/
│   ├── test_callback_pong.sh         # 送一個 Level 0 PONG 任務
│   └── check_task_result.sh          # 用 task_id 查結果
├── data/                             # 執行期產生（tasks.jsonl / results.jsonl）— 不進 git
├── docs/
│   ├── V0.4_DISCORD_E2E_VERIFICATION.md   # 本版驗收報告
│   ├── V0.4_CALLBACK_MVP.md
│   ├── HERMES_MCP_SETUP.md
│   └── ...
├── .env.example                      # 環境變數範本（.env 不進 git）
└── README.md
```

---

## API 速查

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/health` | 健康檢查（免 token） |
| POST | `/tasks/dispatch` | 派任務，立刻回 `accepted` + `task_id`（需 `X-Adapter-Token`） |
| GET | `/tasks/{task_id}` | 查任務狀態 |
| GET | `/tasks/{task_id}/result` | 查任務結果（`completed` / `result_text`） |

> 認證用 header `X-Adapter-Token`（不是 `Authorization: Bearer`）。token 在 `.env` 的 `HERMES_ADAPTER_TOKEN`。

---

## 下一步建議

1. **`v0.4.2-service-units`** —— 把 Adapter 與 Hermes Gateway 做成 systemd unit，開機自動啟動、崩潰自動重啟（解掉目前「要手動拉起」的限制）。
2. **`v0.5-queue-worker`** —— 之後才導入 Queue / Worker（以及 DLQ、重試編排），提升吞吐與失敗韌性。

> 維持原則：先穩定運維（service units），再擴充架構（queue）。
