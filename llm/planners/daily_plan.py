from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from pydantic import ValidationError
from google import genai
from google.genai import types

from llm.schema import DailyPlan
from llm.services.prompt_cache import get_or_create_prompt_cache
from llm.prompts.daily_plan import build_daily_planner_prompt
from core.models import Prompt
from llm.services.save_daily_plan_to_db import save_daily_plan_to_db

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


from llm.services.gemini_client import get_gemini_client


# ====================================================================
# Daily Plan Generation
# ====================================================================


def generate_daily_plan_for_user(
    user: AbstractUser, target_date: datetime | None = None
) -> DailyPlan:
    client = get_gemini_client()
    if target_date is None:
        target_date = datetime.now().date()

    # Fetch user's goal and commitment prompts
    goal_prompts = Prompt.objects.filter(user=user, type="goal").order_by(
        "-created_at"
    )[:10]
    commitment_prompts = Prompt.objects.filter(user=user, type="commitment").order_by(
        "-created_at"
    )[:10]

    goals_list = [
        {"text": p.text, "parsed_data": p.llm_response or {}} for p in goal_prompts
    ]
    commitments_list = [
        {"text": p.text, "parsed_data": p.llm_response or {}}
        for p in commitment_prompts
    ]

    # 🧠 Import system prompt from module
    prompt_text = build_daily_planner_prompt(goals_list, commitments_list, target_date)

    # 🔹 Use cache layer
    cached_prompt, created = get_or_create_prompt_cache(
        user=user,
        prompt_text=prompt_text,
        prompt_type="summary",
    )

    if not created and cached_prompt.llm_response:
        return DailyPlan.model_validate(cached_prompt.llm_response)

    # 🔹 Query LLM
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyPlan,
        ),
    )

    try:
        response_json = json.loads(response.text)
        daily_plan = DailyPlan.model_validate(response_json)
    except (json.JSONDecodeError, ValidationError) as e:
        raise Exception(f"LLM returned invalid response: {e}")

    cached_prompt.llm_response = daily_plan.model_dump()
    cached_prompt.save(update_fields=["llm_response"])
    save_daily_plan_to_db(daily_plan)
    
    return daily_plan
