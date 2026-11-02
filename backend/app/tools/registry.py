import ast
import operator
import re
from pathlib import Path
from typing import Dict, Any, Callable
from app.config import settings
import logging

logger = logging.getLogger(__name__)

SANDBOX_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "sandbox_storage"
SANDBOX_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Safe math operators for AST calculator
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval_math_expr(node):
    if isinstance(node, ast.Expression):
        return safe_eval_math_expr(node.body)
    elif isinstance(node, ast.Constant): # number
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](safe_eval_math_expr(node.operand))
        raise ValueError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            left = safe_eval_math_expr(node.left)
            right = safe_eval_math_expr(node.right)
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero in mathematical expression.")
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")
    else:
        raise ValueError(f"Unsafe or forbidden expression syntax: {type(node).__name__}")


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register(self, name: str, func: Callable, description: str, parameter_schema: Dict[str, Any]):
        self._tools[name] = {
            "name": name,
            "func": func,
            "description": description,
            "parameter_schema": parameter_schema
        }

    def get_tool(self, name: str) -> Dict[str, Any]:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not in the allowed tools registry.")
        if name not in settings.ALLOWED_TOOLS:
            raise PermissionError(f"Tool '{name}' is prohibited by security policy allowlist.")
        return self._tools[name]

    def list_tools(self) -> Dict[str, Any]:
        return {
            name: {
                "name": info["name"],
                "description": info["description"],
                "parameter_schema": info["parameter_schema"]
            }
            for name, info in self._tools.items()
            if name in settings.ALLOWED_TOOLS
        }

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        tool_info = self.get_tool(tool_name)
        func = tool_info["func"]
        return func(**arguments)

    def _register_default_tools(self):
        # 1. Calculator
        def calculator(expression: str) -> Dict[str, Any]:
            cleaned = expression.strip().replace("^", "**")
            parsed = ast.parse(cleaned, mode='eval')
            result = safe_eval_math_expr(parsed)
            return {"expression": expression, "result": result, "status": "calculated"}

        self.register(
            name="calculator",
            func=calculator,
            description="Safely evaluates arithmetic expressions (+, -, *, /, %).",
            parameter_schema={"expression": "string arithmetic expression"}
        )

        # 2. Web Search Mock
        def web_search_mock(query: str) -> Dict[str, Any]:
            q_lower = query.lower()
            results = []
            if "weather" in q_lower:
                results = [
                    {"title": "Global Meteorological Center", "snippet": "Seattle: 62°F, partly cloudy, gentle breeze.", "confidence": 0.95},
                    {"title": "Weather Weekly", "snippet": "Pacific Northwest experiencing mild seasonal conditions.", "confidence": 0.91}
                ]
            elif "crypto" in q_lower or "bitcoin" in q_lower or "market" in q_lower:
                results = [
                    {"title": "Market Indices Today", "snippet": "Tech equities up +1.2%, crypto market index steady.", "confidence": 0.94},
                    {"title": "Financial Trends", "snippet": "Benchmark yield stabilized at 4.15%.", "confidence": 0.89}
                ]
            elif "self-healing" in q_lower or "agent" in q_lower or "ai" in q_lower:
                results = [
                    {"title": "Autonomous Agent Resilience", "snippet": "Self-healing architectures achieve 94% task completion using dynamic replanning and memory retrieval.", "confidence": 0.98},
                    {"title": "Multi-Step Verification Protocols", "snippet": "Confidence scoring filters flawed intermediate states.", "confidence": 0.96}
                ]
            else:
                results = [
                    {"title": f"Index results for: {query}", "snippet": f"Verified factual data records for '{query}' retrieved successfully.", "confidence": 0.88}
                ]
            return {"query": query, "hits": len(results), "results": results}

        self.register(
            name="web_search_mock",
            func=web_search_mock,
            description="Searches an indexed knowledge repository for real-world factual data.",
            parameter_schema={"query": "string search terms"}
        )

        # 3. Text Summarizer
        def text_summarizer(text: str, max_length: int = 150) -> Dict[str, Any]:
            if not text:
                raise ValueError("Text to summarize cannot be empty.")
            sentences = re.split(r'(?<=[.!?]) +', text.strip())
            summary = " ".join(sentences[:2])
            if len(summary) > max_length:
                summary = summary[:max_length].rstrip() + "..."
            return {"original_length": len(text), "summary_length": len(summary), "summary": summary}

        self.register(
            name="text_summarizer",
            func=text_summarizer,
            description="Condenses lengthy documents into executive summaries.",
            parameter_schema={"text": "string source text", "max_length": "integer character limit"}
        )

        # 4. JSON Validator
        def json_validator(data: Any, schema_type: str = "generic") -> Dict[str, Any]:
            if not isinstance(data, (dict, list)):
                raise ValueError("Payload must be a valid JSON dictionary or array.")
            return {"schema_type": schema_type, "is_valid": True, "field_count": len(data) if isinstance(data, dict) else len(data)}

        self.register(
            name="json_validator",
            func=json_validator,
            description="Validates structured data schemas and types.",
            parameter_schema={"data": "dict or array", "schema_type": "string type identifier"}
        )

        # 5. Data Transformer
        def data_transformer(data: Any, transform_type: str = "sanitize") -> Dict[str, Any]:
            if transform_type == "currency_format":
                val = data.get("raw_value", 0) if isinstance(data, dict) else float(data)
                return {"formatted": f"${val:,.2f}", "currency": "USD", "status": "transformed"}
            elif transform_type == "sanitize":
                if isinstance(data, dict):
                    clean_dict = {k: str(v).strip() for k, v in data.items() if v is not None}
                    return {"sanitized_data": clean_dict, "status": "transformed"}
                return {"sanitized_data": str(data).strip(), "status": "transformed"}
            elif transform_type == "aggregate":
                items = data if isinstance(data, list) else [data]
                return {"count": len(items), "status": "transformed"}
            return {"data": data, "transform_type": transform_type, "status": "transformed"}

        self.register(
            name="data_transformer",
            func=data_transformer,
            description="Transforms, formats, and aggregates structured datasets.",
            parameter_schema={"data": "payload", "transform_type": "currency_format|sanitize|aggregate"}
        )

        # 6. HTTP Client Mock
        def http_client_mock(endpoint: str, method: str = "GET", params: Dict[str, Any] = None) -> Dict[str, Any]:
            if not endpoint:
                raise ValueError("Missing required parameter: 'endpoint'.")
            
            ep = endpoint.lower().strip()
            if "fail" in ep or "error" in ep:
                raise ConnectionError(f"HTTP 503 Service Unavailable: Remote endpoint '{endpoint}' is unreachable.")
            elif "timeout" in ep:
                raise TimeoutError(f"HTTP Connection Timeout after 15000ms for '{endpoint}'.")
            elif "weather" in ep:
                city = (params or {}).get("city", "Seattle")
                return {"endpoint": endpoint, "status_code": 200, "data": {"city": city, "temperature_f": 62, "condition": "Partly Cloudy", "humidity": 65}}
            elif "health" in ep:
                return {"endpoint": endpoint, "status_code": 200, "data": {"status": "healthy", "uptime_hours": 348}}
            else:
                return {"endpoint": endpoint, "status_code": 200, "data": {"message": f"Successfully queried endpoint '{endpoint}'", "params": params or {}}}

        self.register(
            name="http_client_mock",
            func=http_client_mock,
            description="Safe mock HTTP client for interacting with RESTful external APIs.",
            parameter_schema={"endpoint": "string path", "method": "GET|POST", "params": "optional dict"}
        )

        # 7. File Sandbox Reader
        def file_sandbox_reader(filename: str) -> Dict[str, Any]:
            # Guard against path traversal
            if ".." in filename or "/" in filename or "\\" in filename:
                raise PermissionError("Path traversal outside sandbox is forbidden.")
            target_path = SANDBOX_STORAGE_DIR / filename
            if not target_path.exists():
                raise FileNotFoundError(f"File '{filename}' does not exist in sandbox.")
            content = target_path.read_text(encoding="utf-8")
            return {"filename": filename, "content": content, "size_bytes": len(content)}

        self.register(
            name="file_sandbox_reader",
            func=file_sandbox_reader,
            description="Safely reads content from the isolated sandbox directory.",
            parameter_schema={"filename": "string relative file name"}
        )

        # 8. File Sandbox Writer
        def file_sandbox_writer(filename: str, content: str) -> Dict[str, Any]:
            if ".." in filename or "/" in filename or "\\" in filename:
                raise PermissionError("Path traversal outside sandbox is forbidden.")
            target_path = SANDBOX_STORAGE_DIR / filename
            target_path.write_text(content, encoding="utf-8")
            return {"filename": filename, "bytes_written": len(content), "status": "saved"}

        self.register(
            name="file_sandbox_writer",
            func=file_sandbox_writer,
            description="Safely writes content into the isolated sandbox storage directory.",
            parameter_schema={"filename": "string relative file name", "content": "text content"}
        )

tool_registry = ToolRegistry()
