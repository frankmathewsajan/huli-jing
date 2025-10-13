# Huli — AI Coding Agent Instructions

## Project Overview
Huli is a Django REST API backend for an AI-driven daily planning app designed for neurodivergent users. The core innovation is the **Huli-Jing Engine**: an LLM-powered scheduler that converts natural language goals + fixed commitments into realistic hour-by-hour plans.

**Tech Stack:** Django 5.2+, DRF, SimpleJWT, Google Gemini 2.5, Pydantic, UV package manager

## Architecture Pattern: LLM-First Flow

The system uses a **prompt → LLM → structured output → database** pattern:

```
User Input (natural language) → Prompt Cache → Gemini API → Pydantic Validation → Django Models
```

Key files:
- `llm/prompts/daily_plan.py` — prompt engineering logic
- `llm/schema.py` — Pydantic schemas for LLM structured output
- `llm/planners/daily_plan.py` — orchestrates LLM calls
- `llm/services/prompt_cache.py` — SHA-256 based prompt caching to avoid redundant API calls

## Critical Conventions

### 1. Pydantic-First, Models Second
**Always define Pydantic schemas first** in `llm/schema.py`, then mirror them in Django models. The LLM returns JSON validated by Pydantic before touching the database.

Example: `DailyPlan` (Pydantic) → `DailySchedule` (Django model in `llm/models.py`)

### 2. Prompt Caching Strategy
All LLM prompts are cached in `core.Prompt` using a deterministic hash (`sha256(scope + type + text)`). Check `llm/services/prompt_cache.py` for `get_or_create_prompt_cache()` — this pattern prevents duplicate API calls for identical inputs.

### 3. Priority System
Task priorities MUST use one of: `"Highest"`, `"High"`, `"Urgent"`, `"Medium"`, `"Low"`. This is enforced in:
- Pydantic: `llm/schema.py` (DailyTask.priority)
- Django: `llm/models.py` (Task.PRIORITY_CHOICES)
- Prompts: `llm/prompts/daily_plan.py` (explicitly documented)

### 4. Custom User Model
The project uses `users.User` (extends `AbstractUser`) with `timezone` field. Always reference via `settings.AUTH_USER_MODEL` or `get_user_model()`.

### 5. URL Namespace Pattern
All API routes are namespaced:
- `/api/users/` → JWT auth endpoints (register, login, refresh, blacklist)
- `/api/llm/` → LLM-powered features (daily-plan)
- `/api/core/` → (future: goals/commitments CRUD)

No trailing slashes enforced via `APPEND_SLASH = False` in settings.

## Developer Workflows

### Running the Server
```powershell
uv run python manage.py runserver
```

### Running Tests
```powershell
uv run python manage.py test
```
See `users/tests.py` for comprehensive JWT testing patterns.

### Migrations
```powershell
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Environment Setup
Required: `GEMINI_API_KEY` environment variable for LLM access (see `llm/services/gemini_client.py`)

## LLM Integration Patterns

### Adding New LLM-Powered Features
1. Define Pydantic schema in `llm/schema.py`
2. Create prompt builder in `llm/prompts/`
3. Add planner function in `llm/planners/`
4. Use `get_or_create_prompt_cache()` for caching
5. Call Gemini with `response_schema` parameter:
   ```python
   response = client.models.generate_content(
       model="gemini-2.5-flash",
       contents=prompt_text,
       config=types.GenerateContentConfig(
           response_mime_type="application/json",
           response_schema=YourPydanticModel,
       ),
   )
   ```

### Time-Aware Scheduling
Prompts include current time + remaining hours calculation (see `llm/prompts/daily_plan.py`). The planner never schedules tasks in the past.

## Data Flow Example: Daily Plan Generation

1. User hits `GET /api/llm/daily-plan/` (authenticated)
2. `DailyPlanView` calls `generate_daily_plan_for_user(request.user)`
3. Function fetches last 10 goals + commitments from `core.Prompt`
4. Builds time-aware prompt via `build_daily_planner_prompt()`
5. Checks prompt cache; if hit, returns cached plan
6. Else: calls Gemini API with `DailyPlan` schema
7. Validates response via Pydantic
8. Saves to cache + persists to `llm.DailySchedule`
9. Returns JSON to client

## Common Patterns

### Error Handling
View layer wraps LLM calls in try/except, returning 500 with error message. See `llm/views.py`:
```python
try:
    plan = generate_daily_plan_for_user(request.user)
    return Response(plan.model_dump(), status=status.HTTP_200_OK)
except Exception as e:
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### JSONField Usage
Both `core.Prompt.llm_response` and `llm.DailySchedule.pattern` use `models.JSONField` for flexible structured data storage.

### Many-to-Many Cleanup
`DailySchedule.delete()` cascades to associated `Task` objects (see `llm/models.py`).

## Testing Patterns
Follow `users/tests.py` examples:
- Use `APITestCase` for integration tests
- Create test users in `setUp()`
- Test happy paths + edge cases (missing fields, invalid tokens, duplicate operations)
- Name tests descriptively: `test_<action>_<scenario>`
