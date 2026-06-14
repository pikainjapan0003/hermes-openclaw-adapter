#!/usr/bin/env bash
# 啟動 Hermes Gateway（含 Discord）。使用已驗證的 tmux 啟動方式。
# 若 Gateway 已在執行，不會重複啟動，也不會破壞現有 gateway。
set -uo pipefail

PROJECT_DIR="$HOME/projects/hermes-openclaw-adapter"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/hermes-gateway.log"
SESSION="hermes"

# 1. 真正的 gateway python process 是否已在跑？（比對 bin/hermes，避免誤判 tmux 啟動字串）
if pgrep -f "bin/hermes gateway run" >/dev/null 2>&1; then
  echo "[start_gateway] Hermes Gateway 已在執行中，不重複啟動。"
  pgrep -af "bin/hermes gateway run" || true
  echo "[start_gateway] 官方詳細 log： ~/.hermes/logs/gateway.log"
  exit 0
fi

# 2. 若 tmux session 已存在（但 gateway 死掉的殘留），不硬上，請人工清理
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[start_gateway] ⚠️ tmux session '$SESSION' 已存在，但沒偵測到執行中的 gateway。" >&2
  echo "[start_gateway] 可能是殘留 session。請先確認後清理： tmux kill-session -t $SESSION" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# 3. 用已驗證的方式啟動：detached tmux session
tmux new -d -s "$SESSION" hermes gateway run

# 4. 把 tmux pane 輸出鏡像到我們的 log（best-effort；官方 log 仍在 ~/.hermes/logs/）
sleep 1
tmux pipe-pane -o -t "$SESSION" "cat >> '$LOG_FILE'" 2>/dev/null || true

echo "[start_gateway] ✅ 已在 tmux session '$SESSION' 啟動 Hermes Gateway。"
echo "[start_gateway] 鏡像 log → ${LOG_FILE}"
echo "[start_gateway] 官方詳細 log → ~/.hermes/logs/gateway.log"
echo "[start_gateway] 幾秒後可執行 ./scripts/status_gateway.sh 確認 Discord 是否 connected。"
