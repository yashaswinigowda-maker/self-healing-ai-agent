from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", index=True) # PENDING, RUNNING, COMPLETED, RECOVERED, FAILED
    
    total_steps = Column(Integer, default=0)
    successful_steps = Column(Integer, default=0)
    failed_steps = Column(Integer, default=0)
    replan_count = Column(Integer, default=0)
    recovery_attempts_count = Column(Integer, default=0)
    
    final_output = Column(Text, nullable=True)
    final_confidence = Column(Float, default=0.0)
    calibrated_probability = Column(Float, default=0.0)
    predicted_risk_level = Column(String(20), default="LOW")
    
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("TaskStepRecord", back_populates="task", cascade="all, delete-orphan", order_by="TaskStepRecord.step_index")
    recovery_attempts = relationship("RecoveryAttemptRecord", back_populates="task", cascade="all, delete-orphan")
    verifications = relationship("VerificationRecord", back_populates="task", cascade="all, delete-orphan")
    predictions = relationship("FailurePredictionRecord", back_populates="task", cascade="all, delete-orphan")

class TaskStepRecord(Base):
    __tablename__ = "task_steps"

    id = Column(String(36), primary_key=True, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), index=True)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_arguments = Column(JSON, default=dict)
    dependencies = Column(JSON, default=list) # e.g. ["step_0"]
    
    status = Column(String(50), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED, RECOVERED, SKIPPED
    output = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    is_critical = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    heuristic_confidence = Column(Float, default=0.0)
    calibrated_probability = Column(Float, default=0.0)
    
    is_replacement = Column(Boolean, default=False)
    replaces_step_id = Column(String(36), nullable=True)
    
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    task = relationship("TaskRecord", back_populates="steps")
    recovery_attempts = relationship("RecoveryAttemptRecord", back_populates="step")
    verification = relationship("VerificationRecord", back_populates="step", uselist=False)

class RecoveryAttemptRecord(Base):
    __tablename__ = "recovery_attempts"

    id = Column(String(36), primary_key=True, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), index=True)
    step_id = Column(String(36), ForeignKey("task_steps.id"), index=True, nullable=True)
    
    attempt_number = Column(Integer, default=1)
    error_detected = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=False)
    error_category = Column(String(100), default="UNKNOWN")
    
    selected_strategy = Column(String(50), nullable=False) # RETRY, CHANGE_ARGUMENTS, REPLAN, STOP
    proposed_action = Column(JSON, default=dict)
    
    is_validated = Column(Boolean, default=True)
    validation_reason = Column(Text, nullable=True)
    
    outcome = Column(String(50), default="PENDING") # SUCCESS, FAILURE, ABORTED
    execution_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    task = relationship("TaskRecord", back_populates="recovery_attempts")
    step = relationship("TaskStepRecord", back_populates="recovery_attempts")

class VerificationRecord(Base):
    __tablename__ = "verifications"

    id = Column(String(36), primary_key=True, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), index=True)
    step_id = Column(String(36), ForeignKey("task_steps.id"), index=True, nullable=True)
    
    score = Column(Float, default=0.0) # Combined confidence score (0.0 - 1.0)
    confidence_level = Column(String(20), default="LOW") # HIGH, MEDIUM, LOW
    is_verified = Column(Boolean, default=False)
    
    # Clearly distinguishing heuristic vs calibrated
    heuristic_score = Column(Float, default=0.0)
    calibrated_probability = Column(Float, default=0.0)
    
    checks_passed = Column(JSON, default=list)
    checks_failed = Column(JSON, default=list)
    critique = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    task = relationship("TaskRecord", back_populates="verifications")
    step = relationship("TaskStepRecord", back_populates="verification")

class FailurePredictionRecord(Base):
    __tablename__ = "failure_predictions"

    id = Column(String(36), primary_key=True, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), index=True)
    
    predicted_risk_score = Column(Float, default=0.0) # 0.0 to 1.0
    predicted_risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    potential_failure_modes = Column(JSON, default=list)
    preventive_recommendations = Column(JSON, default=list)
    mathematical_formula = Column(Text, nullable=True)
    
    actual_outcome = Column(String(50), nullable=True) # SUCCESS, FAILURE, RECOVERED
    was_accurate = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    task = relationship("TaskRecord", back_populates="predictions")

class MemoryRecord(Base):
    __tablename__ = "episodic_memories"

    id = Column(String(36), primary_key=True, index=True)
    memory_type = Column(String(50), nullable=False) # SUCCESS, FAILURE
    task_description = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=False)
    
    error_category = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    
    recovery_strategy = Column(String(50), nullable=True) # RETRY, CHANGE_ARGUMENTS, REPLAN, STOP
    recovery_action = Column(JSON, default=dict)
    outcome = Column(String(50), nullable=False) # SUCCESS, FAILURE
    
    confidence_score = Column(Float, default=0.0)
    frequency = Column(Integer, default=1)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)
