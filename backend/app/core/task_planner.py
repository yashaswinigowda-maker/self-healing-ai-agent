import uuid
from typing import List, Dict, Any, Optional
from app.config import settings
from app.gemini.client import gemini_service
from app.tools.registry import tool_registry
import logging

logger = logging.getLogger(__name__)

class TaskPlanner:
    """Feature 3 & Workflow: Decomposes tasks, validates tools and dependencies."""

    async def plan_task(self, task_description: str, force_fault: Optional[str] = None) -> List[Dict[str, Any]]:
        logger.info(f"Generating task plan for: '{task_description}'")
        raw_steps = await gemini_service.generate_task_plan(
            task_description=task_description,
            allowed_tools=settings.ALLOWED_TOOLS
        )

        validated_steps = []
        for idx, step in enumerate(raw_steps):
            tool_name = step.get("tool_name", "data_transformer")
            # Enforce tool allowlist
            if tool_name not in settings.ALLOWED_TOOLS:
                logger.warning(f"Tool '{tool_name}' not in allowlist. Falling back to 'data_transformer'.")
                tool_name = "data_transformer"

            step_id = str(uuid.uuid4())
            args = step.get("tool_arguments", {})

            # If user explicitly requested a fault scenario to demonstrate self-healing:
            if force_fault and idx == 0:
                if force_fault == "division_by_zero":
                    tool_name = "calculator"
                    args = {"expression": "1000 / 0"}
                elif force_fault == "network_timeout":
                    tool_name = "http_client_mock"
                    args = {"endpoint": "timeout_gateway"}
                elif force_fault == "service_unavailable":
                    tool_name = "http_client_mock"
                    args = {"endpoint": "failed_service"}
                elif force_fault == "missing_param":
                    tool_name = "http_client_mock"
                    args = {}

            validated_steps.append({
                "id": step_id,
                "step_index": idx,
                "step_name": step.get("step_name", f"Step {idx + 1}"),
                "tool_name": tool_name,
                "tool_arguments": args,
                "dependencies": step.get("dependencies", []),
                "status": "PENDING",
                "output": None,
                "error_message": None,
                "is_critical": step.get("is_critical", False),
                "expected_output_format": step.get("expected_output_format", ""),
                "confidence_score": 0.0,
                "heuristic_confidence": 0.0,
                "calibrated_probability": 0.0,
                "is_replacement": False,
                "replaces_step_id": None
            })

        if not validated_steps:
            # Fallback single step
            validated_steps.append({
                "id": str(uuid.uuid4()),
                "step_index": 0,
                "step_name": "Execute Basic Task",
                "tool_name": "web_search_mock",
                "tool_arguments": {"query": task_description},
                "dependencies": [],
                "status": "PENDING",
                "output": None,
                "error_message": None,
                "is_critical": True,
                "expected_output_format": "Search results",
                "confidence_score": 0.0,
                "heuristic_confidence": 0.0,
                "calibrated_probability": 0.0,
                "is_replacement": False,
                "replaces_step_id": None
            })

        return validated_steps

task_planner = TaskPlanner()
