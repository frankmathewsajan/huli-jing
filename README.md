# 🐉 Huli — Neurodivergent-Friendly Day Orchestration Backend

> “Not just another planner — Huli helps you *reclaim your flow*.”

---

### 🧭 Overview
**Huli** is the backend service powering an AI-driven daily planning application designed to help individuals — especially **neurodivergent humans** — manage, prioritize, and structure their days with clarity and compassion.

It uses the **Huli-Jing Engine**, a planning and reflection algorithm that adapts to user behavior, energy levels, and real-world commitments. The system converts natural-language goals and fixed time blocks (like classes, sleep, or work) into realistic hour-by-hour plans.

---

### ⚙️ Tech Stack
- **Django REST Framework** — API backbone  
- **SimpleJWT** — secure, token-based authentication  
- **PostgreSQL / SQLite** — flexible relational storage  
- **Python 3.11+** — main runtime environment  

---

## 🧩 Huli-Jing Engine (Concept)
The *Huli-Jing Engine* acts as the heart of the system — a context-aware scheduler that merges:
1. **User goals** → parsed from natural language
2. **Commitments** → fixed time blocks (classes, work, etc.)
3. **Adaptive logic** → fills available hours intelligently

---

## 📘 Dev Journal

### **Day 1 — 12/10/2025**
**Progress:**
- Added **JWT-based authentication**:
  - User registration (`/users/register/`)
  - Login (`/users/jwt/`)
  - Token refresh (`/users/jwt/refresh/`)
  - Token verification (`/users/jwt/verify/`)
  - Token blacklist/logout (`/users/jwt/blacklist/`)
- Comprehensive **unit tests** for all endpoints
- Configured **namespaced routes** under `/api/users/`

---

### 🧠 Architecture Flow (Mermaid)

```mermaid
flowchart TD
    subgraph User
        A[User Input] -->|Goals & Commitments| B[API Gateway]
    end

    subgraph Backend["Django REST API"]
        B --> C[Auth Module - JWT]
        B --> D[Huli-Jing Engine]
        D --> E[Goal Parser]
        D --> F[Commitment Manager]
        D --> G[Time Allocator]
        G --> H[Daily Plan Generator]
    end

    subgraph Storage["Database Layer"]
        H --> I[(DailyPlans)]
        E --> J[(Goals)]
        F --> K[(Commitments)]
        C --> L[(Users)]
    end

    H -->|Response| M[Structured Day Plan]
    M --> A
