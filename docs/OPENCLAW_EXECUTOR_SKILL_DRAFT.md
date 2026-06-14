# OpenClaw Executor Skill（草稿 / 版控備份）

> 這是 Hermes skill「openclaw-executor」的草稿備份，方便版控保存。
> **實際安裝位置（不納入版控）**：`~/.hermes/skills/automation/openclaw-executor/SKILL.md`
> `~/.hermes` 是 Hermes 私人設定，**不要 commit**；只 commit 這份專案內的草稿。
>
> 安裝方式：把下面 `SKILL.md` 區塊的內容存到
> `~/.hermes/skills/automation/openclaw-executor/SKILL.md`，
> Hermes 會自動掃到（`hermes skills list` 可見，category=automation，local，enabled）。
> 本草稿已於 2026-06-14 用第一個 Level 0 商品資料整理工作流實測通過。

---

## SKILL.md 內容

```markdown
---
name: openclaw-executor
description: When a task needs real execution, tools, automation, CLI, cross-platform operation, fixed-format data organizing, or task delivery, delegate it to OpenClaw by calling the MCP tool dispatch_to_openclaw. Use for "organize/format this data into a table", running tools, or any "go and do it" task — NOT for chat, explanation, or simple Q&A.
---

# OpenClaw Executor

Hermes 是主腦，OpenClaw 是執行端（數位員工的手腳）。
這個 skill 教 Hermes 什麼時候該把任務交給 OpenClaw，以及怎麼安全地交。

工具名稱：dispatch_to_openclaw（MCP，stdio）。它會把任務送到本機 Adapter
（POST /tasks/dispatch），再由 Adapter 呼叫真實 OpenClaw CLI，並把結果回傳。

## 核心原則
- Hermes 是主腦：負責理解、拆解、判斷、記憶、整理結果。
- OpenClaw 是執行端：負責執行、自動化、CLI / 平台 / 工具落地。
- 不要把所有任務都交給 OpenClaw。
- 純聊天、純解釋、純概念教學、不需外部執行的簡單問答 → Hermes 自己處理。
- 只有當任務需要「執行 / 工具 / 自動化 / CLI / 跨平台 / 固定格式整理 / 任務落地」時，才呼叫 dispatch_to_openclaw。

## 安全分級
- Level 0 純文字整理（摘要/改寫/整理成表格）→ 可自動交給 OpenClaw
- Level 1 讀取資料（不修改）→ 可自動交給 OpenClaw
- Level 2 建立草稿 → 可交，但結果要回報
- Level 3 修改檔案 → 先問使用者確認
- Level 4 登入/付款/刪除/下單/發送訊息 → 必須先問使用者
- Level 5 高風險或目標不明確 → 拒絕或要求補充
口訣：等級越高越要先問人。

## 呼叫前自我檢查
1. 真的需要 OpenClaw 嗎？2. 目標明確、輸入完整、可驗證？3. 安全等級？需要確認？
4. 預期輸出？5. 不要把密碼/API key/token/cookie/個資放進 task_text 或 metadata。

## 標準 Task Envelope
{
  "title": "...",
  "goal": "...",
  "task_text": "完整指令（必填）。在這裡明寫安全邊界：不要查網路/操作檔案/登入/下單/發送訊息。",
  "priority": "low",
  "metadata": {
    "source": "hermes", "workflow": "<名稱>",
    "safety_level": "level_0", "requires_confirmation": false,
    "expected_output": "例如：Markdown 表格，欄位 A/B/C"
  }
}
欄位重點：必填是 task_text；沒有 instruction 欄位（用了會 422）；
metadata 自由欄位，safety_level/requires_confirmation/expected_output 現在就能帶。

## 收到結果後
- 讀 openclaw_response，確認 ok 與結果是否合理。
- 整理成使用者看得懂的人話回覆，不要直接貼原始 JSON。
- 失敗時說明原因並給下一步。
```

---

## 驗證紀錄

- `hermes skills list` → `openclaw-executor | automation | local | local | enabled` ✅
- 第一個 Level 0 工作流（商品資料整理）實測：Hermes 依 skill 組出含 `safety_level: level_0` 的
  Task Envelope，呼叫 `dispatch_to_openclaw`，OpenClaw 回傳 Markdown 表格。
- 詳見 `docs/FIRST_PRODUCT_WORKFLOW_TEST_REPORT.md`。
