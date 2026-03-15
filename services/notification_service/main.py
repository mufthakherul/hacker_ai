from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="CosmicSec Notification Service", version="1.0.0")

events: List[Dict[str, Any]] = []


class NotificationPayload(BaseModel):
    channel: str = Field(..., description="slack|teams|discord|email|sms|pagerduty|webhook")
    target: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "notification", "timestamp": datetime.utcnow().isoformat()}


@app.post("/send")
def send(payload: NotificationPayload) -> dict:
    event = {
        "id": f"notif-{len(events)+1:05d}",
        **payload.model_dump(),
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
    }
    events.append(event)
    return event


@app.get("/events")
def list_events(limit: int = 50) -> dict:
    return {"items": events[-limit:], "total": len(events)}
