from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Self-Healing AI Agent Framework"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Storage Configuration
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'self_healing_ai.db'}"
    EPISODIC_MEMORY_FILE: str = str(BASE_DIR / "episodic_memory.json")
    
    # Execution & Recovery Thresholds
    MAX_RECOVERY_ATTEMPTS: int = 3
    MAX_REPLAN_ATTEMPTS: int = 2
    CONFIDENCE_THRESHOLD: float = 0.65
    TOOL_EXECUTION_TIMEOUT_SECONDS: int = 20
    MEMORY_SIMILARITY_THRESHOLD: float = 0.55
    
    # Tool Sandbox Allowlist
    ALLOWED_TOOLS: List[str] = [
        "web_search_mock",
        "calculator",
        "text_summarizer",
        "json_validator",
        "data_transformer",
        "http_client_mock",
        "file_sandbox_reader",
        "file_sandbox_writer"
    ]
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

def update_runtime_settings(
    api_key: str = None,
    model: str = None,
    max_recovery_attempts: int = None,
    max_replan_attempts: int = None,
    confidence_threshold: float = None
):
    global settings
    if api_key is not None:
        settings.GEMINI_API_KEY = api_key
    if model is not None:
        settings.GEMINI_MODEL = model
    if max_recovery_attempts is not None:
        settings.MAX_RECOVERY_ATTEMPTS = max_recovery_attempts
    if max_replan_attempts is not None:
        settings.MAX_REPLAN_ATTEMPTS = max_replan_attempts
    if confidence_threshold is not None:
        settings.CONFIDENCE_THRESHOLD = confidence_threshold
    return settings
