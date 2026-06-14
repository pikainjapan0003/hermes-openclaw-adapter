# 任務格式說明

## Hermes → Adapter 任務格式

```json
{
  "task_id": "可選，不填 Adapter 會自動產生",
  "title": "任務標題",
  "goal": "任務目標",
  "task_text": "完整任務內容",
  "priority": "normal",
  "source": "hermes",
  "metadata": {}
}
```

## 欄位說明

| 欄位 | 必填 | 說明 |
|---|---|---|
| task_id | 否 | 任務 ID，不填會自動產生 |
| title | 是 | 給人看的任務名稱 |
| goal | 是 | 這次任務的成功目標 |
| task_text | 是 | 要交給 OpenClaw 執行的完整指令 |
| priority | 否 | low / normal / high |
| source | 否 | 預設 hermes |
| metadata | 否 | 額外資料，例如客戶、專案、平台 |

---

## Adapter → OpenClaw 預設格式

```json
{
  "type": "agent_task",
  "source": "hermes",
  "task_id": "task-xxxx",
  "priority": "normal",
  "title": "任務標題",
  "instruction": "完整任務內容",
  "goal": "任務目標",
  "metadata": {}
}
```

---

## 最小測試任務

```json
{
  "title": "第一個測試任務",
  "goal": "確認 Hermes 可以透過 Adapter 派任務給 OpenClaw",
  "task_text": "請回覆：OpenClaw 已收到任務。",
  "priority": "normal"
}
```
