# Hermes × OpenClaw 第二階段 Callback 收尾報告

> 給新手小白看的白話版。讀完你會知道：第二階段做完了什麼、怎麼用、要注意什麼。

---

## 1. 第二階段目標是什麼

**原始目標**（理想中的完整迴路）：

```text
Hermes → Adapter → OpenClaw → Callback → Hermes
```

**實際落地版本**（這次真的做出來、而且驗證過的）：

```text
Discord / Hermes
   → MCP（dispatch_to_openclaw）
   → Adapter v0.4（:8000）
   → OpenClaw CLI 背景執行
   → data/results.jsonl
   → Hermes 查結果（get_openclaw_task_result）
```

**請特別理解**：這是 **Callback MVP**（最小可行版本），不是完整 production。

- ✅ 有：背景執行、立刻回 `accepted` + `task_id`、結果寫進 `results.jsonl`、可用工具查結果。
- ❌ 還沒有：Queue（任務佇列）、Worker（獨立執行單元）、DLQ（死信佇列）、自動重試、對外正式 webhook 推播。
- 目前的「callback」預設是 **ledger_only** —— 也就是把結果**寫進帳本檔**（`results.jsonl`），再由 Hermes 主動查；不是即時 HTTP 推回。

---

## 2. 第二階段做了哪些事情

| 項目 | 說明 |
|---|---|
| **`v0.4-callback-mvp`** | 第二階段的核心版本標籤 |
| **Adapter 改成 async-background + callback** | 任務不再卡住請求，改成背景執行 |
| **`/tasks/dispatch` 立刻回 `accepted` + `task_id`** | 送任務後馬上拿到收據，不用等它跑完 |
| **OpenClaw 背景執行** | 用 `openclaw agent --message ... --json`（CLI，不經 shell）在背景跑 |
| **TaskResult 寫入 `data/results.jsonl`** | 每筆結果一行 JSON（schema v1：`completed` / `failed`） |
| **`get_openclaw_task_result` 工具** | Hermes 端用 `task_id` 查結果的 MCP 工具 |
| **Level 3+ / Level 4 高風險拒絕** | 安全閘門：只有 Level 0/1 自動執行，Level 2 以上直接 `rejected` |
| **`v0.4.1` Discord E2E 驗證** | 從 Discord 真人入口跑通整條鏈路（completed / PONG） |
| **`v0.4.2` service helper scripts** | start/stop/status 腳本，並驗證 Adapter 重啟流程 |
| **GitHub master / tags 備份** | 程式碼與版本標籤都推上 GitHub private repo |

---

## 3. 測試了什麼

| 測試項目 | 結果 |
|---|---|
| Adapter health `version` | ✅ `0.4.0` |
| PONG 任務 | ✅ `accepted` → `completed` / `PONG` |
| 商品資料整理任務 | ✅ `accepted`，可用 `task_id` 查到 result |
| Level 4 高風險任務 | ✅ 被 `rejected`（安全閘門有生效） |
| 完整鏈路 Discord → Hermes → MCP → Adapter → OpenClaw → `results.jsonl` | ✅ 實測通過（`task-b7c8c2dd81d9`，completed / PONG） |
| Adapter `stop` / `start` / `status` scripts | ✅ 全部正常，exit code 正確 |
| 重啟後再跑 PONG | ✅ `task-89aa3e6b05ba` → completed / PONG |
| GitHub push + tags | ✅ master 與 tags 已備份到遠端 |

> 判斷「真的成功」的方法：**三方對帳同一個 `task_id`** —— Hermes/Discord 的回覆、Adapter 的 log、`tasks.jsonl` / `results.jsonl` 三處 `task_id` 一致，才算真的通。

---

## 4. 踩了什麼坑

- **Discord 一開始只看到 `skill_view`，看不到 `dispatch_to_openclaw`**
  - 真實症狀：Discord 下「請用 OpenClaw 執行 PONG」，Hermes 只讀了 skill 就自己回 PONG，**完全沒派工**（Adapter log 沒有任何 `POST /tasks/dispatch`）。
- **根因：Hermes Gateway 是長駐 process，MCP 工具是後來才加進設定的**
  - Gateway 只在「啟動當下」載入一次工具清單。MCP 在 Gateway 起來之後才註冊 → Gateway 的工具表是舊的，看不到新工具。**重啟 Gateway 後就好了。**
- **舊 session 會讓 Hermes 自己偷答 PONG**
  - Discord 沿用舊對話 session（帶著舊 history），模型容易「照舊」直接回答，而不是去派工。刪掉舊 session 改開新對話比較保險。
- **PONG 太簡單，模型可能自己回答**
  - 因為「回 PONG」對模型來說太容易，它會想自己做掉。**指令必須明確要求它「呼叫 `dispatch_to_openclaw`、不要自己回答」**。
- **Adapter 必須開著**
  - Adapter 沒開，Hermes 再怎麼喊都派不出去（連線被拒）。
- **GitHub remote / 帳號 / PAT 容易搞混**
  - 換過 repo 帳號（`bill831206` → `pikainjapan0003`），remote URL、帳號、PAT 要對得起來，拼字也要注意。
- **GitHub password 不顯示是正常的**
  - 終端機輸入 PAT 當密碼時畫面不會有任何字元，這是正常的，照打 Enter 即可。
- **README 一開始還是舊 MVP 內容**
  - 早期 README 還在講 mock server / dry_run，已 refresh 成 v0.4.1 現況。
- **Gateway / Adapter 目前不是開機自動啟動**
  - 重開機後要手動把兩個服務拉起來（見第 6 節）。

---

## 5. 做出的結論

- ✅ **第二階段完成。**
- ✅ **Hermes 現在可以真的派工給 OpenClaw**（不再只是嘴巴講講）。
- ✅ **收到 `accepted` + `task_id` 代表派工成功**（任務已送出）。
- ✅ **結果要用 `get_openclaw_task_result` 查**（或終端機 `check_task_result.sh`）。
- ✅ **Level 4 被 `rejected` 代表安全閘門有生效**。
- ⚠️ **目前不是 Queue** —— 任務是用背景執行跑的，所以**重啟時要注意正在背景跑的任務可能被中斷**。
- ➡️ **下一階段才是 `v0.5` Queue Worker。**

---

## 6. 新手小白如何操作

### 確認 / 啟動 / 停止 Adapter

```bash
cd ~/projects/hermes-openclaw-adapter

# 確認 Adapter 有沒有開（唯讀，安全）
./scripts/status_adapter_v04.sh      # 看到 version 0.4.0 就是 OK

# 啟動 Adapter
./scripts/start_adapter_v04.sh

# 停止 Adapter
./scripts/stop_adapter_v04.sh
```

### 確認 Gateway

```bash
./scripts/status_gateway.sh          # 看到 Gateway 執行中 + Discord connected
```

### Discord 怎麼派 Level 0 任務

在 Discord 對 Hermes Bot 說（重點：**要它呼叫工具，不要它自己回答**）：

```text
請呼叫 MCP 工具 dispatch_to_openclaw，把以下 Level 0 任務派給 OpenClaw 執行：
title: 我的測試
goal: 驗證派工
metadata: safety_level = Level 0
task_text: 請只回覆 PONG，不要操作任何檔案、不要登入、不要下單、不要發訊息。
請回覆時附上 dispatch_to_openclaw 是否已呼叫、status、task_id。不要只回 PONG。
```

### 怎麼看 task_id

Hermes 派工成功會回類似：`status: accepted`、`task_id: task-xxxxxxxxxxxx`。**把這個 `task_id` 記下來。**

### 怎麼查結果

- 在 Hermes / Discord：

  ```text
  請呼叫 get_openclaw_task_result 查詢 task-xxxxxxxxxxxx
  ```

- 在終端機：

  ```bash
  ./scripts/check_task_result.sh task-xxxxxxxxxxxx
  ```

  看到 `status: completed`、`result_text: PONG` 就是成功。

---

## 7. 新手小白注意事項

- ⚠️ **看到 `accepted` 不代表結果已完成**，只代表任務「已送出」。
- ⚠️ **一定要用 `task_id` 查結果**（背景任務要幾十秒，剛送出馬上查可能還是 `running`）。
- ⚠️ **Adapter 要開著**，不開就無法派工。
- ⚠️ **Hermes Gateway 要開著**，不開 Discord 就沒人理。
- ⚠️ **新增 MCP tool 後要重啟 Gateway**，否則 Discord 看不到新工具。
- 🚫 **不要拿來測登入、下單、付款、刪除、發訊息**等有副作用的動作。
- 🚦 **Level 3+ / Level 4 要人工確認**（系統會擋下高風險任務）。
- 🔒 **`.env`、`data/*.jsonl`、token 不要 commit**（`.gitignore` 已排除，別硬加）。
- 🔒 **Public GitHub repo 不要放秘密**（目前是 private，仍要養成習慣）。
- 🕵️ **如果 Discord 只回 PONG 但沒有 `task_id`，代表 Hermes 可能自己偷答了，沒有真的派工** —— 請改用「明確要求呼叫 `dispatch_to_openclaw`」的講法，並確認 Gateway 已載入工具。

---

## 8. 目前版本狀態

| 版本標籤 | 內容 |
|---|---|
| `v0.4-callback-mvp` | async-background + callback 核心 |
| `v0.4.1-discord-e2e-verified` | Discord 端到端驗證（completed / PONG） |
| `v0.4.2-service-helper-scripts` | start/stop/status 腳本 + 重啟流程驗證 |
| **GitHub 備份** | master 與 tags 已推上 private repo |

---

## 9. 下一步建議

- **短期**：繼續玩 **Level 0** 任務，熟悉「派工 → 拿 task_id → 查結果」的節奏。
- **中期**：測更多真實工作流 —— 商品資料整理、訂單整理、Beyblade（戰鬥陀螺）分析等。
- **之後**：`v0.5` **Queue Worker**（任務佇列 + 獨立執行單元，提升吞吐與穩定）。
- **再之後**：systemd / 開機自動啟動、DLQ（死信佇列）、retry（自動重試）。

> 原則不變：**先穩定運維，再擴充架構。** 這份報告為第二階段（Callback MVP）正式收尾。
