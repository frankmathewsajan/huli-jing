from pydantic import BaseModel, Field
from typing import List, Optional

# ====================================================================
# Pydantic Models for Structured Output (Daily Plan)
# ====================================================================
# Keep in sync with llm/models.py

class DailyTask(BaseModel):
    task_name: str
    description: str
    estimated_duration_minutes: int = Field(..., ge=0)
    priority: str
    related_goal: Optional[str] = None
    suggested_time: Optional[str] = None
    is_flexible: bool = True


class DailyPlan(BaseModel):
    # Core schedule fields
    date: str
    day_of_week: str
    tasks: List[DailyTask] = []

    # Summary fields
    total_committed_hours: float = 0.0
    total_available_hours: float = 0.0
    notes: str = ""

    # Adaptive fields from LLM feedback loop
    updated_commitments: List[str] = []
    updated_goals: List[str] = []
    user_behaviour_patterns: List[str] = []
