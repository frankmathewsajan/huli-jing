import json
from datetime import date


def format_json(data) -> str:
    """Safely pretty-print JSON data for embedding in prompt text."""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return str(data)


def render_date_info(target_date: date) -> str:
    """Format date + weekday in human-readable format."""
    return f"{target_date.isoformat()} ({target_date.strftime('%A')})"



