import pytest
from app.core.dynamic_replanner import dynamic_replanner

@pytest.mark.asyncio
async def test_dynamic_replanning_preserves_completed_steps():
    original_steps = [
        {
            "id": "step_1",
            "step_index": 0,
            "step_name": "Fetch Initial Query",
            "tool_name": "web_search_mock",
            "status": "COMPLETED",
            "output": {"results": ["item 1", "item 2"]}
        },
        {
            "id": "step_2",
            "step_index": 1,
            "step_name": "Query Unavailable Service",
            "tool_name": "http_client_mock",
            "status": "FAILED",
            "error_message": "HTTP 503 Service Unavailable"
        },
        {
            "id": "step_3",
            "step_index": 2,
            "step_name": "Write Output",
            "tool_name": "file_sandbox_writer",
            "status": "PENDING"
        }
    ]

    new_plan, success, message = await dynamic_replanner.replan_failed_step(
        task_description="Search and fetch data",
        all_steps=original_steps,
        failed_step_index=1,
        execution_context={"step_0": {"results": ["item 1", "item 2"]}},
        current_replan_count=0
    )

    assert success is True
    # Step 0 must still be COMPLETED
    assert new_plan[0]["status"] == "COMPLETED"
    assert new_plan[0]["step_name"] == "Fetch Initial Query"
    # Replacement step exists
    assert any(s.get("is_replacement") is True for s in new_plan)

@pytest.mark.asyncio
async def test_dynamic_replanning_prevents_unlimited_replanning():
    steps = [{"step_name": "Failing", "tool_name": "calculator", "status": "FAILED"}]
    _, success, msg = await dynamic_replanner.replan_failed_step(
        task_description="Infinite replan task",
        all_steps=steps,
        failed_step_index=0,
        execution_context={},
        current_replan_count=2 # Max replans reached
    )
    assert success is False
    assert "limit" in msg.lower()
