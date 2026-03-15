from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="CosmicSec Phishing Simulation Service", version="1.0.0")

campaigns: List[Dict[str, Any]] = []


class CampaignCreate(BaseModel):
    name: str
    target_group: str
    template: str
    tracking: bool = True
    tags: List[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "phishing", "timestamp": datetime.utcnow().isoformat()}


@app.post("/campaigns", status_code=201)
def create_campaign(payload: CampaignCreate) -> dict:
    campaign = {
        "campaign_id": f"ph-{len(campaigns)+1:05d}",
        **payload.model_dump(),
        "status": "scheduled",
        "created_at": datetime.utcnow().isoformat(),
    }
    campaigns.append(campaign)
    return campaign


@app.get("/campaigns")
def list_campaigns() -> dict:
    return {"items": campaigns, "total": len(campaigns)}
