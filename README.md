# ElderCare — Smart Elderly Care & Medication Management Platform

> A comprehensive, accessible, full-stack healthcare management platform connecting elderly individuals with family members and caretakers to manage medications, appointments, adherence tracking, and automated email reminders.

---

## 🌟 Overview & Architecture

ElderCare provides a unified, collaborative healthcare ecosystem:
- **Zero-Friction for Seniors:** High-contrast, large-button daily task checklists, emergency quick-contact buttons, and simple one-click dose confirmations.
- **Peace of Mind for Families:** Real-time visibility into adherence, instant missed-dose escalation alerts, and appointment tracking.
- **Clinical Efficiency for Caretakers:** Master chronological daily administration timeline across assigned patients and dose status logging with clinical notes.
- **Automated Reliability:** Background scheduling engine powered by **APScheduler** and **Resend** for transactional email dispatches.

```
       ┌────────────────────────────────────────────────────────┐
       │             Client Layer (React 18 + Vite)             │
       │       Tailwind CSS • Accessible UI • TypeScript        │
       └───────────────────────────┬────────────────────────────┘
                                   │ (HTTPS / JSON REST API with JWT)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │              Backend Layer (Flask REST API)            │
       │  Blueprints: Auth, Profiles, Meds, Adherence, Appts    │
       └──────────────┬──────────────────────────┬──────────────┘
                      │                          │
                      ▼                          ▼
       ┌────────────────────────┐      ┌────────────────────────┐
       │ Background Scheduler   │      │ Persistence Layer      │
       │ APScheduler + Resend   │      │ Neon / PostgreSQL ORM  │
       └────────────────────────┘      └────────────────────────┘
```

---

## 🛠 Technology Stack

| Domain | Technologies |
|---|---|
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui primitives, React Router v6, Axios, Lucide Icons |
| **Backend** | Python 3.10+, Flask REST API, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, bcrypt, APScheduler |
| **Database** | PostgreSQL (Production via Neon / Render) with automatic SQLite fallback for local development |
| **Email Gateway**| Resend API (Transactional notification dispatches with real delivery tracking) |
| **Testing** | Pytest (16 automated tests covering Auth, RBAC, CRUD, Adherence, Appointments, Dashboards) |

---

## 👥 Demo User Accounts (Pre-Seeded)

The database includes pre-configured demo accounts:

| Role | Name | Email | Password | Details |
|---|---|---|---|---|
| **Senior (Elderly)** | Eleanor Vance | `eleanor.vance@example.com` | `Password123!` | 78 yrs, 4 medications, 93.9% adherence |
| **Family Member** | Sarah Vance | `sarah.vance@example.com` | `Password123!` | Daughter, full care access |
| **Caretaker** | Nurse David Chen | `david.chen@example.com` | `Password123!` | Home health nurse |

### Active Passcodes for Profile Linking:
- **Family Passcode:** `FAM-4310`
- **Caretaker Passcode:** `CARE-7892`

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js v18+ & npm

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configure your environment variables:
```ini
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
# PostgreSQL connection string (defaults to local SQLite if omitted)
# DATABASE_URL=postgresql://user:password@neon.tech/eldercare?sslmode=require

# Resend API Key for Email Notifications
RESEND_API_KEY=re_your_api_key_here
MAIL_FROM=ElderCare Alerts <onboarding@resend.dev>
```

### 3. Backend Setup & Seeding
```bash
# Navigate to backend and seed database with demo data
python backend/seed.py

# Run automated test suite (16 tests)
python -m pytest backend/tests -v

# Start the Flask API server (runs on http://localhost:5000)
python backend/run.py
```

### 4. Frontend Setup & Run
```bash
# Navigate to frontend and install dependencies
cd frontend
npm install

# Start development server (runs on http://localhost:5173)
npm run dev

# Or build for production
npm run build
```

---

## 📡 API Endpoints & Interactive Documentation

ElderCare provides an interactive **Swagger UI** available at:
👉 `http://localhost:5000/api/docs`
👉 OpenAPI JSON specification: `http://localhost:5000/api/openapi.json`

### Core Endpoints Summary:
- **Authentication:** `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- **Healthcare Profiles:** `GET /api/profiles`, `POST /api/profiles`, `POST /api/profiles/join` (passcode access)
- **Care Circle:** `POST /api/profiles/{id}/invitations`, `GET /api/profiles/{id}/members`
- **Medications:** `GET /api/medications`, `POST /api/medications`, `DELETE /api/medications/{id}`
- **Adherence Tracking:** `GET /api/adherence/daily`, `POST /api/adherence/{id}/status`, `GET /api/adherence/stats`
- **Doctor Appointments:** `GET /api/appointments`, `POST /api/appointments`, `PATCH /api/appointments/{id}/cancel`
- **Notifications:** `GET /api/notifications`, `PUT /api/notifications/preferences`, `POST /api/notifications/test-email`
- **Dashboards:** `GET /api/dashboard/elderly`, `GET /api/dashboard/family`, `GET /api/dashboard/caretaker`

---

## ♿ Senior Accessibility Features

Built in alignment with **WCAG 2.2 AA** recommendations:
1. **High-Contrast Mode:** Live toggle in the top navbar for ultra-readable dark text on pure white canvas.
2. **Large Typography Mode:** Vision impairment support boosting readable font scale across all screens.
3. **Large Touch Targets:** Minimum $48\text{px}$ interactive buttons for one-touch dose recording ("I Took It!").
4. **Emergency Quick-Call:** High-visibility banner linking directly to primary family contact.
5. **No Color-Only State:** All statuses combine high-contrast text badges, icons, and distinct shapes.

---

## ☁️ Deployment Instructions

### Frontend (Vercel)
1. Push the repository to GitHub.
2. Connect the repository in Vercel.
3. Set **Root Directory** to `frontend`.
4. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com/api`.
5. Deploy!

### Backend (Render / Railway)
1. In Render, create a new **Web Service**.
2. Set **Root Directory** to `backend`.
3. Set **Build Command** to `pip install -r requirements.txt`.
4. Set **Start Command** to `gunicorn run:app`.
5. Configure Environment Variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `SECRET_KEY`, `RESEND_API_KEY`.
6. Link your Neon PostgreSQL database instance.

---

## 📄 License
MIT License. Built for competition and real-world elderly healthcare management.
