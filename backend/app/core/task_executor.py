import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db_models import (
    TaskRecord,
    TaskStepRecord,
    RecoveryAttemptRecord,
    VerificationRecord,
    FailurePredictionRecord,
    MemoryRecord
)
from app.tools.registry import tool_registry
from app.core.failure_detector import failure_detector
from app.core.recovery_planner import recovery_planner
from app.core.dynamic_replanner import dynamic_replanner
from app.core.confidence_verifier import confidence_verifier
from app.core.failure_predictor import failure_predictor
from app.core.memory_manager import memory_manager
import logging

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes multi-step tasks with end-to-end self-healing, verification, and memory recording."""

    async def execute_task(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        steps: List[Dict[str, Any]],
        prediction_info: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        logger.info(f"Starting execution of task: '{task_title}' ({task_id}) with {len(steps)} steps.")

        task_record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
        if not task_record:
            raise ValueError(f"Task with ID {task_id} not found in database.")

        task_record.status = "RUNNING"
        db.commit()

        # Save initial prediction record
        pred_record = FailurePredictionRecord(
            id=str(uuid.uuid4()),
            task_id=task_id,
            predicted_risk_score=prediction_info.get("predicted_risk_score", 0.0),
            predicted_risk_level=prediction_info.get("predicted_risk_level", "LOW"),
            potential_failure_modes=prediction_info.get("potential_failure_modes", []),
            preventive_recommendations=prediction_info.get("preventive_recommendations", []),
            mathematical_formula=prediction_info.get("mathematical_formula")
        )
        db.add(pred_record)
        db.commit()

        # Synchronize step records into DB
        for s in steps:
            step_rec = TaskStepRecord(
                id=s["id"],
                task_id=task_id,
                step_index=s["step_index"],
                step_name=s["step_name"],
                tool_name=s["tool_name"],
                tool_arguments=s.get("tool_arguments", {}),
                dependencies=s.get("dependencies", []),
                status=s["status"],
                is_critical=s.get("is_critical", False),
                is_replacement=s.get("is_replacement", False),
                replaces_step_id=s.get("replaces_step_id")
            )
            db.merge(step_rec)
        db.commit()

        execution_context: Dict[str, Any] = {}
        had_recovery = False
        replan_count = 0
        total_recovery_attempts = 0
        current_step_idx = 0

        while current_step_idx < len(steps):
            step = steps[current_step_idx]
            step_id = step["id"]
            step_name = step["step_name"]
            tool_name = step["tool_name"]
            args = step.get("tool_arguments", {})
            is_critical = step.get("is_critical", False)
            expected_format = step.get("expected_output_format", "")

            # Update step record status
            step_rec = db.query(TaskStepRecord).filter(TaskStepRecord.id == step_id).first()
            if step_rec:
                step_rec.status = "RUNNING"
                db.commit()

            step_success = False
            step_output = None
            step_attempt = 1

            while step_attempt <= settings.MAX_RECOVERY_ATTEMPTS and not step_success:
                try:
                    logger.info(f"Executing step {current_step_idx} ('{step_name}') with tool '{tool_name}' [Attempt {step_attempt}]")
                    # Step execution via tool registry with timeout protection
                    step_output = await asyncio.wait_for(
                        tool_registry.execute(tool_name, args),
                        timeout=settings.TOOL_EXECUTION_TIMEOUT_SECONDS
                    )

                    # Feature 4: Confidence-Based Verification
                    verification_res = await confidence_verifier.verify_step_output(
                        task_description=task_description,
                        step_name=step_name,
                        tool_name=tool_name,
                        output=step_output,
                        expected_format=expected_format,
                        is_critical=is_critical
                    )

                    # Persist verification record
                    verif_rec = VerificationRecord(
                        id=str(uuid.uuid4()),
                        task_id=task_id,
                        step_id=step_id,
                        score=verification_res["score"],
                        confidence_level=verification_res["confidence_level"],
                        is_verified=verification_res["is_verified"],
                        heuristic_score=verification_res["heuristic_score"],
                        calibrated_probability=verification_res["calibrated_probability"],
                        checks_passed=verification_res["checks_passed"],
                        checks_failed=verification_res["checks_failed"],
                        critique=verification_res["critique"]
                    )
                    db.add(verif_rec)
                    db.commit()

                    if not verification_res["is_verified"]:
                        raise ValueError(f"Confidence verification failed (Score: {verification_res['score']:.2f} < Threshold: {verification_res['threshold']:.2f})")

                    # Step passed!
                    step_success = True
                    execution_context[f"step_{current_step_idx}"] = step_output
                    step["output"] = step_output
                    step["status"] = "RECOVERED" if step_attempt > 1 else "COMPLETED"
                    step["confidence_score"] = verification_res["score"]
                    step["heuristic_confidence"] = verification_res["heuristic_score"]
                    step["calibrated_probability"] = verification_res["calibrated_probability"]

                    if step_rec:
                        step_rec.status = step["status"]
                        step_rec.output = step_output
                        step_rec.confidence_score = verification_res["score"]
                        step_rec.heuristic_confidence = verification_res["heuristic_score"]
                        step_rec.calibrated_probability = verification_res["calibrated_probability"]
                        step_rec.completed_at = datetime.now(timezone.utc)
                        db.commit()

                    # Record successful execution memory if it recovered from an earlier fault
                    if step_attempt > 1:
                        had_recovery = True
                        memory_manager.record_experience(
                            task_description=task_description,
                            tool_name=tool_name,
                            error_category="RESOLVED_FAULT",
                            error_message="Recovered from transient/parameter fault",
                            diagnosis="Self-healing recovery successful",
                            recovery_strategy="ARGUMENT_OR_RETRY_ADAPTATION",
                            recovery_action=args,
                            outcome="SUCCESS",
                            confidence_score=verification_res["score"],
                            db=db
                        )

                except Exception as exc:
                    logger.warning(f"Fault detected in step {current_step_idx} ('{step_name}'): {exc}")
                    total_recovery_attempts += 1
                    
                    # 1. Detect and inspect failure
                    failure_info = failure_detector.detect_failure(
                        step_name=step_name,
                        tool_name=tool_name,
                        tool_args=args,
                        exception=exc
                    )

                    # 2. Plan recovery (Feature 1 & Feature 2)
                    recovery_decision = await recovery_planner.plan_recovery(
                        task_description=task_description,
                        step_name=step_name,
                        tool_name=tool_name,
                        tool_arguments=args,
                        error_message=failure_info["error_message"],
                        error_category=failure_info["error_category"],
                        attempt_number=step_attempt,
                        current_replan_count=replan_count
                    )

                    strategy = recovery_decision["selected_strategy"]
                    proposed_action = recovery_decision["proposed_action"]
                    
                    # Record recovery attempt to DB
                    rec_attempt = RecoveryAttemptRecord(
                        id=str(uuid.uuid4()),
                        task_id=task_id,
                        step_id=step_id,
                        attempt_number=step_attempt,
                        error_detected=failure_info["error_message"],
                        diagnosis=recovery_decision["diagnosis"],
                        error_category=recovery_decision["error_category"],
                        selected_strategy=strategy,
                        proposed_action=proposed_action,
                        is_validated=recovery_decision["is_validated"],
                        validation_reason=recovery_decision["validation_reason"],
                        outcome="PENDING"
                    )
                    db.add(rec_attempt)
                    db.commit()

                    # Execute strategy
                    if strategy == "STOP" or not recovery_decision["is_validated"]:
                        step["status"] = "FAILED"
                        step["error_message"] = failure_info["error_message"]
                        if step_rec:
                            step_rec.status = "FAILED"
                            step_rec.error_message = failure_info["error_message"]
                        rec_attempt.outcome = "ABORTED"
                        db.commit()
                        
                        # Store failed experience in memory (Feature 2)
                        memory_manager.record_experience(
                            task_description=task_description,
                            tool_name=tool_name,
                            error_category=failure_info["error_category"],
                            error_message=failure_info["error_message"],
                            diagnosis=recovery_decision["diagnosis"],
                            recovery_strategy=strategy,
                            recovery_action=proposed_action,
                            outcome="FAILURE",
                            confidence_score=0.1,
                            db=db
                        )
                        break

                    elif strategy == "RETRY":
                        delay = proposed_action.get("retry_delay_seconds", 1)
                        await asyncio.sleep(delay)
                        step_attempt += 1
                        rec_attempt.outcome = "RETRY_TRIGGERED"
                        db.commit()

                    elif strategy == "CHANGE_ARGUMENTS":
                        corrected = proposed_action.get("corrected_arguments", {})
                        if corrected:
                            args = corrected
                            step["tool_arguments"] = args
                            if step_rec:
                                step_rec.tool_arguments = args
                        step_attempt += 1
                        rec_attempt.outcome = "ARGUMENTS_ADAPTED"
                        db.commit()

                    elif strategy == "REPLAN":
                        had_recovery = True
                        replan_count += 1
                        rec_attempt.outcome = "REPLAN_TRIGGERED"
                        db.commit()

                        # Feature 3: Dynamic Replanning
                        new_plan, replan_ok, replan_msg = await dynamic_replanner.replan_failed_step(
                            task_description=task_description,
                            all_steps=steps,
                            failed_step_index=current_step_idx,
                            execution_context=execution_context,
                            current_replan_count=replan_count
                        )

                        if replan_ok:
                            # Mark failed step as replaced
                            step["status"] = "RECOVERED"
                            if step_rec:
                                step_rec.status = "RECOVERED"
                                step_rec.error_message = f"Replaced by dynamic replanning: {replan_msg}"
                            db.commit()

                            # Persist newly inserted replacement steps
                            steps = new_plan
                            for n_step in steps:
                                if not n_step.get("id"):
                                    n_step["id"] = str(uuid.uuid4())
                                    new_db_step = TaskStepRecord(
                                        id=n_step["id"],
                                        task_id=task_id,
                                        step_index=n_step["step_index"],
                                        step_name=n_step["step_name"],
                                        tool_name=n_step["tool_name"],
                                        tool_arguments=n_step.get("tool_arguments", {}),
                                        dependencies=n_step.get("dependencies", []),
                                        status=n_step["status"],
                                        is_replacement=n_step.get("is_replacement", False),
                                        replaces_step_id=n_step.get("replaces_step_id")
                                    )
                                    db.add(new_db_step)
                            db.commit()

                            # Record memory of replan success attempt
                            memory_manager.record_experience(
                                task_description=task_description,
                                tool_name=tool_name,
                                error_category=failure_info["error_category"],
                                error_message=failure_info["error_message"],
                                diagnosis=recovery_decision["diagnosis"],
                                recovery_strategy="REPLAN",
                                recovery_action=proposed_action,
                                outcome="SUCCESS",
                                confidence_score=0.88,
                                db=db
                            )
                            # Restart loop at current step with replacement step
                            step_success = True
                            break
                        else:
                            step["status"] = "FAILED"
                            if step_rec:
                                step_rec.status = "FAILED"
                            break

            if not step_success and step["status"] == "FAILED":
                # Unrecoverable step failed
                break

            current_step_idx += 1

        # Final task outcome synthesis
        completed_count = sum(1 for s in steps if s.get("status") in ("COMPLETED", "RECOVERED"))
        failed_count = sum(1 for s in steps if s.get("status") == "FAILED")
        
        if failed_count > 0:
            final_status = "FAILED"
        elif had_recovery:
            final_status = "RECOVERED"
        else:
            final_status = "COMPLETED"

        # Calculate final overall task confidence
        valid_confidences = [s.get("confidence_score", 0.0) for s in steps if s.get("confidence_score", 0.0) > 0]
        final_conf = round(sum(valid_confidences) / len(valid_confidences), 3) if valid_confidences else (0.85 if final_status in ("COMPLETED", "RECOVERED") else 0.20)
        
        # Calculate task-level calibrated probability
        calibrated_probs = [s.get("calibrated_probability", 0.0) for s in steps if s.get("calibrated_probability", 0.0) > 0]
        final_calibrated = round(sum(calibrated_probs) / len(calibrated_probs), 3) if calibrated_probs else 0.82

        # Final output summary
        final_output_str = f"Task '{task_title}' finished with status: {final_status}. Executed {completed_count}/{len(steps)} steps."
        if execution_context:
            last_key = list(execution_context.keys())[-1]
            final_output_str += f" Result: {execution_context[last_key]}"

        # Update TaskRecord
        task_record.status = final_status
        task_record.total_steps = len(steps)
        task_record.successful_steps = completed_count
        task_record.failed_steps = failed_count
        task_record.replan_count = replan_count
        task_record.recovery_attempts_count = total_recovery_attempts
        task_record.final_output = final_output_str
        task_record.final_confidence = final_conf
        task_record.calibrated_probability = final_calibrated
        task_record.predicted_risk_level = prediction_info.get("predicted_risk_level", "LOW")
        task_record.completed_at = datetime.now(timezone.utc)

        # Feature 5: Evaluate prediction accuracy
        was_accurate = failure_predictor.evaluate_prediction_accuracy(
            predicted_risk_level=prediction_info.get("predicted_risk_level", "LOW"),
            predicted_risk_score=prediction_info.get("predicted_risk_score", 0.0),
            actual_outcome=final_status,
            recovered=had_recovery
        )
        pred_record.actual_outcome = final_status
        pred_record.was_accurate = was_accurate

        db.commit()

        logger.info(f"Task {task_id} completed. Status: {final_status}, Confidence: {final_conf}, Recovered: {had_recovery}")

        return {
            "task_id": task_id,
            "status": final_status,
            "total_steps": len(steps),
            "successful_steps": completed_count,
            "failed_steps": failed_count,
            "replan_count": replan_count,
            "recovery_attempts_count": total_recovery_attempts,
            "final_confidence": final_conf,
            "calibrated_probability": final_calibrated,
            "final_output": final_output_str,
            "was_accurate": was_accurate
        }

task_executor = TaskExecutor()
