import asyncio
import uuid
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal, init_db
from app.models.db_models import TaskRecord
from app.core.task_planner import task_planner
from app.core.failure_predictor import failure_predictor
from app.core.task_executor import task_executor

async def seed_demo_tasks():
    init_db()
    db = SessionLocal()
    try:
        count = db.query(TaskRecord).count()
        if count >= 3:
            print(f"Database already populated with {count} tasks. Skipping seed.")
            return

        print("Seeding demo tasks into database...")

        demo_scenarios = [
            {
                "title": "Corporate Financial ROI Calculation",
                "desc": "Calculate annual profit metrics and revenue multiplier with formula evaluation.",
                "fault": "division_by_zero"
            },
            {
                "title": "Legacy Service Query with Failover",
                "desc": "Query remote service endpoint, validate schema, and persist summary artifact.",
                "fault": "service_unavailable"
            },
            {
                "title": "Autonomous AI Agent Research Synthesis",
                "desc": "Search latest autonomous agent self-healing papers, summarize findings, and output clean report.",
                "fault": None
            }
        ]

        for s in demo_scenarios:
            print(f"Creating & executing demo task: '{s['title']}'...")
            task_id = str(uuid.uuid4())
            planned_steps = await task_planner.plan_task(s["desc"], force_fault=s["fault"])
            prediction = failure_predictor.predict_task_risk(s["desc"], planned_steps)

            task_rec = TaskRecord(
                id=task_id,
                title=s["title"],
                description=s["desc"],
                status="PENDING",
                total_steps=len(planned_steps),
                predicted_risk_level=prediction["predicted_risk_level"]
            )
            db.add(task_rec)
            db.commit()

            steps_data = [
                {
                    "id": str(uuid.uuid4()),
                    "step_index": step["step_index"],
                    "step_name": step["step_name"],
                    "tool_name": step["tool_name"],
                    "tool_arguments": step.get("tool_arguments", {}),
                    "dependencies": step.get("dependencies", []),
                    "status": "PENDING",
                    "is_critical": step.get("is_critical", False),
                    "is_replacement": False,
                    "replaces_step_id": None
                }
                for step in planned_steps
            ]

            await task_executor.execute_task(
                task_id=task_id,
                task_title=s["title"],
                task_description=s["desc"],
                steps=steps_data,
                prediction_info=prediction,
                db=db
            )

        print("Demo tasks seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_tasks())
