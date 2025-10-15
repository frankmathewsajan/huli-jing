from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from pydantic import ValidationError
from google import genai
from google.genai import types

from llm.schema import DailyPlan
from llm.services.prompt_cache import get_or_create_prompt_cache
from llm.prompts.onboarding import onboard_user
from core.models import Prompt
from llm.services.save_onboarding import save_onboarding
from django.http import JsonResponse
if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


from llm.services.gemini_client import get_gemini_client


# ====================================================================
# Daily Plan Generation
# ====================================================================


def generate_onboarding_plan(user: AbstractUser) -> JsonResponse:
    client = get_gemini_client()

    goal_prompt = Prompt.objects.filter(user=user, type="goal").first()
    commitment_prompt = Prompt.objects.filter(user=user, type="commitment").first()

    goal_data = {
        "text": goal_prompt.text,
        "parsed_data": goal_prompt.llm_response or {}
    } if goal_prompt else None

    commitment_data = {
        "text": commitment_prompt.text,
        "parsed_data": commitment_prompt.llm_response or {}
    } if commitment_prompt else None

    
    prompt_text = onboard_user(goal_data, commitment_data)
    
    # 🔹 Use cache layer
    cached_prompt, created = get_or_create_prompt_cache(
        user=user,
        prompt_text=prompt_text,
        prompt_type="onboarding",
        ignore_time=True, 
    )

    if not created and cached_prompt.llm_response:
        save_onboarding(user, cached_prompt.llm_response)
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
        initial_plan = DailyPlan.model_validate(response_json)
    except (json.JSONDecodeError, ValidationError) as e:
        raise Exception(f"LLM returned invalid response: {e}")

    cached_prompt.llm_response = initial_plan.model_dump()
    cached_prompt.save(update_fields=["llm_response"])
    save_onboarding(user, initial_plan)
    
    return initial_plan
