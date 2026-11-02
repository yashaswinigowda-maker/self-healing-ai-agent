from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)
    force_fault: Optional[str] = None # For testing & demonstration of self-healing mechanisms

class StepSchema(BaseModel):
    id: Optional[str] = None
    step_index: int
    step_name: str
    tool_name: str
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: str = "PENDING"
    output: Optional[Any] = None
    error_message: Optional[str] = None
    is_critical: bool = False
    confidence_score: float = 0.0
    heuristic_confidence: float = 0.0
    calibrated_probability: float = 0.0
    is_replacement: bool = False
    replaces_step_id: Optional[str] = None

class RecoveryAttemptSchema(BaseModel):
    id: str
    step_id: Optional[str] = None
    attempt_number: int
    error_detected: str
    diagnosis: str
    error_category: str
    selected_strategy: str
    proposed_action: Dict[str, Any]
    is_validated: bool
    validation_reason: Optional[str] = None
    outcome: str
    execution_details: Optional[str] = None
    created_at: Optional[datetime] = None

class VerificationSchema(BaseModel):
    id: str
    step_id: Optional[str] = None
    score: float
    confidence_level: str
    is_verified: bool
    heuristic_score: float
    calibrated_probability: float
    checks_passed: List[str] = Field(default_factory=list)
    checks_failed: List[str] = Field(default_factory=list)
    critique: Optional[str] = None

class FailurePredictionSchema(BaseModel):
    id: str
    predicted_risk_score: float
    predicted_risk_level: str
    potential_failure_modes: List[str] = Field(default_factory=list)
    preventive_recommendations: List[str] = Field(default_factory=list)
    mathematical_formula: Optional[str] = None
    actual_outcome: Optional[str] = None
    was_accurate: Optional[bool] = None

class TaskDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    total_steps: int
    successful_steps: int
    failed_steps: int
    replan_count: int
    recovery_attempts_count: int
    final_output: Optional[str] = None
    final_confidence: float = 0.0
    calibrated_probability: float = 0.0
    predicted_risk_level: str = "LOW"
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: List[StepSchema] = Field(default_factory=list)
    recovery_attempts: List[RecoveryAttemptSchema] = Field(default_factory=list)
    verifications: List[VerificationSchema] = Field(default_factory=list)
    predictions: List[FailurePredictionSchema] = Field(default_factory=list)

class MemoryItemSchema(BaseModel):
    id: str
    memory_type: str # SUCCESS, FAILURE
    task_description: str
    tool_name: str
    error_category: Optional[str] = None
    error_message: Optional[str] = None
    diagnosis: Optional[str] = None
    recovery_strategy: Optional[str] = None
    recovery_action: Dict[str, Any] = Field(default_factory=dict)
    outcome: str
    confidence_score: float = 0.0
    frequency: int = 1
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

class DashboardStatsResponse(BaseModel):
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    recovered_tasks: int
    recovery_success_rate: float
    avg_confidence_score: float
    failure_prediction_accuracy: float
    risk_distribution: Dict[str, int]
    recent_tasks: List[TaskDetailResponse] = Field(default_factory=list)

class SettingsUpdateRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None
    max_recovery_attempts: Optional[int] = None
    max_replan_attempts: Optional[int] = None
    confidence_threshold: Optional[float] = None

class SettingsResponse(BaseModel):
    api_key_configured: bool
    gemini_model: str
    max_recovery_attempts: int
    max_replan_attempts: int
    confidence_threshold: float
    allowed_tools: List[str]
