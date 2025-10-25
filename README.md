# 🐉 Huli — AI-Powered Daily Planning for Neurodivergent Minds

> "Not just another planner — Huli helps you *reclaim your flow*."

[![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16+-a30000?style=flat)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5-4285F4?style=flat&logo=google)](https://ai.google.dev/)

---

## 🧭 What is Huli?

**Huli** is an AI-driven daily planning assistant backend designed specifically for **neurodivergent individuals** who struggle with focus, time management, and executive dysfunction. 

Think of Huli as your **compassionate productivity companion** that:
- 🧠 **Understands natural language** — just tell it your goals in plain English
- ⏰ **Respects your commitments** — works around fixed time blocks (classes, meetings, sleep)
- 🎯 **Creates realistic plans** — generates hour-by-hour schedules using AI (Google Gemini 2.5)
- 🔄 **Learns from feedback** — adapts to your patterns and preferences
- 💬 **Nudges you gently** — designed to keep you on track without overwhelming you

**Note:** This is a **backend-only API**. There's no frontend yet — that's where you come in! (See [Contributing](#-contributing))

---

## 🏗️ Architecture: The Huli-Jing Engine

The core innovation is the **Huli-Jing Engine**: an LLM-powered scheduler that follows this pattern:

```
User Input (natural language) → Prompt Cache → Google Gemini API → Pydantic Validation → Django Models
```

**Key Components:**
1. **LLM Integration** (`llm/`) — AI-powered planning using Google Gemini
2. **Prompt Caching** (`llm/services/prompt_cache.py`) — SHA-256 based deduplication to save API costs
3. **Structured Output** (`llm/schema.py`) — Pydantic schemas ensure type-safe LLM responses
4. **User Management** (`users/`) — JWT-based authentication with custom user model
5. **Core Data** (`core/`) — Goals, commitments, and prompt storage

---

## 🛠️ Tech Stack

### Core Framework
- **Django 5.2+** — Web framework
- **Django REST Framework 3.16+** — RESTful API toolkit
- **djangorestframework-simplejwt 5.5+** — JWT authentication
- **SQLite** — Default database (easily switchable to PostgreSQL)

### AI & Validation
- **Google Gemini 2.5 Flash** (`google-genai 1.43+`) — LLM for natural language planning
- **Pydantic 2.12+** — Structured data validation for LLM outputs
- **LangChain 0.3+** — Optional orchestration layer

### Utilities
- **python-dotenv 1.1+** — Environment variable management
- **django-cors-headers 4.9+** — CORS handling for future frontend integration
- **UV** — Fast Python package manager (optional, but recommended)

---

## 📁 Django Apps Overview

| App | Purpose | Key Models |
|-----|---------|------------|
| **`users/`** | User authentication & profiles | `User` (custom AbstractUser with timezone) |
| **`core/`** | Shared data structures | `Prompt` (stores all LLM interactions with caching) |
| **`llm/`** | AI-powered planning logic | `DailySchedule`, `Task` |

### Why These Dependencies?

- **SimpleJWT**: Stateless authentication — perfect for mobile/web frontends
- **Google Gemini**: Cutting-edge LLM with structured output support (cheaper than GPT-4)
- **Pydantic**: Guarantees the LLM returns valid JSON matching our schemas
- **CORS Headers**: Allows React/React Native frontends to communicate with the API
- **UV**: 10-100x faster than pip for dependency management

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+** installed
- **Git** installed
- **Google Gemini API Key** (get free tier at [ai.google.dev](https://ai.google.dev/))

### 1. Clone the Repository
```powershell
git clone https://github.com/frankmathewsajan/huli-jing.git
cd huli-jing
```

### 2. Set Up Virtual Environment

**Option A: Using UV (Recommended)**
```powershell
# Install UV if you don't have it
pip install uv

# Create virtual environment and install dependencies
uv sync
```

**Option B: Using Standard venv**
```powershell
# Create virtual environment
python -m venv .venv

# Activate it (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=django-insecure-!u*g_lvynbn^jocwn^zdrwa_-!k%dy=ro(ngl0i&f6z=np6i)^
DEBUG=True
```

⚠️ **Replace `your_api_key_here` with your actual Gemini API key!**

### 4. Run Migrations
```powershell
# Using UV
uv run python manage.py migrate

# Or standard Python
python manage.py migrate
```

### 5. Create a Superuser (Admin Account)
```powershell
# Using UV
uv run python manage.py createsuperuser

# Or standard Python
python manage.py createsuperuser
```

Follow the prompts to create username, email, and password.

### 6. Run the Development Server
```powershell
# Using UV
uv run python manage.py runserver

# Or standard Python
python manage.py runserver
```

The API will be available at **`http://127.0.0.1:8000`**

---

## 🔐 Authentication Flow

Huli uses **JWT (JSON Web Tokens)** for authentication. Here's how to use it:

### 1. Register a New User
**Endpoint:** `POST http://127.0.0.1:8000/api/users/register`

**Request Body (JSON):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!",
  "timezone": "America/New_York"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "timezone": "America/New_York"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
  }
}
```

### 2. Login (Get Tokens)
**Endpoint:** `POST http://127.0.0.1:8000/api/users/jwt`

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### 3. Access Protected Endpoints

Use the **access token** as a **Bearer token** in the `Authorization` header:

**Example:** Generate Daily Plan

**Endpoint:** `GET http://127.0.0.1:8000/api/llm/daily-plan`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi...
Content-Type: application/json
```

### 4. Refresh Access Token (When Expired)
**Endpoint:** `POST http://127.0.0.1:8000/api/users/jwt/refresh`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### 5. Logout (Blacklist Token)
**Endpoint:** `POST http://127.0.0.1:8000/api/users/jwt/blacklist`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

---

## 🧪 Testing the API with Postman

1. **Download Postman**: [https://www.postman.com/downloads/](https://www.postman.com/downloads/)

2. **Import Collection** (or create requests manually):
   - Register User → `POST /api/users/register`
   - Login → `POST /api/users/jwt`
   - Copy the `access` token from response

3. **Set Authorization**:
   - In Postman, go to **Authorization** tab
   - Select **Type:** `Bearer Token`
   - Paste your access token

4. **Test Protected Endpoints**:
   - `GET /api/llm/daily-plan` — Generate AI-powered daily schedule
   - `GET /api/users/profile` — View user profile (if implemented)

---

## 🎛️ Django Admin Panel

### Accessing the Admin Panel
1. Make sure you created a superuser (see step 5 in Getting Started)
2. Navigate to: **`http://127.0.0.1:8000/admin`**
3. Login with your superuser credentials

### What You Can Do in Admin:
- **Manage Users** — View/edit user accounts
- **View Prompts** — Inspect cached LLM prompts and responses
- **Manage Daily Schedules** — See generated plans
- **Manage Tasks** — View individual scheduled tasks
- **View User Patterns** — Check onboarding data

### Adding Data via Admin:
You can manually create goals, commitments, or test prompts directly through the admin interface for testing purposes.

---

## 🗺️ API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/users/register` | Register new user | ❌ |
| `POST` | `/api/users/jwt` | Login (get tokens) | ❌ |
| `POST` | `/api/users/jwt/refresh` | Refresh access token | ❌ |
| `POST` | `/api/users/jwt/verify` | Verify token validity | ❌ |
| `POST` | `/api/users/jwt/blacklist` | Logout (invalidate token) | ✅ |
| `GET` | `/api/llm/daily-plan` | Generate AI daily plan | ✅ |
| `POST` | `/api/llm/onboarding` | Submit onboarding questionnaire | ✅ |

---

## 🤝 Contributing

**We need your help!** Huli is backend-only right now. Here's how you can contribute:

### Frontend Development (High Priority!)
Build a user interface using:
- **React** — Modern web app (recommended)
- **React Native** — Mobile app for iOS/Android
- **Django Templates** — Simple server-rendered UI (good for MVPs)

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

### Other Ways to Help:
- 🐛 Report bugs or suggest features (open an issue)
- 📖 Improve documentation
- 🧪 Write more tests
- 🎨 Design UI/UX mockups
- 🌍 Add internationalization support

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙏 Acknowledgments

Built with 💙 for the neurodivergent community.

Special thanks to:
- The Django and DRF communities
- Google for making Gemini accessible
- Everyone who struggles with executive dysfunction — this is for you

---

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/frankmathewsajan/huli-jing/issues)
- **Email**: frankmathewsajan@gmail.com

---

*"Every day is a new chance to get it right. Huli's here to help."* 🦊
