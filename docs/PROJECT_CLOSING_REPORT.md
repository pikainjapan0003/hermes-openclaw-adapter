# Hermes + OpenClaw 專案收尾總結報告（MVP）

> 給新手小白看的版本。一份就看懂「我們做了什麼、測了什麼、怎麼用、接下來怎麼辦」。
> 日期：2026-06-14　專案位置：`~/projects/hermes-openclaw-adapter`

---

## 1. 這個專案最後完成了什麼

我們把「**會聊天會規劃的 Hermes**」和「**會動手做事的 OpenClaw**」接在一起了。
現在你在 Discord（或 Hermes）下一個任務，它會自動跑完整條路，再把結果拿回來給你：

```text
你（Discord / Hermes 聊天）
        │  下任務
        ▼
Hermes（主腦）── 用「OpenClaw Executor」skill 判斷：這要不要交給 OpenClaw？
        │  要 → 呼叫工具
        ▼
MCP 工具：dispatch_to_openclaw
        │  把任務變成一個 HTTP 請求
        ▼
Adapter：POST /tasks/dispatch（FastAPI，port 8000）
        │  翻譯任務 + 呼叫指令
        ▼
openclaw agent CLI
        │
        ▼
真實 OpenClaw（執行端，用 MiniMax-M3 模型）
        │  把事情做完
        ▼
結果原路送回 → Adapter → MCP → Hermes → 回到 Discord / 你眼前
```

白話：**Hermes 是大腦想，OpenClaw 是手腳做，中間 MCP + Adapter 是神經把它們接起來。**

---

## 2. 我們做了哪些事情（時間順序）

1. **建立 Adapter**：一個中間轉接站（FastAPI），負責收 Hermes 的任務。
2. **Mock OpenClaw 測試**：先用「假的 OpenClaw」跑通流程，確認 Adapter 會動。
3. **找真實 OpenClaw 入口**：研究真的 OpenClaw 要怎麼接。
4. **發現 OpenClaw 不是 REST API**：它是 **WebSocket Gateway**，而且有 **CLI 指令**可用。
5. **改成 CLI 模式**：讓 Adapter 用 `openclaw agent --message ... --json` 真正呼叫 OpenClaw。
6. **建立 Hermes MCP bridge**：寫一個小 MCP server，讓 Hermes 能用「工具」的方式呼叫 Adapter。
7. **建立 Hermes OpenClaw Executor skill**：教 Hermes「什麼時候該把任務交給 OpenClaw」。
8. **建立 routing rules（分流規則）**：把「該交/不該交、安全分級 0–5」寫成規範。
9. **測 PONG**：最安全的連線測試（只回 PONG）。
10. **測三點摘要**：第一個有內容的真實小任務。
11. **測商品資料整理工作流**：第一個正式工作流（純文字 → 表格）。
12. **測 Discord Bot 呼叫**：從 Discord 端下任務，確認真人入口也通。

---

## 3. 測試了哪些東西

> 註：task_id 是每個任務的身分證號碼，記在 `data/tasks.jsonl`（任務帳本）。
> Mock 與 Discord 測試由不同階段/使用者執行，下表只列出 logs 裡查得到的 task_id。

### (1) Mock OpenClaw 測試
- **目標**：確認 Adapter 流程本身會動（先不接真 OpenClaw）。
- **方式**：用一個假的 OpenClaw server 接收任務。
- **成功證據**：Adapter 能收任務並回應。
- **task_id**：無（測試替身階段）。
- **結論**：✅ 流程打通，可以接真的。

### (2) 真實 OpenClaw CLI PONG 測試
- **目標**：確認 Adapter 真的能呼叫真 OpenClaw。
- **方式**：Adapter 用 `openclaw agent --json` 送一個只回 PONG 的任務。
- **成功證據**：OpenClaw 回 `PONG`，`adapter_status: sent`。
- **task_id**：`task-6d6337602909`
- **結論**：✅ Adapter → 真實 OpenClaw 通。

### (3) Hermes MCP PONG 測試
- **目標**：確認 Hermes 能透過 MCP 工具呼叫 Adapter。
- **方式**：在 Hermes 叫它呼叫 `dispatch_to_openclaw`，送 PONG 任務。
- **成功證據**：MCP log 有 `CallToolRequest`、Adapter `POST 200`、OpenClaw 回 PONG。
- **task_id**：`task-f1ac05baf045`
- **結論**：✅ Hermes → MCP → Adapter → OpenClaw 通。

### (4) 第一個安全真實小任務：三點摘要
- **目標**：確認不只會回 PONG，也能做真實文字任務。
- **方式**：Hermes 經 MCP 把「把一段需求整理成三點摘要」交給 OpenClaw。
- **成功證據**：OpenClaw 回傳正確的三點摘要，Hermes 完整回報。
- **task_id**：`task-2000b69a1a97`（第一次因腳本 timeout 設太短被截斷的那次是 `task-c70455d71eea`，鏈路其實也成功）。
- **結論**：✅ 非 PONG 真實任務通。

### (5) 第一個正式工作流：商品資料整理
- **目標**：驗證 OpenClaw Executor skill + Level 0 工作流。
- **方式**：Hermes 依 skill 判斷為 Level 0，組標準 Task Envelope，交給 OpenClaw 整理成表格。
- **成功證據**：`metadata` 帶 `safety_level: level_0`；OpenClaw 回 6 欄 Markdown 表格；三方對帳 task_id 一致。
- **task_id**：`task-0199478f7be1`
- **結論**：✅ 可作為第一個正式工作流。

### (6) Discord Bot PONG 測試
- **目標**：確認從 Discord 真人入口也能觸發整條鏈路。
- **方式**：在 Discord 對 Hermes Bot 下 PONG 任務。
- **成功證據**：使用者端 Discord 收到回覆（初步成功）。
- **task_id**：需到 `data/tasks.jsonl` 對帳查看（本報告未逐一列出）。
- **結論**：✅ 初步成功（使用者端測試）。

### (7) Discord Bot 商品整理測試
- **目標**：確認 Discord 端也能跑商品資料整理工作流。
- **方式**：在 Discord 對 Hermes Bot 下商品整理任務。
- **成功證據**：使用者端 Discord 收到表格回覆（初步成功）。
- **task_id**：需到 `data/tasks.jsonl` 對帳查看。
- **結論**：✅ 初步成功（使用者端測試）。

---

## 4. 踩了哪些坑（與解法）

| 坑 | 說明 | 解法 |
|---|---|---|
| Python 3.14 裝不起來 | pydantic-core 需要 Rust 編譯，3.14 出問題 | 改用 **Python 3.12** |
| Windows 路徑 ≠ WSL 路徑 | PowerShell 與 WSL 路徑寫法不同，容易混亂 | 統一在 **WSL** 內操作專案 |
| ZIP 解壓有雙層資料夾 | 解開後變 `hermes-openclaw-adapter/hermes-openclaw-adapter/` | 進到正確的內層資料夾再操作 |
| Windows 的 .venv 不能搬到 WSL | 虛擬環境跟系統綁定，跨系統不能直接用 | 在 WSL **重新建 venv** |
| 18789 是 Control UI 不是 API | `curl 18789` 看到的是網頁，不是任務 API | 認清它是 **WebSocket Gateway** |
| `/api/tasks`、`/api/agent/run` 都 404 | 以為有 REST API，其實沒有 | OpenClaw 沒有 REST 任務 API |
| 真正入口是 CLI / Gateway | 找了半天才確認 | 用 **CLI 模式**（最簡單可行） |
| `mcp[cli]` 裝進 Adapter .venv 會壞 | 它升級 starlette/pydantic，弄壞 FastAPI（`on_startup` 報錯） | MCP server 改用**獨立 `mcp/.venv`**，Adapter `.venv` 還原 |
| tasks.jsonl 很長像出錯 | 新手以為是錯誤訊息 | 它只是**任務帳本**，越用越長是正常的 |
| 半自動派工可能誤觸 | 自動判斷可能把不該交的也交出去 | 改成**保守派工**：明確說「用 OpenClaw」才派 |

---

## 5. 目前工作流狀態

| 項目 | 狀態 |
|---|---|
| Adapter → OpenClaw | ✅ 完成 |
| Hermes → MCP → Adapter → OpenClaw | ✅ 完成 |
| Discord → Hermes → OpenClaw | ✅ 已初步成功（使用者端） |
| 商品資料整理工作流 | ✅ 可列為第一個正式工作流 |
| Callback（做完主動回報） | ⬜ 尚未做 |
| Queue（任務排隊） | ⬜ 尚未做 |
| WebSocket RPC（高效版） | ⬜ 尚未做 |
| GitHub remote（雲端備份） | ⬜ 尚未做 |

---

## 6. 測試完成結果

**目前可以正式說：Hermes → MCP → Adapter → 真實 OpenClaw 整條鏈路已通。**

而且不是只會回 PONG，是真的會做事：
- ✅ **三點摘要**真實任務成功（`task-2000b69a1a97`）。
- ✅ **商品資料整理 Markdown 表格**成功（`task-0199478f7be1`）。
- ✅ **Discord Bot 端**有回覆成功（PONG 與商品整理，使用者端初步驗證）。

> 判斷成功的方法：**三方對帳同一個 task_id** —— Discord/Hermes 的回覆、Adapter 的 log、tasks.jsonl 的紀錄，三處 task_id 一致，才算真的通（不是 Hermes 嘴巴講講）。

---

## 7. 新手小白操作教程（日常怎麼用）

### A. 啟動 Adapter（每次使用前先開，視窗不要關）

```bash
cd ~/projects/hermes-openclaw-adapter
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

### B. 在 Discord 對 Hermes Bot 下任務

**範例 1：PONG 測試**
```text
請用 OpenClaw 執行一個安全測試。
任務內容：請只回覆 PONG，不要操作任何檔案、不要執行外部命令、不要登入網站、不要下單、不要發送訊息。
```

**範例 2：商品資料整理**
```text
請用 OpenClaw 執行商品資料整理工作流。
安全等級：Level 0。不要查網路、不要操作檔案、不要登入網站、不要下單、不要發送訊息。
請把以下商品資料整理成 Markdown 表格（欄位：商品名稱/品牌/商品特色/適合對象/注意事項/代購提醒）：
1. ...
2. ...
3. ...
```

### C. 驗證是否成功（查任務帳本最後一筆）

```bash
cd ~/projects/hermes-openclaw-adapter
python - <<'PY'
import json
with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
    lines = [line for line in f if line.strip()]
item = json.loads(lines[-1])
print("task_id   :", item.get("task_id"))
print("title     :", item.get("hermes_task", {}).get("title"))
print("status    :", item.get("adapter_status"))
print("transport :", item.get("transport"))
print("message   :", item.get("openclaw_message") or item.get("message"))
PY
```

看到 `status: sent` 且 task_id 跟 Discord 回的對得起來，就是成功。

---

## 8. 新手小白注意事項

- 🟢 **Adapter 視窗不能關**（關了就沒人接任務）。
- 🟢 **不用再開 Mock OpenClaw**（已接真的了）。
- 🔴 **不要直接改 `.env` 裡的 token**（改了 Hermes/MCP 就連不上，要一起改）。
- 🔴 **不要 commit** `.env` / `.venv` / `data/` / 任何 token。
- 🔴 **不要測**登入、下單、付款、刪除、發訊息（高風險）。
- 🟢 **先只玩 Level 0 純文字整理**。
- 🟢 看到 `tasks.jsonl` 很長**不是錯**，那是帳本。
- 🟡 **OpenClaw 會消耗模型額度**，別狂打。
- 🟡 **任務太久可能是 timeout**，不一定是失敗（等等或調大逾時）。
- 🟡 **Discord 有回覆不代表一定通** —— 要看 `tasks.jsonl` 對帳。
- 🟢 記住**三方對帳**：Discord 結果 + Adapter log + tasks.jsonl 的 task_id。

---

## 9. 新手小白建議（下一步怎麼練）

- 先用 **PONG** 與 **商品整理** 反覆練手感。
- 採用**保守派工**：明確說「請用 OpenClaw 執行…」才派工，避免誤觸。
- **不要急著做 Callback / Queue**（現在用不到）。
- 下一個適合的工作流：**Beyblade 採購分析** —— 但**先只分析你貼上的資料**，不查網路、不下單。
- 再下一個：**代購訂單整理** —— 但**先只整理**，不發訊息、不付款、不下單。

---

## 10. 接下來還能施工什麼

### 現在不急（用不到先別做）
- Callback（任務做完主動回報）
- Queue（任務排隊）
- WebSocket RPC（高效版串接）
- Docker 化
- GitHub remote（雲端備份）
- 自動排程

### 未來可做（想擴充時）
- 保守派工型 skill（更嚴格的派工守則）
- Level 3+ 人工確認規則（高風險先問人）
- Beyblade 採購分析工作流
- 代購訂單整理工作流
- 工作流模板庫（一鍵套用常用任務）
- 任務查詢小工具
- 更好看的 `tasks.jsonl` 檢視器

---

## 附：版控里程碑

| Tag | 意義 |
|---|---|
| `v0.1-cli-success` | Adapter → 真實 OpenClaw CLI 跑通（PONG） |
| `v0.2-mcp-e2e-real-task` | Hermes → MCP → Adapter → OpenClaw（三點摘要）跑通 |
| `v0.3-first-product-workflow` | OpenClaw Executor skill + 商品資料整理工作流跑通 |

**結論：Hermes + OpenClaw MVP 已可正式收尾。整條鏈路已通，且有真實任務、正式工作流、Discord 入口三重驗證。**
