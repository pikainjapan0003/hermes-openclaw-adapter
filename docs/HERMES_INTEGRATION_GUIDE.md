# Hermes 接入 Adapter 完整準備文件

> 給新手小白看的版本。
> 目的：等「真實 Hermes Agent」未來能呼叫外部 HTTP / tool / skill 時，可以直接照這份文件實測，把任務送進 Adapter → 真實 OpenClaw。
> 本文件只做說明，**沒有修改任何核心程式**。所有 endpoint、header、欄位都是從 `app/main.py` 與 `scripts/test_send_task.py` 實際確認來的，不是用猜的。

---

## ⚠️ 先看這兩個最容易踩的雷（從程式實際確認）

1. **驗證 header 不是 `Authorization: Bearer`，而是自訂 header `X-Adapter-Token`。**
   程式裡完全沒有 Bearer / Authorization 的處理，只有 `X-Adapter-Token`。

2. **任務內容的欄位叫 `task_text`，不是 `instruction`。**
   `app/main.py` 的資料模型 `TaskEnvelope` 要求的是 `task_text`。
   如果 Hermes 只送 `instruction` 而沒送 `task_text`，會收到 **HTTP 422（缺 task_text）**。
   多送的欄位（例如 `instruction`、`expected_output`、`safety_level`）目前會被**忽略**，不會報錯。

記住這兩點，後面就不會卡住。

---

## 1. 目前系統架構

### 現在實際在跑的（已驗證成功）

```text
測試腳本 scripts/test_send_task.py   ← 模擬 Hermes（還不是真的 Hermes）
        │  HTTP POST /tasks/dispatch
        ▼
Adapter (FastAPI, uvicorn, port 8000)
        │  asyncio.create_subprocess_exec（不經過 shell）
        ▼
openclaw agent --message "..." --json --agent main --session-key hermes-<task_id>
        │
        ▼
真實 OpenClaw（WebSocket Gateway, MiniMax-M3）→ 回覆 PONG
```

### 目前「還不是」這樣（這就是下一階段的目標）

```text
真實 Hermes Agent      ← 還沒接上，目前是測試腳本在模擬
        │
        ▼
Adapter
        │
        ▼
真實 OpenClaw
```

換句話說：**Adapter 與 OpenClaw 這段已經打通了**，缺的只是「把模擬的測試腳本，換成真實 Hermes Agent 去呼叫同一個 HTTP endpoint」。
好消息是：對 Adapter 來說，誰來呼叫都一樣 —— 只要會發 HTTP POST 就行。

---

## 2. Adapter 啟動方式

在 **WSL Ubuntu** 裡（要用跟 OpenClaw 同一個使用者，才讀得到 `openclaw` 和它的設定）：

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

啟動成功會看到：

```text
Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

先用這個確認活著（不需要 token）：

```bash
curl http://127.0.0.1:8000/health
```

會回類似：

```json
{"ok":true,"app":"Hermes OpenClaw Adapter","transport":"cli","openclaw_cli_bin":"openclaw","openclaw_cli_timeout_seconds":600.0,"token_required":true}
```

`token_required: true` 代表派任務時一定要帶 `X-Adapter-Token`。

---

## 3. Hermes 未來應該 POST 到哪個 URL

Adapter 用 `--host 0.0.0.0 --port 8000` 啟動，所以本機任何介面都聽得到。

| 情境 | URL |
|---|---|
| **endpoint path（派任務）** | `POST /tasks/dispatch` |
| **本機 / WSL 內**（Hermes 也跑在同一個 WSL） | `http://127.0.0.1:8000/tasks/dispatch` |
| **Windows 程式 / 瀏覽器**（WSL2 有 localhost 轉發） | `http://localhost:8000/tasks/dispatch` |
| **區網其他機器 / 指定 WSL IP** | `http://172.31.184.159:8000/tasks/dispatch` |

> ⚠️ `172.31.184.159` 是現在這次的 WSL IP，**重開機會變**。要重新查就跑：
> ```bash
> hostname -I        # 取第一個就是 WSL IP
> ```
> 最穩的做法：**讓真實 Hermes 也跑在同一個 WSL 裡，直接用 `127.0.0.1:8000`**，就不用煩惱 IP。

其他可用 endpoint（除了 `/health` 都要帶 `X-Adapter-Token`）：

| 方法 | path | 用途 |
|---|---|---|
| GET | `/health` | 健康檢查（免 token） |
| POST | `/tasks/dispatch` | 派任務（主要入口） |
| GET | `/tasks` | 列出最近 50 筆任務紀錄 |
| GET | `/tasks/{task_id}` | 查單一任務紀錄 |

---

## 4. 需要帶哪些 headers

從 `app/main.py`（`require_token` + `Header("X-Adapter-Token")`）與 `scripts/test_send_task.py` 確認：

| Header | 必要？ | 值 | 說明 |
|---|---|---|---|
| `Content-Type` | ✅ 是 | `application/json` | body 是 JSON |
| `X-Adapter-Token` | ✅ 是（當有設 token） | 目前是 `change-me` | 對應 `.env` 的 `HERMES_ADAPTER_TOKEN` |

**重點澄清（針對「Authorization / Bearer」的疑問）：**

- ❌ 目前**不使用** `Authorization` header。
- ❌ 目前**不使用** `Bearer <token>` 格式。
- ✅ 只認自訂 header：`X-Adapter-Token: change-me`。

`HERMES_ADAPTER_TOKEN` 怎麼運作：
1. Adapter 啟動時從 `.env` 讀 `HERMES_ADAPTER_TOKEN`（目前 = `change-me`）。
2. 每次 `POST /tasks/dispatch`，Adapter 比對請求的 `X-Adapter-Token` 是否等於這個值。
3. 不相等 → 回 **401 Invalid or missing X-Adapter-Token**。
4. 若 `.env` 把 `HERMES_ADAPTER_TOKEN` 留空，則不檢查（不建議正式用）。

> 正式上線請把 `change-me` 改成一段長亂數，並只放在 `.env`（不要寫進 README / 不要 commit）。

---

## 5. Body JSON 格式範例（以程式實際支援為準）

你給的範例用了 `instruction`，但程式實際要的是 `task_text`。
**正確（可直接用）的格式如下：**

```json
{
  "title": "PONG 安全測試",
  "goal": "確認 Hermes 可以透過 Adapter 呼叫 OpenClaw",
  "task_text": "請只回覆 PONG，不要操作任何檔案、不要執行外部動作。",
  "priority": "low",
  "metadata": {
    "source": "hermes",
    "workflow": "connectivity_test"
  }
}
```

### `TaskEnvelope` 實際欄位對照（來自 `app/main.py`）

| 欄位 | 必填 | 型別 / 允許值 | 預設 | 對應你文件裡的概念 |
|---|---|---|---|---|
| `title` | ✅ | string | — | title |
| `goal` | ✅ | string | — | goal |
| `task_text` | ✅ | string | — | **就是你說的 instruction** |
| `priority` | ❌ | `"low"` / `"normal"` / `"high"` | `"normal"` | priority |
| `task_id` | ❌ | string | 自動產生 `task-xxxx` | task_id |
| `source` | ❌ | string | `"hermes"` | metadata.source |
| `metadata` | ❌ | object | `{}` | metadata |

> ⚠️ 目前**還沒有**的欄位：`instruction`（請改用 `task_text`）、`expected_output`、`safety_level`。
> 這些多送不會報錯（會被忽略），但 Adapter 目前不會用到它們。詳見第 10 節的升級建議。

---

## 6. curl 測試指令（安全 PONG，可直接在 WSL 跑）

```bash
curl -X POST "http://127.0.0.1:8000/tasks/dispatch" \
  -H "Content-Type: application/json" \
  -H "X-Adapter-Token: change-me" \
  -d '{
    "title": "PONG 安全測試",
    "goal": "確認 Hermes 可以透過 Adapter 呼叫 OpenClaw",
    "task_text": "請只回覆 PONG，不要操作任何檔案、不要執行外部動作。",
    "priority": "low",
    "metadata": { "source": "hermes", "workflow": "connectivity_test" }
  }'
```

這個任務只要求回覆 PONG，不碰檔案、不執行外部命令，是最安全的連線測試。

---

## 7. Python requests 測試範例（未來 Hermes / 工具可照抄）

```python
import requests

ADAPTER_URL = "http://127.0.0.1:8000/tasks/dispatch"
ADAPTER_TOKEN = "change-me"  # 對應 .env 的 HERMES_ADAPTER_TOKEN

payload = {
    "title": "PONG 安全測試",
    "goal": "確認 Hermes 可以透過 Adapter 呼叫 OpenClaw",
    "task_text": "請只回覆 PONG，不要操作任何檔案、不要執行外部動作。",
    "priority": "low",
    "metadata": {"source": "hermes", "workflow": "connectivity_test"},
}

headers = {
    "Content-Type": "application/json",
    "X-Adapter-Token": ADAPTER_TOKEN,
}

# OpenClaw agent 可能跑數十秒～數百秒，HTTP timeout 要比 CLI timeout(600) 更長
resp = requests.post(ADAPTER_URL, json=payload, headers=headers, timeout=660)
print(resp.status_code)
print(resp.json())
```

> 專案內已有等效的 `httpx` 版本：`scripts/test_send_task.py`，可直接 `python scripts/test_send_task.py`。

---

## 8. 給 Hermes Agent 的工具描述（tool description）

可以把下面這段放進 Hermes 的 tool / function 定義：

- **tool 名稱建議**：`dispatch_to_openclaw`（或 `openclaw_task`）
- **用途**：把「需要實際執行、操作或自動化」的任務，交給 OpenClaw 執行端去做，並取回結果。Hermes 自己能直接回答的問題不要用這個工具。
- **輸入欄位**：
  - `title`（必填）：任務標題（短）
  - `goal`（必填）：這個任務想達成什麼
  - `task_text`（必填）：給 OpenClaw 的完整、明確指令（這就是 instruction）
  - `priority`（選填）：`low` / `normal` / `high`，預設 `normal`
  - `metadata`（選填）：附加資訊，如 `{"source":"hermes","workflow":"..."}`
- **輸出欄位**：
  - `ok`：是否成功（true/false）
  - `adapter_status`：`sent`（已送出）/ `failed`（失敗）/ `dry_run`
  - `transport`：目前固定 `cli`
  - `task_id`：這次任務 ID
  - `openclaw_response`：OpenClaw 的實際回覆（成功時）。最終文字在
    `openclaw_response.payloads[0].text`，或 `openclaw_response.meta.agentMeta.finalAssistantVisibleText`
  - `error` / `stderr` / `exit_code`：失敗時的錯誤資訊
- **安全限制**：
  - 只送「可驗證、可回報」的任務。
  - 高風險動作（改檔案、刪資料、登入帳號、操作平台、發送對外訊息）**先問使用者確認**再送。
  - **不要把密碼、API key、token、個資等敏感資訊**直接寫進 `task_text` 或 `metadata`。

### tool description（可直接貼，英文版，方便放進 function schema）

```text
Name: dispatch_to_openclaw
Description: Send an actionable task to the OpenClaw execution backend (via the local Adapter)
and return its result. Use ONLY when a task needs real execution, operation, automation, or
CLI/cross-platform work — NOT for questions you can answer yourself.
Endpoint: POST http://127.0.0.1:8000/tasks/dispatch
Headers: Content-Type: application/json ; X-Adapter-Token: <token>
Input (JSON): title (string, required), goal (string, required),
  task_text (string, required, the full clear instruction),
  priority ("low"|"normal"|"high", optional), metadata (object, optional).
Output (JSON): ok (bool), adapter_status ("sent"|"failed"|"dry_run"), transport ("cli"),
  task_id (string), openclaw_response (object on success), error/stderr/exit_code (on failure).
Safety: never include secrets/credentials; ask the user before any high-risk action
  (modify/delete files, login, post messages, operate external platforms).
```

---

## 9. Hermes Agent 系統提示詞範例（可放進 profile / skill / system prompt）

```text
你是 Hermes，是整個系統的「主腦」。
你負責理解使用者需求、規劃，並決定什麼時候把任務交給 OpenClaw 執行端。

你有一個工具：dispatch_to_openclaw
它會把任務送到本機 Adapter（POST http://127.0.0.1:8000/tasks/dispatch，
header 帶 X-Adapter-Token），再由 OpenClaw 實際執行，並回傳結果。

你的工作流程：
1. 把使用者需求拆解成清楚、可驗證的子任務。
2. 判斷每個子任務「是否真的需要 OpenClaw 執行」。
3. 需要時，組成標準 JSON（title / goal / task_text / priority / metadata）呼叫 dispatch_to_openclaw。
4. 讀取 OpenClaw 回傳（openclaw_response），檢查是否成功、結果是否合理。
5. 把結果整理成人話，回報給使用者。

什麼時候「不要」交給 OpenClaw：
- 你自己就能回答的知識性、解釋性、聊天類問題 → 直接回答，不要呼叫工具。
- 不要把所有問題都丟給 OpenClaw。

什麼時候「才」交給 OpenClaw：
- 需要實際執行、操作檔案/系統、跨平台、自動化、CLI、排程之類的任務。

任務品質要求：
- task_text 要清楚、具體、可驗證、可回報，不要含糊。
- 一次一個明確目標，必要時拆成多個任務。

安全要求：
- 高風險任務（改檔案、刪資料、登入帳號、操作平台、對外發送訊息）→ 先向使用者說明並取得確認，才呼叫工具。
- 絕不把密碼、API key、token、個資寫進 task_text 或 metadata。
- 不確定風險時，先問使用者，不要自行執行。
```

---

## 10. Hermes 派任務給 OpenClaw 的標準格式（Task Envelope）

「任務信封（Task Envelope）」是 Hermes 與 Adapter 之間約定好的 JSON 格式。

### 目前已支援（Adapter 現在就讀得懂）

| 欄位 | 說明 |
|---|---|
| `task_id` | 任務 ID（不填會自動產生 `task-xxxx`） |
| `title` | 任務標題（必填） |
| `goal` | 任務目標（必填） |
| `task_text` | 完整指令 = 你文件裡的 **instruction**（必填） |
| `priority` | `low` / `normal` / `high`（預設 `normal`） |
| `metadata` | 自由附加資訊（建議放 `source`、`workflow` 等） |

### 未來建議加入（目前送了會被忽略，不會報錯）

| 欄位 | 建議用途 | 需要改哪裡 |
|---|---|---|
| `instruction` | 當成 `task_text` 的別名，讓欄位名更直覺 | `TaskEnvelope` 加欄位 + 在 `build_openclaw_message` 取用 |
| `expected_output` | 描述期望輸出格式（例如「三點摘要」「JSON」），可放進給 OpenClaw 的 message | 同上 |
| `safety_level` | 標記任務風險（如 `safe` / `caution` / `danger`），Adapter 可據此擋下或要求確認 | 同上 + 加一段檢查邏輯 |

> 這些屬於「下一階段的小升級」，本文件先不動程式。等真實 Hermes 接上、跑順了，再決定要不要加。
> 一個務實建議：先讓 Hermes 在 `metadata` 裡帶 `expected_output` / `safety_level`，這樣**現在就能傳、未來再正式升級成正規欄位**，過程不會壞掉。

---

## 11. 安全測試任務 PONG 範例（請保留）

最安全的測試任務，任何時候要驗證「整條線通不通」都用這個：

```text
請只回覆 PONG，不要操作任何檔案、不要執行外部動作。
```

成功時你應該看到（已實測）：

- `ok: true`
- `adapter_status: "sent"`
- `transport: "cli"`
- `openclaw_response` 裡有 `PONG`，例如：
  - `openclaw_response.payloads[0].text == "PONG"`
  - `openclaw_response.meta.agentMeta.finalAssistantVisibleText == "PONG"`

對應的測試腳本就是 `scripts/test_send_task.py`，內容已經是這個安全 PONG 任務。

---

## 12. 第一個真實小任務範例（安全、不碰檔案）

當 PONG 通了，可以試一個「真的要動腦、但不碰系統」的小任務：

```json
{
  "title": "需求整理小任務",
  "goal": "把一段需求整理成三點摘要",
  "task_text": "請閱讀以下需求，整理成三點摘要：我要建立 Hermes + OpenClaw 多 Agent 工作流。不要操作檔案，不要執行外部命令。",
  "priority": "low",
  "metadata": { "source": "hermes", "workflow": "first_real_task" }
}
```

預期：OpenClaw 回一段「三點摘要」文字，`ok: true`、`adapter_status: "sent"`。

> ❌ 第一個真實任務請**不要**設計成會改檔案、刪資料、登入帳號、操作平台的任務。先用純「閱讀 / 整理 / 摘要 / 規劃」這種零副作用的任務建立信心。

---

## 13. 常見錯誤排查

| 症狀 | 可能原因 | 怎麼解 |
|---|---|---|
| `curl: (7) Failed to connect ... 8000` | Adapter 沒啟動 | 回到第 2 節啟動 uvicorn |
| 啟動時 `Address already in use` | port 8000 被占用 | 換 port（`--port 8010`）或 `lsof -i:8000` 找出占用的程式 kill 掉 |
| HTTP **401** `Invalid or missing X-Adapter-Token` | token 沒帶或帶錯 | header 要帶 `X-Adapter-Token: change-me`，且和 `.env` 的 `HERMES_ADAPTER_TOKEN` 一致 |
| HTTP **422** `field required: task_text` | 送了 `instruction` 卻沒送 `task_text` | 把指令放進 `task_text`（見第 5 節） |
| 回 `ok:false` + `stderr: No target session selected` | OpenClaw agent 沒指定 session | `.env` 要有 `OPENCLAW_AGENT_ID=main`（Adapter 會自動帶 `--agent` + `--session-key`） |
| 回 `ok:false` + `error: 找不到 OpenClaw CLI 執行檔` | `openclaw` 不在 PATH | 在 WSL 跑 `which openclaw` 確認；Adapter 要跑在能看到 openclaw 的 WSL 環境 |
| 回 `ok:false` + `error: 超過 ... 秒未回應` | OpenClaw CLI timeout | 任務太重或模型卡住；可調大 `.env` 的 `OPENCLAW_CLI_TIMEOUT_SECONDS` |
| 任務一直能跑但「很花錢」 | `openclaw agent` 會真的呼叫模型（MiniMax-M3），消耗額度 | 測試多用 PONG；正式任務再用，別狂打 |
| Windows 連 `localhost:8000` 連不到 | WSL2 localhost 轉發偶爾失效，或 Hermes 在別台機器 | 改用 WSL IP（`hostname -I`），或把 Hermes 跑進同一個 WSL |
| 啟動了但行為怪 / 還在用舊設定 | `.env` 沒載入 | 啟動指令一定要加 `--env-file .env`；或確認 `.env` 真的存在 |
| `ModuleNotFoundError` / 找不到 uvicorn | Python venv 沒啟動 | 先 `source .venv/bin/activate` 再啟動 |

---

## 14. 為什麼現在先不要做 Callback / Queue

**目前是 CLI 同步模式**：Adapter 呼叫 `openclaw agent` 後會**原地等它跑完**，直接在同一個 HTTP 回應把結果回給 Hermes。
所以 Hermes 發一次 POST 就能拿到結果，**第一版不需要 Callback**。

**Callback 適合**（之後再做）：
- 任務跑很久（不想讓 HTTP 一直掛著等）
- 任務很多、要背景執行
- 需要事後查任務狀態
- 需要失敗自動重試

**Queue 適合**（更後面再做）：
- 任務量明顯變大
- 要有多個 OpenClaw worker 一起消化
- 需要排隊、限流
- 需要重試、需要完整任務追蹤

現在任務是「一次一個、同步拿結果」，CLI 模式剛好夠用，先別增加複雜度。

---

## 15. 下一階段路線（建議順序）

1. **保存 CLI 成功版**（已可做：git commit / 備份；備份已存在 `~/projects/hermes-openclaw-adapter.backup-*`）
2. **完成 Hermes 接入文件**（就是這份文件 ✅）
3. **等真實 Hermes 支援呼叫外部 HTTP / tool / skill**
4. **實測真實 Hermes → Adapter → OpenClaw**（先用第 11 節的 PONG）
5. **做第一個安全真實小任務**（第 12 節的「三點摘要」）
6. **再考慮 Callback**（任務變久 / 要背景化時）
7. **任務量變大再做 Queue**
8. **進階升級 WebSocket RPC `agent.run`**（要更高吞吐、想省掉每次 spawn process 時）

---

## 16. 請不要做的事情（本階段守則）

- ❌ 不要修改 OpenClaw 本體
- ❌ 不要修改 Hermes 本體
- ❌ 不要加入 Queue
- ❌ 不要加入 Callback
- ❌ 不要改成 WebSocket RPC
- ❌ 不要刪掉 `mock_openclaw_server.py`
- ❌ 不要做高風險任務（改檔 / 刪資料 / 登入 / 操作平台）
- ❌ 不要把 token 或任何敏感資訊寫進 README / commit 進 git

---

## 附：快速複製區（給未來的你）

```text
Endpoint : POST http://127.0.0.1:8000/tasks/dispatch
Headers  : Content-Type: application/json
           X-Adapter-Token: change-me
Body     : { "title": "...", "goal": "...", "task_text": "...", "priority": "low", "metadata": {} }
必填欄位 : title, goal, task_text
注意     : 是 task_text（不是 instruction）；是 X-Adapter-Token（不是 Bearer）
啟動     : cd ~/projects/hermes-openclaw-adapter && source .venv/bin/activate &&
           uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
測試     : python scripts/test_send_task.py   （安全 PONG）
```
