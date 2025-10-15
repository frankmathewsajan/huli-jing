from llm.services.save_daily_plan_to_db import save_daily_plan_to_db
from users.models import UserPattern, Goal, Commitment
from llm.schema import DailyPlan
import hashlib

def save_onboarding(user, initial_plan: DailyPlan):
    """Save onboarding outputs: goals, commitments, patterns, and first day's schedule."""

    if not isinstance(initial_plan, DailyPlan):
        initial_plan = DailyPlan.model_validate(initial_plan)

    # Save refined goals
    if initial_plan.updated_goals:
        Goal.objects.update_or_create(
            user=user,
            defaults={"llm_response": {"goals": initial_plan.updated_goals, "source": "onboarding_refined"}}
        )

    # Save refined commitments
    if initial_plan.updated_commitments:
        Commitment.objects.update_or_create(
            user=user,
            defaults={"llm_response": {"commitments": initial_plan.updated_commitments, "source": "onboarding_refined"}}
        )

    # Save user behavior patterns (separate model, no hash or JSON)
    if initial_plan.user_behaviour_patterns:
        UserPattern.objects.create(
            user=user,
            pattern_text="\n".join(initial_plan.user_behaviour_patterns),
            date=initial_plan.date if hasattr(initial_plan, "date") else None
        )

    # Save first day schedule
    save_daily_plan_to_db(user, initial_plan)
