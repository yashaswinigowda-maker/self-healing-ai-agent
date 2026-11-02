import pytest
from app.core.confidence_verifier import confidence_verifier

def test_heuristic_confidence_calculation():
    # Valid structured output
    valid_output = {"data": "verified", "count": 10}
    score, passed, failed = confidence_verifier.calculate_heuristic_score(valid_output, expected_format="JSON")
    assert score >= 0.80
    assert len(passed) >= 3
    assert len(failed) == 0

    # Malformed / error payload output
    bad_output = {"error": "Invalid operation", "data": None}
    bad_score, b_passed, b_failed = confidence_verifier.calculate_heuristic_score(bad_output, expected_format="JSON")
    assert bad_score < 0.60
    assert any("error signature" in f.lower() for f in b_failed)

def test_calibrated_probability_calculation():
    prob = confidence_verifier.calculate_calibrated_probability("calculator")
    assert 0.0 <= prob <= 1.0

@pytest.mark.asyncio
async def test_verify_step_output_rejects_below_threshold():
    # Empty output should be rejected
    res = await confidence_verifier.verify_step_output(
        task_description="Compute metrics",
        step_name="Empty Step",
        tool_name="calculator",
        output=None,
        expected_format="numeric",
        is_critical=True
    )
    assert res["is_verified"] is False
    assert res["confidence_level"] == "LOW"
    assert res["score"] < res["threshold"]
