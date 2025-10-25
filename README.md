# 🐉 Huli — AI-Powered Daily Planning for Neurodivergent Minds# 🐉 Huli — Neurodivergent-Friendly Day Orchestration Backend



> "Not just another planner — Huli helps you *reclaim your flow*."> “Not just another planner — Huli helps you *reclaim your flow*.”



[![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=flat&logo=django)](https://www.djangoproject.com/)---

[![DRF](https://img.shields.io/badge/DRF-3.16+-a30000?style=flat)](https://www.django-rest-framework.org/)

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)### 🧭 Overview

[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5-4285F4?style=flat&logo=google)](https://ai.google.dev/)**Huli** is the backend service powering an AI-driven daily planning application designed to help individuals — especially **neurodivergent humans** — manage, prioritize, and structure their days with clarity and compassion.



---It uses the **Huli-Jing Engine**, a planning and reflection algorithm that adapts to user behavior, energy levels, and real-world commitments. The system converts natural-language goals and fixed time blocks (like classes, sleep, or work) into realistic hour-by-hour plans.



## 🧭 What is Huli?---



**Huli** is an AI-driven daily planning assistant backend designed specifically for **neurodivergent individuals** who struggle with focus, time management, and executive dysfunction. ### ⚙️ Tech Stack

- **Django REST Framework** — API backbone  

Think of Huli as your **compassionate productivity companion** that:- **SimpleJWT** — secure, token-based authentication  

- 🧠 **Understands natural language** — just tell it your goals in plain English- **PostgreSQL / SQLite** — flexible relational storage  

- ⏰ **Respects your commitments** — works around fixed time blocks (classes, meetings, sleep)- **Python 3.11+** — main runtime environment  

- 🎯 **Creates realistic plans** — generates hour-by-hour schedules using AI (Google Gemini 2.5)

- 🔄 **Learns from feedback** — adapts to your patterns and preferences---

- 💬 **Nudges you gently** — designed to keep you on track without overwhelming you

## 🧩 Huli-Jing Engine (Concept)

**Note:** This is a **backend-only API**. There's no frontend yet — that's where you come in! (See [Contributing](#-contributing))The *Huli-Jing Engine* acts as the heart of the system — a context-aware scheduler that merges:

1. **User goals** → parsed from natural language

---2. **Commitments** → fixed time blocks (classes, work, etc.)

3. **Adaptive logic** → fills available hours intelligently

## 🏗️ Architecture: The Huli-Jing Engine

---

The core innovation is the **Huli-Jing Engine**: an LLM-powered scheduler that follows this pattern:

## 📘 Dev Journal

```

User Input (natural language) → Prompt Cache → Google Gemini API → Pydantic Validation → Django Models### **Day 1 — 12/10/2025**

```**Progress:**

- Added **JWT-based authentication**:

**Key Components:**  - User registration (`/users/register/`)

1. **LLM Integration** (`llm/`) — AI-powered planning using Google Gemini  - Login (`/users/jwt/`)

2. **Prompt Caching** (`llm/services/prompt_cache.py`) — SHA-256 based deduplication to save API costs  - Token refresh (`/users/jwt/refresh/`)

3. **Structured Output** (`llm/schema.py`) — Pydantic schemas ensure type-safe LLM responses  - Token verification (`/users/jwt/verify/`)

4. **User Management** (`users/`) — JWT-based authentication with custom user model  - Token blacklist/logout (`/users/jwt/blacklist/`)

5. **Core Data** (`core/`) — Goals, commitments, and prompt storage- Comprehensive **unit tests** for all endpoints

- Configured **namespaced routes** under `/api/users/`

---

---

## 🛠️ Tech Stack

### 🧠 Architecture Flow (Mermaid)

### Core Framework

- **Django 5.2+** — Web framework```mermaid

- **Django REST Framework 3.16+** — RESTful API toolkitflowchart TD

- **djangorestframework-simplejwt 5.5+** — JWT authentication    subgraph User

- **SQLite** — Default database (easily switchable to PostgreSQL)        A[User Input] -->|Goals & Commitments| B[API Gateway]

    end

### AI & Validation

- **Google Gemini 2.5 Flash** (`google-genai 1.43+`) — LLM for natural language planning    subgraph Backend["Django REST API"]

- **Pydantic 2.12+** — Structured data validation for LLM outputs        B --> C[Auth Module - JWT]

- **LangChain 0.3+** — Optional orchestration layer        B --> D[Huli-Jing Engine]

        D --> E[Goal Parser]

### Utilities        D --> F[Commitment Manager]

- **python-dotenv 1.1+** — Environment variable management        D --> G[Time Allocator]

- **django-cors-headers 4.9+** — CORS handling for future frontend integration        G --> H[Daily Plan Generator]

- **UV** — Fast Python package manager (optional, but recommended)    end



---    subgraph Storage["Database Layer"]

        H --> I[(DailyPlans)]

## 📁 Django Apps Overview        E --> J[(Goals)]

        F --> K[(Commitments)]

| App | Purpose | Key Models |        C --> L[(Users)]

|-----|---------|------------|    end

| **`users/`** | User authentication & profiles | `User` (custom AbstractUser with timezone) |

| **`core/`** | Shared data structures | `Prompt` (stores all LLM interactions with caching) |    H -->|Response| M[Structured Day Plan]

| **`llm/`** | AI-powered planning logic | `DailySchedule`, `Task` |    M --> A


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
