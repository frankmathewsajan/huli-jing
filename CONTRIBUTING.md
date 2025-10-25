# 🤝 Contributing to Huli

Thank you for your interest in contributing to **Huli**! This project aims to help neurodivergent individuals manage their daily tasks with compassion and intelligence. Every contribution — big or small — makes a difference.

---

## 📋 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
3. [Frontend Development Guide](#-frontend-development-guide)
4. [Backend Development Guide](#-backend-development-guide)
5. [Development Setup](#-development-setup)
6. [Testing Guidelines](#-testing-guidelines)
7. [Submitting Changes](#-submitting-changes)
8. [Style Guidelines](#-style-guidelines)

---

## 📜 Code of Conduct

This project is built for and by the neurodivergent community. We expect all contributors to:
- **Be kind and patient** — everyone has different working styles
- **Be respectful** — disagreements are fine, personal attacks are not
- **Be inclusive** — welcome contributions from all skill levels
- **Assume good intent** — we're all here to help

---

## 🛠️ How Can I Contribute?

### 🎨 Frontend Development (HIGHEST PRIORITY!)

**The backend is complete, but we need a user interface!** Here are three paths:

#### Option 1: React Web App (Recommended)
Build a modern, responsive web application using React.

**Why React?**
- Large community and ecosystem
- Great for complex, interactive UIs
- Works seamlessly with our REST API
- Easy to deploy (Vercel, Netlify, etc.)

**Tech Stack Suggestions:**
- **Framework:** React 18+ with TypeScript
- **State Management:** Zustand or React Query
- **Styling:** Tailwind CSS or Material-UI
- **Routing:** React Router v6
- **API Client:** Axios or Fetch API
- **Authentication:** Store JWT tokens in localStorage/sessionStorage

**Key Features to Implement:**
1. ✅ User registration & login
2. ✅ Dashboard showing today's plan
3. ✅ Task list with checkboxes and ratings
4. ✅ Goal & commitment management (future)
5. ✅ Onboarding questionnaire
6. ✅ Settings (timezone, preferences)

**Getting Started:**
```bash
npx create-react-app huli-frontend --template typescript
cd huli-frontend
npm install axios react-router-dom
```

---

#### Option 2: React Native Mobile App
Build a native mobile app for iOS and Android.

**Why React Native?**
- Perfect for neurodivergent users who need on-the-go nudges
- Push notifications for task reminders
- Native calendar integration
- Same codebase for iOS and Android

**Tech Stack Suggestions:**
- **Framework:** React Native with TypeScript
- **Navigation:** React Navigation
- **State:** Zustand or Redux Toolkit
- **API Client:** Axios
- **UI Components:** React Native Paper or NativeBase

**Key Features to Implement:**
1. ✅ All features from web app
2. ✅ Push notifications for task reminders
3. ✅ Calendar integration
4. ✅ Dark mode (important for neurodivergent users!)
5. ✅ Offline mode with sync

**Getting Started:**
```bash
npx react-native init HuliFrontend --template react-native-template-typescript
cd HuliFrontend
npm install axios @react-navigation/native
```

---

#### Option 3: Django Templates (Simple MVP)
Build a server-rendered UI using Django's built-in templating.

**Why Django Templates?**
- Fastest time to MVP
- No separate deployment needed
- Great for prototyping
- Easier for backend-focused developers

**Tech Stack:**
- **Templates:** Django's built-in templating engine
- **Styling:** Bootstrap 5 or Tailwind CSS
- **JavaScript:** Alpine.js or Vanilla JS for interactivity

**Getting Started:**
1. Create a new Django app: `python manage.py startapp frontend`
2. Add templates in `frontend/templates/`
3. Use `django-crispy-forms` for better form rendering
4. Serve static assets with `WhiteNoise`

**Trade-offs:**
- ✅ Faster initial development
- ✅ SEO-friendly by default
- ❌ Less interactive than SPA
- ❌ Harder to build mobile app later

---

### 🐛 Bug Reports & Feature Requests

Found a bug or have an idea? **Open an issue!**

**For Bug Reports:**
1. Clear, descriptive title
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots (if applicable)
5. Environment (OS, Python version, browser)

**For Feature Requests:**
1. Problem statement (what pain point does this solve?)
2. Proposed solution
3. Alternative solutions considered
4. Why this helps neurodivergent users

---

### 📖 Documentation

Help improve our docs:
- Fix typos or unclear explanations
- Add examples or diagrams
- Translate to other languages
- Write tutorials or guides

---

### 🧪 Testing & QA

- Write unit tests for new features
- Test edge cases (timezone handling, long goal lists, etc.)
- Perform accessibility audits (WCAG compliance)
- Test on different devices/browsers

---

## 🖥️ Backend Development Guide

### Current Architecture

The backend follows a **Pydantic-first, LLM-powered** pattern:

```
User Request → Django View → LLM Planner → Gemini API → Pydantic Validation → Django Models → JSON Response
```

### Adding New Features

#### 1. Adding a New LLM-Powered Endpoint

**Example: Weekly Planner**

1. **Define Pydantic Schema** (`llm/schema.py`):
```python
from pydantic import BaseModel, Field

class WeeklyTask(BaseModel):
    day: str = Field(description="Day of the week")
    time: str = Field(description="HH:MM format")
    task: str = Field(description="Task description")
    priority: str = Field(description="Priority level")

class WeeklyPlan(BaseModel):
    week_start: str
    week_end: str
    tasks: list[WeeklyTask]
```

2. **Create Prompt Builder** (`llm/prompts/weekly_plan.py`):
```python
def build_weekly_planner_prompt(user, goals, commitments):
    return f"""
    Generate a weekly plan for {user.username}.
    Goals: {goals}
    Commitments: {commitments}
    
    Create a balanced schedule across 7 days.
    """
```

3. **Add Planner Function** (`llm/planners/weekly_plan.py`):
```python
from llm.services.gemini_client import client
from llm.services.prompt_cache import get_or_create_prompt_cache
from llm.schema import WeeklyPlan

def generate_weekly_plan(user):
    prompt = build_weekly_planner_prompt(user, ...)
    
    # Check cache first
    cached = get_or_create_prompt_cache(
        scope="weekly_planning",
        prompt_type="weekly_plan",
        text=prompt
    )
    
    if cached.llm_response:
        return WeeklyPlan(**cached.llm_response)
    
    # Call Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WeeklyPlan,
        ),
    )
    
    # Save to cache
    plan = WeeklyPlan(**response.text)
    cached.llm_response = plan.model_dump()
    cached.save()
    
    return plan
```

4. **Create View** (`llm/views.py`):
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class WeeklyPlanView(APIView):
    def get(self, request):
        try:
            plan = generate_weekly_plan(request.user)
            return Response(plan.model_dump(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

5. **Add URL** (`llm/urls.py`):
```python
urlpatterns = [
    path('weekly-plan', WeeklyPlanView.as_view(), name='weekly-plan'),
]
```

---

#### 2. Adding CRUD Endpoints (Non-LLM)

**Example: Goals Management**

1. **Model** (already exists in `users/models.py`):
```python
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

2. **Serializer** (`users/serializers.py`):
```python
from rest_framework import serializers
from .models import Goal

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']
```

3. **ViewSet** (`users/views.py`):
```python
from rest_framework import viewsets
from .models import Goal
from .serializers import GoalSerializer

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    
    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

4. **URLs** (`users/urls.py`):
```python
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet

router = DefaultRouter()
router.register('goals', GoalViewSet, basename='goal')

urlpatterns = router.urls
```

---

### Database Migrations

**Always run migrations after model changes:**
```powershell
uv run python manage.py makemigrations
uv run python manage.py migrate
```

**Check migration status:**
```powershell
uv run python manage.py showmigrations
```

---

### Important Conventions

1. **Custom User Model**: Always use `settings.AUTH_USER_MODEL` or `get_user_model()`
2. **Priority System**: Use `["Highest", "High", "Urgent", "Medium", "Low"]` (case-sensitive!)
3. **Prompt Caching**: Always check cache before calling Gemini API
4. **Error Handling**: Wrap LLM calls in try/except, return 500 with error message
5. **Time Zones**: Store all times in UTC, convert using user's timezone field

---

## 🔧 Development Setup

### 1. Fork & Clone
```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/huli-jing.git
cd huli-jing
```

### 2. Set Up Environment
```powershell
# Using UV (recommended)
pip install uv
uv sync

# Or standard venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```env
GEMINI_API_KEY=your_key_here
SECRET_KEY=your_secret_key
DEBUG=True
```

### 4. Run Migrations
```powershell
uv run python manage.py migrate
```

### 5. Create Superuser
```powershell
uv run python manage.py createsuperuser
```

### 6. Run Server
```powershell
uv run python manage.py runserver
```

---

## 🧪 Testing Guidelines

### Running Tests
```powershell
# Run all tests
uv run python manage.py test

# Run specific app tests
uv run python manage.py test users
uv run python manage.py test llm

# Run with verbose output
uv run python manage.py test --verbosity=2
```

### Writing Tests

**Example: Testing a New Endpoint**
```python
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User

class WeeklyPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            timezone='America/New_York'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_generate_weekly_plan_success(self):
        response = self.client.get('/api/llm/weekly-plan')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('week_start', response.data)
    
    def test_weekly_plan_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/llm/weekly-plan')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

## 📤 Submitting Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/weekly-planner
# or
git checkout -b fix/timezone-bug
```

### 2. Make Your Changes
- Write clean, readable code
- Follow existing patterns (see `.github/copilot-instructions.md`)
- Add comments for complex logic
- Update documentation if needed

### 3. Test Your Changes
```powershell
# Run tests
uv run python manage.py test

# Check for errors
uv run python manage.py check

# Test manually with Postman
```

### 4. Commit with Clear Messages
```bash
git add .
git commit -m "feat: Add weekly planning endpoint"
# or
git commit -m "fix: Correct timezone conversion in daily planner"
```

**Commit Message Format:**
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `style:` — Formatting (no code change)
- `refactor:` — Code restructuring
- `test:` — Adding tests
- `chore:` — Maintenance tasks

### 5. Push & Create Pull Request
```bash
git push origin feature/weekly-planner
```

Then open a PR on GitHub with:
- **Clear title** describing the change
- **Description** explaining what and why
- **Screenshots** (for UI changes)
- **Testing** notes (how you verified it works)

---

## 🎨 Style Guidelines

### Python Code Style
- Follow **PEP 8** (use `black` or `autopep8` for formatting)
- Use **type hints** where possible
- Maximum line length: **88 characters** (Black default)
- Use **descriptive variable names** (no single letters except in loops)

**Example:**
```python
def generate_daily_plan_for_user(user: User) -> DailyPlan:
    """
    Generate AI-powered daily plan for given user.
    
    Args:
        user: User instance with timezone preference
    
    Returns:
        DailyPlan: Structured plan with tasks and commitments
    """
    # Implementation...
```

### Django Conventions
- Use **class-based views** for CRUD operations (ViewSets)
- Use **function-based views** for simple logic
- Always validate input using **serializers**
- Use **F expressions** for database updates
- Avoid N+1 queries (use `select_related`/`prefetch_related`)

### Frontend Code Style (When Built)
- Use **TypeScript** for type safety
- Follow **Airbnb React Style Guide**
- Use **functional components** + hooks (no class components)
- Use **Prettier** for formatting
- Use **ESLint** for linting

---

## 🌟 Priority Areas

### Immediate Needs:
1. **React/React Native Frontend** — Most critical!
2. **Task Feedback System** — Let users rate/comment on tasks
3. **Goal & Commitment CRUD** — Add/edit/delete via API
4. **Weekly Planner** — Extend daily planning to weekly view

### Future Enhancements:
- **Habit Tracking** — Recurring tasks with streak tracking
- **Energy Level Tracking** — Adapt plans based on user's energy
- **Smart Notifications** — Gentle nudges based on task time
- **Analytics Dashboard** — Visualize productivity patterns
- **Social Features** — Accountability partners (optional)
- **Voice Input** — Add goals/tasks via speech (accessibility)

---

## 💬 Questions?

- **GitHub Issues**: [Ask questions here](https://github.com/frankmathewsajan/huli-jing/issues)
- **Email**: frankmathewsajan@gmail.com

---

## 🙏 Thank You!

Your contribution helps make life easier for people who struggle with executive function. Every feature, bug fix, or documentation improvement makes a real difference.

**Remember:** Perfect code isn't the goal — *helping people* is. Don't let imposter syndrome stop you from contributing! 💙
