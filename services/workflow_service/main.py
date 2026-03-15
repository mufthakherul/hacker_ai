from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="CosmicSec Workflow Service", version="1.0.0")

workflows: Dict[str, Dict[str, Any]] = {}


class WorkflowCreate(BaseModel):
    name: str
    triggers: List[str] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "workflow", "timestamp": datetime.utcnow().isoformat()}


@app.post("/workflows", status_code=201)
def create_workflow(payload: WorkflowCreate) -> dict:
    workflow_id = f"wf-{len(workflows)+1:05d}"
    item = {**payload.model_dump(), "workflow_id": workflow_id, "status": "active", "created_at": datetime.utcnow().isoformat()}
    workflows[workflow_id] = item
    return item


@app.get("/workflows")
def list_workflows() -> dict:
    return {"items": list(workflows.values()), "total": len(workflows)}


@app.post("/workflows/{workflow_id}/run")
def run_workflow(workflow_id: str, context: Dict[str, Any]) -> dict:
    workflow = workflows.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "executed_steps": len(workflow.get("steps", [])),
        "context": context,
        "completed_at": datetime.utcnow().isoformat(),
    }
