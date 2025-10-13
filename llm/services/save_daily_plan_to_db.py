from llm.schema import DailyPlan
from llm.models import DailySchedule, Task
from datetime import datetime
from typing import TYPE_CHECKING
from django.db import transaction

def save_daily_plan_to_db(daily_plan: DailyPlan) -> DailySchedule:
    """
    Convert a DailyPlan (Pydantic model) into Django models:
    - DailySchedule
    - Task
    Also store adaptive fields like updated_goals, updated_commitments, and user_behaviour_patterns.
    """

    schedule_date = datetime.fromisoformat(daily_plan.date).date()

    # Using transaction.atomic for safer writes
    with transaction.atomic():
        schedule, _ = DailySchedule.objects.get_or_create(
            date=schedule_date,
            defaults={
                "day_of_week": daily_plan.day_of_week,
                "total_committed_hours": daily_plan.total_committed_hours,
                "total_available_hours": daily_plan.total_available_hours,
                "notes": daily_plan.notes,
            },
        )

        # Clear old tasks (if regenerating)
        schedule.tasks.clear()

        for t in daily_plan.tasks:
            suggested_time = None
            if t.suggested_time:
                # Handle both 12-hour and 24-hour formats safely
                for fmt in ("%I:%M %p", "%H:%M"):
                    try:
                        suggested_time = datetime.strptime(t.suggested_time, fmt).time()
                        break
                    except ValueError:
                        continue

            task, _ = Task.objects.get_or_create(
                task_name=t.task_name,
                defaults={
                    "description": t.description,
                    "estimated_duration_minutes": t.estimated_duration_minutes,
                    "priority": t.priority,
                    "related_goal": t.related_goal,
                    "is_flexible": t.is_flexible,
                    "suggested_time": suggested_time,
                },
            )
            schedule.tasks.add(task)

        # Save adaptive metadata if model has fields for them
        if hasattr(schedule, "updated_commitments"):
            schedule.updated_commitments = daily_plan.updated_commitments
        if hasattr(schedule, "updated_goals"):
            schedule.updated_goals = daily_plan.updated_goals
        if hasattr(schedule, "user_behaviour_patterns"):
            schedule.user_behaviour_patterns = daily_plan.user_behaviour_patterns

        schedule.save()

    return schedule
