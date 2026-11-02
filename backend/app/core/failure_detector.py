import traceback
from typing import Dict, Any, Optional

class FailureDetector:
    """Detects, inspects, and categorizes task and step execution failures."""

    def categorize_exception(self, exception: Exception) -> str:
        exc_type = type(exception).__name__
        exc_msg = str(exception).lower()

        if isinstance(exception, ZeroDivisionError) or "division by zero" in exc_msg:
            return "PARAMETER_ERROR"
        elif isinstance(exception, (ValueError, TypeError, KeyError)):
            return "PARAMETER_ERROR"
        elif isinstance(exception, (TimeoutError, ConnectionError)) or "timeout" in exc_msg or "503" in exc_msg:
            return "TRANSIENT_NETWORK"
        elif isinstance(exception, FileNotFoundError) or "not found" in exc_msg or "404" in exc_msg:
            return "RESOURCE_UNAVAILABLE"
        elif isinstance(exception, PermissionError) or "forbidden" in exc_msg or "traversal" in exc_msg:
            return "SAFETY_VIOLATION"
        elif "verification" in exc_msg or "confidence" in exc_msg:
            return "VERIFICATION_FAILURE"
        else:
            return "TOOL_EXECUTION_FAILURE"

    def detect_failure(self, step_name: str, tool_name: str, tool_args: Dict[str, Any], exception: Exception) -> Dict[str, Any]:
        category = self.categorize_exception(exception)
        tb_str = traceback.format_exc()
        return {
            "has_failed": True,
            "step_name": step_name,
            "tool_name": tool_name,
            "arguments": tool_args,
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "error_category": category,
            "traceback": tb_str,
            "is_critical": category == "SAFETY_VIOLATION"
        }

failure_detector = FailureDetector()
