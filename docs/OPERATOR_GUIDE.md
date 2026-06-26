# Hermes x OpenClaw Operator Guide

> 這是一份「新手小白也看得懂」的操作手冊。不需要懂太多工程術語，照著做就好。

---

## 1. 這個系統是什麼

把它想成一間「自動接案的小工廠」，分工如下：

- **Discord** — 對話入口。你在 Discord 講話，系統就收到。
- **Hermes** — 主腦 / 判斷。決定要不要做、怎麼做、要不要先問人。
- **Adapter** — 櫃台 / API。負責收任務、發狀態，是中間轉接層（FastAPI）。
- **Queue（任務帳本）** — 一本「待辦清單」。每個任務都登記在這裡，狀態隨時更新。
- **OpenClaw Worker** — 執行者。從帳本拿任務、實際去做、把結果寫回來。
- **Dashboard** — 控制台。用網頁看任務、看健康狀態、做安全的小控制。
- **Blackboard（留言板）** — 每個任務底下的留言區，給人和系統互相留訊息用。

架構圖：

```text
你
  ↓ Discord
Hermes Bot / Hermes Agent
  ↓ MCP / Adapter
Queue
  ↓
OpenClaw Worker
  ↓
結果回傳
Discord / Dashboard / Blackboard
```

一句話：**任務從 Discord 進來 → Hermes 判斷 → 排進 Queue → Worker 執行 → 結果回到 Discord / Dashboard / Blackboard。**

---

## 2. 目前版本能力（v0.5.7）

目前系統已經有這些功能：

- **Queue Worker**（v0.5.0）— 任務排隊、由 worker 在背景一筆一筆執行。
- **Queue Observability**（v0.5.1）— 用 API 查 queue 狀態、計數、最近錯誤。
- **Read-only Dashboard**（v0.5.2）— 用網頁看任務（唯讀）。
- **Blackboard Comments**（v0.5.3）— 每個任務可以留言。
- **Approval Flow**（v0.5.4）— 高風險任務先進「待審核」，人工 approve 才會執行。
- **Limited Control Actions**（v0.5.5）— 安全的 Cancel / Retry / Archive。
- **System Health / Worker Heartbeat**（v0.5.6）— 看 adapter / worker 是否在線。
- **Dashboard Polish**（v0.5.7）— 控制台 UI 清理，更好讀。

---

## 3. 每天怎麼啟動

需要開「兩個終端機」：一個跑 Adapter（櫃台），一個跑 Worker（執行者）。

### A. 啟動 Adapter

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

### B. 啟動 Worker

打開「另一個終端機」：

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
python -m app.worker
```

### C. 打開 Dashboard

在瀏覽器輸入：

```text
http://localhost:8000/dashboard
```

### D. 檢查 System Health

```text
http://localhost:8000/dashboard/system
```

> 小提醒：Adapter 沒開，Dashboard 就打不開；Worker 沒開，任務會一直停在 `queued` 不動。

---

## 4. Dashboard 怎麼看

| 頁面 | 路徑 | 用途 |
|---|---|---|
| **Overview** | `/dashboard` | 控制台總覽：System Health、Queue Counts、Quick Links。 |
| **Tasks** | `/dashboard/tasks` | 任務列表，可依狀態篩選（All / Queued / Running …）。 |
| **Reviews** | `/dashboard/reviews` | 等待人工審核的任務，可 approve / reject。 |
| **System** | `/dashboard/system` | 系統健康：adapter / worker / queue db / OpenClaw CLI 路徑。 |
| **Task Detail** | `/dashboard/tasks/{task_id}` | 單一任務的全部資訊 + 控制 + 留言。 |
| **Blackboard Comments** | （在 Task Detail 頁底部） | 任務留言區。 |

全部都是「看」為主；只有 approve / reject / cancel / retry / archive 這幾個**安全動作**會改任務狀態。

---

## 5. 任務狀態說明

| 狀態 | 意思 | 可做什麼 |
|---|---|---|
| `queued` | 等待執行 | 可以 cancel |
| `running` | 正在執行 | 只能等待 |
| `completed` | 完成 | 可以 archive |
| `failed` | 失敗 | 可以 retry 或 archive |
| `cancelled` | 已取消 | 可以 archive |
| `waiting_review` | 等待人工審核 | 可以 approve / reject / cancel |
| `rejected` | 已拒絕 | 可以 archive |
| `archived` | 已封存 | 只保留紀錄 |

> Worker 只會執行 `queued` 的任務。其他狀態（特別是 `waiting_review`、`rejected`、`cancelled`、`archived`）worker **絕對不會碰**。

---

## 6. Approval Flow 怎麼用

規則很簡單：

- **safety_level 0–2** → 自動進 `queued`（會被執行）。
- **safety_level 3–4** → 進 `waiting_review`（等人工審核）。
- **requires_confirmation = true** → 不管等級，都進 `waiting_review`。
- 在 **Reviews 頁**按 **Approve** → 任務變 `queued`（之後 worker 自然執行）。
- 按 **Reject** → 任務變 `rejected`（不會執行）。
- **worker 不會執行 `waiting_review` / `rejected`** 的任務。

> 用途：高風險任務先讓人看一眼再放行，不會偷偷自動跑。

---

## 7. Limited Control Actions 怎麼用

這些是「安全的小控制」，全部透過 Queue 狀態機處理。

### Cancel（取消）

只能取消：
- `queued`
- `waiting_review`

**不能**取消：
- `running`（正在跑的不能砍，要等它自然 completed / failed）

### Retry（重試）

只能重試：
- `failed`

重試後任務回到 `queued`，等 worker 再跑一次。

### Archive（封存）

只能封存：
- `completed`
- `failed`
- `cancelled`
- `rejected`

封存只是「收進抽屜」，**不會刪掉資料**。

> 重要：這些控制**不會** kill worker、**不會** force run、**不會**直接呼叫 OpenClaw CLI。它們只是改 queue 裡的狀態。

---

## 8. Blackboard 留言板怎麼用

- 每個任務詳情頁底部都有「Blackboard Comments」留言區。
- 可以記錄**使用者指示**（例如：「這個任務只能查公開資料，不要登入網站」）。
- 可以記錄 **Hermes / OpenClaw / system** 的備註。
- 系統做 approve / reject / cancel / retry / archive 時，也會自動留一則 `system` 紀錄。
- **留言只是紀錄，不會反向控制 queue。** 寫留言不會讓任務開始跑、也不會改任務狀態。

---

## 9. System Health 怎麼看

到 `/dashboard/system`，你會看到：

- **Adapter online** — 櫃台有沒有在線。
- **Queue DB exists** — 任務帳本檔案在不在。
- **Worker online / stale / unknown**：
  - `online` — worker 最近 30 秒內有心跳，正常。
  - `stale` — 超過 30 秒沒心跳，可能卡住或被關掉。
  - `unknown` — 從來沒有心跳，可能根本沒啟動。
- **Worker last_seen_at** — 最後一次心跳時間。
- **current_task_id** — 現在正在處理哪個任務（有的話可以點進去）。
- **OpenClaw CLI path exists** — OpenClaw 指令的路徑在不在。
- **checked without execution** — 代表系統**只檢查路徑，沒有真的執行 OpenClaw**。

---

## 10. 常見問題排查

### Dashboard 打不開
→ 檢查 **Adapter 是否有啟動**（第 3 節 A 步驟）。

### Worker 顯示 unknown
→ 可能是 **worker 沒啟動**（第 3 節 B 步驟）。

### Worker 顯示 stale
→ 可能是 worker 停住了，或跑 worker 的終端機被關掉了。重開 worker。

### 任務一直 queued 不動
→ 多半是 **worker 沒開**。開了 worker 就會開始處理。

### 任務 waiting_review
→ 這是正常的「等待審核」。到 **Reviews 頁** approve 或 reject。

### 任務 failed
→ 打開 Task Detail 看 `error_message`，確認原因後，必要時按 **Retry**。

### OpenClaw CLI path missing
→ 檢查 `.env` 裡的 OpenClaw CLI 設定（路徑或指令名）。**但不要把 `.env` commit 上去。**

### 看到 untracked HEAD
→ 這是一個外來雜檔，**不要亂刪**；等 owner 確認再處理。

---

## 11. 安全原則

- 不 commit `.env`
- 不 commit `data/`
- 不 commit `queue.db`
- 不 commit `results.jsonl` / `tasks.jsonl`
- 不在 Dashboard 做高風險自動化
- **Level 3+ 一律要人工審核**
- 不讓 Dashboard 直接呼叫 OpenClaw CLI
- 不讓 Dashboard 改 Hermes memory
- **Queue 是唯一真相來源（single source of truth）**

---

## 12. 版本里程碑

- **v0.5.0** Queue Worker
- **v0.5.1** Queue Observability
- **v0.5.2** Read-only Dashboard
- **v0.5.3** Blackboard Comments
- **v0.5.4** Approval Flow
- **v0.5.5** Limited Control Actions
- **v0.5.6** System Health / Worker Heartbeat
- **v0.5.7** Dashboard Polish
- **v0.5.8** Operator Guide（本文件）

---

## 13. 新手每日檢查清單

```text
1. Adapter 是否開著？
2. Worker 是否開著？
3. Dashboard 是否能打開？
4. System 頁 worker 是否 online？
5. Reviews 有沒有 waiting_review？
6. Failed 任務有沒有需要 retry？
7. 不要 commit .env / data / queue.db
```
