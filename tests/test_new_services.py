from fastapi.testclient import TestClient

from services.notification_service.main import app as notification_app
from services.analytics_service.main import app as analytics_app
from services.workflow_service.main import app as workflow_app
from services.exploit_service.main import app as exploit_app
from services.phishing_service.main import app as phishing_app


def test_notification_service() -> None:
    client = TestClient(notification_app)
    assert client.get("/health").status_code == 200
    sent = client.post("/send", json={"channel": "email", "target": "sec@example.com", "message": "test"})
    assert sent.status_code == 200
    assert client.get("/events").json()["total"] >= 1


def test_analytics_service() -> None:
    client = TestClient(analytics_app)
    assert client.get("/health").status_code == 200
    ingest = client.post("/metrics/ingest", json={"metric": "scan_duration", "value": 32.5, "dimensions": {"service": "scan"}})
    assert ingest.status_code == 200
    summary = client.get("/dashboard/summary")
    assert summary.status_code == 200
    forecast = client.post("/predictions/forecast", json={"metric": "scan_duration", "history": [10, 20, 30]})
    assert forecast.status_code == 200


def test_workflow_service() -> None:
    client = TestClient(workflow_app)
    created = client.post("/workflows", json={"name": "auto-remediation", "triggers": ["finding.created"], "steps": [{"name": "notify"}]})
    assert created.status_code == 201
    workflow_id = created.json()["workflow_id"]
    run = client.post(f"/workflows/{workflow_id}/run", json={"finding_id": "f-1"})
    assert run.status_code == 200


def test_exploit_service() -> None:
    client = TestClient(exploit_app)
    guidance = client.post("/guidance", json={"cve_id": "CVE-2021-44228", "target_stack": "java"})
    assert guidance.status_code == 200
    assert guidance.json()["safety_mode"] == "defensive-only"


def test_phishing_service() -> None:
    client = TestClient(phishing_app)
    created = client.post("/campaigns", json={"name": "Q1 Simulation", "target_group": "engineering", "template": "awareness-template"})
    assert created.status_code == 201
    listed = client.get("/campaigns")
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1
