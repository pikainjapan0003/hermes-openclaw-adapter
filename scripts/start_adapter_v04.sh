#!/usr/bin/env bash
# 啟動 Hermes OpenClaw Adapter v0.4（背景常駐）。
# 若 port 8000 已被佔用，會提示並結束，不會硬開第二個。
set -eo pipefail

PROJECT_DIR="$HOME/projects/hermes-openclaw-adapter"
PORT=8000
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/adapter-v0.4.log"

cd "$PROJECT_DIR"

# 1. 檢查 port 是否已被佔用
if ss -ltn 2>/dev/null | grep -qE "[:.]${PORT}([[:space:]]|$)"; then
  echo "[start_adapter] ⚠️ Port ${PORT} 已被佔用，不重複啟動。" >&2
  ss -ltnp 2>/dev/null | grep -E "[:.]${PORT}([[:space:]]|$)" || true
  echo "[start_adapter] 若要重啟，請先執行： ./scripts/stop_adapter_v04.sh" >&2
  exit 1
fi

# 2. 檢查 venv
if [ ! -f .venv/bin/activate ]; then
  echo "[start_adapter] ❌ 找不到 .venv/bin/activate。請先建立虛擬環境並安裝套件：" >&2
  echo "    python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

# 3. 檢查 .env
if [ ! -f .env ]; then
  echo "[start_adapter] ❌ 找不到 .env（可從 .env.example 複製）。" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

# shellcheck disable=SC1091
source .venv/bin/activate

# 4. 背景啟動（setsid + nohup，關掉終端機也不中斷）
setsid nohup uvicorn app.main:app --host 0.0.0.0 --port "${PORT}" --env-file .env \
  >> "$LOG_FILE" 2>&1 < /dev/null &

echo "[start_adapter] ✅ 已啟動 Adapter v0.4 (port ${PORT})。"
echo "[start_adapter] log → ${LOG_FILE}"
echo "[start_adapter] 幾秒後可執行 ./scripts/status_adapter_v04.sh 確認 version 0.4.0。"
