from typing import Dict, Any, List, Tuple
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RecoveryValidator:
    """Validates proposed recovery strategies to prevent infinite loops, repeat failures, and safety violations."""

    def validate_recovery_action(
        self,
        strategy: str,
        proposed_action: Dict[str, Any],
        tool_name: str,
        attempt_number: int,
        current_replan_count: int,
        strategies_to_avoid: List[str]
    ) -> Tuple[bool, str, str]:
        """
        Validates recovery action.
        Returns: (is_valid, validated_strategy, reason)
        """
        # 1. Check max recovery attempts limit
        if attempt_number > settings.MAX_RECOVERY_ATTEMPTS:
            return False, "STOP", f"Max recovery attempts limit ({settings.MAX_RECOVERY_ATTEMPTS}) reached for this step."

        # 2. Check strategy validity
        allowed_strategies = {"RETRY", "CHANGE_ARGUMENTS", "REPLAN", "STOP"}
        if strategy not in allowed_strategies:
            return False, "STOP", f"Unknown recovery strategy: '{strategy}'."

        # 3. Check replan bounds
        if strategy == "REPLAN" and current_replan_count >= settings.MAX_REPLAN_ATTEMPTS:
            return False, "STOP", f"Max task replans ({settings.MAX_REPLAN_ATTEMPTS}) exceeded. Stopping to prevent infinite replan loop."

        # 4. Check memory: avoid repeating previously failed strategies
        if strategy in strategies_to_avoid and strategy != "STOP":
            # Switch to an alternate strategy if possible
            if strategy == "RETRY":
                return True, "CHANGE_ARGUMENTS", f"Memory indicates RETRY previously failed for this error pattern. Overriding strategy to CHANGE_ARGUMENTS."
            elif strategy == "CHANGE_ARGUMENTS":
                return True, "REPLAN", f"Memory indicates CHANGE_ARGUMENTS previously failed. Overriding strategy to REPLAN."

        # 5. Parameter safety for CHANGE_ARGUMENTS
        if strategy == "CHANGE_ARGUMENTS":
            corrected = proposed_action.get("corrected_arguments", {})
            for key, val in corrected.items():
                val_str = str(val).lower()
                # Disallow path traversal
                if ".." in val_str or "/etc" in val_str or "c:\\windows" in val_str:
                    return False, "STOP", f"Security violation: path traversal detected in argument '{key}'."
                # Disallow shell injection keywords
                for bad in ["rmdir", "del /", "powershell", "cmd.exe", "bash -c"]:
                    if bad in val_str:
                        return False, "STOP", f"Security violation: prohibited command injection in argument '{key}'."

        return True, strategy, "Recovery decision passed all security and loop-prevention checks."

recovery_validator = RecoveryValidator()
