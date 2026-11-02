import pytest
from app.core.failure_predictor import failure_predictor

def test_predict_task_risk_with_high_risk_parameters():
    steps = [
        {
            "step_name": "Divide by zero step",
            "tool_name": "calculator",
            "tool_arguments": {"expression": "5000 / 0"}
        }
    ]
    pred = failure_predictor.predict_task_risk(
        task_description="Dangerous math calculation",
        planned_steps=steps
    )
    assert pred["predicted_risk_level"] in ("HIGH", "MEDIUM")
    assert pred["predicted_risk_score"] >= 0.50
    assert len(pred["potential_failure_modes"]) > 0
    assert len(pred["preventive_recommendations"]) > 0
    assert "RiskScore" in pred["mathematical_formula"]

def test_predict_task_risk_with_benign_steps():
    steps = [
        {
            "step_name": "Search weather",
            "tool_name": "web_search_mock",
            "tool_arguments": {"query": "weather forecast"}
        }
    ]
    pred = failure_predictor.predict_task_risk(
        task_description="Harmless search query",
        planned_steps=steps
    )
    assert pred["predicted_risk_level"] == "LOW"
    assert pred["predicted_risk_score"] < 0.35

def test_evaluate_prediction_accuracy():
    # Accurate: predicted HIGH risk and task needed recovery
    acc_1 = failure_predictor.evaluate_prediction_accuracy(
        predicted_risk_level="HIGH",
        predicted_risk_score=0.85,
        actual_outcome="RECOVERED",
        recovered=True
    )
    assert acc_1 is True

    # Accurate: predicted LOW risk and task completed without error
    acc_2 = failure_predictor.evaluate_prediction_accuracy(
        predicted_risk_level="LOW",
        predicted_risk_score=0.15,
        actual_outcome="COMPLETED",
        recovered=False
    )
    assert acc_2 is True
