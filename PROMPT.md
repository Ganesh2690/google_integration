# 🛠️ Build Prompt — Interview / Meeting Calendar Module (ClinReady)

> **Stack:** Python (FastAPI) backend + React (TypeScript) frontend
> **Use this prompt with:** GitHub Copilot Workspace, Copilot Chat, Cursor, Claude Code, or any AI coding agent.
> **Goal:** Generate a production-ready full-stack **Interview Calendar** module that matches the attached ClinReady UI screenshots, with Google Calendar + Google Meet integration.

---

## 1. Project Summary

Build a full-stack **Interview / Meeting Calendar** module for a healthcare HR product called **ClinReady**. It lets recruiters schedule candidate interviews, auto-generate Google Meet links via the Google Calendar API, view meetings in Month/Week/Day calendar views, and manage the meeting lifecycle (Scheduled → Completed / Cancelled / Rescheduled).

The module must visually match the provided screenshots: teal header banner, left sidebar (ClinReady branding), breadcrumb, filter row, month-grid calendar with soft-colored candidate cards, and a center-screen **Interview Details** modal.

---

## 2. Tech Stack (strict)

### Backend — Python
- **Python 3.11+**
- **FastAPI** (async REST framework)
- **Uvicorn** (ASGI server)
- **SQLAlchemy 2.x** (async) + **Alembic** (migrations)
- **PostgreSQL 15**
- **Pydantic v2** for request/response validation
- **google-api-python-client** + **google-auth-oauthlib** + **google-auth-httplib2**
- **python-jose[cryptography]** for JWT
- **passlib[bcrypt]** (future local auth)
- **httpx** for outbound HTTP
- **fastapi-mail** (optional) for email notifications
- **structlog** for structured logging
- **tenacity** for retries on Google API calls
- **pytest** + **pytest-asyncio** + httpx `AsyncClient`
- **ruff** (lint + format), **mypy --strict**
- Dependency manager: **uv** (or Poetry — pick one, be consistent)

### Frontend — React
- **React 18 + TypeScript** (Vite)
- **TailwindCSS**
- **shadcn/ui** primitives (Dialog, Select, Button, Badge, Popover, Toast)
- **lucide-react** icons (Calendar, Clock, MapPin, Video, User, Users, Link, Copy, Bell, Settings, Moon)
- **FullCalendar** (`@fullcalendar/react` + daygrid/timegrid/interaction) for Month/Week/Day
- **react-hook-form** + **zod** for form validation
- **@tanstack/react-query** for server state
- **axios** for HTTP
- **date-fns** for date math
- **Vitest** + **React Testing Library**

### DevOps
- Monorepo: `/backend` (Python) + `/frontend` (React) + `/docs`
- `docker-compose.yml` spinning up Postgres + backend + frontend
- `.env.example` in both apps
- Pre-commit hooks: `ruff`, `mypy`, `eslint`, `prettier`
- GitHub Actions CI: lint + typecheck + tests on every PR

---

## 3. Repository Layout

```
clinready-interview-calendar/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py            # pydantic-settings
│   │   │   ├── security.py          # JWT encode/decode
│   │   │   └── logging.py
│   │   ├── db/
│   │   │   ├── base.py              # SQLAlchemy declarative base
│   │   │   ├── session.py           # async engine + session
│   │   │   └── seed.py
│   │   ├── models/                  # SQLAlchemy ORM
│   │   │   ├── user.py
│   │   │   ├── meeting.py
│   │   │   └── audit_log.py
│   │   ├── schemas/                 # Pydantic DTOs
│   │   │   ├── meeting.py
│   │   │   └── user.py
│   │   ├── api/
│   │   │   ├── deps.py              # get_db, get_current_user
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── meetings.py
│   │   │       ├── users.py
│   │   │       └── departments.py
│   │   ├── services/
│   │   │   ├── meeting_service.py   # business logic + state machine
│   │   │   ├── google_service.py    # Calendar + Meet
│   │   │   └── notification_service.py
│   │   └── exceptions.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_meetings.py
│   │   └── test_google_service.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/              # Sidebar, TopHeader, Breadcrumb
│   │   │   ├── calendar/            # CalendarView, MeetingCard, FilterBar
│   │   │   └── meeting/             # CreateMeetingModal, MeetingDetailsModal
│   │   ├── hooks/
│   │   ├── pages/InterviewCalendar.tsx
│   │   ├── lib/
│   │   ├── types/
│   │   └── App.tsx
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## 4. Data Model (SQLAlchemy 2.x)

```python
# app/models/meeting.py
from enum import Enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class MeetingStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"

class LocationType(str, Enum):
    GOOGLE_MEET = "GOOGLE_MEET"
    ZOOM = "ZOOM"
    MS_TEAMS = "MS_TEAMS"
    PHYSICAL = "PHYSICAL"

class Department(str, Enum):
    CARDIOLOGY = "CARDIOLOGY"
    LABORATORY = "LABORATORY"
    NURSING = "NURSING"
    PHARMACY = "PHARMACY"
    RADIOLOGY = "RADIOLOGY"
    ADMINISTRATION = "ADMINISTRATION"
    CLINICAL_COORDINATION = "CLINICAL_COORDINATION"

class Meeting(Base):
    __tablename__ = "meetings"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_name: Mapped[str]
    candidate_email: Mapped[str | None]
    position: Mapped[str]
    department: Mapped[Department] = mapped_column(SAEnum(Department))
    host_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    host: Mapped["User"] = relationship(back_populates="meetings_hosted")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_mins: Mapped[int] = mapped_column(default=30)
    location_type: Mapped[LocationType] = mapped_column(SAEnum(LocationType))
    location_detail: Mapped[str | None]
    google_event_id: Mapped[str | None]
    meet_link: Mapped[str | None]
    notes: Mapped[str | None]
    participants: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[MeetingStatus] = mapped_column(SAEnum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    color_tag: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    role: Mapped[str]                          # RECRUITER | INTERVIEWER | ADMIN
    google_tokens: Mapped[dict | None] = mapped_column(JSON)
    meetings_hosted: Mapped[list["Meeting"]] = relationship(back_populates="host")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    meeting: Mapped["Meeting"] = relationship(back_populates="audit_logs")
    action: Mapped[str]                        # CREATED | UPDATED | RESCHEDULED | CANCELLED | COMPLETED
    actor_id: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

Seed ~12 realistic candidates matching the screenshots (Michael Thompson — Lab Technician, Amanda Foster — Clinical Coordinator, Sarah Mitchell — Registered Nurse, John Davis — Lab Technician, Emily Chen — Medical Assistant, David Park — Pharmacist, Jessica Lee — Registered Nurse, Robert Kim — Physician, Maria Garcia — Medical Assistant, etc.) on the correct late-March-2026 dates so the UI reproduces the screenshot exactly.

---

## 5. Pydantic Schemas (examples)

```python
# app/schemas/meeting.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class MeetingCreate(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=120)
    candidate_email: EmailStr | None = None
    position: str
    department: Department
    host_id: str
    date: datetime                          # ISO, UTC
    duration_mins: int = Field(ge=15, le=240, default=30)
    location_type: LocationType
    location_detail: str | None = None
    notes: str | None = None
    participants: list[EmailStr] = []

class MeetingRead(BaseModel):
    id: str
    candidate_name: str
    position: str
    department: Department
    host_id: str
    date: datetime
    duration_mins: int
    location_type: LocationType
    meet_link: str | None
    status: MeetingStatus
    class Config:
        from_attributes = True
```

---

## 6. REST API Endpoints

All routes under `/api/v1`. JWT-protected except `/auth/*`. FastAPI auto-documents at `/docs` (Swagger) and `/redoc`.

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/auth/google`                  | Start Google OAuth (scopes: `calendar`, `calendar.events`) |
| GET    | `/auth/google/callback`         | OAuth callback — store tokens, issue JWT |
| POST   | `/auth/refresh`                 | Refresh JWT |
| GET    | `/meetings`                     | List (query: `from`, `to`, `department`, `status`, `host_id`) |
| POST   | `/meetings`                     | Create + Google Calendar event + Meet link |
| GET    | `/meetings/{id}`                | Get details |
| PATCH  | `/meetings/{id}`                | Update / reschedule |
| POST   | `/meetings/{id}/cancel`         | Cancel (syncs to Google) |
| POST   | `/meetings/{id}/complete`       | Mark completed |
| GET    | `/meetings/{id}/audit`          | Audit trail |
| GET    | `/departments`                  | Filter dropdown |
| GET    | `/users/interviewers`           | Host dropdown |

**Error handling:** global `exception_handler` mapping:
- `DomainError` → 400
- `NotFoundError` → 404
- `InvalidStateTransition` → 409
- `GoogleAPIError` → 502 with `{ error, upstream }`

---

## 7. Google Calendar + Meet Integration (Python)

Implement `app/services/google_service.py`:

```python
import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential

class GoogleService:
    def _client(self, tokens: dict):
        creds = Credentials(
            token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def create_event_with_meet(self, *, summary, description, start_iso, end_iso,
                               attendees: list[str], tokens: dict) -> dict:
        service = self._client(tokens)
        body = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_iso, "timeZone": "UTC"},
            "end":   {"dateTime": end_iso,   "timeZone": "UTC"},
            "attendees": [{"email": e} for e in attendees],
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid.uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }
        event = service.events().insert(
            calendarId="primary",
            body=body,
            conferenceDataVersion=1,
            sendUpdates="all",
        ).execute()
        meet_link = event.get("hangoutLink") or \
            event["conferenceData"]["entryPoints"][0]["uri"]
        return {"event_id": event["id"], "meet_link": meet_link,
                "html_link": event["htmlLink"]}

    def update_event(self, event_id, patch: dict, tokens: dict) -> None: ...
    def cancel_event(self, event_id, tokens: dict) -> None: ...
```

**Critical implementation notes:**
- `conferenceDataVersion=1` is **mandatory** for Meet link creation.
- Use a fresh UUID for `requestId` on every create.
- Persist `google_event_id` + `meet_link` on the Meeting row.
- On reschedule, call `events().patch(...)` on the same event — **keep the same Meet link** unless the user explicitly ticks "regenerate link".
- On cancel, either `events().delete` or `events().patch(status="cancelled")` — controlled by env `GOOGLE_CANCEL_MODE=delete|soft`.
- `googleapiclient` is blocking — wrap calls in `await run_in_threadpool(...)` from Starlette so FastAPI's event loop is never blocked.

---

## 8. Frontend — Screens & Components

### 8.1 Layout (matches all 3 screenshots)

- **Left Sidebar** (fixed, 240px): ClinReady logo + shield icon, "Main Menu" group (Dashboard, Job Posting, Job Applications, Shortlisted Candidates, **Interview Calendar** — active state with teal pill), "Staff Management" group, "Finance & Accounts" group, "Administration" group, facility card (Apollo Hospitals, Houston), Logout.
- **Top Header**: search bar with ⌘K hint, dark-mode toggle, settings icon, notification bell with red dot.
- **Page Banner**: teal (`#0E7C86`) full-width band with breadcrumb `Home / Interview Calendar`, H1 "Interview Calendar", subtitle "Manage and track candidate interviews".

### 8.2 `InterviewCalendar.tsx` (main page)

1. **Toolbar row**
   - Left: `‹` | `Today` | `›` navigation + current month label (`March 2026`).
   - Center: `Filters:` label + two dropdowns — `All Departments`, `All Statuses`.
   - Right: view toggle `Month | Week | Day` (pill buttons) + download icon (export to ICS).

2. **Calendar grid** — FullCalendar with custom event rendering. Each event renders as a **rounded soft-colored card**:
   - Candidate name (semibold)
   - Position (muted, smaller)
   - ⏱ icon + time (e.g., `09:00 AM`)

   Status → card color mapping:
   - `SCHEDULED` → `bg-slate-100 text-slate-900`
   - `COMPLETED` → `bg-emerald-100 text-emerald-900`
   - `CANCELLED` → `bg-rose-100 text-rose-900`
   - `RESCHEDULED` → `bg-amber-100 text-amber-900`

   Today's date cell shows a blue filled circle around the day number (see screenshot 3, day 24).

3. Clicking a card opens **`MeetingDetailsModal`**.
4. A **"+ Create Meeting"** button (top-right of the toolbar) opens **`CreateMeetingModal`**.

### 8.3 `CreateMeetingModal`

Fields (validated via zod):
- Candidate Name *
- Candidate Email
- Position *
- Department * (select)
- Interviewer / Host * (select, fetched from `/users/interviewers`)
- Date * (date picker)
- Time * (time picker)
- Duration (15 / 30 / 45 / 60 / 90 min)
- Location Type (radio: Google Meet / Zoom / MS Teams / Physical)
- Location Detail (only if Physical)
- Notes (textarea)
- Participant Emails (tag input)

Footer: `Cancel` | `Save & Schedule` (primary teal). On submit → POST `/meetings` → toast → close → react-query invalidation refreshes the calendar.

### 8.4 `MeetingDetailsModal` (match screenshots 1 & 2 exactly)

Header: `Interview Details` + close ✕, subtitle `View and manage details of the interview.`, then a row with **status pill** (Scheduled / Completed / Cancelled in its matching color) + `🎥 Video` badge.

Sections with small uppercase labels (`CANDIDATE INFORMATION`, `SCHEDULE`) and icon + label + value rows:
- 👤 Candidate Name
- 🏢 Position
- 👥 Department
- 📅 Date
- 🕐 Time
- 📍 Location
- 👤 Interviewer
- 🎥 Meeting Link — URL in a pill with a copy button; below it a full-width teal **`Join Video Meeting`** button (only when status = `SCHEDULED` and a meet link exists).

Footer buttons vary by status:
- **Scheduled** → `Close` | `Reschedule` | `Cancel Interview` | `Mark Completed` | `Confirm Interview`
- **Completed** → `Close` only (per screenshot 2)
- **Cancelled** → `Close` only, modal content dimmed

Reschedule reopens the create form in edit mode. Cancel shows a confirm dialog ("Are you sure you want to cancel this meeting?").

---

## 9. State Machine (enforce in `MeetingService`)

```
              ┌───────────┐
  create ───▶ │ SCHEDULED │ ───▶ COMPLETED
              └─────┬─────┘
                    ├──▶ CANCELLED
                    └──▶ RESCHEDULED ──▶ SCHEDULED
```

Reject invalid transitions by raising `InvalidStateTransition` → HTTP 409. Write an `AuditLog` row for every transition.

```python
# app/services/meeting_service.py (sketch)
ALLOWED = {
    MeetingStatus.SCHEDULED:   {MeetingStatus.COMPLETED, MeetingStatus.CANCELLED, MeetingStatus.RESCHEDULED},
    MeetingStatus.RESCHEDULED: {MeetingStatus.SCHEDULED},
    MeetingStatus.COMPLETED:   set(),
    MeetingStatus.CANCELLED:   set(),
}
def transition(current, target):
    if target not in ALLOWED.get(current, set()):
        raise InvalidStateTransition(current, target)
```

---

## 10. UI Design Tokens

In `tailwind.config.ts`:

```ts
colors: {
  brand: {
    teal:   '#0E7C86',    // banner & primary buttons
    tealDk: '#0A5F68',
    accent: '#10B981',
  },
  status: {
    scheduled:   { bg: '#F1F5F9', fg: '#0F172A' },
    completed:   { bg: '#D1FAE5', fg: '#065F46' },
    cancelled:   { bg: '#FEE2E2', fg: '#991B1B' },
    rescheduled: { bg: '#FEF3C7', fg: '#92400E' },
  },
}
```

Font: Inter. Radius: `rounded-xl` for cards, `rounded-lg` for inputs. Shadow: `shadow-sm` on cards, `shadow-2xl` on modals.

---

## 11. Environment Variables

**`backend/.env.example`**
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/clinready
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
GOOGLE_CANCEL_MODE=soft
SMTP_HOST=
SMTP_USER=
SMTP_PASS=
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
```

**`frontend/.env.example`**
```
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 12. Docker

**`backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN pip install --no-cache-dir uv && uv sync --frozen
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`docker-compose.yml`**
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: clinready
    ports: ["5432:5432"]
    volumes: ["dbdata:/var/lib/postgresql/data"]
  backend:
    build: ./backend
    env_file: ./backend/.env
    depends_on: [db]
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    env_file: ./frontend/.env
    depends_on: [backend]
    ports: ["5173:5173"]
volumes:
  dbdata:
```

---

## 13. Testing

**Backend (pytest + httpx AsyncClient)**
- Unit test every state transition in `MeetingService`.
- Integration test `POST /meetings` with `google_service` monkey-patched — assert Meet link is persisted.
- Separate test DB fixture in `conftest.py`, created + dropped per session.
- ≥ 80% coverage on `services/` and `api/v1/`.

**Frontend (Vitest + RTL)**
- Render calendar with seeded events; assert card colors per status.
- Test `CreateMeetingModal` validation errors surface correctly.
- Test `MeetingDetailsModal` footer buttons change with status.
- ≥ 70% coverage on `src/components`.

---

## 14. README Requirements

`README.md` must include:
1. The 3 attached screenshots.
2. Feature list.
3. Architecture diagram (Mermaid).
4. Local setup:
   ```
   docker compose up -d db
   cd backend && uv sync && alembic upgrade head && python -m app.db.seed
   uvicorn app.main:app --reload
   cd ../frontend && pnpm i && pnpm dev
   ```
5. Google Cloud setup checklist (create project, enable Calendar API, OAuth consent screen, add redirect URI).
6. API docs link (`http://localhost:8000/docs`).
7. Running-app screenshots.
8. MIT License.

---

## 15. Deliverables Checklist

- [ ] Working monorepo — `docker compose up` boots db + backend + frontend.
- [ ] SQLAlchemy models + Alembic migration + seed script.
- [ ] All endpoints from §6 implemented with Pydantic validation.
- [ ] FastAPI auto-docs at `/docs` working.
- [ ] Google Meet creation proven via integration test (mocked).
- [ ] Frontend visually matches screenshots (sidebar, banner, calendar grid, both modals).
- [ ] Month / Week / Day views toggle correctly.
- [ ] Filters (Department, Status) actually filter events.
- [ ] Status color system wired to card rendering.
- [ ] Create / Edit / Reschedule / Cancel / Complete flows work end-to-end.
- [ ] Audit log rows written for every lifecycle event.
- [ ] README with screenshots and setup instructions.
- [ ] CI workflow (`.github/workflows/ci.yml`) runs `ruff`, `mypy`, `pytest`, `eslint`, `tsc --noEmit`, `vitest run` on PR.

---

## 16. Non-Goals (out of scope)

- Multi-tenant isolation.
- Calendar providers other than Google (Outlook/iCal noted as future work).
- Mobile apps.
- Realtime collaboration (no websockets).

---

## 17. Style & Quality Rules for the Agent

**Python**
- `ruff check` + `ruff format` clean.
- `mypy --strict` clean; no untyped functions in `app/`.
- Async everywhere — async SQLAlchemy session, async endpoints.
- No raw SQL unless wrapped in `text()`; prefer ORM queries.
- Never block the event loop — use `run_in_threadpool` for googleapiclient.
- All secrets come from `pydantic_settings.BaseSettings`; never hardcoded.

**TypeScript**
- Strict mode on.
- No `any` in committed code.
- Components < 200 lines; extract hooks aggressively.
- Use react-query for every network call; no manual `useEffect` fetches.

**Git**
- Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`).
- Small, reviewable commits.
- Do **not** commit `.env` or real Google credentials.

---

**Start by scaffolding the monorepo, then backend (models → Alembic migration → services → routers → Google integration → tests), then frontend (layout → calendar page → modals → wiring to API). Match the screenshots precisely.**
