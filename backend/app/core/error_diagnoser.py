from typing import Dict, Any, List
from app.gemini.client import gemini_service
import logging

logger = logging.getLogger(__name__)

class ErrorDiagnoser:
    """Diagnoses root cause of execution errors using Gemini and historical context."""

    async def diagnose(
        self,
        task_description: str,
        step_name: str,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        error_message: str,
        relevant_memories: List[Dict[str, Any]],
        attempt_number: int
    ) -> Dict[str, Any]:
        logger.info(f"Diagnosing error for step '{step_name}', attempt #{attempt_number}...")
        
        diagnosis_result = await gemini_service.diagnose_and_select_recovery(
            task_description=task_description,
            step_name=step_name,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            error_message=error_message,
            relevant_memories=relevant_memories,
            attempt_number=attempt_number
        )

        return diagnosis_result

error_diagnoser = ErrorDiagnoser()
