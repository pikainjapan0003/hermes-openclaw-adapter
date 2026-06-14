# 下一步路線

## 目前版本（CLI 模式）

```text
Hermes → Adapter → OpenClaw CLI (openclaw agent --message ... --json) → 真實 OpenClaw
```

- Adapter 用 `asyncio.create_subprocess_exec` 呼叫 `openclaw agent`（不經過 shell）。
- 任務文字由 `build_openclaw_message()` 組出（用 instruction / goal / title / metadata）。
- 逾時預設 600 秒（`OPENCLAW_CLI_TIMEOUT_SECONDS`）。
- 要求：Adapter 必須跑在能存取 `openclaw` 的環境（WSL），且與 OpenClaw 同一使用者。

## 下一版：Callback

加入 Callback，讓 OpenClaw 做完回報 Hermes：

```text
Hermes → Adapter → OpenClaw → Callback → Hermes
```

需要新增：

```text
POST /callbacks/openclaw
```

OpenClaw 做完後回傳：

```json
{
  "task_id": "task-xxxx",
  "status": "completed",
  "summary": "任務完成摘要",
  "result": {}
}
```

## 升級：改用 WebSocket RPC（效能版）

CLI 模式每次任務會 spawn 一個 node process（數百 ms 起步），不適合超高頻。
任務量變大時，可改成直接連 OpenClaw 的 WebSocket Gateway：

```text
ws://127.0.0.1:18789  →  呼叫 gateway method "agent.run"
```

- 需要回應第一個 `connect.challenge` 事件，並帶上 gateway token
  （位置：`~/.openclaw/openclaw.json` → `gateway.auth.token`）。
- 對應的改法是把 `run_openclaw_cli()` 換成一個 WebSocket client（例如 `websockets` 套件）。

## 再下一版：Queue

任務再多就加 Queue：

```text
Hermes → Adapter → Queue → OpenClaw Worker → Callback → Hermes
```
