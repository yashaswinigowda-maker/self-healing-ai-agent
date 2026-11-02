from typing import List, Dict, Any, Tuple
from app.config import settings
from app.gemini.client import gemini_service
import logging

logger = logging.getLogger(__name__)

class DynamicReplanner:
    """Feature 3: Dynamic Task Re-planning with state and result preservation."""

    async def replan_failed_step(
        self,
        task_description: str,
        all_steps: List[Dict[str, Any]],
        failed_step_index: int,
        execution_context: Dict[str, Any],
        current_replan_count: int
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Dynamically replaces a failed step while keeping already completed steps intact.
        Returns: (new_steps_list, success_flag, message)
        """
        if current_replan_count >= settings.MAX_REPLAN_ATTEMPTS:
            return all_steps, False, f"Replan aborted: Maximum replan limit ({settings.MAX_REPLAN_ATTEMPTS}) reached."

        # Separate completed, failed, and remaining steps
        completed_steps = [s for s in all_steps if s.get("status") == "COMPLETED" or s.get("status") == "RECOVERED"]
        failed_step = all_steps[failed_step_index]
        remaining_steps = all_steps[failed_step_index + 1 :]

        completed_info = [
            {
                "step_name": s["step_name"],
                "tool_name": s["tool_name"],
                "output_preview": str(s.get("output"))[:120]
            }
            for s in completed_steps
        ]
        failed_info = {
            "step_name": failed_step["step_name"],
            "tool_name": failed_step["tool_name"],
            "arguments": failed_step.get("tool_arguments", {}),
            "error": failed_step.get("error_message")
        }
        remaining_info = [
            {"step_name": s["step_name"], "tool_name": s["tool_name"]}
            for s in remaining_steps
        ]

        logger.info(f"Triggering dynamic replanning for step '{failed_step['step_name']}' (replan #{current_replan_count + 1})...")

        replacement_steps = await gemini_service.generate_dynamic_replan(
            task_description=task_description,
            completed_steps_info=completed_info,
            failed_step_info=failed_info,
            remaining_steps_info=remaining_info,
            allowed_tools=settings.ALLOWED_TOOLS
        )

        # Rebuild new sequence of steps
        new_plan = []
        # Keep completed steps unchanged
        for s in completed_steps:
            new_plan.append(s)

        # Insert replacement steps
        idx = len(new_plan)
        for r in replacement_steps:
            new_step = {
                "id": None, # Will be assigned when created
                "step_index": idx,
                "step_name": r.get("step_name", f"Replacement Step {idx}"),
                "tool_name": r.get("tool_name", "data_transformer"),
                "tool_arguments": r.get("tool_arguments", {}),
                "dependencies": [f"step_{idx - 1}"] if idx > 0 else [],
                "status": "PENDING",
                "output": None,
                "error_message": None,
                "is_critical": r.get("is_critical", False),
                "confidence_score": 0.0,
                "heuristic_confidence": 0.0,
                "calibrated_probability": 0.0,
                "is_replacement": True,
                "replaces_step_id": failed_step.get("id")
            }
            new_plan.append(new_step)
            idx += 1

        # Re-attach remaining steps with updated indices and dependencies
        for r_step in remaining_steps:
            updated_rem = dict(r_step)
            updated_rem["step_index"] = idx
            updated_rem["dependencies"] = [f"step_{idx - 1}"]
            new_plan.append(updated_rem)
            idx += 1

        return new_plan, True, f"Dynamic replanning successful: inserted {len(replacement_steps)} replacement step(s)."

dynamic_replanner = DynamicReplanner()
