#!/usr/bin/env bash
# 溫和停止在 port 8000 上的 Adapter v0.4（SIGTERM）。
set -uo pipefail

PORT=8000

# 1. 先用 ss 找出佔用 8000 的 pid
PID="$(ss -ltnp 2>/dev/null | grep -E "[:.]${PORT}([[:space:]]|$)" \
  | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"

# 2. 退而求其次：用 pgrep 找 uvicorn
if [ -z "${PID:-}" ]; then
  PID="$(pgrep -f "uvicorn app.main:app.*--port ${PORT}" | head -1)"
fi

if [ -z "${PID:-}" ]; then
  echo "[stop_adapter] 沒有找到在 port ${PORT} 的 Adapter process，無需停止。"
  exit 0
fi

echo "[stop_adapter] 找到 Adapter process：pid ${PID}"
ps -o pid,lstart,cmd -p "${PID}" 2>/dev/null || true

echo "[stop_adapter] 送出 SIGTERM 溫和停止..."
kill -TERM "${PID}" 2>/dev/null || true

# 3. 最多等 10 秒
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if ! kill -0 "${PID}" 2>/dev/null; then
    echo "[stop_adapter] ✅ 已停止 (pid ${PID})。"
    exit 0
  fi
  sleep 1
done

echo "[stop_adapter] ⚠️ 10 秒後 pid ${PID} 仍在執行。" >&2
echo "[stop_adapter] 如確認要強制結束，可自行執行： kill -9 ${PID}" >&2
exit 1
