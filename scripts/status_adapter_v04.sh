#!/usr/bin/env bash
# 檢查 Adapter v0.4 health，並確認 version 是否為 0.4.0。
set -uo pipefail

URL="http://127.0.0.1:8000/health"

echo "[status_adapter] GET ${URL}"
BODY="$(curl -s -m 5 "${URL}" || true)"

if [ -z "${BODY:-}" ]; then
  echo "[status_adapter] ❌ 沒有回應 —— Adapter 可能沒有在跑（port 8000）。"
  echo "[status_adapter] 可執行 ./scripts/start_adapter_v04.sh 啟動。"
  exit 1
fi

echo "${BODY}"

if echo "${BODY}" | grep -q '"version":"0.4.0"'; then
  echo "[status_adapter] ✅ version 0.4.0 確認，正式 Adapter 是 v0.4。"
  exit 0
else
  echo "[status_adapter] ⚠️ 回應裡沒有 \"version\":\"0.4.0\" —— 可能是舊版或別的程式佔用 8000。"
  exit 2
fi
