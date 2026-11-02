import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

def test_e2e_self_healing_division_by_zero():
    """
    End-to-End Test:
    Task with forced fault 'division_by_zero'.
    The self-healing framework must:
    1. Detect ZeroDivisionError
    2. Diagnose parameter failure
    3. Retrieve relevant memory (past division by zero experience)
    4. Reject blind retry because memory indicates retry previously failed
    5. Choose CHANGE_ARGUMENTS
    6. Validate corrected parameter
    7. Successfully execute corrected step
    8. Verify confidence
    9. Finish task with status 'RECOVERED'
    """
    create_payload = {
        "title": "ROI Calculation with Fault",
        "description": "Calculate quarterly return on investment with arithmetic divisor.",
        "force_fault": "division_by_zero"
    }
    create_res = client.post("/api/tasks", json=create_payload)
    assert create_res.status_code == 200
    task_id = create_res.json()["id"]

    # Execute
    exec_res = client.post(f"/api/tasks/{task_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()

    assert data["status"] == "RECOVERED"
    assert data["recovery_attempts_count"] >= 1
    assert len(data["recovery_attempts"]) >= 1

    first_recovery = data["recovery_attempts"][0]
    assert first_recovery["selected_strategy"] == "CHANGE_ARGUMENTS"
    assert first_recovery["is_validated"] is True
    assert "division by zero" in first_recovery["error_detected"].lower()

def test_e2e_self_healing_dynamic_replan():
    """
    End-to-End Test:
    Task with forced fault 'service_unavailable'.
    The self-healing framework must:
    1. Detect HTTP 503 / connection failure
    2. Trigger REPLAN strategy
    3. Dynamically insert replacement step
    4. Recover task to completion
    """
    create_payload = {
        "title": "Legacy Gateway Query",
        "description": "Fetch status from remote service gateway.",
        "force_fault": "service_unavailable"
    }
    create_res = client.post("/api/tasks", json=create_payload)
    assert create_res.status_code == 200
    task_id = create_res.json()["id"]

    exec_res = client.post(f"/api/tasks/{task_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()

    assert data["status"] == "RECOVERED"
    assert data["replan_count"] >= 1
    # Check that replacement step exists
    assert any(s.get("is_replacement") is True for s in data["steps"])
