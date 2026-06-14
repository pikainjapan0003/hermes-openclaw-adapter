#!/bin/bash
# v0.4 callback MVP — 派一個 Level 0 PONG 任務，應該「立刻」回 accepted + task_id。
# 之後用：  ./scripts/check_task_result.sh <task_id>  查結果。
set -e

ADAPTER_URL="${ADAPTER_URL:-http://127.0.0.1:8000}"
ADAPTER_TOKEN="${HERMES_ADAPTER_TOKEN:-change-me}"

curl -s -X POST "$ADAPTER_URL/tasks/dispatch" \
  -H "Content-Type: application/json" \
  -H "X-Adapter-Token: $ADAPTER_TOKEN" \
  -d '{
    "title": "Callback PONG 測試",
    "goal": "測試背景任務與 callback",
    "task_text": "請只回覆 PONG，不要操作任何檔案、不要登入、不要下單、不要發訊息。",
    "priority": "normal",
    "metadata": {
      "safety_level": "Level 0",
      "source": "callback_test",
      "workflow": "callback_pong"
    }
  }'
echo
