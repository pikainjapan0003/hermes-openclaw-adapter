from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Mock OpenClaw Server", version="0.1.0")


class OpenClawPayload(BaseModel):
    type: str = Field(default="agent_task")
    source: str
    task_id: str
    priority: str = "normal"
    title: str
    instruction: str
    goal: str
    metadata: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "app": "mock-openclaw"}


@app.post("/openclaw/webhook")
def receive_task(payload: OpenClawPayload) -> dict[str, Any]:
    print("\n=== Mock OpenClaw received task ===")
    print(payload.model_dump_json(indent=2))
    print("==================================\n")
    return {
        "ok": True,
        "received_by": "mock-openclaw",
        "task_id": payload.task_id,
        "status": "accepted",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "message": "OpenClaw mock 已收到任務。正式串接時，把 OPENCLAW_WEBHOOK_URL 改成你的 OpenClaw endpoint。",
    }
