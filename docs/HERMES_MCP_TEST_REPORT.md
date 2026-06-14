# Hermes MCP 串接測試報告

> 測試日期：2026-06-14
> 結論：**整條鏈路全部通過 ✅**　Hermes → MCP → Adapter → 真實 OpenClaw → PONG。

---

## 1. MCP server 是否建立成功 → ✅ 是

- 檔案：`mcp/openclaw_mcp.py`（stdio MCP server，工具 `dispatch_to_openclaw`）。
- 依賴：`mcp/requirements.txt`（`mcp[cli]`, `httpx`），裝在獨立 venv `mcp/.venv`。
- 獨立連線測試（不經 Hermes，直接用 MCP client 連 server）：
  ```text
  server initialized: openclaw 1.27.2
  tool count: 1
  TOOL: dispatch_to_openclaw
    props: ['title', 'goal', 'task_text', 'priority', 'metadata']
    required: ['title', 'goal', 'task_text']
  ```

## 2. Hermes MCP 是否註冊成功 → ✅ 是

- 指令：`hermes mcp add openclaw --command .../mcp/.venv/bin/python --args .../mcp/openclaw_mcp.py --env ...`
- 結果：`Saved 'openclaw' to ~/.hermes/config.yaml (1/1 tools enabled)`
- `hermes mcp list`：
  ```text
  Name        Transport                    Tools   Status
  openclaw    /home/lnovo/projects/herm…   all     ✓ enabled
  ```
- `hermes mcp test openclaw`：
  ```text
  Transport: stdio → .../mcp/.venv/bin/python
  Auth: none
  ✓ Connected (2847ms)
  ✓ Tools discovered: 1
  ```

> 註：第一次 `mcp add` 卡在互動提示 `Enable all 1 tools? [Y/n/select]`，在無 TTY 環境會 EOF 中止而沒存檔。用 `printf 'y\n' | hermes mcp add ...` 回答後即成功存檔。

## 3. Adapter 是否啟動成功 → ✅ 是

```text
GET /health → {"ok":true,"app":"Hermes OpenClaw Adapter","transport":"cli",
               "openclaw_cli_bin":"openclaw","openclaw_cli_timeout_seconds":600.0,
               "token_required":true}
```

## 4. PONG 端到端測試是否成功 → ✅ 成功

透過 `hermes -z "...呼叫 dispatch_to_openclaw..." --yolo` 觸發，Hermes 自動呼叫 MCP 工具。

**Hermes 回報：**
```text
ok: true
adapter_status: "sent"
transport: "cli"
task_id: "task-f1ac05baf045"
openclaw_response 最終文字: "PONG"
```

**Adapter HTTP log（證明 POST 確實由 MCP 送達）：**
```text
INFO: 127.0.0.1 - "GET  /health HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /tasks/dispatch HTTP/1.1" 200 OK
```

**Adapter `data/tasks.jsonl` 最後一筆：**
```text
task_id: task-f1ac05baf045
adapter_status: sent
openclaw text: PONG
```

> 🔑 **關鍵佐證**：同一個 `task_id = task-f1ac05baf045` 同時出現在
> (a) Hermes 的工具回傳、(b) Adapter 的 HTTP log、(c) Adapter 的 tasks.jsonl —
> 證明這是真實鏈路，不是 Hermes 自己回 PONG。

## 5. 測試指令

```bash
# (a) MCP server 獨立連線
hermes mcp test openclaw

# (b) 啟動 Adapter
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env

# (c) 端到端（另一個終端機）
hermes -z '請呼叫 dispatch_to_openclaw 工具：title="PONG 安全測試"；goal="連線測試"；task_text="請只回覆 PONG，不要操作任何檔案、不要執行外部動作。"；priority="low"；metadata={"source":"hermes_mcp_test","workflow":"connectivity_test"}。把工具回傳結果回報給我。' --yolo
```

## 6. 成功輸出摘要

| 檢查點 | 結果 |
|---|---|
| MCP server 建立 | ✅ `mcp/openclaw_mcp.py`，1 個工具 |
| Hermes 註冊 MCP | ✅ `openclaw` enabled in config.yaml |
| `hermes mcp test` | ✅ Connected 2847ms |
| Adapter 啟動 | ✅ /health ok |
| Hermes 呼叫工具 | ✅ dispatch_to_openclaw 被呼叫 |
| MCP → Adapter POST | ✅ 200 OK |
| Adapter → OpenClaw CLI | ✅ adapter_status=sent |
| OpenClaw 回 PONG | ✅ openclaw text = PONG |
| Hermes 看到 PONG | ✅ 已回報 |

## 7. 如果失敗，失敗原因與下一步

本次最終**成功**。過程中遇到並已解決的一個問題（記錄供參考）：

- **問題**：原本依指示把 `mcp[cli]` 裝進 Adapter 的 `.venv`，導致 `starlette` 升級、Adapter 啟動時 `Router.__init__() got an unexpected keyword argument 'on_startup'`。
- **原因**：`mcp` 需要較新的 starlette/pydantic，與 `fastapi==0.115.6` 衝突。
- **解法**：把 Adapter `.venv` 還原（`pip install -r requirements.txt`），並把 MCP server 改裝在**獨立 venv `mcp/.venv`**。兩個 process 各自獨立，問題消失。

未來若失敗，依 `docs/HERMES_MCP_SETUP.md` 第 9 節排查表處理（Adapter 沒啟動 / token 不符 / 缺 task_text / 逾時 / 舊 session 沒載入工具 等）。

## 8. 怎樣才算整條鏈路已通

判準（本次全部達成 ✅）：

1. `hermes mcp test openclaw` 連線成功。
2. Adapter `/health` 正常。
3. 在 Hermes 給一個 PONG 任務，Hermes **自動**呼叫 `dispatch_to_openclaw`。
4. Adapter 收到 `POST /tasks/dispatch` 並回 200。
5. 回傳含 `ok:true`、`adapter_status:"sent"`、`openclaw_response` 最終文字 = `PONG`。
6. Hermes、Adapter log、tasks.jsonl 三處 `task_id` 一致。

→ **結論：整條鏈路已通。** 下一步可開始設計第一個安全的真實小任務（例如「三點摘要」），或視需要再做 Callback / Queue（目前不需要）。

---

## 第一個安全真實小任務測試

> 測試日期：2026-06-14（PONG 之後的進階驗證）

### 1. 測試目標

確認 `Hermes → MCP → Adapter → OpenClaw` 不只會回 PONG，**也能完成一個安全的真實文字整理任務**。

### 2. 任務內容

- **title**：第一個安全真實小任務：三點摘要
- **goal**：確認 Hermes 可以透過 MCP 把一個簡單文字整理任務交給 OpenClaw，並取得可讀結果。
- **task_text**：
  ```text
  請閱讀以下需求，整理成三點摘要。不要操作任何檔案、不要執行外部命令、不要登入任何帳號、不要呼叫任何外部平台。

  需求內容：
  我正在建立一套 Hermes + OpenClaw 多 AI Agent 工作流系統。Hermes 負責主腦、規劃、記憶、任務拆解；OpenClaw 負責執行、自動化、任務落地。中間透過 MCP tool 與 Adapter 串接，Adapter 再呼叫真實 OpenClaw CLI。
  ```
- **priority**：low
- **metadata**：`{"source":"hermes_mcp_real_task_test","workflow":"first_safe_real_task"}`

### 3. 測試結果（第二次完整成功）

- **task_id**：`task-2000b69a1a97`
- **OpenClaw 回傳三點摘要**：
  1. **角色分工**：Hermes 主腦，負責規劃、記憶、任務拆解；OpenClaw 執行端，負責自動化與任務落地。
  2. **串接介面**：兩者透過 MCP tool + Adapter 中介層串接，而非直接呼叫。
  3. **呼叫鏈**：Adapter 進一步呼叫真實 OpenClaw CLI 執行底層操作。

### 4. 驗證證據

- ✅ Hermes **自動呼叫** MCP tool `dispatch_to_openclaw`（Hermes 自述：「已透過 MCP stdio 呼叫 dispatch_to_openclaw，不是用 curl」）。
- ✅ MCP server log（`~/.hermes/logs/mcp-stderr.log`）有 **`CallToolRequest`** → 緊接 `HTTP Request: POST http://127.0.0.1:8000/tasks/dispatch "HTTP/1.1 200 OK"`。
- ✅ Adapter 收到 **`POST /tasks/dispatch` 並回 `200 OK`**。
- ✅ `data/tasks.jsonl` 有同一個 **`task_id: task-2000b69a1a97`**（`adapter_status: sent`、title 一致），且行數 +1（剛好新增一筆）。
- ✅ Hermes **看得到** OpenClaw 回傳的三點摘要，並完整回報給使用者（Hermes exit code 0）。
- ✅ 整條鏈路**不是人工 curl**，也**不是直接呼叫 Adapter 或 OpenClaw CLI** —— 完全由 Hermes 經 MCP 工具觸發。

### 5. 第一次 timeout 說明

第一次測試把 narration 的 timeout 設為 **320 秒**；因為「三點摘要」比 PONG 重，Hermes 在**工具已完成**但要輸出最終回覆時被 timeout 截斷（鏈路本身仍成功，task 與摘要都有正常產生，task_id 為 `task-c70455d71eea`）。
第二次把 timeout 調整為 **600 秒**後完整成功。
→ 這是**測試腳本 timeout 設定問題，不是系統串接問題**。

### 6. 結論

`Hermes → MCP → Adapter → OpenClaw CLI → 真實 OpenClaw → 回傳 Hermes` 已完成**非 PONG 真實小任務**驗證。
**可以確認第一個安全真實小任務跑通。**
