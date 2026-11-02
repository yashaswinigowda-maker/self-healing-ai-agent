import pytest
from app.core.failure_detector import failure_detector

def test_detect_parameter_error():
    try:
        1 / 0
    except ZeroDivisionError as e:
        info = failure_detector.detect_failure(
            step_name="Math Step",
            tool_name="calculator",
            tool_args={"expression": "1 / 0"},
            exception=e
        )
        assert info["has_failed"] is True
        assert info["error_category"] == "PARAMETER_ERROR"
        assert "ZeroDivisionError" in info["error_type"]

def test_detect_transient_network_error():
    exc = TimeoutError("HTTP Connection Timeout after 15000ms")
    info = failure_detector.detect_failure(
        step_name="Fetch Data",
        tool_name="http_client_mock",
        tool_args={"endpoint": "weather"},
        exception=exc
    )
    assert info["error_category"] == "TRANSIENT_NETWORK"

def test_detect_resource_unavailable():
    exc = FileNotFoundError("File 'missing.txt' does not exist in sandbox.")
    info = failure_detector.detect_failure(
        step_name="Read File",
        tool_name="file_sandbox_reader",
        tool_args={"filename": "missing.txt"},
        exception=exc
    )
    assert info["error_category"] == "RESOURCE_UNAVAILABLE"

def test_detect_safety_violation():
    exc = PermissionError("Path traversal outside sandbox is forbidden.")
    info = failure_detector.detect_failure(
        step_name="Read File",
        tool_name="file_sandbox_reader",
        tool_args={"filename": "../secret.env"},
        exception=exc
    )
    assert info["error_category"] == "SAFETY_VIOLATION"
    assert info["is_critical"] is True
