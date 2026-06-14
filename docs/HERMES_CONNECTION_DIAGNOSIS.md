# Hermes 接入診斷報告

> 只讀診斷（read-only）。本報告**沒有修改** Hermes、OpenClaw、Adapter 的任何核心功能或設定，只新增這份文件。
> 產生時間：2026-06-14
> 目的：確認「真實 Hermes Agent」要用哪種方式呼叫 Adapter（`POST /tasks/dispatch`），把任務交給 OpenClaw。

---

## 0. 一句話結論

**Hermes 找到了，而且正在跑。** 它是一個功能完整的 tool-calling agent（Hermes Agent v0.16.0），**原生支援 MCP（stdio + HTTP）、skills、profiles、terminal 工具**。

要把 Hermes 接到 Adapter，**最推薦做一個小小的 MCP server**（tool 名稱 `dispatch_to_openclaw`），讓 Hermes 像呼叫任何工具一樣把任務送進 Adapter。
（如果想最快先跑通，也可以先用「terminal 工具直接 curl」或「一個 Skill」過渡，見第 9 節排序。）

---

## 1. Hermes 是否找到 → ✅ 有

| 項目 | 值 |
|---|---|
| CLI 執行檔 | `/home/lnovo/.local/bin/hermes`（另有專案內 wrapper `~/.hermes/hermes-agent/hermes`） |
| 專案目錄 | `/home/lnovo/.hermes/hermes-agent/`（Python 專案，含 `.git`） |
| 版本 | **Hermes Agent v0.16.0 (2026.6.5)**，Python 3.11.15，OpenAI SDK 2.24.0 |
| 主設定檔 | `~/.hermes/config.yaml`（YAML，chmod 600，**含密鑰，未讀取內容**） |
| 密鑰檔 | `~/.hermes/.env`、`~/.hermes/auth.json`（**未讀取**） |
| 狀態 / DB | `~/.hermes/state.db`、`~/.hermes/sessions/`、`~/.local/state/hermes/` |

> 註：在「非登入 shell」裡 `which hermes` 會找不到，但 `~/.local/bin` 有在你登入後的 PATH 裡，所以你平常的終端機可以直接打 `hermes`。binary 已確認存在。

## 2. Hermes 啟動方式

目前是用 tmux 背景跑 gateway：

```bash
# 目前實際在跑的（tmux session 名稱 = hermes）
tmux new -d -s hermes hermes gateway run
```

其他常用啟動方式：

```bash
hermes chat            # 互動式對話（CLI agent）
hermes gateway run     # 訊息 gateway（Telegram/Discord/Slack 等渠道）
hermes --help          # 看所有子指令
hermes status          # 看各元件狀態
```

## 3. Hermes 是否正在執行 → ✅ 是

```text
PID 581  tmux new -d -s hermes hermes gateway run
PID 582  /home/lnovo/.hermes/hermes-agent/venv/bin/python3 .../hermes gateway run
```

- gateway 正在跑（背景）。
- **注意：Hermes gateway 沒有開任何 TCP port**（`ss -lntp` 只看到 OpenClaw 的 18789）。
  代表 Hermes 不是用「對外 HTTP port」運作，而是走訊息渠道 + 內部狀態。
  → 這也說明：**不能直接 POST 到 Hermes**；整合方向是「Hermes 主動呼叫 Adapter」，方向正確。

## 4. Hermes 是否有 CLI → ✅ 有（非常完整）

`hermes` 子指令（節錄與整合最相關的）：

| 指令 | 用途 |
|---|---|
| `chat` | 互動式 agent 對話 |
| `mcp` | **管理 MCP server / 把 Hermes 當 MCP server 跑** ← 整合重點 |
| `tools` | 啟用/停用各平台的工具（built-in 用單名，MCP 用 `server:tool`） |
| `skills` | 搜尋/安裝/管理 skills |
| `profile` | 多個隔離的 Hermes 實例 |
| `webhook` | 管理「動態 webhook 訂閱」（偏向 inbound 事件，不是拿來打外部 API） |
| `hooks` | shell-script hooks |
| `gateway` | 訊息 gateway |
| `cron` | 排程 |

## 5. Hermes 是否有 HTTP tool → ⚠️ 沒有「通用 HTTP POST 工具」

`hermes tools list` 顯示的 built-in 工具（✓=啟用）：

```text
✓ web 🔍 Web Search & Scraping      ✓ browser 🌐 Browser Automation
✓ terminal 💻 Terminal & Processes  ✓ file 📁 File Operations
✓ code_execution ⚡ Code Execution  ✓ vision 👁 Vision
✓ image_gen 🎨                       ✓ tts 🔊
✓ skills 📚                          ✓ todo 📋
✓ memory 💾                          ✓ session_search 🔎
✓ clarify ❓                          ✓ delegation 👥
✓ cronjob ⏰                          ✓ messaging 📨
✓ computer_use 🖱                     （video / x_search / moa / homeassistant / spotify 等預設停用）
```

重點：
- **沒有**一個「任意 URL + 自訂 header 的 HTTP POST」工具。`web` 是搜尋/抓網頁（偏 GET），不適合帶 `X-Adapter-Token` 打我們的 endpoint。
- **但 `terminal`（💻）是啟用的** → Hermes 可以直接執行 `curl` 來打 Adapter（這就是過渡用的 CLI wrapper 方案）。
- **真正乾淨的「給 Hermes 一個自訂工具」的官方機制是 MCP**（見下一節）。

**Hermes 能不能呼叫 `POST http://127.0.0.1:8000/tasks/dispatch`？→ 可以**，而且有三條路：MCP 工具（推薦）、Skill、或 terminal 直接 curl。

## 6. Hermes 是否有 MCP → ✅ 有（一等公民，stdio + HTTP 都支援）

`hermes mcp` 子指令：`serve / add / remove / list / test / configure / login / picker / catalog / install`

- **目前沒有設定任何 MCP server**（`hermes mcp list` → "No MCP servers configured."）。
- 新增方式（`hermes mcp add --help` 實際參數）：
  ```text
  hermes mcp add <name> --url <URL>                 # HTTP/SSE MCP
  hermes mcp add <name> --command <cmd> --args ...  # stdio MCP
                 [--auth {oauth,header}] [--env KEY=VALUE ...] [--preset ...]
  ```
  → **stdio MCP 與 HTTP MCP 都支援。**
- MCP server 設定會寫進 `~/.hermes/config.yaml` 的 `mcp_servers.<name>` 區塊。
- MCP 提供的工具會以 `server:tool` 形式出現，可用 `hermes tools enable/disable` 控制、`hermes mcp test <name>` 測試連線。
- 既有的 catalog 範例在 `~/.hermes/hermes-agent/optional-mcps/`（`n8n`、`linear`），manifest 格式為 `manifest.yaml`（transport stdio：`command` + `args`）。

## 7. Hermes 是否有 Skills / Profiles → ✅ 都有

- **Skills**：`hermes skills`（browse/search/install/inspect/list…）。範例在 `optional-skills/`（health、devops、productivity… 共 19 類）。
  - 格式：每個 skill 是一個資料夾 + `SKILL.md`，前面是 YAML frontmatter：
    ```yaml
    ---
    name: <skill-name>
    description: >
      ...
    platforms: [linux, macos, windows]
    version: 1.0.0
    metadata:
      hermes:
        prerequisites:
          commands: [curl, python3]
    required_environment_variables:
      - name: SOME_API_KEY
        ...
    ---
    # 後面是給 agent 看的說明（何時用、怎麼用、要呼叫哪個 API…）
    ```
  - Skill **本身不是程式**，而是「告訴 agent 怎麼做」的說明書；agent 用 `terminal` / `code_execution` 去實際執行（例如 `curl` 某 API）。所以一個 skill 可以叫 Hermes「用 curl POST 到 Adapter」。
- **Profiles**：`hermes profile`（多個隔離實例），可為「OpenClaw 任務」開一個專用 profile，但對「呼叫 Adapter」這件事不是必需。

## 8. Hermes 最適合用哪一種方式接 Adapter

**最適合：MCP（stdio）。** 原因：
- 它是 Hermes 官方「擴充自訂工具」的標準機制，目前還沒有任何 MCP server，乾淨。
- agent 會看到一個有明確輸入欄位（title/goal/task_text…）的 typed 工具 `openclaw:dispatch_to_openclaw`，呼叫穩定、可控，不必每次自己拼 curl 字串。
- 不需要 `--yolo` 或開放 terminal 任意執行，安全性好。
- 可用 `hermes tools` 開關、`hermes mcp test` 驗證。

## 9. 推薦方案排序

| 排名 | 方案 | 可行性 | 優點 | 缺點 |
|---|---|---|---|---|
| 🥇 **B. MCP tool → Adapter** | **推薦** | 高 | typed 工具、穩定、安全、官方機制 | 要寫一個小 MCP server（約 30 行） |
| 🥈 C. Skill → Adapter | 可行 | 高 | 只寫一個 `SKILL.md`、最快、用 terminal 執行 | agent 每次自己組 curl，較不穩定/不 typed |
| 🥉 D. CLI wrapper（terminal 直接 curl） | 可行 | 中 | 零設定，馬上能測 | 最不可控，要靠 prompt 約束，需注意跳脫與審批 |
| ⛔ A. 原生 HTTP tool → Adapter | 不適用 | 低 | — | Hermes **沒有通用 HTTP POST 工具**；HTTP 版其實就是「HTTP MCP」，等於併入 B |

> 建議：**正式版用 B（MCP）**。若想今天就先看到「真實 Hermes → Adapter → OpenClaw」跑通，可先用 D（terminal curl）或 C（skill）過渡，再升級到 B。

## 10. 若推薦 MCP：MCP server 設計

做一個 **stdio MCP server**，放在 Adapter 專案內（新檔，之後才建）：

```
~/projects/hermes-openclaw-adapter/mcp/openclaw_mcp.py
```

它只做一件事：把工具呼叫轉成對 Adapter 的 HTTP POST。

**工具規格：**

- tool name：`dispatch_to_openclaw`
- 用途：把任務送到 Adapter `/tasks/dispatch`，由 OpenClaw 執行
- 輸入：
  - `title`（必填）
  - `goal`（必填）
  - `task_text`（必填，完整指令）
  - `priority`（選填：`low`/`normal`/`high`，預設 `normal`）
  - `metadata`（選填 object）
- 輸出：Adapter 的 JSON（`ok` / `adapter_status` / `transport` / `task_id` / `openclaw_response` 或 `error`）

**程式骨架（示意，尚未建立）：**

```python
# mcp/openclaw_mcp.py
import os, httpx
from mcp.server.fastmcp import FastMCP   # pip install "mcp[cli]" 或 fastmcp

ADAPTER_URL = os.getenv("OPENCLAW_ADAPTER_URL", "http://127.0.0.1:8000/tasks/dispatch")
ADAPTER_TOKEN = os.getenv("OPENCLAW_ADAPTER_TOKEN", "change-me")

mcp = FastMCP("openclaw")

@mcp.tool()
def dispatch_to_openclaw(title: str, goal: str, task_text: str,
                         priority: str = "normal", metadata: dict | None = None) -> dict:
    """把任務送到 OpenClaw 執行端（透過本機 Adapter）。只在需要實際執行/操作/自動化時使用。"""
    payload = {"title": title, "goal": goal, "task_text": task_text,
               "priority": priority, "metadata": metadata or {"source": "hermes"}}
    headers = {"Content-Type": "application/json", "X-Adapter-Token": ADAPTER_TOKEN}
    r = httpx.post(ADAPTER_URL, json=payload, headers=headers, timeout=660)
    try:
        return r.json()
    except Exception:
        return {"ok": False, "status_code": r.status_code, "raw": r.text}

if __name__ == "__main__":
    mcp.run()  # stdio
```

**註冊到 Hermes（之後執行，會寫進 `~/.hermes/config.yaml`）：**

```bash
hermes mcp add openclaw \
  --command /home/lnovo/projects/hermes-openclaw-adapter/.venv/bin/python \
  --args /home/lnovo/projects/hermes-openclaw-adapter/mcp/openclaw_mcp.py \
  --env OPENCLAW_ADAPTER_URL=http://127.0.0.1:8000/tasks/dispatch \
        OPENCLAW_ADAPTER_TOKEN=change-me

hermes mcp test openclaw          # 測連線
hermes tools enable openclaw      # 若未自動啟用
# 正在跑的 gateway 可能要重啟才會吃到新設定：
#   tmux kill-session -t hermes ; tmux new -d -s hermes hermes gateway run
```

> 需要先 `pip install "mcp[cli]"`（或 `fastmcp`）到 Adapter 的 `.venv`。

## 11. 若推薦 HTTP tool：Hermes tool 設定範例

Hermes **沒有**通用 HTTP POST 工具，所以沒有「純 HTTP tool」設定可填。
最接近 HTTP 的官方做法就是 **HTTP MCP**：

```bash
hermes mcp add openclaw --url http://127.0.0.1:8000/mcp --auth header
```

但我們的 Adapter 目前只提供一般 REST（`/tasks/dispatch`），**不是 MCP endpoint**，所以這條路需要先讓 Adapter 額外開一個 MCP HTTP endpoint —— 比第 10 節的 stdio server 麻煩。**不建議**，仍以第 10 節 stdio MCP 為主。

## 12. 若推薦 Skill / Profile：skill 設定範例

最快的過渡方案。建立一個 skill 資料夾（之後才建）：

```
~/.hermes/skills/openclaw-executor/SKILL.md
```

```markdown
---
name: openclaw-executor
description: >
  把需要實際執行/操作/自動化的任務，透過本機 Adapter 交給 OpenClaw 執行。
  只在需要「執行」而非「回答」時使用。
platforms: [linux]
version: 0.1.0
metadata:
  hermes:
    tags: [openclaw, executor, automation]
    prerequisites:
      commands: [curl]
---

# OpenClaw Executor

當使用者的需求需要實際執行、操作檔案/系統、跨平台或自動化時，
用下面的方式把任務送到 OpenClaw（透過本機 Adapter）。

## 怎麼做
用 terminal 執行（把 <...> 換成實際內容；task_text 是完整指令）：

```bash
curl -s -X POST "http://127.0.0.1:8000/tasks/dispatch" \
  -H "Content-Type: application/json" \
  -H "X-Adapter-Token: change-me" \
  -d '{"title":"<標題>","goal":"<目標>","task_text":"<完整指令>","priority":"low","metadata":{"source":"hermes"}}'
```

成功時回傳會有 "ok": true、"adapter_status": "sent"，
結果文字在 openclaw_response.payloads[0].text。

## 安全
- 高風險任務（改檔/刪資料/登入/操作平台）先問使用者確認。
- 不要把密碼、API key、token 放進 task_text 或 metadata。
```

- skill 能執行 HTTP POST 嗎？→ 能，透過 `terminal` 工具跑 curl。
- skill 能呼叫本機命令嗎？→ 能（terminal / code_execution）。
- skill 能呼叫 MCP tool 嗎？→ 能，若該 MCP tool 已啟用，agent 會自行選用。

## 13. 下一步要修改 / 新增哪些檔案

> 以下都是「下一階段才動」，本報告不修改。

| 檔案 | 動作 | 屬於 |
|---|---|---|
| `~/projects/hermes-openclaw-adapter/mcp/openclaw_mcp.py` | **新增**（MCP server） | Adapter 專案 |
| `~/projects/hermes-openclaw-adapter/mcp/requirements.txt` 或主 `requirements.txt` | **新增/補** `mcp`（或 `fastmcp`）、`httpx` | Adapter 專案 |
| `~/projects/hermes-openclaw-adapter/.env.example` | （可選）補 MCP 用的 `OPENCLAW_ADAPTER_URL` / `OPENCLAW_ADAPTER_TOKEN` 說明 | Adapter 專案 |
| `~/.hermes/config.yaml` 的 `mcp_servers.openclaw` | **由 `hermes mcp add` 自動寫入**（不要手改） | Hermes 設定 |
| （Skill 方案才需要）`~/.hermes/skills/openclaw-executor/SKILL.md` | **新增** | Hermes skill |

## 14. 哪些檔案不能動

- ❌ Hermes 核心：`~/.hermes/hermes-agent/**`（整個專案碼）
- ❌ Hermes 密鑰 / 私人設定：`~/.hermes/config.yaml`（手改）、`~/.hermes/.env`、`~/.hermes/auth.json`、`~/.hermes/state.db`、`~/.hermes/sessions/**`
- ❌ OpenClaw 本體與設定：`/usr/lib/node_modules/openclaw/**`、`~/.openclaw/**`
- ❌ Adapter 已驗證可用的核心：`app/main.py`（除非要改翻譯邏輯，否則不動）
- ✅ 只在 Adapter 專案內**新增** `mcp/` 子目錄，並用 `hermes mcp add` 正規方式註冊

## 15. 安全測試方式

每一步都用最安全的 **PONG** 任務（只回 PONG、不碰檔案、不執行外部動作）。

- **Adapter 層**（已驗證 ✅）：
  ```bash
  curl -s -X POST "http://127.0.0.1:8000/tasks/dispatch" \
    -H "Content-Type: application/json" -H "X-Adapter-Token: change-me" \
    -d '{"title":"PONG 安全測試","goal":"連線測試","task_text":"請只回覆 PONG，不要操作任何檔案、不要執行外部動作。","priority":"low","metadata":{"source":"manual_test","workflow":"connectivity_test"}}'
  ```
- **MCP server 層**（建立後）：`hermes mcp test openclaw`
- **Hermes 端到端**：在 `hermes chat` 裡叫它「用 dispatch_to_openclaw 送一個只回 PONG 的安全任務」，看它是否呼叫工具並取回 PONG。

## 16. 怎樣才算「整條鏈路全部通」

當下面這條鏈**全自動**跑完，不需要人工 curl，就算全通：

```text
真實 Hermes Agent（hermes chat / gateway 收到指令）
   │  自己判斷「需要執行」→ 呼叫工具 dispatch_to_openclaw
   ▼
MCP server (openclaw_mcp.py)
   │  HTTP POST /tasks/dispatch（帶 X-Adapter-Token）
   ▼
Adapter (FastAPI, port 8000)
   │  asyncio.create_subprocess_exec → openclaw agent --message ... --json
   ▼
真實 OpenClaw（MiniMax-M3）
   │  回覆 PONG
   ▼
結果一路回傳：OpenClaw → Adapter → MCP → Hermes → 顯示給使用者
```

驗收標準：
1. `hermes mcp test openclaw` 連線 OK。
2. 在 `hermes chat` 給一個 PONG 任務，Hermes **自動**呼叫 `dispatch_to_openclaw`。
3. 回傳含 `ok: true`、`adapter_status: "sent"`、`openclaw_response` 裡有 `PONG`。
4. Hermes 把 PONG 整理成人話回給使用者。
5. （進階）再跑第一個安全小任務（如「三點摘要」）同樣全自動成功。

---

## 附：本次已驗證項目

- ✅ Hermes 存在、正在跑（PID 582，tmux `hermes`）、CLI 完整。
- ✅ Hermes 原生支援 MCP（stdio + HTTP）、skills、profiles、terminal 工具。
- ✅ Hermes 目前沒有任何 MCP server（乾淨可加）。
- ✅ Adapter 仍可用：curl PONG → `ok: true / adapter_status: sent / transport: cli / openclaw text: PONG`。
- ✅ 未修改 Hermes / OpenClaw / Adapter 任何核心功能或設定。
