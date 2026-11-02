import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "app_name" in data

def test_settings_endpoints():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "gemini_model" in data
    assert "allowed_tools" in data

    update_res = client.post("/api/settings", json={"confidence_threshold": 0.70})
    assert update_res.status_code == 200
    assert update_res.json()["confidence_threshold"] == 0.70

def test_memories_endpoint():
    res = client.get("/api/memories")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_dashboard_stats_endpoint():
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_tasks" in data
    assert "recovery_success_rate" in data
    assert "risk_distribution" in data

def test_task_creation_and_execution():
    # 1. Create task
    create_payload = {
        "title": "Calculate Corporate Financials",
        "description": "Calculate total annual expenditure and format metrics."
    }
    create_res = client.post("/api/tasks", json=create_payload)
    assert create_res.status_code == 200
    task_data = create_res.json()
    task_id = task_data["id"]
    assert task_data["total_steps"] > 0
    assert len(task_data["predictions"]) > 0

    # 2. Execute task
    exec_res = client.post(f"/api/tasks/{task_id}/execute")
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] in ("COMPLETED", "RECOVERED")
    assert exec_data["final_confidence"] > 0.60
    assert len(exec_data["verifications"]) > 0
