import json
import logging
import re
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self):
        api_key = settings.GEMINI_API_KEY
        if api_key and api_key.strip():
            try:
                self._client = genai.Client(api_key=api_key.strip())
                logger.info(f"Gemini client initialized with model: {settings.GEMINI_MODEL}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")
                self._client = None
        else:
            self._client = None

    def is_configured(self) -> bool:
        return self._client is not None or bool(settings.GEMINI_API_KEY)

    def reload(self):
        self._init_client()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Safely extract JSON object from markdown fenced block or raw string."""
        text = text.strip()
        # Remove markdown code fences if present
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback search for first { and last }
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
            raise

    async def generate_task_plan(self, task_description: str, allowed_tools: List[str]) -> List[Dict[str, Any]]:
        """Divide user task into structured sub-steps with dependencies."""
        prompt = f"""
You are an expert AI Task Planner. Decompose the following multi-step automation task into discrete, verifiable steps.

Task:
"{task_description}"

Allowed Tools:
{json.dumps(allowed_tools)}

Requirements:
1. Divide the task into 2 to 5 logical sequential steps.
2. Each step MUST use one of the Allowed Tools.
3. Identify dependencies: dependency list should refer to previous step indices like "step_0", "step_1".
4. Mark critical steps (is_critical = true) if failure of this step invalidates the entire goal.
5. Provide realistic tool arguments.

Return ONLY a valid JSON array of objects with fields:
[
  {{
    "step_index": 0,
    "step_name": "Short descriptive name",
    "tool_name": "tool_from_allowed_list",
    "tool_arguments": {{ "arg1": "value" }},
    "dependencies": [],
    "is_critical": true,
    "expected_output_format": "description"
  }}
]
"""
        if self._client:
            try:
                response = self._client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    plan = json.loads(response.text)
                    if isinstance(plan, dict) and "steps" in plan:
                        plan = plan["steps"]
                    if isinstance(plan, list):
                        return plan
            except Exception as e:
                logger.error(f"Gemini API error during task planning: {e}. Falling back to internal planner.")

        # Fallback deterministic planner
        return self._fallback_task_plan(task_description, allowed_tools)

    def _fallback_task_plan(self, task_description: str, allowed_tools: List[str]) -> List[Dict[str, Any]]:
        desc_lower = task_description.lower()
        steps = []
        
        if "weather" in desc_lower or "forecast" in desc_lower:
            steps = [
                {
                    "step_index": 0,
                    "step_name": "Fetch Weather Data",
                    "tool_name": "http_client_mock",
                    "tool_arguments": {"endpoint": "weather", "city": "Seattle"},
                    "dependencies": [],
                    "is_critical": True,
                    "expected_output_format": "JSON weather report"
                },
                {
                    "step_index": 1,
                    "step_name": "Summarize Weather Report",
                    "tool_name": "text_summarizer",
                    "tool_arguments": {"text": "Weather in Seattle: 62F, partly cloudy, humidity 65%", "max_length": 60},
                    "dependencies": ["step_0"],
                    "is_critical": False,
                    "expected_output_format": "Clean summary text"
                },
                {
                    "step_index": 2,
                    "step_name": "Save Weather Briefing",
                    "tool_name": "file_sandbox_writer",
                    "tool_arguments": {"filename": "weather_report.txt", "content": "Weather summary: Seattle 62F"},
                    "dependencies": ["step_1"],
                    "is_critical": False,
                    "expected_output_format": "Confirmation file saved"
                }
            ]
        elif "calculate" in desc_lower or "math" in desc_lower or "sum" in desc_lower or "roi" in desc_lower:
            steps = [
                {
                    "step_index": 0,
                    "step_name": "Perform Primary Calculation",
                    "tool_name": "calculator",
                    "tool_arguments": {"expression": "1500 * 1.12 - 350"},
                    "dependencies": [],
                    "is_critical": True,
                    "expected_output_format": "Numeric result"
                },
                {
                    "step_index": 1,
                    "step_name": "Format Financial Metric",
                    "tool_name": "data_transformer",
                    "tool_arguments": {"data": {"raw_value": 1330.0}, "transform_type": "currency_format"},
                    "dependencies": ["step_0"],
                    "is_critical": False,
                    "expected_output_format": "Formatted currency JSON"
                }
            ]
        elif "search" in desc_lower or "research" in desc_lower or "find" in desc_lower:
            steps = [
                {
                    "step_index": 0,
                    "step_name": "Search Information Repository",
                    "tool_name": "web_search_mock",
                    "tool_arguments": {"query": task_description},
                    "dependencies": [],
                    "is_critical": True,
                    "expected_output_format": "Search results array"
                },
                {
                    "step_index": 1,
                    "step_name": "Extract & Summarize Findings",
                    "tool_name": "text_summarizer",
                    "tool_arguments": {"text": f"Findings for {task_description}", "max_length": 100},
                    "dependencies": ["step_0"],
                    "is_critical": True,
                    "expected_output_format": "Executive summary"
                },
                {
                    "step_index": 2,
                    "step_name": "Save Research Artifact",
                    "tool_name": "file_sandbox_writer",
                    "tool_arguments": {"filename": "research_summary.txt", "content": "Research findings verified."},
                    "dependencies": ["step_1"],
                    "is_critical": False,
                    "expected_output_format": "File write status"
                }
            ]
        else:
            # General multi-step workflow
            steps = [
                {
                    "step_index": 0,
                    "step_name": "Gather Source Data",
                    "tool_name": "web_search_mock",
                    "tool_arguments": {"query": task_description},
                    "dependencies": [],
                    "is_critical": True,
                    "expected_output_format": "Source records"
                },
                {
                    "step_index": 1,
                    "step_name": "Validate & Transform Payload",
                    "tool_name": "json_validator",
                    "tool_arguments": {"data": {"task": task_description, "status": "active"}, "schema_type": "generic"},
                    "dependencies": ["step_0"],
                    "is_critical": False,
                    "expected_output_format": "Validation status"
                },
                {
                    "step_index": 2,
                    "step_name": "Persist Final Result",
                    "tool_name": "file_sandbox_writer",
                    "tool_arguments": {"filename": "task_result.txt", "content": f"Completed: {task_description}"},
                    "dependencies": ["step_1"],
                    "is_critical": False,
                    "expected_output_format": "Confirmation"
                }
            ]
        return steps

    async def diagnose_and_select_recovery(
        self,
        task_description: str,
        step_name: str,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        error_message: str,
        relevant_memories: List[Dict[str, Any]],
        attempt_number: int
    ) -> Dict[str, Any]:
        """Diagnose failure root cause and select intelligent recovery strategy."""
        prompt = f"""
You are the AI Self-Healing Diagnostic Engine. An automated step has failed.

Task: "{task_description}"
Failed Step: "{step_name}"
Tool: "{tool_name}"
Arguments: {json.dumps(tool_arguments)}
Error Message: "{error_message}"
Attempt Number: {attempt_number}

Past Memory Context (Experiences from past runs):
{json.dumps(relevant_memories, indent=2)}

Recovery Strategies Available:
1. "RETRY" - For transient or network glitches when trying again is likely to succeed.
2. "CHANGE_ARGUMENTS" - If arguments are malformed, invalid, or out of range. Provide corrected arguments!
3. "REPLAN" - If current tool or plan cannot work and we must substitute alternative steps/tools.
4. "STOP" - If unrecoverable or unsafe to proceed.

Important Guidelines:
- Inspect past memories: DO NOT repeat strategies that failed in similar past situations.
- Favor strategies that succeeded in past memories.
- Return valid JSON only.

Return JSON in this format:
{{
  "error_category": "PARAMETER_ERROR|TRANSIENT_NETWORK|TOOL_EXECUTION_FAILURE|VALIDATION_FAILURE|RESOURCE_UNAVAILABLE",
  "diagnosis": "Detailed root-cause analysis explaining why the step failed",
  "selected_strategy": "RETRY|CHANGE_ARGUMENTS|REPLAN|STOP",
  "proposed_action": {{
      "action_type": "string",
      "corrected_arguments": {{}},
      "replan_notes": "string",
      "retry_delay_seconds": 1
  }},
  "reasoning": "Why this recovery strategy was chosen"
}}
"""
        if self._client:
            try:
                response = self._client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    return self._extract_json(response.text)
            except Exception as e:
                logger.error(f"Gemini API error during error diagnosis: {e}. Falling back to internal diagnoser.")

        # Deterministic fallback diagnoser
        return self._fallback_diagnose_and_select_recovery(
            task_description, step_name, tool_name, tool_arguments, error_message, relevant_memories, attempt_number
        )

    def _fallback_diagnose_and_select_recovery(
        self,
        task_description: str,
        step_name: str,
        tool_name: str,
        tool_arguments: Dict[str, Any],
        error_message: str,
        relevant_memories: List[Dict[str, Any]],
        attempt_number: int
    ) -> Dict[str, Any]:
        err_lower = error_message.lower()
        
        # Check if memory says a previous recovery failed
        forbidden_strategies = set()
        for mem in relevant_memories:
            if mem.get("outcome") == "FAILURE" and mem.get("recovery_strategy"):
                forbidden_strategies.add(mem["recovery_strategy"])

        if "division by zero" in err_lower or "zero division" in err_lower or "invalid expression" in err_lower:
            strategy = "CHANGE_ARGUMENTS"
            corrected = dict(tool_arguments)
            if "expression" in corrected:
                corrected["expression"] = corrected["expression"].replace("/ 0", "/ 1").replace("/0", "/1")
            return {
                "error_category": "PARAMETER_ERROR",
                "diagnosis": "Division by zero detected in arithmetic expression arguments.",
                "selected_strategy": strategy,
                "proposed_action": {
                    "action_type": "sanitize_parameters",
                    "corrected_arguments": corrected,
                    "retry_delay_seconds": 0
                },
                "reasoning": "Fixed mathematical divisor parameter to prevent arithmetic error."
            }
        
        elif "timeout" in err_lower or "connection reset" in err_lower or "transient" in err_lower:
            strategy = "RETRY" if ("RETRY" not in forbidden_strategies or attempt_number < 2) else "REPLAN"
            return {
                "error_category": "TRANSIENT_NETWORK",
                "diagnosis": "Transient network timeout occurred communicating with external resource.",
                "selected_strategy": strategy,
                "proposed_action": {
                    "action_type": "exponential_backoff_retry",
                    "corrected_arguments": tool_arguments,
                    "retry_delay_seconds": 1
                },
                "reasoning": "Transient network glitch. Retrying with small delay."
            }

        elif "missing required parameter" in err_lower or "invalid argument" in err_lower:
            return {
                "error_category": "PARAMETER_ERROR",
                "diagnosis": f"Required parameter missing or malformed for tool {tool_name}.",
                "selected_strategy": "CHANGE_ARGUMENTS",
                "proposed_action": {
                    "action_type": "inject_default_arguments",
                    "corrected_arguments": {**tool_arguments, "endpoint": tool_arguments.get("endpoint", "status")},
                    "retry_delay_seconds": 0
                },
                "reasoning": "Injected valid required parameters based on tool schema."
            }

        elif "not found" in err_lower or "unavailable" in err_lower or "unsupported" in err_lower:
            return {
                "error_category": "RESOURCE_UNAVAILABLE",
                "diagnosis": f"Resource or endpoint was not found for {tool_name}.",
                "selected_strategy": "REPLAN",
                "proposed_action": {
                    "action_type": "substitute_subtasks",
                    "replan_notes": "Substitute with alternative mock data fetcher and synthesizer.",
                    "retry_delay_seconds": 0
                },
                "reasoning": "Primary target resource unavailable; dynamic replan required."
            }

        # Default fallback: if attempt 1, try replan or change arguments
        if attempt_number > 2:
            return {
                "error_category": "TOOL_EXECUTION_FAILURE",
                "diagnosis": "Persistent tool failure after multiple recovery attempts.",
                "selected_strategy": "STOP",
                "proposed_action": {"action_type": "abort"},
                "reasoning": "Max recovery attempts exceeded for this fault."
            }

        return {
            "error_category": "TOOL_EXECUTION_FAILURE",
            "diagnosis": f"Execution error in {tool_name}: {error_message}",
            "selected_strategy": "REPLAN",
            "proposed_action": {
                "action_type": "dynamic_step_replacement",
                "replan_notes": "Generate replacement steps to achieve step objective."
            },
            "reasoning": "Dynamic replanning to bypass the failing execution branch."
        }

    async def generate_dynamic_replan(
        self,
        task_description: str,
        completed_steps_info: List[Dict[str, Any]],
        failed_step_info: Dict[str, Any],
        remaining_steps_info: List[Dict[str, Any]],
        allowed_tools: List[str]
    ) -> List[Dict[str, Any]]:
        """Dynamically generate replacement steps for a failed step while preserving completed work."""
        prompt = f"""
You are the AI Dynamic Re-planning Engine. A step in a multi-step task failed, and you must generate a replacement plan.

User Task: "{task_description}"

ALREADY COMPLETED STEPS (PRESERVED - DO NOT REDO):
{json.dumps(completed_steps_info, indent=2)}

FAILED STEP:
{json.dumps(failed_step_info, indent=2)}

REMAINING PLANNED STEPS:
{json.dumps(remaining_steps_info, indent=2)}

Allowed Tools:
{json.dumps(allowed_tools)}

Instructions:
1. Do NOT re-execute already completed steps.
2. Formulate 1 or 2 replacement steps that replace the failed step using a safe alternative tool.
3. Link the remaining steps seamlessly to the replacement step's output.
4. Return ONLY a valid JSON array of replacement step objects.

Format:
[
  {{
    "step_name": "Alternative data retrieval",
    "tool_name": "tool_from_allowed_list",
    "tool_arguments": {{ "arg": "val" }},
    "dependencies": [],
    "is_critical": false,
    "expected_output_format": "string"
  }}
]
"""
        if self._client:
            try:
                response = self._client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    replacements = json.loads(response.text)
                    if isinstance(replacements, list) and len(replacements) > 0:
                        return replacements
            except Exception as e:
                logger.error(f"Gemini API error during dynamic replanning: {e}")

        # Fallback dynamic replan
        failed_tool = failed_step_info.get("tool_name", "")
        if failed_tool == "http_client_mock":
            alt_tool = "web_search_mock"
            alt_args = {"query": f"Query data for {failed_step_info.get('step_name')}"}
        elif failed_tool == "web_search_mock":
            alt_tool = "text_summarizer"
            alt_args = {"text": "Verified local cached knowledge and indexed baseline data."}
        else:
            alt_tool = "data_transformer"
            alt_args = {"data": {"status": "recovered", "fallback_payload": True}, "transform_type": "sanitize"}

        return [
            {
                "step_name": f"Alternative for {failed_step_info.get('step_name', 'Failed Step')}",
                "tool_name": alt_tool,
                "tool_arguments": alt_args,
                "dependencies": failed_step_info.get("dependencies", []),
                "is_critical": False,
                "expected_output_format": "Structured recovered output"
            }
        ]

    async def verify_output_semantic(
        self,
        task_description: str,
        step_name: str,
        output: Any,
        expected_format: str
    ) -> Dict[str, Any]:
        """Perform semantic validation of step output via Gemini."""
        prompt = f"""
You are the AI Verification Engine. Verify if the following execution output satisfies the step expectations.

Task: "{task_description}"
Step: "{step_name}"
Expected Output Description: "{expected_format}"
Actual Output:
{json.dumps(output, default=str)}

Evaluate:
1. Is the output substantively complete and non-empty?
2. Does it answer the step requirement?
3. Calculate an assessment score between 0.0 and 1.0.

Return JSON ONLY:
{{
  "score": 0.95,
  "is_valid": true,
  "passed_checks": ["Non-empty payload", "Schema compliance", "Semantic relevance"],
  "failed_checks": [],
  "critique": "Output contains accurate and complete data."
}}
"""
        if self._client:
            try:
                response = self._client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    return self._extract_json(response.text)
            except Exception as e:
                logger.error(f"Gemini API error during verification: {e}")

        # Deterministic output verification fallback
        is_empty = output is None or output == "" or output == {} or output == []
        has_error = isinstance(output, dict) and "error" in output
        score = 0.2 if (is_empty or has_error) else 0.88
        
        passed = []
        failed = []
        if not is_empty:
            passed.append("Non-empty output produced")
        else:
            failed.append("Output is null or empty")
            
        if not has_error:
            passed.append("No error payload present")
        else:
            failed.append("Output payload contains error field")
            
        return {
            "score": score,
            "is_valid": score >= settings.CONFIDENCE_THRESHOLD,
            "passed_checks": passed,
            "failed_checks": failed,
            "critique": "Deterministic verification performed based on structural integrity and content completeness."
        }

gemini_service = GeminiService()
