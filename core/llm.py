from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from pydantic import BaseModel, Field, ValidationError
from google import genai
from google.genai import types

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from .models import Prompt

User = get_user_model()


# ====================================================================
# Pydantic Models for Structured Output (Daily Plan)
# ====================================================================

class DailyTask(BaseModel):
    task_name: str
    description: str
    estimated_duration_minutes: int
    priority: str
    related_goal: str | None = None
    suggested_time: str | None = None
    is_flexible: bool = True


class DailyPlan(BaseModel):
    date: str
    day_of_week: str
    tasks: list[DailyTask] = []
    total_committed_hours: float = 0.0
    total_available_hours: float = 0.0
    notes: str = ""


# ====================================================================
# Gemini Client Setup
# ====================================================================

def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)


# ====================================================================
# Daily Plan Generation with Caching
# ====================================================================

def generate_daily_plan_for_user(user: AbstractUser, target_date: datetime | None = None) -> DailyPlan:
    """
    Generate a daily plan for the given user and date.
    If no date is provided, defaults to today.
    Uses cached LLM response if available.
    """
    client = get_gemini_client()

    if target_date is None:
        target_date = datetime.now().date()

    day_name = target_date.strftime("%A")

    # Fetch user's goal and commitment prompts
    goal_prompts = Prompt.objects.filter(user=user, type="goal").order_by('-created_at')[:10]
    commitment_prompts = Prompt.objects.filter(user=user, type="commitment").order_by('-created_at')[:10]

    goals_list = [{"text": p.text, "parsed_data": p.llm_response or {}} for p in goal_prompts]
    commitments_list = [{"text": p.text, "parsed_data": p.llm_response or {}} for p in commitment_prompts]

    # Build prompt text
    prompt_text = f"""
You are an AI planner for neurodivergent users.
Create a realistic, compassionate, achievable plan for a single day.

Date: {target_date.isoformat()} ({day_name})

USER'S GOALS:
{json.dumps(goals_list, indent=2) if goals_list else "No goals provided yet."}

USER'S COMMITMENTS:
{json.dumps(commitments_list, indent=2) if commitments_list else "No commitments provided yet."}

Requirements:
- Respect fixed commitments
- Break goals into daily tasks with estimated durations
- Prioritize high-priority goals
- Suggest flexible task times where possible
- Include rest and transition periods
- Provide total committed vs available hours
- Give clear, neurodivergent-friendly instructions
"""

    # Compute hash for caching
    hash_key = hashlib.sha256(f"daily::{target_date.isoformat()}::{prompt_text}".encode("utf-8")).hexdigest()

    # Check cache
    cached_prompt = Prompt.objects.filter(user=user, hash=hash_key, type="summary").first()
    if cached_prompt:
        cached_prompt.used_count += 1
        cached_prompt.save()
        return DailyPlan.model_validate(cached_prompt.llm_response)

    # Call Gemini if not cached
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyPlan,
        )
    )

    try:
        response_json = json.loads(response.text)
        daily_plan = DailyPlan.model_validate(response_json)
    except (json.JSONDecodeError, ValidationError) as e:
        raise Exception(f"LLM returned invalid response: {e}")

    # Save to cache
    Prompt.objects.create(
        user=user,
        type="summary",
        text=prompt_text,
        llm_response=daily_plan.model_dump(),
        hash=hash_key
    )

    return daily_plan
