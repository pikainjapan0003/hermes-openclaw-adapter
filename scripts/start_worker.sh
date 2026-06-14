#!/usr/bin/env bash
# 啟動 v0.5 OpenClaw Queue Worker（背景常駐）。
# 等價於： python -m app.worker
set -eo pipefail

PROJECT_DIR="$HOME/projects/hermes-openclaw-adapter"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/worker.log"

cd "$PROJECT_DIR"

if [ ! -f .venv/bin/activate ]; then
  echo "[start_worker] ❌ 找不到 .venv。先建立： python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

if pgrep -f "app.worker" >/dev/null 2>&1; then
  echo "[start_worker] ⚠️ 偵測到已有 worker 在跑，不重複啟動（單一 worker 架構）。" >&2
  pgrep -af "app.worker" || true
  exit 1
fi

mkdir -p "$LOG_DIR"
# shellcheck disable=SC1091
source .venv/bin/activate

setsid nohup python -m app.worker >> "$LOG_FILE" 2>&1 < /dev/null &

echo "[start_worker] ✅ 已啟動 Queue Worker。"
echo "[start_worker] log → ${LOG_FILE}"
echo "[start_worker] 停止： pkill -f 'app.worker'"
