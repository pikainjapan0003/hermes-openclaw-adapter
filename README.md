# Hermes → Adapter → OpenClaw MVP 專案

這是一個給新手小白使用的最小可行版本專案。

目標只有一個：

```text
Hermes 主腦
↓
Adapter 翻譯官
↓
OpenClaw 執行端
```

這版先不做 Queue，也先不做 Callback。  
先確認 Hermes 可以成功派任務給 OpenClaw。

---

## 1. 這個專案在做什麼？

這個 Adapter 是中間轉接層。

Hermes 送來這種任務：

```json
{
  "title": "整理商品資料",
  "goal": "找出商品價格與來源",
  "task_text": "請幫我整理指定商品的名稱、價格、來源與備註"
}
```

Adapter 會把它翻譯成一段清楚的任務文字，再透過 **OpenClaw CLI**（`openclaw agent --message "..." --json`）派給真實 OpenClaw。

> 為什麼是 CLI？因為真實 OpenClaw 沒有可直接 POST 的 REST/Webhook 任務 API，它是 WebSocket Gateway。
> CLI 會自動處理 token 與連線握手，是新手最容易先跑通的真實入口。
> （本機快速測試時，也可以維持舊的 Mock 模式，見下方。）

---

## 2. 專案結構

```text
hermes-openclaw-adapter/
├── app/
│   └── main.py                  # Adapter 主程式
├── mock_openclaw_server.py       # 假的 OpenClaw，方便本機測試
├── scripts/
│   └── test_send_task.py         # 測試送任務腳本
├── docs/
│   ├── ARCHITECTURE.md           # 架構說明
│   ├── HERMES_PROMPT_TEMPLATE.md # Hermes 端提示詞模板
│   └── TASK_FORMAT.md            # 任務格式說明
├── .env.example                  # 環境變數範本
├── requirements.txt              # Python 套件
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 3. 本機啟動方式

### 第一步：安裝套件

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 第二步：建立 `.env`

```bash
cp .env.example .env
```

Windows 可直接複製 `.env.example`，重新命名成 `.env`。

---

### 第三步：先開假的 OpenClaw 測試服務

開第一個終端機：

```bash
uvicorn mock_openclaw_server:app --reload --port 9000
```

這會啟動一個假的 OpenClaw：

```text
http://127.0.0.1:9000/openclaw/webhook
```

---

### 第四步：啟動 Adapter

開第二個終端機：

```bash
uvicorn app.main:app --reload --port 8000
```

Adapter 會在：

```text
http://127.0.0.1:8000
```

---

### 第五步：測試送任務

開第三個終端機：

```bash
python scripts/test_send_task.py
```

成功時會看到：

```json
{
  "ok": true,
  "adapter_status": "sent",
  "message": "任務已轉送給 OpenClaw。"
}
```

---

## 4. 用 curl 測試

```bash
curl -X POST "http://127.0.0.1:8000/tasks/dispatch" \
  -H "Content-Type: application/json" \
  -H "X-Adapter-Token: change-me" \
  -d '{
    "title": "第一個測試任務",
    "goal": "確認 Hermes 可以透過 Adapter 派任務給 OpenClaw",
    "task_text": "請回覆：OpenClaw 已收到任務。",
    "priority": "normal"
  }'
```

---

## 5. Docker 啟動方式

你也可以用 Docker 一次啟動 Adapter + 假 OpenClaw。

```bash
docker compose up --build
```

測試：

```bash
python scripts/test_send_task.py
```

---

## 5.5 真實 OpenClaw CLI 模式啟動方式（正式串接）

這是把 Adapter 接到**真實 OpenClaw**的方式。Adapter 會用
`asyncio.create_subprocess_exec` 呼叫 OpenClaw CLI（不經過 shell）：

```bash
openclaw agent --message "<Hermes 任務內容>" --json --timeout 600
```

### 前置條件

- Adapter 必須跑在**能存取 `openclaw` 指令的環境**（例如 WSL Ubuntu，且 PATH 內有 `openclaw`）。
- 用跟 OpenClaw 同一個使用者執行（才讀得到 `~/.openclaw/openclaw.json` 與 gateway token）。
- 先手動確認 OpenClaw 正常：

  ```bash
  openclaw status
  openclaw gateway call health --json
  ```

### 第一步：設定 `.env`

```env
HERMES_ADAPTER_TOKEN=change-me
OPENCLAW_TRANSPORT=cli
OPENCLAW_CLI_BIN=openclaw
OPENCLAW_CLI_TIMEOUT_SECONDS=600
# 可選：OPENCLAW_AGENT_ID=main
DATA_DIR=data
```

> 若暫時沒有 OpenClaw，可把 `OPENCLAW_TRANSPORT=dry_run`，Adapter 只會組任務文字、不真的呼叫 CLI。

### 第二步：啟動 Adapter

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

### 第三步：送一個安全測試任務

```bash
python scripts/test_send_task.py
```

這個測試任務的內容是「**請只回覆 PONG，不要操作任何檔案、不要執行外部動作**」，
所以不會讓 OpenClaw 產生任何副作用，適合第一次驗證連線。

成功時會看到類似：

```json
{
  "ok": true,
  "adapter_status": "sent",
  "transport": "cli",
  "task_id": "task-xxxxxxxx",
  "openclaw_response": { "...": "OpenClaw agent 的 JSON 回覆" }
}
```

失敗時會看到：

```json
{
  "ok": false,
  "adapter_status": "failed",
  "transport": "cli",
  "task_id": "task-xxxxxxxx",
  "error": "OpenClaw CLI 以非零代碼結束 ...",
  "stderr": "...",
  "exit_code": 1
}
```

> 注意：`openclaw agent` 真的會呼叫模型（會消耗額度），逾時也較長（預設 600 秒）。
> 因此測試腳本的 HTTP 逾時會自動設得比 CLI 逾時更長。

---

## 6. Replit 使用方式

1. 建立新的 Replit Python 專案
2. 把這個專案檔案上傳
3. 在 Secrets 加入：

```text
HERMES_ADAPTER_TOKEN=change-me
OPENCLAW_TRANSPORT=dry_run
```

> 注意：Replit 等遠端容器裡通常**沒有 `openclaw` 指令**，無法用 CLI 模式。
> 在 Replit 建議先用 `OPENCLAW_TRANSPORT=dry_run` 測流程；要真的串 OpenClaw，
> 請把 Adapter 跑在與 OpenClaw 同一台機器（WSL），或改用 WebSocket RPC 模式。

4. Run 指令使用：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 7. 正式接 OpenClaw 時要改哪裡？

最重要的是 `.env`：

```env
OPENCLAW_TRANSPORT=cli
OPENCLAW_CLI_BIN=openclaw
OPENCLAW_CLI_TIMEOUT_SECONDS=600
```

如果要調整「組給 OpenClaw 的任務文字長相」，請改這個 function：

```python
build_openclaw_message()
```

如果要調整「實際呼叫 OpenClaw 的指令」（例如加參數、改成別的子指令），請改：

```python
build_openclaw_command()   # 組指令
run_openclaw_cli()         # 用 asyncio.create_subprocess_exec 執行
```

位置都在：

```text
app/main.py
```

這就是 Adapter 的核心翻譯與執行區。

---

## 8. Hermes 端要怎麼接？

Hermes 只要能呼叫 HTTP API，就送 POST 到：

```text
POST /tasks/dispatch
```

Header：

```text
X-Adapter-Token: change-me
```

Body：

```json
{
  "title": "任務標題",
  "goal": "任務目標",
  "task_text": "完整任務內容",
  "priority": "normal",
  "metadata": {}
}
```

---

## 9. 第一版成功標準

只要你做到下面這件事，就算第一版成功：

```text
Hermes 發任務
↓
Adapter 收到任務
↓
Adapter 轉成 OpenClaw 格式
↓
OpenClaw 收到任務
```

這就是 Hermes → Adapter → OpenClaw 的 MVP。

---

## 10. 下一版才做什麼？

第一版完成後，再做：

```text
OpenClaw → Callback → Hermes
```

再下一版才做：

```text
Hermes → Adapter → Queue → OpenClaw Worker
```
