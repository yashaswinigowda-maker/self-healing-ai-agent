import math
from typing import List, Dict, Any, Tuple
from app.core.memory_manager import memory_manager
from sqlalchemy.orm import Session
from app.models.db_models import FailurePredictionRecord
import logging

logger = logging.getLogger(__name__)

class FailurePredictor:
    """Feature 5: Transparent and testable Failure Pattern Prediction engine."""

    def analyze_tool_historical_risk(self, tool_name: str) -> Tuple[float, int, int]:
        """
        Calculates empirical failure rate for a tool based on episodic memory:
        returns: (failure_rate, total_attempts, total_failures)
        """
        memories = memory_manager.get_all_memories()
        tool_records = [m for m in memories if m.get("tool_name") == tool_name]

        if not tool_records:
            return 0.15, 0, 0 # Baseline unobserved risk

        total = len(tool_records)
        failures = sum(1 for m in tool_records if m.get("outcome") == "FAILURE")
        # Empirical failure rate
        rate = failures / total if total > 0 else 0.0
        return round(rate, 3), total, failures

    def detect_vulnerable_parameters(self, tool_name: str, args: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Scans parameters for known vulnerable patterns."""
        risk_penalty = 0.0
        vulnerabilities = []

        if tool_name == "calculator":
            expr = str(args.get("expression", ""))
            if "/ 0" in expr or "/0" in expr:
                risk_penalty += 0.55
                vulnerabilities.append("Arithmetic expression contains explicit division by zero pattern.")
            elif not expr.strip():
                risk_penalty += 0.40
                vulnerabilities.append("Empty arithmetic expression.")

        elif tool_name == "http_client_mock":
            endpoint = str(args.get("endpoint", "")).lower()
            if "fail" in endpoint or "error" in endpoint:
                risk_penalty += 0.60
                vulnerabilities.append("Target endpoint path explicitly references simulated fault.")
            elif "timeout" in endpoint:
                risk_penalty += 0.45
                vulnerabilities.append("Target endpoint path references latent timeout condition.")

        elif tool_name in ("file_sandbox_reader", "file_sandbox_writer"):
            filename = str(args.get("filename", ""))
            if ".." in filename:
                risk_penalty += 0.70
                vulnerabilities.append("Path traversal attempt detected in filename parameter.")

        return risk_penalty, vulnerabilities

    def predict_task_risk(self, task_description: str, planned_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Transparent mathematical risk prediction:
        Risk = max_step( 0.50 * ToolFailureRate + ParamPenalty ) + 0.05 * StepCount
        """
        potential_failures = []
        recommendations = []
        max_step_risk = 0.0

        for step in planned_steps:
            tool = step.get("tool_name", "")
            args = step.get("tool_arguments", {})
            step_name = step.get("step_name", tool)

            tool_fail_rate, total_hist, fails_hist = self.analyze_tool_historical_risk(tool)
            param_penalty, param_vulns = self.detect_vulnerable_parameters(tool, args)

            step_risk = (0.50 * tool_fail_rate) + param_penalty
            if step_risk > max_step_risk:
                max_step_risk = step_risk

            if tool_fail_rate > 0.25:
                potential_failures.append(
                    f"Step '{step_name}' uses '{tool}' with historical failure rate of {tool_fail_rate:.1%} ({fails_hist}/{total_hist} runs)."
                )
                recommendations.append(
                    f"Enable automatic retry backoff and intermediate checkpointing for '{step_name}'."
                )

            for v in param_vulns:
                potential_failures.append(f"Vulnerability in '{step_name}': {v}")
                recommendations.append(f"Pre-validate arguments for '{step_name}' before dispatching tool.")

        # Complexity penalty: 0.05 per step over 2 steps, capped at 0.20
        complexity_penalty = min(0.20, max(0.0, (len(planned_steps) - 2) * 0.05))
        total_risk_score = round(min(1.0, max_step_risk + complexity_penalty), 3)

        # Baseline minimum risk for any real task
        if total_risk_score < 0.10:
            total_risk_score = 0.12

        # Risk level categorization
        if total_risk_score >= 0.70:
            risk_level = "HIGH"
        elif total_risk_score >= 0.35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if not recommendations:
            recommendations.append("Standard execution pipeline approved. Monitor output confidence.")

        formula = (
            "RiskScore = clamp(max_step(0.50 * HistoricalFailureRate + ParameterVulnerability) "
            f"+ ComplexityPenalty, 0.0, 1.0) => max_step={max_step_risk:.2f}, complexity={complexity_penalty:.2f}"
        )

        return {
            "predicted_risk_score": total_risk_score,
            "predicted_risk_level": risk_level,
            "potential_failure_modes": potential_failures,
            "preventive_recommendations": recommendations,
            "mathematical_formula": formula,
            "evaluated_steps_count": len(planned_steps)
        }

    def evaluate_prediction_accuracy(
        self,
        predicted_risk_level: str,
        predicted_risk_score: float,
        actual_outcome: str,
        recovered: bool
    ) -> bool:
        """
        Compares predicted risk with ground-truth execution outcome:
        - HIGH/MEDIUM risk is accurate if task had a failure or needed recovery.
        - LOW risk is accurate if task completed directly without failure.
        """
        experienced_fault = actual_outcome == "FAILED" or recovered
        if predicted_risk_level in ("HIGH", "MEDIUM"):
            return experienced_fault
        else:
            return not experienced_fault

failure_predictor = FailurePredictor()
