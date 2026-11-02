import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings, update_runtime_settings
from app.gemini.client import gemini_service
from app.core.task_planner import task_planner
from app.core.task_executor import task_executor
from app.core.failure_predictor import failure_predictor
from app.core.memory_manager import memory_manager
from app.models.db_models import (
    TaskRecord,
    TaskStepRecord,
    RecoveryAttemptRecord,
    VerificationRecord,
    FailurePredictionRecord,
    MemoryRecord
)
from app.models.schemas import (
    TaskCreateRequest,
    TaskDetailResponse,
    StepSchema,
    RecoveryAttemptSchema,
    VerificationSchema,
    FailurePredictionSchema,
    MemoryItemSchema,
    DashboardStatsResponse,
    SettingsUpdateRequest,
    SettingsResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "gemini_configured": gemini_service.is_configured(),
        "gemini_model": settings.GEMINI_MODEL
    }

@router.post("/tasks", response_model=TaskDetailResponse)
async def create_task(req: TaskCreateRequest, db: Session = Depends(get_db)):
    """Creates a new task, decomposes it into steps via Gemini, and predicts failure risk."""
    task_id = str(uuid.uuid4())
    
    # 1. Plan task with Gemini
    planned_steps = await task_planner.plan_task(req.description, force_fault=req.force_fault)
    
    # 2. Predict failure risk (Feature 5)
    prediction = failure_predictor.predict_task_risk(req.description, planned_steps)
    
    # 3. Create TaskRecord
    task_rec = TaskRecord(
        id=task_id,
        title=req.title,
        description=req.description,
        status="PENDING",
        total_steps=len(planned_steps),
        predicted_risk_level=prediction["predicted_risk_level"]
    )
    db.add(task_rec)
    db.commit()

    # 4. Save Prediction Record
    pred_rec = FailurePredictionRecord(
        id=str(uuid.uuid4()),
        task_id=task_id,
        predicted_risk_score=prediction["predicted_risk_score"],
        predicted_risk_level=prediction["predicted_risk_level"],
        potential_failure_modes=prediction["potential_failure_modes"],
        preventive_recommendations=prediction["preventive_recommendations"],
        mathematical_formula=prediction["mathematical_formula"]
    )
    db.add(pred_rec)
    db.commit()

    # 5. Save Steps
    step_schemas = []
    for s in planned_steps:
        s_id = s.get("id") or str(uuid.uuid4())
        step_rec = TaskStepRecord(
            id=s_id,
            task_id=task_id,
            step_index=s["step_index"],
            step_name=s["step_name"],
            tool_name=s["tool_name"],
            tool_arguments=s.get("tool_arguments", {}),
            dependencies=s.get("dependencies", []),
            status="PENDING",
            is_critical=s.get("is_critical", False)
        )
        db.add(step_rec)
        step_schemas.append(StepSchema(
            id=s_id,
            step_index=s["step_index"],
            step_name=s["step_name"],
            tool_name=s["tool_name"],
            tool_arguments=s.get("tool_arguments", {}),
            dependencies=s.get("dependencies", []),
            status="PENDING",
            is_critical=s.get("is_critical", False)
        ))
    db.commit()

    return TaskDetailResponse(
        id=task_id,
        title=req.title,
        description=req.description,
        status="PENDING",
        total_steps=len(planned_steps),
        successful_steps=0,
        failed_steps=0,
        replan_count=0,
        recovery_attempts_count=0,
        final_confidence=0.0,
        calibrated_probability=0.0,
        predicted_risk_level=prediction["predicted_risk_level"],
        created_at=task_rec.created_at,
        steps=step_schemas,
        recovery_attempts=[],
        verifications=[],
        predictions=[
            FailurePredictionSchema(
                id=pred_rec.id,
                predicted_risk_score=pred_rec.predicted_risk_score,
                predicted_risk_level=pred_rec.predicted_risk_level,
                potential_failure_modes=pred_rec.potential_failure_modes or [],
                preventive_recommendations=pred_rec.preventive_recommendations or [],
                mathematical_formula=pred_rec.mathematical_formula
            )
        ]
    )

@router.post("/tasks/{task_id}/execute", response_model=TaskDetailResponse)
async def execute_task_endpoint(task_id: str, db: Session = Depends(get_db)):
    """Executes a previously planned task end-to-end with self-healing."""
    task_rec = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not task_rec:
        raise HTTPException(status_code=404, detail="Task not found")

    step_recs = db.query(TaskStepRecord).filter(TaskStepRecord.task_id == task_id).order_by(TaskStepRecord.step_index).all()
    steps_data = [
        {
            "id": s.id,
            "step_index": s.step_index,
            "step_name": s.step_name,
            "tool_name": s.tool_name,
            "tool_arguments": s.tool_arguments or {},
            "dependencies": s.dependencies or [],
            "status": s.status,
            "is_critical": s.is_critical,
            "is_replacement": s.is_replacement,
            "replaces_step_id": s.replaces_step_id
        }
        for s in step_recs
    ]

    pred_rec = db.query(FailurePredictionRecord).filter(FailurePredictionRecord.task_id == task_id).first()
    pred_data = {
        "predicted_risk_score": pred_rec.predicted_risk_score if pred_rec else 0.2,
        "predicted_risk_level": pred_rec.predicted_risk_level if pred_rec else "LOW",
        "potential_failure_modes": pred_rec.potential_failure_modes if pred_rec else [],
        "preventive_recommendations": pred_rec.preventive_recommendations if pred_rec else [],
        "mathematical_formula": pred_rec.mathematical_formula if pred_rec else ""
    }

    # Execute
    await task_executor.execute_task(
        task_id=task_id,
        task_title=task_rec.title,
        task_description=task_rec.description,
        steps=steps_data,
        prediction_info=pred_data,
        db=db
    )

    return get_task_details_response(task_id, db)

@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    return get_task_details_response(task_id, db)

@router.get("/tasks/{task_id}/status")
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task_rec = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not task_rec:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": task_rec.status,
        "total_steps": task_rec.total_steps,
        "successful_steps": task_rec.successful_steps,
        "failed_steps": task_rec.failed_steps,
        "replan_count": task_rec.replan_count,
        "recovery_attempts_count": task_rec.recovery_attempts_count,
        "final_confidence": task_rec.final_confidence
    }

@router.get("/tasks", response_model=List[TaskDetailResponse])
def list_tasks(
    status: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(TaskRecord).order_by(TaskRecord.created_at.desc())
    if status:
        query = query.filter(TaskRecord.status == status.upper())
    tasks = query.limit(limit).all()
    return [get_task_details_response(t.id, db) for t in tasks]

@router.get("/recovery/history", response_model=List[RecoveryAttemptSchema])
def get_recovery_history(db: Session = Depends(get_db)):
    attempts = db.query(RecoveryAttemptRecord).order_by(RecoveryAttemptRecord.created_at.desc()).limit(50).all()
    return [
        RecoveryAttemptSchema(
            id=a.id,
            step_id=a.step_id,
            attempt_number=a.attempt_number,
            error_detected=a.error_detected,
            diagnosis=a.diagnosis,
            error_category=a.error_category,
            selected_strategy=a.selected_strategy,
            proposed_action=a.proposed_action or {},
            is_validated=a.is_validated,
            validation_reason=a.validation_reason,
            outcome=a.outcome,
            execution_details=a.execution_details,
            created_at=a.created_at
        )
        for a in attempts
    ]

@router.get("/memories", response_model=List[MemoryItemSchema])
def get_memories(
    memory_type: Optional[str] = None,
    query: Optional[str] = None
):
    items = memory_manager.get_all_memories(memory_type=memory_type, search_query=query)
    return [
        MemoryItemSchema(
            id=m["id"],
            memory_type=m["memory_type"],
            task_description=m["task_description"],
            tool_name=m["tool_name"],
            error_category=m.get("error_category"),
            error_message=m.get("error_message"),
            diagnosis=m.get("diagnosis"),
            recovery_strategy=m.get("recovery_strategy"),
            recovery_action=m.get("recovery_action", {}),
            outcome=m["outcome"],
            confidence_score=m.get("confidence_score", 0.0),
            frequency=m.get("frequency", 1),
            tags=m.get("tags", []),
            created_at=m.get("created_at")
        )
        for m in items
    ]

@router.get("/predictions", response_model=List[FailurePredictionSchema])
def get_predictions(db: Session = Depends(get_db)):
    preds = db.query(FailurePredictionRecord).order_by(FailurePredictionRecord.created_at.desc()).limit(50).all()
    return [
        FailurePredictionSchema(
            id=p.id,
            predicted_risk_score=p.predicted_risk_score,
            predicted_risk_level=p.predicted_risk_level,
            potential_failure_modes=p.potential_failure_modes or [],
            preventive_recommendations=p.preventive_recommendations or [],
            mathematical_formula=p.mathematical_formula,
            actual_outcome=p.actual_outcome,
            was_accurate=p.was_accurate
        )
        for p in preds
    ]

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(TaskRecord).count()
    completed = db.query(TaskRecord).filter(TaskRecord.status == "COMPLETED").count()
    recovered = db.query(TaskRecord).filter(TaskRecord.status == "RECOVERED").count()
    failed = db.query(TaskRecord).filter(TaskRecord.status == "FAILED").count()

    total_faults = recovered + failed
    recovery_rate = round((recovered / total_faults * 100), 1) if total_faults > 0 else 100.0

    # Average confidence
    tasks = db.query(TaskRecord).all()
    conf_scores = [t.final_confidence for t in tasks if t.final_confidence > 0]
    avg_conf = round(sum(conf_scores) / len(conf_scores), 2) if conf_scores else 0.88

    # Prediction accuracy
    preds = db.query(FailurePredictionRecord).filter(FailurePredictionRecord.was_accurate.isnot(None)).all()
    accurate_count = sum(1 for p in preds if p.was_accurate)
    pred_accuracy = round((accurate_count / len(preds) * 100), 1) if preds else 85.0

    # Risk distribution
    low_risk = db.query(TaskRecord).filter(TaskRecord.predicted_risk_level == "LOW").count()
    med_risk = db.query(TaskRecord).filter(TaskRecord.predicted_risk_level == "MEDIUM").count()
    high_risk = db.query(TaskRecord).filter(TaskRecord.predicted_risk_level == "HIGH").count()

    recent_recs = db.query(TaskRecord).order_by(TaskRecord.created_at.desc()).limit(5).all()
    recent = [get_task_details_response(t.id, db) for t in recent_recs]

    return DashboardStatsResponse(
        total_tasks=total,
        successful_tasks=completed,
        failed_tasks=failed,
        recovered_tasks=recovered,
        recovery_success_rate=recovery_rate,
        avg_confidence_score=avg_conf,
        failure_prediction_accuracy=pred_accuracy,
        risk_distribution={"LOW": low_risk, "MEDIUM": med_risk, "HIGH": high_risk},
        recent_tasks=recent
    )

@router.get("/settings", response_model=SettingsResponse)
def get_settings():
    return SettingsResponse(
        api_key_configured=gemini_service.is_configured(),
        gemini_model=settings.GEMINI_MODEL,
        max_recovery_attempts=settings.MAX_RECOVERY_ATTEMPTS,
        max_replan_attempts=settings.MAX_REPLAN_ATTEMPTS,
        confidence_threshold=settings.CONFIDENCE_THRESHOLD,
        allowed_tools=settings.ALLOWED_TOOLS
    )

@router.post("/settings", response_model=SettingsResponse)
def update_settings(req: SettingsUpdateRequest):
    update_runtime_settings(
        api_key=req.api_key,
        model=req.model,
        max_recovery_attempts=req.max_recovery_attempts,
        max_replan_attempts=req.max_replan_attempts,
        confidence_threshold=req.confidence_threshold
    )
    gemini_service.reload()
    return get_settings()

def get_task_details_response(task_id: str, db: Session) -> TaskDetailResponse:
    task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    step_records = db.query(TaskStepRecord).filter(TaskStepRecord.task_id == task_id).order_by(TaskStepRecord.step_index).all()
    rec_records = db.query(RecoveryAttemptRecord).filter(RecoveryAttemptRecord.task_id == task_id).order_by(RecoveryAttemptRecord.created_at).all()
    ver_records = db.query(VerificationRecord).filter(VerificationRecord.task_id == task_id).order_by(VerificationRecord.created_at).all()
    pred_records = db.query(FailurePredictionRecord).filter(FailurePredictionRecord.task_id == task_id).all()

    return TaskDetailResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        total_steps=task.total_steps,
        successful_steps=task.successful_steps,
        failed_steps=task.failed_steps,
        replan_count=task.replan_count,
        recovery_attempts_count=task.recovery_attempts_count,
        final_output=task.final_output,
        final_confidence=task.final_confidence,
        calibrated_probability=task.calibrated_probability,
        predicted_risk_level=task.predicted_risk_level or "LOW",
        created_at=task.created_at,
        completed_at=task.completed_at,
        steps=[
            StepSchema(
                id=s.id,
                step_index=s.step_index,
                step_name=s.step_name,
                tool_name=s.tool_name,
                tool_arguments=s.tool_arguments or {},
                dependencies=s.dependencies or [],
                status=s.status,
                output=s.output,
                error_message=s.error_message,
                is_critical=s.is_critical,
                confidence_score=s.confidence_score,
                heuristic_confidence=s.heuristic_confidence,
                calibrated_probability=s.calibrated_probability,
                is_replacement=s.is_replacement,
                replaces_step_id=s.replaces_step_id
            )
            for s in step_records
        ],
        recovery_attempts=[
            RecoveryAttemptSchema(
                id=r.id,
                step_id=r.step_id,
                attempt_number=r.attempt_number,
                error_detected=r.error_detected,
                diagnosis=r.diagnosis,
                error_category=r.error_category,
                selected_strategy=r.selected_strategy,
                proposed_action=r.proposed_action or {},
                is_validated=r.is_validated,
                validation_reason=r.validation_reason,
                outcome=r.outcome,
                execution_details=r.execution_details,
                created_at=r.created_at
            )
            for r in rec_records
        ],
        verifications=[
            VerificationSchema(
                id=v.id,
                step_id=v.step_id,
                score=v.score,
                confidence_level=v.confidence_level,
                is_verified=v.is_verified,
                heuristic_score=v.heuristic_score,
                calibrated_probability=v.calibrated_probability,
                checks_passed=v.checks_passed or [],
                checks_failed=v.checks_failed or [],
                critique=v.critique
            )
            for v in ver_records
        ],
        predictions=[
            FailurePredictionSchema(
                id=p.id,
                predicted_risk_score=p.predicted_risk_score,
                predicted_risk_level=p.predicted_risk_level,
                potential_failure_modes=p.potential_failure_modes or [],
                preventive_recommendations=p.preventive_recommendations or [],
                mathematical_formula=p.mathematical_formula,
                actual_outcome=p.actual_outcome,
                was_accurate=p.was_accurate
            )
            for p in pred_records
        ]
    )
