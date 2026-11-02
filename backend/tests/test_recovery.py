import pytest
from app.core.recovery_validator import recovery_validator
from app.core.recovery_planner import recovery_planner

def test_recovery_validator_enforces_max_attempts():
    is_valid, strategy, reason = recovery_validator.validate_recovery_action(
        strategy="RETRY",
        proposed_action={},
        tool_name="calculator",
        attempt_number=4, # Exceeds default limit of 3
        current_replan_count=0,
        strategies_to_avoid=[]
    )
    assert is_valid is False
    assert strategy == "STOP"
    assert "limit" in reason.lower()

def test_recovery_validator_avoids_repeated_failed_strategies():
    # If RETRY is in strategies to avoid, validator should change it
    is_valid, strategy, reason = recovery_validator.validate_recovery_action(
        strategy="RETRY",
        proposed_action={},
        tool_name="calculator",
        attempt_number=1,
        current_replan_count=0,
        strategies_to_avoid=["RETRY"]
    )
    assert strategy == "CHANGE_ARGUMENTS"
    assert "indicates retry previously failed" in reason.lower()

def test_recovery_validator_detects_unsafe_path_traversal():
    is_valid, strategy, reason = recovery_validator.validate_recovery_action(
        strategy="CHANGE_ARGUMENTS",
        proposed_action={"corrected_arguments": {"filename": "../../etc/passwd"}},
        tool_name="file_sandbox_reader",
        attempt_number=1,
        current_replan_count=0,
        strategies_to_avoid=[]
    )
    assert is_valid is False
    assert strategy == "STOP"
    assert "path traversal" in reason.lower()

@pytest.mark.asyncio
async def test_recovery_planner_selects_and_validates():
    plan = await recovery_planner.plan_recovery(
        task_description="Calculate profit ratio",
        step_name="Division Step",
        tool_name="calculator",
        tool_arguments={"expression": "100 / 0"},
        error_message="Division by zero in mathematical expression.",
        error_category="PARAMETER_ERROR",
        attempt_number=1,
        current_replan_count=0
    )
    assert plan["is_validated"] is True
    assert plan["selected_strategy"] == "CHANGE_ARGUMENTS"
    assert "corrected_arguments" in plan["proposed_action"]
