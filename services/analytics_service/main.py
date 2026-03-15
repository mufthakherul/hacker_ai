from datetime import datetime
from statistics import mean
from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="CosmicSec Analytics Service", version="1.0.0")

metrics_store: List[Dict[str, Any]] = []


class MetricPoint(BaseModel):
    metric: str
    value: float
    dimensions: Dict[str, str] = Field(default_factory=dict)


class PredictionRequest(BaseModel):
    metric: str
    history: List[float] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "analytics", "timestamp": datetime.utcnow().isoformat()}


@app.post("/metrics/ingest")
def ingest(payload: MetricPoint) -> dict:
    item = {**payload.model_dump(), "ts": datetime.utcnow().isoformat()}
    metrics_store.append(item)
    return item


@app.get("/dashboard/summary")
def dashboard_summary() -> dict:
    if not metrics_store:
        return {"total_metrics": 0, "services_observed": 0, "timestamp": datetime.utcnow().isoformat()}
    services = {m.get("dimensions", {}).get("service", "unknown") for m in metrics_store}
    return {
        "total_metrics": len(metrics_store),
        "services_observed": len(services),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/predictions/forecast")
def forecast(payload: PredictionRequest) -> dict:
    series = payload.history or [0.0]
    baseline = mean(series)
    trend = (series[-1] - series[0]) / max(len(series), 1)
    next_value = round(baseline + trend, 3)
    return {"metric": payload.metric, "forecast_next": next_value, "confidence": 0.74}
