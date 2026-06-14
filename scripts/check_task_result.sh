#!/bin/bash
# 查某個任務的結果： ./scripts/check_task_result.sh task-xxxx
set -e

if [ -z "$1" ]; then
  echo "用法： $0 <task_id>"
  exit 1
fi

ADAPTER_URL="${ADAPTER_URL:-http://127.0.0.1:8000}"
ADAPTER_TOKEN="${HERMES_ADAPTER_TOKEN:-change-me}"

curl -s "$ADAPTER_URL/tasks/$1/result" \
  -H "X-Adapter-Token: $ADAPTER_TOKEN"
echo
