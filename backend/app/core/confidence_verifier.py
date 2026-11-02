from typing import Dict, Any, List, Tuple
from app.config import settings
from app.core.memory_manager import memory_manager
from app.gemini.client import gemini_service
import logging

logger = logging.getLogger(__name__)

class ConfidenceVerifier:
    """Feature 4: Confidence-Based Verification engine with heuristic vs calibrated distinction."""

    def calculate_calibrated_probability(self, tool_name: str, error_category: str = None) -> float:
        """
        Calculates empirical calibrated success probability based on historical episodic memory.
        Uses Laplace smoothing: (successes + 1) / (total_records + 2).
        """
        memories = memory_manager.get_all_memories()
        tool_memories = [m for m in memories if m.get("tool_name") == tool_name]

        if not tool_memories:
            return 0.80 # Default uninformative prior

        successes = sum(1 for m in tool_memories if m.get("outcome") == "SUCCESS")
        total = len(tool_memories)

        calibrated = (successes + 1) / (total + 2)
        return round(calibrated, 3)

    def calculate_heuristic_score(self, output: Any, expected_format: str = "") -> Tuple[float, List[str], List[str]]:
        """
        Deterministic, rule-based heuristic scoring based on structural and schema integrity.
        Returns: (heuristic_score, passed_checks, failed_checks)
        """
        passed = []
        failed = []
        score = 0.0

        # Check 1: Non-null and non-empty
        if output is not None and output != "" and output != {} and output != []:
            passed.append("Non-null and non-empty output verified (+0.30)")
            score += 0.30
        else:
            failed.append("Output payload is empty or null (-0.30)")

        # Check 2: No error signature in payload
        if isinstance(output, dict) and any(k in output for k in ["error", "exception", "failed"]):
            failed.append("Output dictionary contains error signature (-0.35)")
            score = max(0.0, score - 0.35)
        elif isinstance(output, str) and ("error:" in output.lower() or "exception:" in output.lower()):
            failed.append("Output text contains error signature (-0.35)")
            score = max(0.0, score - 0.35)
        else:
            passed.append("No error or exception indicators detected (+0.25)")
            score += 0.25

        # Check 3: Structured schema integrity
        if isinstance(output, (dict, list)):
            passed.append("Output adheres to structured JSON format (+0.25)")
            score += 0.25
        elif isinstance(output, (int, float, bool)):
            passed.append("Output adheres to scalar primitive format (+0.25)")
            score += 0.25
        elif isinstance(output, str) and len(output.strip()) > 3:
            passed.append("Output contains meaningful textual length (+0.25)")
            score += 0.25
        else:
            failed.append("Output lacks structured format or minimum length (-0.25)")

        # Check 4: Expected format heuristic check
        if expected_format:
            fmt_lower = expected_format.lower()
            if "json" in fmt_lower and isinstance(output, (dict, list)):
                passed.append("Matched expected JSON format constraint (+0.20)")
                score += 0.20
            elif "numeric" in fmt_lower or "number" in fmt_lower:
                if isinstance(output, (int, float)) or (isinstance(output, dict) and "result" in output):
                    passed.append("Matched expected numeric calculation format (+0.20)")
                    score += 0.20
                else:
                    failed.append("Did not match expected numeric format (-0.20)")
            else:
                passed.append("General semantic format check satisfied (+0.20)")
                score += 0.20
        else:
            passed.append("General format checks satisfied (+0.20)")
            score += 0.20

        return round(min(score, 1.0), 3), passed, failed

    async def verify_step_output(
        self,
        task_description: str,
        step_name: str,
        tool_name: str,
        output: Any,
        expected_format: str = "",
        is_critical: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates confidence score, classifies into High/Medium/Low,
        and enforces rejection below configured threshold.
        """
        # 1. Deterministic heuristic score
        heuristic_score, passed_checks, failed_checks = self.calculate_heuristic_score(output, expected_format)

        # 2. Historical calibrated probability
        calibrated_prob = self.calculate_calibrated_probability(tool_name)

        # 3. Blended confidence score (60% deterministic heuristic + 40% empirical calibrated)
        combined_score = round((0.60 * heuristic_score) + (0.40 * calibrated_prob), 3)

        # 4. Classification
        if combined_score >= 0.80:
            level = "HIGH"
        elif combined_score >= 0.50:
            level = "MEDIUM"
        else:
            level = "LOW"

        # 5. Threshold enforcement
        threshold = settings.CONFIDENCE_THRESHOLD
        is_verified = combined_score >= threshold

        critique = (
            f"Verification {'PASSED' if is_verified else 'REJECTED'}. "
            f"Heuristic rule score: {heuristic_score:.2f}, "
            f"Calibrated empirical probability: {calibrated_prob:.2f}. "
            f"Overall score {combined_score:.2f} vs required threshold {threshold:.2f}."
        )

        return {
            "score": combined_score,
            "confidence_level": level,
            "is_verified": is_verified,
            "heuristic_score": heuristic_score,
            "calibrated_probability": calibrated_prob,
            "threshold": threshold,
            "checks_passed": passed_checks,
            "checks_failed": failed_checks,
            "critique": critique
        }

confidence_verifier = ConfidenceVerifier()
