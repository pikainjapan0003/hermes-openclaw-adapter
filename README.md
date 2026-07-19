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

## 目前狀態（2026-07-20 更新 — 本節取代下方所有舊版本狀態描述）

- Phase 2（v1.0 Definition Freeze）與 Phase 3–6 已完成；Phase 7 audit write 設計已備但 writer 尚未授權；Phase 8 規劃與離線 projection contract 已完成，remote 接線仍未授權。正確狀態與 commit 證據見 `docs/agent_operating_system/05_VERIFIED_LONG_TERM_PLAN.md` 第 5 節。
- 目前測試基線為 **493 passed**（NIGHT-BATCH-7 合併後）；mypy 白名單 6 模組全綠。
- v1.0 仍未簽核完成：Phase 7 首次 local audit write 需 05 Phase 7 指定的 Owner 逐字授權；Phase 9 N=1 需 Owner 在場與另案 token/gate。仍然無 Worker dispatch、無 real OpenClaw call、無 Hermes runtime activation、無 connector call、無外部副作用。
- 治理制度與長期路線圖已建立於 **`docs/agent_operating_system/`**：
  - 入口索引：`README.md`｜安全邊界正本：`01_SAFETY_BOUNDARIES.md`｜Phase 0–11 計劃表：`05_VERIFIED_LONG_TERM_PLAN.md`
  - 任何 AI session 開工前，先讀 `CLAUDE.md` 第 12 節路由。
- 現況的唯一權威鏈：`CLAUDE.md` §12 → `docs/agent_operating_system/README.md` → `05_VERIFIED_LONG_TERM_PLAN.md` 第 5 節狀態表。**本檔以下章節與其他 166 份 docs 均為歷史紀錄**，與現況不符處以上述權威鏈為準。
- 下一步：Phase 7 audit writer 仍停在 Owner 逐字授權閘；未授權前只可繼續唯讀、測試與規劃工作。

---

## Project Status (v0.7.2 line)（歷史紀錄 historical — 見上方目前狀態）

Hermes × OpenClaw Adapter is a **safety-focused intermediary layer (adapter)** between the
Hermes "brain" and an OpenClaw execution backend. The current development focus is a
**controlled queue, a human approval gate, local-only security gates, a safe auto-approval
policy, and a local-only simulation** — it is **not** a production autonomous worker.

This adapter is **not** production-ready for autonomous execution. It does **not** auto-start
a Worker, does **not** call a real OpenClaw or Hermes backend, and does **not** perform
Google Sheets live writes. The v0.7.2 auto-approval work is currently **policy / helper /
simulation / current-state verification only — it does not execute anything**.

### Architecture

The full intended dataflow is shown in the diagram at the top (Hermes → MCP → Adapter →
queue/worker → OpenClaw CLI → results). On top of that base, the v0.7.x line adds the
following as **observation-only** layers (decision / preview only, no execution):

- a controlled queue intake bridge and a read-only dashboard;
- local-only, pure-function security gates and an approval-to-queued gate;
- a safe auto-approval **policy** (`app/auto_approval_policy_v0_7.py` → `evaluate_auto_approval`);
- a local-only **simulator** that previews policy decisions for built-in sample tasks.

### Safety Boundaries

These must always hold for the v0.7.2 auto-approval / simulation work:

- Auto-approval does not mean auto-execution.
- Simulation does not mean execution.
- auto_approved does not mean queued.
- can_execute is false.
- queue_transition_allowed is false.
- observation_only is true.

And the following must never be auto-approved or silently enabled:

- No dangerous skip-permissions mode is approved.
- No --dangerously-skip-permissions equivalent is approved.
- Push, tag, secrets, production DB writes, Worker start, OpenClaw calls, Hermes calls, and Google Sheets live writes must not be auto-approved.

### Current v0.7.2 Line — Implemented / pushed

- v0.7.1 controlled queue / dashboard / local-only security gates
- v0.7.2-A auto-approval policy plan
- v0.7.2-B pure auto-approval helper (observation-only)
- v0.7.2-B2 expected-stale current-state update
- v0.7.2-C local-only simulation CLI
- v0.7.2-C2 simulation current-state update

### What Works Now

- Controlled task queue with explicit states; human approval flow (approve / reject) and
  limited safe controls (cancel / retry / archive).
- Read-only dashboard and read-only queue / system observation APIs.
- Local-only, pure-function security gates and an approval-to-queued gate (decision-only).
- A safe auto-approval **policy** as a pure function, plus a **local-only simulator**
  (`scripts/simulate_auto_approval_policy_v0_7_2_c.py --sample all` / `--json`) that previews
  decisions for built-in sample tasks. Every decision is observation-only.

### What Is Not Connected Yet

- no Worker execution
- no real OpenClaw calls
- no real Hermes live client
- no approve-route auto-wiring
- no production Queue mutation from auto-approval
- no Google Sheets live write
- no webhook
- no v0.7 tag

### Roadmap (not started)

- v0.7.2-D — intake annotation (observation-only; no state change)
- F2-A — approve-route wiring (gated; requires explicit owner approval)

> Principle: control first, then automate; mock first, then real; queue first, then worker;
> owner approval before any external side effect.

---

## Operator Guide

新手操作手冊請看 [`docs/OPERATOR_GUIDE.md`](docs/OPERATOR_GUIDE.md)。

---

## Backup / Push Plan

備份與 GitHub push 計畫請看 [`docs/BACKUP_PUSH_PLAN.md`](docs/BACKUP_PUSH_PLAN.md)。

---

## v0.4 Milestone (historical)

> For current status see **Project Status (v0.7.2 line)** above. This section documents the
> earlier v0.4 milestone and the detailed component reference below (v0.5.x) for historical
> and operational reference; it does not describe the current development focus.

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

### Queue 觀測 API（v0.5.1，唯讀）

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/queue/overview` | 各狀態計數、total、worker 狀態 |
| GET | `/queue/tasks` | 任務列表（支援 `status` / `limit` / `offset`） |
| GET | `/queue/tasks/{task_id}` | 單筆任務詳情 |
| GET | `/queue/recent-errors` | 最近 failed 任務 |
| GET | `/queue/health` | queue db 健康狀態 |

---

## Read-only Dashboard（v0.5.2，本機唯讀）

掛在同一個 FastAPI Adapter 裡的 server-side 渲染頁面（FastAPI + Jinja2，無 React / 無前後端分離 / 無登入）。
只「讀」資料、重用上面 `/queue/*` 的觀測唯讀邏輯，**不會修改任何 queue 狀態、不呼叫 OpenClaw CLI、不碰 Discord / Hermes**。

| 路徑 | 說明 |
|---|---|
| `GET /dashboard` | Overview：version / execution_mode / 各狀態計數 / total / queue_db_exists / worker status |
| `GET /dashboard/tasks` | 任務列表（表格，支援 `status` / `limit` / `offset`，每筆連到詳情頁） |
| `GET /dashboard/tasks/{task_id}` | 任務詳情（task_text / result_text / error_message / metadata 等；找不到回 404） |

> 純本機使用，頁面頂部標示「Hermes x OpenClaw Queue Control Board」與「Read-only Dashboard」。
> 樣式：[`static/dashboard.css`](static/dashboard.css)；模板：[`templates/`](templates/)。

**v0.5.7 Dashboard Polish / UX Cleanup**（純 UI/UX，未改任何後端行為）：
- 首頁 `/dashboard` 整理成控制台總覽：System Health 卡（Adapter / Worker online·stale·unknown / Queue DB / OpenClaw CLI）、Queue Counts 卡、Quick Links（View Tasks / Pending Reviews / System Health / Recent Errors，純連結非控制）。
- `/dashboard/tasks`：status badge、短版 task_id（hover 看完整）、error 截斷、All/Queued/Running/Waiting Review/Failed/Completed/Cancelled/Rejected/Archived 篩選 pill（保留 status/limit/offset query）。
- task detail：分區成 Summary / Task Text / Result / Error / Metadata / Human Review / Safe Controls / Blackboard Comments；空值顯示 muted「No result yet.」「No error.」。
- `/dashboard/reviews`：頂部 pending count、safety_level / requires_confirmation badge、空狀態訊息。
- `/dashboard/system`：worker online/stale/unknown badge、current_task_id 連到詳情、OpenClaw 標示 checked without execution。
- 全站 CSS：統一 status badge 顏色、卡片、表格 hover、muted、semantic（success/info/warning/danger）、手機基本可讀；無 React/Vite/CDN/外部字型。
- 新增唯讀 template helper：`short_task_id` / `truncate` / `status_class` / `format_empty` / `yesno`（不寫任何資料）。

---

## Blackboard / Task Comments（v0.5.3，留言板）

每個 task 可以掛上一串留言（給人/Hermes/OpenClaw/system 互相留訊息）。留言存在
**獨立的 `task_comments` 表**（[`app/blackboard_store.py`](app/blackboard_store.py)，可與 `queue.db`
共用檔案但不碰 `queue` 表）。**留言只會寫入 blackboard，絕不改 queue 任務狀態、不觸發 worker、
不呼叫 OpenClaw CLI、不碰 Hermes / Discord。**

`task_comments` schema：`comment_id` / `task_id` / `author_type` / `author_name` / `content` /
`created_at` / `metadata_json`。`author_type` 白名單：`user` / `hermes` / `openclaw` / `system`。

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/tasks/{task_id}/comments` | 取任務留言串（任務不存在回 404） |
| POST | `/tasks/{task_id}/comments` | 新增留言（任務不存在回 404；空 content / 非法 author_type 回 400/422） |
| POST | `/dashboard/tasks/{task_id}/comments` | Dashboard 留言表單（PRG，寫完 redirect 回詳情頁） |

詳情頁 `GET /dashboard/tasks/{task_id}` 會顯示「Blackboard Comments」留言串與一個最簡單的新增留言表單。

---

## Approval Flow（v0.5.4，人工審核）

把「需要人工確認」的任務真正落到 Queue 狀態機。新增兩個狀態：`waiting_review` / `rejected`
（**沒有** `approved` 狀態——approve 是動作，approve 後任務回到 `queued`）。

**派工時的審核判斷**（`app/main.py` `needs_human_review()`）：

| 條件 | 結果 |
|---|---|
| `metadata.requires_confirmation == true` | `waiting_review` |
| `safety_level` 可解析且 `>= 3` | `waiting_review` |
| 其餘（含無 metadata、`safety_level` 缺失/無法解析） | 照舊 `queued`（向後相容） |

**狀態流轉**（新增部分）：`waiting_review --approve--> queued`、`waiting_review --reject--> rejected`。
`waiting_review` / `rejected` 任務**絕不會被 worker claim**（`claim_next` 只取 `queued`，worker 邏輯未改）。

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/reviews/pending` | 列出所有 `waiting_review` 任務（`limit` / `offset`） |
| POST | `/tasks/{task_id}/approve` | 批准 → `queued`（不存在 404、非 waiting_review 409） |
| POST | `/tasks/{task_id}/reject` | 拒絕 → `rejected`，body 可帶 `{"reason": "..."}`（404 / 409 同上） |
| GET | `/dashboard/reviews` | Pending Reviews 頁（每筆有 Approve / Reject 表單） |
| POST | `/dashboard/tasks/{task_id}/approve` | Dashboard approve 表單（PRG，redirect 回詳情頁） |
| POST | `/dashboard/tasks/{task_id}/reject` | Dashboard reject 表單（PRG，可帶 reason） |

approve / reject 只透過 `QueueStore` 狀態機（`approve()` / `reject()`），**不直接啟動 worker、不呼叫
OpenClaw CLI、不碰 Hermes / Discord**；並會在 blackboard 寫一則 `system` 留言作為記錄（純記錄，不反向控制 queue）。

> 與 v0.4 行為差異：舊版 dispatch 對 `safety_level >= 2` 一律「直接 rejected」；v0.5.4 起改為
> Level 0–2 自動 `queued`、Level ≥ 3 或 `requires_confirmation` 進 `waiting_review` 等待人工 approve。

---

## Limited Control Actions（v0.5.5，安全控制）

只做**安全**的 Cancel / Retry / Archive，**不做** kill worker、force run、不碰 `running` 任務。
新增一個收納狀態 `archived`（只收納、不刪資料）。所有控制都透過 `QueueStore` 條件式狀態機
（狀態不允許 → 回 409），不直接啟動 worker、不呼叫 OpenClaw CLI。

| 動作 | 允許的來源狀態 | 結果 |
|---|---|---|
| **Cancel** | `queued` / `waiting_review` | `cancelled`（不取消 running） |
| **Retry** | `failed` | `queued`（不歸零 attempts；清空 error） |
| **Archive** | `completed` / `failed` / `cancelled` / `rejected` | `archived`（保留原 error，不刪資料） |

`waiting_review` / `rejected` / `cancelled` / `archived` 皆不會被 worker claim（`claim_next` 只取 `queued`）。

| 方法 | 路徑 | 說明 |
|---|---|---|
| POST | `/tasks/{task_id}/cancel` | 取消 queued/waiting_review（body 可帶 `{"reason": "..."}`） |
| POST | `/tasks/{task_id}/retry` | 重試 failed（不直接執行；worker 之後自然 claim） |
| POST | `/tasks/{task_id}/archive` | 封存終止狀態任務 |
| POST | `/dashboard/tasks/{task_id}/cancel` | Dashboard cancel 表單（PRG） |
| POST | `/dashboard/tasks/{task_id}/retry` | Dashboard retry 表單（PRG） |
| POST | `/dashboard/tasks/{task_id}/archive` | Dashboard archive 表單（PRG） |

共同規則：不存在 404、狀態不允許 409、成功回 task detail。三個動作成功時都會在 blackboard
寫一則 `system` 留言作為記錄（純記錄，不反向控制 queue）。

**Retry 的 attempts 取捨**：保守起見 **不歸零 attempts**（避免無限重試）；`error` 在 retry 時清空，
retry 原因改記到 `tasks.jsonl` ledger 與 blackboard system 留言。由於 worker claim 後一定會把該筆
執行一次，manual retry 等同「再跑一次」；若該次再失敗且 `attempts` 已達 `max_attempts`，worker 不會
再自動 requeue（不會無限迴圈）。

> 與 v0.4 cancel 差異：舊版 `/tasks/{id}/cancel` 只取消 `queued` 且非法狀態仍回 200+message；
> v0.5.5 起改用更嚴格的 `cancel_control`（也支援取消 `waiting_review`，非法狀態回 409）。
> 既有 `QueueStore.cancel_if_queued()` 方法保留不動。

詳情頁 `GET /dashboard/tasks/{task_id}` 會依當前狀態顯示對應的 Cancel / Retry / Archive 表單
（`running` / `archived` 不顯示任何控制）；Overview 計數與任務列表都已支援 `archived`。

---

## System Health / Worker Heartbeat（v0.5.6，純觀測）

讓 Dashboard 看得到 adapter / queue / worker 是否健康。Worker 會把心跳寫進**獨立的
`worker_heartbeats` 表**（[`app/health_store.py`](app/health_store.py)，可與 `queue.db` 共用檔案
但不碰 `queue` 表）。**心跳只記錄、不反向控制 worker；寫入失敗也絕不讓 worker 崩潰。**

`worker_heartbeats` 欄位：`worker_id`(PK) / `status` / `pid` / `hostname` / `started_at` /
`last_seen_at` / `current_task_id` / `current_task_started_at` / `last_claimed_at` /
`last_completed_at` / `last_error_at` / `last_error_message` / `metadata_json`。

**raw_status**：`starting` / `idle` / `running` / `stopping` / `error`。
**推導的 online 狀態**（由 `last_seen_at` 推算，門檻常數 `WORKER_HEARTBEAT_STALE_SECONDS=30`）：
`last_seen_at` 距現在 ≤ 30 秒 → `online`；> 30 秒 → `stale`；沒有心跳 → `unknown`。

worker 何時寫心跳：啟動 `starting` → 進輪詢 `idle` → claim 到任務 `running`(+`current_task_id`/
`last_claimed_at`) → 完成 `idle`(清 `current_task_id`、更新 `last_completed_at`) → 失敗時記
`last_error_at`/`last_error_message` 後照既有邏輯處理 retry/failed → 收到停止訊號 `stopping`。
（只加心跳記錄，**未改 worker 任務執行邏輯、未改 queue 狀態機**。）

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/system/health` | adapter / queue counts / worker / OpenClaw CLI 路徑（**只檢查路徑、不執行**） |
| GET | `/system/worker` | worker heartbeat 詳情（含推導的 online/stale/unknown） |
| GET | `/dashboard/system` | Dashboard 系統健康頁（導覽列 System） |

> **OpenClaw CLI 檢查**：只用 `shutil.which()` / `os.path` 檢查路徑是否存在/可執行，
> **絕不執行 OpenClaw CLI、不跑 `--version`、不觸發任何任務**；回傳一律帶
> `cli_checked_without_execution: true`。

---

## Historical Next-step Notes (v0.4 era)

> Kept for history. The current roadmap is in **Project Status (v0.7.2 line) → Roadmap**
> above. The queue / worker infrastructure below already landed in the v0.5–v0.6 line; the
> v0.7.x line then layered controlled intake / approval / security / auto-approval-policy /
> simulation on top (observation-only).

1. **`v0.4.2-service-units`** —— 把 Adapter 與 Hermes Gateway 做成 systemd unit（運維強化）。
2. **`v0.5-queue-worker`** —— Queue / Worker（以及 DLQ、重試編排）—— 已於 v0.5–v0.6 落地。

> 維持原則：先穩定運維，再擴充架構；先控管，再自動化。
