#!/usr/bin/env bash
# v0.5 Queue 端到端 smoke test。
#
# 預設使用「假的 openclaw CLI」(回傳 PONG)，所以不需要真實 OpenClaw / Gateway 在跑，
# 純粹驗證 Adapter → Queue → Worker → results.jsonl 這條鏈。
#
# 若要對「真實 openclaw」做 PONG 測試，設定 USE_REAL_OPENCLAW=1：
#   USE_REAL_OPENCLAW=1 ./scripts/smoke_test_queue.sh
#
# 用法： ./scripts/smoke_test_queue.sh
set -uo pipefail

PROJECT_DIR="$HOME/projects/hermes-openclaw-adapter"
cd "$PROJECT_DIR"

PORT="${SMOKE_PORT:-8020}"
ADAPTER_URL="http://127.0.0.1:${PORT}"
WORKDIR="$(mktemp -d /tmp/adapter_smoke.XXXXXX)"
DATA_DIR="$WORKDIR/data"
mkdir -p "$DATA_DIR"

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then PY="python3"; fi

# --- 準備假的 openclaw CLI（除非要求用真的）---
if [ "${USE_REAL_OPENCLAW:-0}" = "1" ]; then
  OPENCLAW_BIN="openclaw"
  echo "[smoke] 使用『真實』 openclaw CLI。"
else
  OPENCLAW_BIN="$WORKDIR/fake_openclaw"
  cat > "$OPENCLAW_BIN" <<'EOF'
#!/usr/bin/env bash
# 假 openclaw：忽略所有參數，輸出 openclaw agent --json 風格、內容為 PONG。
echo '{"payloads":[{"text":"PONG"}]}'
EOF
  chmod +x "$OPENCLAW_BIN"
  echo "[smoke] 使用『假』 openclaw CLI（回 PONG）：$OPENCLAW_BIN"
fi

export DATA_DIR
# 尊重外部傳入的 EXECUTION_MODE（預設 queue）；background 模式可驗證 v0.4 舊路徑。
export EXECUTION_MODE="${EXECUTION_MODE:-queue}"
export QUEUE_DB_PATH="$DATA_DIR/queue.db"
export OPENCLAW_CLI_BIN="$OPENCLAW_BIN"
export OPENCLAW_AGENT_ID=main
export OPENCLAW_TIMEOUT_SECONDS=60
export HERMES_ADAPTER_TOKEN="${HERMES_ADAPTER_TOKEN:-smoke-token}"
export CALLBACK_ENABLED=true
export HERMES_CALLBACK_MODE=ledger_only
export WORKER_POLL_INTERVAL_SECONDS=1

ADAPTER_PID=""
WORKER_PID=""
cleanup() {
  [ -n "$WORKER_PID" ] && kill "$WORKER_PID" 2>/dev/null
  [ -n "$ADAPTER_PID" ] && kill "$ADAPTER_PID" 2>/dev/null
  wait 2>/dev/null
  echo "[smoke] 已清理（workdir 保留：$WORKDIR）"
}
trap cleanup EXIT

# --- 1. 啟動 Adapter ---
echo "[smoke] 啟動 Adapter on :$PORT ..."
$PY -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" > "$WORKDIR/adapter.log" 2>&1 &
ADAPTER_PID=$!

for i in $(seq 1 30); do
  if curl -sf "$ADAPTER_URL/health" >/dev/null 2>&1; then break; fi
  sleep 0.5
done
if ! curl -sf "$ADAPTER_URL/health" >/dev/null 2>&1; then
  echo "[smoke] ❌ Adapter 沒起來。log:"; cat "$WORKDIR/adapter.log"; exit 1
fi
echo "[smoke] Adapter health:"; curl -s "$ADAPTER_URL/health"; echo

# --- 2. 啟動 Worker ---
echo "[smoke] 啟動 Worker ..."
$PY -m app.worker > "$WORKDIR/worker.log" 2>&1 &
WORKER_PID=$!
sleep 1

# --- 3. POST 一筆 PONG 任務 ---
echo "[smoke] 派一筆 PONG 任務 ..."
RESP=$(curl -s -X POST "$ADAPTER_URL/tasks/dispatch" \
  -H "Content-Type: application/json" \
  -H "X-Adapter-Token: $HERMES_ADAPTER_TOKEN" \
  -d '{"title":"smoke PONG","goal":"verify queue worker","task_text":"請只回覆 PONG。","metadata":{"safety_level":0}}')
echo "  dispatch resp: $RESP"
TASK_ID=$(echo "$RESP" | $PY -c "import sys,json; print(json.load(sys.stdin)['task_id'])")
echo "  task_id: $TASK_ID"

# --- 4. 輪詢 task status 直到 completed/failed ---
echo "[smoke] 等待任務完成 ..."
STATUS=""
for i in $(seq 1 60); do
  Q=$(curl -s "$ADAPTER_URL/tasks/$TASK_ID" -H "X-Adapter-Token: $HERMES_ADAPTER_TOKEN")
  STATUS=$(echo "$Q" | $PY -c "import sys,json; d=json.load(sys.stdin); print((d.get('queue') or {}).get('status') or (d.get('task') or {}).get('status') or '')" 2>/dev/null)
  echo "  [$i] status=$STATUS"
  case "$STATUS" in completed|failed) break;; esac
  sleep 1
done

# --- 5. 查 result ---
echo "[smoke] GET /tasks/$TASK_ID/result :"
RESULT=$(curl -s "$ADAPTER_URL/tasks/$TASK_ID/result" -H "X-Adapter-Token: $HERMES_ADAPTER_TOKEN")
echo "$RESULT"
echo

# --- 6. 確認 results.jsonl 有結果 ---
echo "[smoke] results.jsonl:"
if [ -f "$DATA_DIR/results.jsonl" ]; then
  grep -F "$TASK_ID" "$DATA_DIR/results.jsonl" || echo "  (找不到 $TASK_ID)"
else
  echo "  ❌ 沒有 results.jsonl"
fi

# --- 判定 ---
RESULT_TEXT=$(echo "$RESULT" | $PY -c "import sys,json; d=json.load(sys.stdin); print((d.get('result') or {}).get('result_text',''))" 2>/dev/null)
echo
if [ "$STATUS" = "completed" ] && echo "$RESULT_TEXT" | grep -qi "PONG"; then
  echo "[smoke] ✅ PASS — 任務 completed 且 result_text 含 PONG。"
  EXIT=0
else
  echo "[smoke] ❌ FAIL — status=$STATUS result_text=$RESULT_TEXT"
  echo "----- worker.log -----"; cat "$WORKDIR/worker.log"
  EXIT=1
fi
exit $EXIT
