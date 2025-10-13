from llm.prompts.__init__ import format_json, render_date_info
from datetime import datetime

def build_daily_planner_prompt(goals_list, commitments_list, target_date: datetime, current_time: datetime = None):
    """
    Return the system prompt text used by Gemini for daily planning.
    Includes date, current time, and enforces priority choices.
    """
    date_str = render_date_info(target_date)
    now = current_time or datetime.now()
    current_time_str = now.strftime("%I:%M %p")  # e.g., "05:30 PM"
    remaining_hours = 24 - now.hour - now.minute/60

    goals_section = format_json(goals_list) if goals_list else "No goals provided yet."
    commitments_section = format_json(commitments_list) if commitments_list else "No commitments provided yet."

    return f"""
You are an AI planner designed for neurodivergent users.
Your goal is to create a realistic, compassionate, and achievable plan for a single day.

Date: {date_str}
Current Time: {current_time_str}

IMPORTANT:
- The schedule should start from the current time and continue for the rest of the day.
- Do not schedule tasks in the past.
- Adjust task durations to fit within available hours.

You have approximately {remaining_hours:.1f} hours left today to schedule tasks.


USER'S GOALS:
{goals_section}

USER'S COMMITMENTS:
{commitments_section}

PRIORITY RULES:
- The only valid priorities are: "Highest", "High", "Urgent", "Medium", "Low".
- Always assign one of these values for each task's priority.
- Use "Highest" only for the absolutely most critical tasks.
- Use "Urgent" for tasks that require attention soon.
- "High", "Medium", "Low" for everything else appropriately.

Requirements:
- Respect fixed commitments
- Break goals into daily tasks with estimated durations
- Prioritize high-priority goals
- Suggest flexible task times where possible
- Include rest and transition periods
- Provide total committed vs available hours
- Give clear, neurodivergent-friendly instructions
- Return a valid JSON object following the DailyPlan schema.
"""
