import pytest
from app.core.memory_manager import memory_manager

def test_similarity_calculation():
    current_task = "Calculate monthly profit margin"
    current_tool = "calculator"
    current_category = "PARAMETER_ERROR"
    current_error = "Division by zero in mathematical expression."

    sample_memory = {
        "task_description": "Calculate quarterly profit and ROI",
        "tool_name": "calculator",
        "error_category": "PARAMETER_ERROR",
        "error_message": "Division by zero in mathematical expression."
    }

    score = memory_manager.calculate_similarity(
        current_task=current_task,
        current_tool=current_tool,
        current_category=current_category,
        current_error=current_error,
        memory_item=sample_memory
    )
    # High similarity expected (> 0.70)
    assert score >= 0.70

def test_retrieve_relevant_memories_separates_success_and_failure():
    result = memory_manager.retrieve_relevant_memories(
        task_description="Calculate profit margin",
        tool_name="calculator",
        error_category="PARAMETER_ERROR",
        error_message="Division by zero in mathematical expression."
    )
    assert "successful_experiences" in result
    assert "failed_experiences" in result
    assert "strategies_to_avoid" in result
    # RETRY should be in strategies to avoid for division by zero based on memory seed
    assert "RETRY" in result["strategies_to_avoid"]

def test_record_new_experience():
    rec = memory_manager.record_experience(
        task_description="Test recording unit task",
        tool_name="web_search_mock",
        error_category="TRANSIENT_NETWORK",
        error_message="Connection timed out",
        diagnosis="Gateway latency",
        recovery_strategy="RETRY",
        recovery_action={"retry_delay_seconds": 1},
        outcome="SUCCESS",
        confidence_score=0.91
    )
    assert rec["outcome"] == "SUCCESS"
    assert rec["recovery_strategy"] == "RETRY"
    assert rec["confidence_score"] == 0.91
