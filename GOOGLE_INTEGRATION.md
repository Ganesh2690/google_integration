# Google Calendar & Google Meet Integration Guide
### ClinReady — Interview Calendar Module

> **Who is this for?**  
> Junior developers who want to understand, replicate, or extend the Google Calendar and Google Meet integration in this project. No prior Google API experience needed.

---

## Table of Contents

1. [What Does This Integration Do?](#1-what-does-this-integration-do)
2. [Big Picture — How It All Fits Together](#2-big-picture--how-it-all-fits-together)
3. [Phase 1 — Google Cloud Setup](#phase-1--google-cloud-setup)
4. [Phase 2 — OAuth 2.0 Login Flow](#phase-2--oauth-20-login-flow)
5. [Phase 3 — Creating a Calendar Event with Meet Link](#phase-3--creating-a-calendar-event-with-meet-link)
6. [Phase 4 — Updating an Event (Reschedule)](#phase-4--updating-an-event-reschedule)
7. [Phase 5 — Cancelling an Event](#phase-5--cancelling-an-event)
8. [Phase 6 — Notifications & Email Alerts](#phase-6--notifications--email-alerts)
9. [Error Handling & Retry Logic](#error-handling--retry-logic)
10. [File-by-File Code Reference](#file-by-file-code-reference)
11. [Data Flow Diagrams](#data-flow-diagrams)
12. [Common Mistakes & Fixes](#common-mistakes--fixes)
13. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## 1. What Does This Integration Do?

When a recruiter schedules an interview in ClinReady:

- A **Google Calendar event** is automatically created in the interviewer's Google Calendar
- A **Google Meet video link** is generated and attached to that event
- All **attendees** (candidates, interviewers) get an **email invite** from Google
- When the interview is **rescheduled**, the calendar event is **updated** automatically
- When the interview is **cancelled**, the calendar event is **cancelled** and attendees are notified
- The Google Meet link is stored in the database and shown in the UI as a **"Join Video Meeting"** button

---

## 2. Big Picture — How It All Fits Together

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLINREADY SYSTEM                          │
│                                                                  │
│  ┌──────────────┐    REST API     ┌────────────────────────┐    │
│  │   React UI   │ ─────────────► │   FastAPI Backend       │    │
│  │  (Frontend)  │                │                         │    │
│  └──────────────┘                │  ┌──────────────────┐   │    │
│                                  │  │  MeetingService   │   │    │
│                                  │  │  (business logic) │   │    │
│                                  │  └────────┬─────────┘   │    │
│                                  │           │              │    │
│                                  │  ┌────────▼─────────┐   │    │
│                                  │  │  GoogleService    │   │    │
│                                  │  │  (API wrapper)    │   │    │
│                                  │  └────────┬─────────┘   │    │
│                                  │           │              │    │
│                                  └───────────┼──────────────┘    │
│                                              │                   │
└──────────────────────────────────────────────┼───────────────────┘
                                               │ HTTPS
                                               ▼
                                  ┌────────────────────────┐
                                  │   Google APIs          │
                                  │                        │
                                  │  ┌──────────────────┐  │
                                  │  │  Calendar API    │  │
                                  │  │  (events CRUD)   │  │
                                  │  └──────────────────┘  │
                                  │  ┌──────────────────┐  │
                                  │  │  Google Meet     │  │
                                  │  │  (video links)   │  │
                                  │  └──────────────────┘  │
                                  │  ┌──────────────────┐  │
                                  │  │  Gmail           │  │
                                  │  │  (email invites) │  │
                                  │  └──────────────────┘  │
                                  └────────────────────────┘
```

**Key concept:** The backend never touches Google directly on behalf of the system. It always acts using the **interviewer's Google tokens** (OAuth credentials) stored in the database. This means the calendar event appears in the interviewer's own Google Calendar.

---

## Phase 1 — Google Cloud Setup

Before writing any code, you need to configure Google Cloud.

### Step 1 — Create a Project

```
Google Cloud Console → New Project → name it → Create
```

### Step 2 — Enable Required APIs

```
APIs & Services → Library → Search and Enable:
  ✅ Google Calendar API
  ✅ (Google Meet is included — no separate API needed)
```

### Step 3 — Configure OAuth Consent Screen

```
APIs & Services → OAuth consent screen
  → Choose: External
  → Fill: App name, Support email, Developer email
  → Scopes → Add:
      .../auth/calendar
      .../auth/calendar.events
      openid
      email
      profile
  → Test users → Add your email
  → Save
```

> **Why test users?**  
> Until your app is "verified" by Google, only emails you add here can log in.

### Step 4 — Create OAuth Credentials

```
APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
  → Application type: Web application
  → Authorised redirect URI: http://localhost:8000/api/v1/auth/google/callback
  → Create
  → Copy: Client ID and Client Secret
```

### Step 5 — Add to .env

```env
# backend/.env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

**Relevant file:** `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
```

---

## Phase 2 — OAuth 2.0 Login Flow

The interviewer must log in with Google so ClinReady can act on their behalf.

### What Happens Step by Step

```
User clicks "Login with Google"
        │
        ▼
GET /api/v1/auth/google
        │
        │  Build OAuth URL with scopes
        ▼
Redirect to: accounts.google.com/o/oauth2/auth
        │
        │  User logs in + grants permission
        ▼
Google redirects to: /api/v1/auth/google/callback?code=XYZ
        │
        │  Exchange code for tokens
        │  Fetch user profile from Google
        │  Save user + tokens to DB
        ▼
Return: JWT access token to frontend
        │
        ▼
Frontend stores JWT, uses it for all API calls
```

### The Scopes We Request

```python
SCOPES = [
    "https://www.googleapis.com/auth/calendar",        # read/write calendar
    "https://www.googleapis.com/auth/calendar.events", # create/edit events
    "openid",   # verify identity
    "email",    # get email address
    "profile",  # get name and photo
]
```

> **Important:** `access_type="offline"` is set so Google returns a **refresh token**.  
> Without this, tokens expire in 1 hour and can't be renewed automatically.

### Tokens Stored in Database

After login, we store tokens on the `User` row:

```python
tokens = {
    "access_token":  "ya29.xxxxx",   # short-lived (1 hour)
    "refresh_token": "1//xxxxx",     # long-lived, used to get new access tokens
}
user.google_tokens = tokens
```

**Relevant file:** `backend/app/api/v1/auth.py`

---

## Phase 3 — Creating a Calendar Event with Meet Link

This is the core integration. When a recruiter clicks **"Save & Schedule"**, this entire flow runs.

### Flow Diagram

```
POST /api/v1/meetings  (with meeting details)
        │
        ▼
MeetingService.create_meeting()
        │
        ├── 1. Load interviewer's Google tokens from DB
        │
        ├── 2. Is location_type == GOOGLE_MEET?
        │       │
        │       YES
        │       │
        │       ▼
        │   GoogleService.create_event_with_meet()
        │       │
        │       ├── Build event body with conferenceData
        │       ├── Call Google Calendar API (insert)
        │       ├── Extract meet_link from response
        │       └── Return { event_id, meet_link }
        │
        ├── 3. Save Meeting to DB (with meet_link + google_event_id)
        ├── 4. Write audit log entry ("CREATED")
        └── 5. Return MeetingRead to API
```

### The Google API Call — Explained

**File:** `backend/app/services/google_service.py`

```python
body = {
    "summary": "Interview: Maria Garcia - Registered Nurse",
    "description": "Notes about the interview...",
    "start": {"dateTime": "2026-03-24T10:00:00", "timeZone": "UTC"},
    "end":   {"dateTime": "2026-03-24T10:30:00", "timeZone": "UTC"},
    "attendees": [
        {"email": "candidate@example.com"},
        {"email": "interviewer@hospital.com"},
    ],
    "conferenceData": {
        "createRequest": {
            "requestId": "some-unique-uuid",          # must be unique per request
            "conferenceSolutionKey": {
                "type": "hangoutsMeet"                # tells Google to create a Meet link
            },
        }
    },
}

event = service.events().insert(
    calendarId="primary",       # interviewer's own calendar
    body=body,
    conferenceDataVersion=1,    # REQUIRED to get Meet link — without this, no Meet!
    sendUpdates="all",          # sends email invites to all attendees
).execute()
```

### Getting the Meet Link from the Response

```python
meet_link = (
    event.get("hangoutLink")                              # usually here
    or event["conferenceData"]["entryPoints"][0]["uri"]   # fallback
)
```

### Why `run_in_threadpool`?

The `googleapiclient` library is **synchronous** (blocking).  
FastAPI uses `async` (non-blocking). Mixing them would freeze the server.

**Solution:** Wrap the blocking call in `run_in_threadpool` from Starlette:

```python
# This runs the blocking Google API call in a separate thread
# so FastAPI stays responsive
async def create_event_with_meet(self, ...) -> dict:
    return await run_in_threadpool(
        self._create_event_sync,   # the blocking function
        summary=summary,
        ...
    )
```

---

## Phase 4 — Updating an Event (Reschedule)

When the recruiter clicks **"Reschedule"** and saves a new date/time:

### Flow Diagram

```
PATCH /api/v1/meetings/{id}  (with new date/time)
        │
        ▼
MeetingService.update_meeting()
        │
        ├── Update fields in DB
        │
        ├── Does meeting have a google_event_id?
        │       │
        │       YES
        │       │
        │       ▼
        │   GoogleService.update_event()
        │       │
        │       └── PATCH event on Google Calendar
        │           (sends update email to all attendees)
        │
        ├── Write audit log ("UPDATED")
        └── Return updated Meeting
```

### The Google API Call

```python
patch = {
    "start": {"dateTime": "2026-03-28T14:00:00", "timeZone": "UTC"},
    "end":   {"dateTime": "2026-03-28T14:30:00", "timeZone": "UTC"},
}

service.events().patch(
    calendarId="primary",
    eventId=meeting.google_event_id,   # stored when event was created
    body=patch,
    sendUpdates="all",                 # Google emails attendees about the change
).execute()
```

> **Note:** We use `patch()` not `update()`. Patch only changes the fields you send.  
> `update()` would wipe everything else.

---

## Phase 5 — Cancelling an Event

Two modes are supported, controlled by `GOOGLE_CANCEL_MODE` in `.env`:

### Mode 1: `soft` (default — recommended)

```
Sets event status to "cancelled" on Google Calendar.
The event stays visible (greyed out) — attendees see it was cancelled.
Google sends cancellation emails automatically.
```

```python
service.events().patch(
    calendarId="primary",
    eventId=event_id,
    body={"status": "cancelled"},
    sendUpdates="all",
).execute()
```

### Mode 2: `delete`

```
Permanently deletes the event from Google Calendar.
Attendees get a cancellation email then the event disappears.
```

```python
service.events().delete(
    calendarId="primary",
    eventId=event_id,
    sendUpdates="all",
).execute()
```

### Cancel Flow Diagram

```
POST /api/v1/meetings/{id}/cancel
        │
        ▼
MeetingService.cancel_meeting()
        │
        ├── Check state machine: SCHEDULED → CANCELLED ✅
        │   (COMPLETED or CANCELLED → CANCELLED ❌ raises 409)
        │
        ├── Update status in DB → CANCELLED
        │
        ├── Call GoogleService.cancel_event()
        │       └── Patch or Delete on Google Calendar
        │           (Google sends cancellation email to all)
        │
        ├── Write audit log ("CANCELLED")
        └── Return Meeting
```

---

## Phase 6 — Notifications & Email Alerts

Google handles email notifications automatically when `sendUpdates="all"` is set.

### What Google Sends Automatically

| Action | Who Gets Notified | Email Type |
|--------|-------------------|------------|
| Event created | All attendees | Calendar invite |
| Event updated (reschedule) | All attendees | Updated invite |
| Event cancelled (soft) | All attendees | Cancellation notice |
| Event deleted | All attendees | Cancellation notice |

### How Attendees Are Set

```python
"attendees": [
    {"email": "candidate@example.com"},       # from candidate_email field
    {"email": "interviewer@hospital.com"},    # from participants list
]
```

> **Tip:** The **organiser** (whose tokens we use) is added automatically by Google.  
> You only need to list the guests.

### `sendUpdates` Options

| Value | Behaviour |
|-------|-----------|
| `"all"` | Email everyone (used in this project) |
| `"externalOnly"` | Only email people outside your Google Workspace |
| `"none"` | No emails sent |

### Custom Notifications (Advanced)

You can add custom popup/email reminders to the event body:

```python
body["reminders"] = {
    "useDefault": False,
    "overrides": [
        {"method": "email", "minutes": 1440},  # email 24 hours before
        {"method": "popup", "minutes": 30},    # popup 30 min before
    ],
}
```

> This is not currently implemented but can be added to `_create_event_sync()`.

---

## Error Handling & Retry Logic

### Retry on Failure

Google APIs sometimes fail due to network issues. The project uses **tenacity** to auto-retry:

```python
@retry(
    stop=stop_after_attempt(3),             # try max 3 times
    wait=wait_exponential(min=1, max=8)     # wait 1s, then 2s, then 4s between tries
)
def _create_event_sync(self, ...):
    ...
```

### Graceful Degradation

If Google API fails, the **meeting is still saved** in the DB. The Google link is just left empty:

```python
try:
    result = await google_service.create_event_with_meet(...)
    meet_link = result["meet_link"]
    google_event_id = result["event_id"]
except Exception as exc:
    logger.warning("google_meet_creation_skipped", reason=str(exc))
    # meet_link and google_event_id remain None
    # meeting is still created successfully
```

### Custom Exception

```python
# app/exceptions.py
class GoogleAPIError(DomainError):
    def __init__(self, message: str, upstream: str = ""):
        super().__init__(message)
        self.upstream = upstream   # original Google error message
```

This maps to HTTP **502 Bad Gateway** in `app/main.py`:

```python
@app.exception_handler(GoogleAPIError)
async def google_error_handler(request, exc):
    return JSONResponse(status_code=502, content={"detail": str(exc)})
```

---

## File-by-File Code Reference

```
backend/
├── app/
│   ├── core/
│   │   └── config.py              ← GOOGLE_CLIENT_ID, SECRET, REDIRECT_URI settings
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py            ← OAuth login + callback endpoints
│   │       └── meetings.py        ← CRUD endpoints that trigger Google sync
│   │
│   ├── services/
│   │   ├── google_service.py      ← ALL Google API calls live here
│   │   └── meeting_service.py     ← Business logic, calls google_service
│   │
│   ├── models/
│   │   └── meeting.py             ← Meeting model stores google_event_id + meet_link
│   │
│   └── exceptions.py              ← GoogleAPIError exception class
│
└── .env                           ← Your Google credentials go here
```

### What Each File Does

| File | Responsibility |
|------|---------------|
| `config.py` | Reads Google credentials from `.env` into a typed `Settings` object |
| `auth.py` | Step 1: redirect to Google login. Step 2: exchange code for tokens, save to DB |
| `google_service.py` | The only file that talks to Google. Has create/update/cancel event methods |
| `meeting_service.py` | Decides WHEN to call Google (create meeting → create event, cancel → cancel event) |
| `meetings.py` | HTTP endpoints. Calls `meeting_service` which calls `google_service` |
| `meeting.py` (model) | Stores `google_event_id` and `meet_link` columns in DB |

---

## Data Flow Diagrams

### Full Create Meeting Flow

```
Recruiter fills form → clicks "Save & Schedule"
        │
        ▼
POST /api/v1/meetings
{
  candidate_name: "Maria Garcia",
  position: "Nurse",
  host_id: "user-uuid",
  date: "2026-03-24T10:00:00Z",
  duration_mins: 30,
  location_type: "GOOGLE_MEET",
  participants: ["dr.smith@hospital.com"]
}
        │
        ▼
┌─ meeting_service.py ──────────────────────────────────────────┐
│                                                                │
│  1. Load host's tokens from DB                                 │
│     SELECT google_tokens FROM users WHERE id = host_id         │
│                                                                │
│  2. location_type == GOOGLE_MEET? → YES                        │
│                                                                │
│  3. google_service.create_event_with_meet(                     │
│       summary  = "Interview: Maria Garcia - Nurse"             │
│       start    = 2026-03-24T10:00:00Z                          │
│       end      = 2026-03-24T10:30:00Z  (start + 30 mins)      │
│       attendees= ["dr.smith@hospital.com", "maria@gmail.com"]  │
│       tokens   = host's access_token                           │
│     )                                                          │
│                                                                │
│  4. Google returns:                                            │
│     event_id  = "abc123google"                                 │
│     meet_link = "https://meet.google.com/xyz-uvw-def"          │
│                                                                │
│  5. Save Meeting to DB with meet_link + google_event_id        │
│  6. Write AuditLog: action="CREATED"                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
Response to UI:
{
  id: "meeting-uuid",
  meet_link: "https://meet.google.com/xyz-uvw-def",
  status: "SCHEDULED",
  ...
}
        │
        ▼
UI shows "Join Video Meeting" button with the meet_link
```

### State Machine (What Actions Are Allowed)

```
                   ┌──────────────┐
                   │   SCHEDULED  │
                   └──────┬───────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
     ┌──────────┐  ┌────────────┐  ┌───────────┐
     │COMPLETED │  │ CANCELLED  │  │RESCHEDULED│
     │(terminal)│  │ (terminal) │  └─────┬─────┘
     └──────────┘  └────────────┘        │
                                         │
                                         ▼
                                   ┌──────────────┐
                                   │  SCHEDULED   │
                                   └──────────────┘
```

- **COMPLETED** and **CANCELLED** are final — no further changes allowed
- **RESCHEDULED** → back to **SCHEDULED** (loop allowed)

---

## Common Mistakes & Fixes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `conferenceDataVersion=1` missing | No Meet link in response | Always pass `conferenceDataVersion=1` to `events().insert()` |
| `access_type="offline"` missing | No `refresh_token` | Add `access_type="offline"` to `authorization_url()` call |
| `prompt="consent"` missing | Google skips consent, no refresh token issued | Add `prompt="consent"` |
| Using sync `googleapiclient` in async FastAPI | Server freezes under load | Wrap in `run_in_threadpool()` |
| `requestId` reused for conference | Google returns existing event instead of new one | Use `str(uuid.uuid4())` every time |
| Tokens not refreshed | API calls fail after 1 hour | Store refresh_token, use google-auth library's auto-refresh |
| Missing Calendar API scope | 403 error from Google | Add `auth/calendar` and `auth/calendar.events` to SCOPES |
| Wrong redirect URI | `redirect_uri_mismatch` from Google | Must exactly match what's in Google Cloud Console |

---

## Quick Reference Cheat Sheet

### Environment Variables

```env
GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxx
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
GOOGLE_CANCEL_MODE=soft    # or "delete"
```

### OAuth Scopes Needed

```
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
openid
email
profile
```

### Key API Endpoints in This Project

| Endpoint | What It Does to Google |
|----------|----------------------|
| `GET /api/v1/auth/google` | Starts OAuth login |
| `GET /api/v1/auth/google/callback` | Exchanges code → tokens, saves to DB |
| `POST /api/v1/meetings` | Creates Google Calendar event + Meet link |
| `PATCH /api/v1/meetings/{id}` | Updates Google Calendar event time |
| `POST /api/v1/meetings/{id}/cancel` | Cancels Google Calendar event |

### Key Google API Methods Used

```python
# Create event with Meet
service.events().insert(calendarId="primary", body=body, conferenceDataVersion=1, sendUpdates="all")

# Update event
service.events().patch(calendarId="primary", eventId=id, body=patch, sendUpdates="all")

# Cancel (soft)
service.events().patch(calendarId="primary", eventId=id, body={"status": "cancelled"}, sendUpdates="all")

# Delete (hard)
service.events().delete(calendarId="primary", eventId=id, sendUpdates="all")
```

### Python Packages Required

```toml
google-api-python-client   # main Google API client
google-auth-oauthlib       # OAuth flow helper
google-auth-httplib2       # HTTP transport for Google auth
tenacity                   # retry logic
```

---

## Summary — Integration Checklist

```
Phase 1 — Google Cloud
  ☐ Create project
  ☐ Enable Google Calendar API
  ☐ Configure OAuth consent screen with correct scopes
  ☐ Add test users
  ☐ Create OAuth 2.0 credentials
  ☐ Add Client ID + Secret to .env

Phase 2 — OAuth Login
  ☐ /auth/google → redirects to Google
  ☐ /auth/google/callback → exchanges code, saves tokens
  ☐ access_type="offline" → gets refresh_token
  ☐ Tokens stored per user in DB

Phase 3 — Create Event
  ☐ Load host tokens from DB
  ☐ Build event body with conferenceData
  ☐ conferenceDataVersion=1 in insert call
  ☐ Extract meet_link from response
  ☐ Store event_id + meet_link in Meeting row

Phase 4 — Update Event
  ☐ On reschedule, build patch with new start/end
  ☐ Use events().patch() with sendUpdates="all"

Phase 5 — Cancel Event
  ☐ Soft cancel: patch status="cancelled"
  ☐ Hard cancel: events().delete()
  ☐ sendUpdates="all" sends emails

Phase 6 — Error Handling
  ☐ Wrap Google calls in try/except
  ☐ Use tenacity @retry for transient failures
  ☐ Fall back gracefully if Google is unavailable
  ☐ Log errors with structured logger
```
