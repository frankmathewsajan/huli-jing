from __future__ import annotations
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from pydantic import ValidationError
from google.genai import types

from llm.schema import DailyPlan
from llm.prompts.daily_plan import plan_the_day
from llm.services.gemini_client import get_gemini_client
from llm.services.prompt_cache import get_or_create_prompt_cache
from llm.services.save_daily_plan_to_db import save_daily_plan_to_db

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


def format_feedback_from_tasks(tasks):
    if not tasks:
        return "No feedback available yet."
    return "\n".join(
        f"- {t.task_name} ({'✅ Completed' if t.completed else '❌ Missed'}, "
        f"Rating: {t.rating or 'No rating'}/5)"
        f"{' — Feedback: ' + t.feedback if t.feedback else ''}"
        for t in tasks
    )


def generate_daily_plan(user: AbstractUser, reschedule: bool = False) -> JsonResponse:
    """Generate or reuse a daily plan; optionally reschedule if override content exists."""
    client = get_gemini_client()
    today = datetime.now().date()

    # 🔹 Cached summary prompt
    cached_summary = user.prompts.filter(type="summary").order_by("-created_at").first()
    
    # 🧠 If reschedule requested, check override prompt
    override_prompt = None
    if reschedule:
        override_prompt = user.prompts.filter(type="override").order_by("-created_at").first()
        if override_prompt and not override_prompt.text.strip() and cached_summary and cached_summary.llm_response:
            # No new override content → return cached plan
            try:
                return JsonResponse(DailyPlan.model_validate(cached_summary.llm_response).model_dump(), safe=False)
            except Exception as e:
                print(f"⚠️ Failed to load cached summary: {e}")

    # 🔹 Return cached summary if exists & no reschedule
    if cached_summary and not reschedule:
        try:
            return JsonResponse(DailyPlan.model_validate(cached_summary.llm_response).model_dump(), safe=False)
        except Exception as e:
            print(f"⚠️ Failed to load cached summary: {e}")

    # 🔹 Latest user data
    latest_goal = user.goals.order_by("-updated_at").first()
    goals = latest_goal.llm_response if latest_goal else []

    latest_commitment = user.commitments.order_by("-updated_at").first()
    commitments = latest_commitment.llm_response if latest_commitment else []

    patterns = list(user.userpattern_set.order_by("-created_at").values_list("pattern_text", flat=True))

    # 🔹 Gather yesterday’s feedback
    yesterday_schedule = user.daily_schedules.filter(date=today - timedelta(days=1)).prefetch_related("tasks").first()
    feedback = format_feedback_from_tasks(yesterday_schedule.tasks.all()) if yesterday_schedule else "No previous schedule found."

    # 🔹 Include override content in prompt if exists
    override_content = override_prompt.text if override_prompt else None

    # 🔹 Build LLM prompt
    prompt_text = plan_the_day(goals, commitments, patterns, feedback, target_date=datetime.now(), override=override_content)

    # 🔹 Use cache layer
    cached, created = get_or_create_prompt_cache(user, prompt_text, "summary", ignore_time=True)
    if not created and cached.llm_response:
        plan = DailyPlan.model_validate(cached.llm_response)
        save_daily_plan_to_db(user, plan)
        return JsonResponse(plan.model_dump(), safe=False)

    # 🔹 Query Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyPlan,
        ),
    )

    try:
        daily_plan = DailyPlan.model_validate(json.loads(response.text))
    except (json.JSONDecodeError, ValidationError) as e:
        raise Exception(f"LLM returned invalid response: {e}")

    # 🔹 Cache & save
    cached.llm_response = daily_plan.model_dump()
    cached.save(update_fields=["llm_response"])
    save_daily_plan_to_db(user, daily_plan)

    return JsonResponse(daily_plan.model_dump(), safe=False)
