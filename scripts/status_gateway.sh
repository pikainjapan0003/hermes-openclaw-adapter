#!/usr/bin/env bash
# 檢查 Hermes Gateway 是否在跑，以及 Discord 最近的連線狀態。
set -uo pipefail

GW_LOG="$HOME/.hermes/logs/gateway.log"

echo "=== Hermes Gateway process ==="
if pgrep -f "bin/hermes gateway run" >/dev/null 2>&1; then
  pgrep -af "bin/hermes gateway run"
  echo "[status_gateway] ✅ Gateway 正在執行。"
  GW_OK=0
else
  echo "[status_gateway] ❌ 找不到 Gateway process（可執行 ./scripts/start_gateway.sh 啟動）。"
  GW_OK=1
fi

echo
echo "=== tmux sessions ==="
tmux ls 2>/dev/null || echo "(無 tmux session)"

echo
echo "=== Discord 連線（最近 log）==="
if [ -f "$GW_LOG" ]; then
  LAST="$(grep -E "\[Discord\].*(Connected|Disconnected|connected|disconnected)" "$GW_LOG" | tail -5)"
  if [ -n "$LAST" ]; then
    echo "$LAST"
    if echo "$LAST" | tail -1 | grep -qiE "Connected|connected" ; then
      echo "[status_gateway] ✅ 最近一筆 Discord 紀錄是 connected。"
    else
      echo "[status_gateway] ⚠️ 最近一筆 Discord 紀錄不是 connected，請檢查。"
    fi
  else
    echo "(log 裡找不到 Discord 連線紀錄)"
  fi
else
  echo "(找不到 $GW_LOG)"
fi

exit "${GW_OK}"
