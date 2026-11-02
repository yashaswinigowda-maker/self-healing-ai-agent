import json
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db_models import MemoryRecord
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages episodic memory of past successful and failed task executions and recoveries."""

    def __init__(self):
        self.memory_file = Path(settings.EPISODIC_MEMORY_FILE)
        self._ensure_memory_file()

    def _ensure_memory_file(self):
        if not self.memory_file.exists():
            # Seed with baseline knowledge of common patterns
            initial_memories = [
                {
                    "id": str(uuid.uuid4()),
                    "memory_type": "SUCCESS",
                    "task_description": "Calculate quarterly profit and ROI",
                    "tool_name": "calculator",
                    "error_category": "PARAMETER_ERROR",
                    "error_message": "Division by zero in mathematical expression.",
                    "diagnosis": "Formula attempted division by zero when calculating growth metric.",
                    "recovery_strategy": "CHANGE_ARGUMENTS",
                    "recovery_action": {
                        "action_type": "sanitize_parameters",
                        "corrected_arguments": {"expression": "1000 / 1"}
                    },
                    "outcome": "SUCCESS",
                    "confidence_score": 0.95,
                    "frequency": 3,
                    "tags": ["math", "division_by_zero", "sanitize"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "memory_type": "FAILURE",
                    "task_description": "Calculate quarterly profit and ROI",
                    "tool_name": "calculator",
                    "error_category": "PARAMETER_ERROR",
                    "error_message": "Division by zero in mathematical expression.",
                    "diagnosis": "Naive retry without modifying zero divisor.",
                    "recovery_strategy": "RETRY",
                    "recovery_action": {
                        "action_type": "immediate_retry"
                    },
                    "outcome": "FAILURE",
                    "confidence_score": 0.1,
                    "frequency": 2,
                    "tags": ["math", "failed_retry", "loop"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "memory_type": "SUCCESS",
                    "task_description": "Fetch live weather report for Seattle",
                    "tool_name": "http_client_mock",
                    "error_category": "TRANSIENT_NETWORK",
                    "error_message": "HTTP Connection Timeout after 15000ms",
                    "diagnosis": "Transient latency spike on remote gateway.",
                    "recovery_strategy": "RETRY",
                    "recovery_action": {
                        "action_type": "exponential_backoff_retry",
                        "retry_delay_seconds": 1
                    },
                    "outcome": "SUCCESS",
                    "confidence_score": 0.92,
                    "frequency": 4,
                    "tags": ["network", "timeout", "retry_success"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "memory_type": "SUCCESS",
                    "task_description": "Query unavailable legacy endpoint",
                    "tool_name": "http_client_mock",
                    "error_category": "RESOURCE_UNAVAILABLE",
                    "error_message": "HTTP 503 Service Unavailable: Remote endpoint is unreachable.",
                    "diagnosis": "Remote service permanently decommissioned or unreachable.",
                    "recovery_strategy": "REPLAN",
                    "recovery_action": {
                        "action_type": "substitute_subtasks",
                        "replan_notes": "Switch to web search mock tool"
                    },
                    "outcome": "SUCCESS",
                    "confidence_score": 0.89,
                    "frequency": 2,
                    "tags": ["replan", "fallback_tool"],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            self.memory_file.write_text(json.dumps(initial_memories, indent=2), encoding="utf-8")

    def _read_memories_file(self) -> List[Dict[str, Any]]:
        try:
            if self.memory_file.exists():
                return json.loads(self.memory_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Error reading episodic memory file: {e}")
        return []

    def _write_memories_file(self, memories: List[Dict[str, Any]]):
        try:
            self.memory_file.write_text(json.dumps(memories, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Error writing episodic memory file: {e}")

    def _tokenize(self, text: str) -> set:
        if not text:
            return set()
        words = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        stopwords = {"the", "and", "for", "with", "from", "that", "this", "after", "before", "step", "task"}
        return {w for w in words if w not in stopwords}

    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        set1 = self._tokenize(s1)
        set2 = self._tokenize(s2)
        if not set1 or not set2:
            return 0.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def calculate_similarity(
        self,
        current_task: str,
        current_tool: str,
        current_category: str,
        current_error: str,
        memory_item: Dict[str, Any]
    ) -> float:
        """Transparent, multi-factor similarity score between 0.0 and 1.0."""
        # 1. Tool match: 0.30 weight
        tool_score = 1.0 if current_tool.lower() == memory_item.get("tool_name", "").lower() else 0.0
        
        # 2. Error category match: 0.25 weight
        cat_score = 1.0 if current_category.upper() == memory_item.get("error_category", "").upper() else 0.0
        
        # 3. Error message textual similarity: 0.30 weight
        err_sim = self._jaccard_similarity(current_error, memory_item.get("error_message", ""))
        
        # 4. Task description similarity: 0.15 weight
        task_sim = self._jaccard_similarity(current_task, memory_item.get("task_description", ""))
        
        total_similarity = (0.30 * tool_score) + (0.25 * cat_score) + (0.30 * err_sim) + (0.15 * task_sim)
        return round(total_similarity, 3)

    def retrieve_relevant_memories(
        self,
        task_description: str,
        tool_name: str,
        error_category: str,
        error_message: str,
        limit: int = 5,
        threshold: float = 0.35
    ) -> Dict[str, Any]:
        """Find past experiences matching the failure pattern and rank them."""
        memories = self._read_memories_file()
        scored_memories = []

        for mem in memories:
            sim = self.calculate_similarity(task_description, tool_name, error_category, error_message, mem)
            if sim >= threshold:
                mem_copy = dict(mem)
                mem_copy["similarity_score"] = sim
                scored_memories.append(mem_copy)

        # Sort by similarity descending
        scored_memories.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_memories = scored_memories[:limit]

        # Separate successful and failed past recovery experiences
        successful = [m for m in top_memories if m.get("outcome") == "SUCCESS"]
        failed = [m for m in top_memories if m.get("outcome") == "FAILURE"]

        # Strategies that failed in past experiences for this specific pattern
        avoid_strategies = list({m.get("recovery_strategy") for m in failed if m.get("recovery_strategy")})

        return {
            "all_relevant": top_memories,
            "successful_experiences": successful,
            "failed_experiences": failed,
            "strategies_to_avoid": avoid_strategies,
            "highest_similarity": top_memories[0]["similarity_score"] if top_memories else 0.0
        }

    def record_experience(
        self,
        task_description: str,
        tool_name: str,
        error_category: Optional[str],
        error_message: Optional[str],
        diagnosis: Optional[str],
        recovery_strategy: Optional[str],
        recovery_action: Dict[str, Any],
        outcome: str,
        confidence_score: float,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Record task execution or recovery experience into episodic memory."""
        memories = self._read_memories_file()
        
        # Check if identical pattern already exists to increment frequency
        matched_mem = None
        for mem in memories:
            if (
                mem.get("tool_name") == tool_name and
                mem.get("error_category") == error_category and
                mem.get("recovery_strategy") == recovery_strategy and
                mem.get("outcome") == outcome
            ):
                matched_mem = mem
                break

        if matched_mem:
            matched_mem["frequency"] = matched_mem.get("frequency", 1) + 1
            matched_mem["confidence_score"] = round((matched_mem.get("confidence_score", 0.5) + confidence_score) / 2, 2)
            matched_mem["diagnosis"] = diagnosis or matched_mem.get("diagnosis")
            item = matched_mem
        else:
            item = {
                "id": str(uuid.uuid4()),
                "memory_type": "SUCCESS" if outcome == "SUCCESS" else "FAILURE",
                "task_description": task_description,
                "tool_name": tool_name,
                "error_category": error_category,
                "error_message": error_message,
                "diagnosis": diagnosis,
                "recovery_strategy": recovery_strategy,
                "recovery_action": recovery_action or {},
                "outcome": outcome,
                "confidence_score": round(confidence_score, 2),
                "frequency": 1,
                "tags": [tool_name, error_category or "general", outcome.lower()],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            memories.insert(0, item)

        self._write_memories_file(memories)

        # Also persist to SQLite if DB session is supplied
        if db:
            try:
                db_mem = MemoryRecord(
                    id=item["id"],
                    memory_type=item["memory_type"],
                    task_description=item["task_description"],
                    tool_name=item["tool_name"],
                    error_category=item.get("error_category"),
                    error_message=item.get("error_message"),
                    diagnosis=item.get("diagnosis"),
                    recovery_strategy=item.get("recovery_strategy"),
                    recovery_action=item.get("recovery_action", {}),
                    outcome=item["outcome"],
                    confidence_score=item["confidence_score"],
                    frequency=item["frequency"],
                    tags=item.get("tags", [])
                )
                db.merge(db_mem)
                db.commit()
            except Exception as e:
                logger.error(f"Error saving memory to database: {e}")
                db.rollback()

        return item

    def get_all_memories(self, memory_type: Optional[str] = None, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        memories = self._read_memories_file()
        if memory_type:
            memories = [m for m in memories if m.get("memory_type") == memory_type.upper()]
        if search_query:
            q = search_query.lower()
            memories = [
                m for m in memories
                if q in m.get("task_description", "").lower()
                or q in m.get("tool_name", "").lower()
                or q in m.get("error_message", "").lower()
                or q in m.get("recovery_strategy", "").lower()
            ]
        return memories

memory_manager = MemoryManager()
