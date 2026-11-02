from typing import Dict, Any, List
from app.core.error_diagnoser import error_diagnoser
from app.core.recovery_validator import recovery_validator
from app.core.memory_manager import memory_manager
import logging

logger = logging.getLogger(__name__)

class RecoveryPlanner:
    """Feature 1: Intelligent Recovery Strategy Selection orchestrator."""

    async def plan_recovery(
        self,
        task_description: str,
        step_name: str,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        error_message: str,
        error_category: str,
        attempt_number: int,
        current_replan_count: int
    ) -> Dict[str, Any]:
        # 1. Retrieve relevant memories (Feature 2)
        memory_result = memory_manager.retrieve_relevant_memories(
            task_description=task_description,
            tool_name=tool_name,
            error_category=error_category,
            error_message=error_message
        )
        relevant_memories = memory_result.get("all_relevant", [])
        strategies_to_avoid = memory_result.get("strategies_to_avoid", [])

        # 2. Diagnose error using Gemini with memory context injected (Feature 1 & 2)
        diagnosis_result = await error_diagnoser.diagnose(
            task_description=task_description,
            step_name=step_name,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            error_message=error_message,
            relevant_memories=relevant_memories,
            attempt_number=attempt_number
        )

        initial_strategy = diagnosis_result.get("selected_strategy", "RETRY")
        proposed_action = diagnosis_result.get("proposed_action", {})
        diagnosis_text = diagnosis_result.get("diagnosis", "Unknown error condition.")
        detected_category = diagnosis_result.get("error_category", error_category)

        # 3. Validate recovery decision before execution (Feature 1)
        is_valid, validated_strategy, validation_reason = recovery_validator.validate_recovery_action(
            strategy=initial_strategy,
            proposed_action=proposed_action,
            tool_name=tool_name,
            attempt_number=attempt_number,
            current_replan_count=current_replan_count,
            strategies_to_avoid=strategies_to_avoid
        )

        return {
            "selected_strategy": validated_strategy,
            "original_strategy": initial_strategy,
            "diagnosis": diagnosis_text,
            "error_category": detected_category,
            "proposed_action": proposed_action,
            "is_validated": is_valid,
            "validation_reason": validation_reason,
            "relevant_memories_count": len(relevant_memories),
            "avoided_strategies": strategies_to_avoid,
            "memory_context": relevant_memories
        }

recovery_planner = RecoveryPlanner()
