# CLAUDE.md — Chandramonians Web
## Dulalpur Chandramoni High School (DCMHS) Alumni & Student Portal

> **Read this file at the start of every session.** It gives you the full context needed to work on this codebase effectively without re-exploring from scratch.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **School** | Dulalpur Chandramoni High School |
| **Abbreviation** | DCMHS (use this everywhere — NOT DPCMHS) |
| **Association** | Chandramonians Alumni Association |
| **Owner** | proffesergio (bhnbids@gmail.com) |
| **Mission** | A single gateway for students, alumni, staff, and the Association Committee |
| **Primary Language** | English (Bengali strings are acceptable in content, not in code) |
| **Timezone** | Asia/Dhaka (configured in settings.py) |

---

## 2. Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Django 5.1.6 | Traditional MVT + REST endpoints |
| Database | SQLite (dev) / PostgreSQL (prod) | Configured via `DATABASE_URL` env var |
| ORM | Django ORM | No raw SQL unless absolutely necessary |
| Auth | Custom email-based (`app.EmailBackend`) | Email = username field |
| Admin UI | django-jazzmin | Themed Django admin panel |
| API Layer | Django REST Framework | For HTMX AJAX endpoints only |
| Frontend | Bootstrap 5.3 + HTMX + Alpine.js | No React/Next.js |
| Charts | ApexCharts | Already in `static/assets/plugins/apexchart/` |
| Tables | DataTables | Already in `static/assets/plugins/datatables/` |
| AI | Google Gemini Flash | `webapp/ai_service.py` wrapper |
| Sheets Sync | gspread + google-auth | `webapp/sheets_sync.py` |
| Scheduler | django-apscheduler | Hourly Sheets sync job |
| Static Files | WhiteNoise | Production static serving |
| Env Vars | django-environ | `.env` file |
| WSGI | Gunicorn | `Procfile` |
| Deployment | Railway.app (recommended) | Push to GitHub → auto-deploy |

---

## 3. User Roles & Permissions

```
user_type '1' = HOD        → /hod/*  — full admin, content management, payment records
user_type '2' = Staff      → /Staff/* — notifications, upload exam suggestions
user_type '3' = Alumni     → /Alumni/* — membership, directory, job board, own payment
user_type '4' = Student    → /edu/*  — AI tutor, daily challenge, exam suggestions
```

**Role check pattern** (always use this in views, not `is_staff`):
```python
if request.user.user_type != '1':
    messages.error(request, 'Access denied.')
    return redirect('landing')
```

**After login, users redirect to:**
- HOD → `hod_home`
- Staff → `staff_home`
- Alumni → `alumni_home`
- Student → `edu_home`

---

## 4. Directory Structure

```
chandramonians-web/
├── app/
│   ├── models.py          ← ALL database models live here
│   ├── admin.py           ← Admin registrations with filters/search
│   ├── views.py           ← Core auth views only (login, register, logout, profile)
│   ├── EmailBackend.py    ← Custom email authentication backend
│   ├── apps.py            ← Starts background scheduler on server boot
│   └── urls.py            ← App-level URL patterns (auth + home)
│
├── webapp/
│   ├── settings.py        ← All configuration, env-driven
│   ├── urls.py            ← Master URL router (includes all sub-routers)
│   ├── Hod_Views.py       ← HOD admin feature views
│   ├── Staff_Views.py     ← Staff dashboard views
│   ├── Alumni_Views.py    ← Alumni portal views
│   ├── Public_Views.py    ← Public-facing pages (no login required)
│   ├── Education_Views.py ← Student educational hub views
│   ├── Member_Views.py    ← Payment records + alumni directory views
│   ├── ai_service.py      ← Gemini AI wrapper (swap provider here only)
│   ├── sheets_sync.py     ← Google Sheets → MembershipPayment sync
│   ├── scheduler.py       ← APScheduler job registration
│   └── forms.py           ← Django forms
│
├── templates/
│   ├── base.html          ← Base layout with Bootstrap 5.3 + HTMX + Alpine.js
│   ├── partials/
│   │   ├── header.html    ← Sticky navbar (role-aware links)
│   │   ├── sidebar.html   ← Dashboard sidebar (role-aware)
│   │   ├── footer.html    ← Site footer
│   │   └── messages.html  ← Django flash messages display
│   ├── public/            ← Public pages (home, about, news, events, gallery, contact)
│   ├── education/         ← Student hub (AI tutor, challenge, suggestions, leaderboard)
│   ├── members/           ← Payment records, directory, job board, mentorship
│   ├── hod/               ← HOD admin templates
│   ├── Alumni/            ← Alumni portal templates
│   └── Staff/             ← Staff templates
│
├── static/assets/         ← Frontend assets (Bootstrap, jQuery, ApexCharts, DataTables)
├── media/                 ← User-uploaded files (profile pics, suggestions, gallery)
├── .env                   ← Secrets (never commit — listed in .gitignore)
├── .env.example           ← Template for .env (safe to commit)
├── requirements.txt       ← Python dependencies
├── Procfile               ← Gunicorn start command for Railway/Render
└── CLAUDE.md              ← This file
```

---

## 5. Naming Conventions

### Python / Django
| Element | Convention | Example |
|---------|-----------|---------|
| Models | PascalCase | `MembershipPayment`, `DailyChallenge` |
| View functions | `snake_case_view` | `payment_records_view`, `edu_home_view` |
| View files | PascalCase + `_Views.py` | `Public_Views.py`, `Member_Views.py` |
| URL names | `snake_case` | `payment_records`, `edu_home` |
| Template dirs | `lowercase/` | `public/`, `education/` |
| Template files | `snake_case.html` | `payment_records.html`, `ai_tutor.html` |
| HTMX partials | `partials/name.html` | `partials/chat_bubble.html` |
| Forms | PascalCase + `Form` | `UserRegisterForm`, `ContactForm` |
| Settings keys | `UPPER_SNAKE_CASE` | `GEMINI_API_KEY`, `GOOGLE_SHEET_ID` |

### URL Patterns
- Public pages: `/about/`, `/news/`, `/events/` (lowercase with trailing slash)
- HOD panel: `/hod/feature/` (lowercase, hyphen for multi-word)
- Alumni portal: `/Alumni/Feature/` (PascalCase, matching existing convention)
- Staff panel: `/Staff/Feature/` (PascalCase, matching existing convention)
- Student hub: `/edu/feature/` (lowercase)

---

## 6. Key Models Reference

```python
# Authentication
CustomUser          # email-based auth, user_type field (1-4)

# Original models (existing)
Alumni              # +profession, +company, +linkedin_url, +bio (new fields)
Staff
Student
SessionYear
StaffNotification
ApplyForMembership  # status: 0=pending, 1=approved, 2=denied
AlumniFeedback

# New: Payments
MembershipPayment   # synced from Google Sheets, sheet_row_id is unique key

# New: Education
Subject             # grade choices: CLASS_6_8, SSC, HSC
ExamSuggestion      # is_published flag controls student visibility
DailyChallenge      # one per date (unique=True on date field)
StudentProgress     # gamification: XP, streak, challenges_completed

# New: Public content
NewsArticle         # slug field, is_published flag, category choices
Event               # event_date, is_published flag
GalleryPhoto        # category for filtering
CommitteeMember     # order field for display sorting

# New: AI
AIChat              # log of all AI tutor conversations
```

---

## 7. How to Add a New Feature

Follow this checklist every time:

1. **Model** (if data is needed):
   - Add to `app/models.py`
   - Register in `app/admin.py` with `list_display`, `list_filter`, `search_fields`
   - Run: `python manage.py makemigrations && python manage.py migrate`

2. **View**:
   - Add to the appropriate `webapp/*_Views.py` file (or create a new one)
   - Always check `user_type` at the top of protected views
   - Use `@login_required(login_url='/login')` decorator

3. **URL**:
   - Add to `webapp/urls.py`
   - Choose a descriptive `name=` for use in templates with `{% url 'name' %}`

4. **Template**:
   - Create in the appropriate `templates/` subdirectory
   - Extend `base.html`: `{% extends 'base.html' %} {% block content %}...{% endblock %}`
   - Use existing Bootstrap 5.3 classes and component patterns

5. **Test**:
   - Register/login as the relevant user type
   - Verify the role check works (try accessing as wrong role)
   - Check mobile layout at 375px

---

## 8. Environment Variables Reference

```bash
# Required for production
SECRET_KEY=             # Django secret key (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=False             # Always False in production
ALLOWED_HOSTS=          # Comma-separated: yoursite.com,www.yoursite.com
DATABASE_URL=           # postgres://user:pass@host:5432/dbname (from Railway)

# Required for features
GEMINI_API_KEY=         # From https://aistudio.google.com (free)
GOOGLE_CREDS_JSON=      # Base64-encoded service account JSON
GOOGLE_SHEET_ID=1X4T058McT6GTnmUyu1OsmLua9BwKPEz03Rr-rbcMRvs

# Optional (for email/contact form)
EMAIL_HOST_USER=        # Gmail address
EMAIL_HOST_PASSWORD=    # Gmail App Password (not your main password)

# Development defaults (safe for local use only)
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 9. Google Sheets Sync Setup (One-Time)

The member payment data lives in Google Sheets. The website syncs it hourly automatically.

**Sheet structure expected:**
- Tab 0 (index 0): Life Members — columns: Name, Payment Date, Amount, Receipt No, Batch Year, Phone, Status
- Tab 1 (index 1): General Members — same columns

**Setup steps:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable **Google Sheets API** and **Google Drive API**
3. Go to **Service Accounts** → Create service account → Download JSON key
4. Base64-encode the JSON file:
   - Windows PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))`
   - Linux/Mac: `base64 credentials.json`
5. Paste the result as `GOOGLE_CREDS_JSON` in your `.env` file
6. **Share the Google Sheet** with the service account email (looks like `name@project.iam.gserviceaccount.com`) — give it **Viewer** access
7. The scheduler syncs automatically every hour. HOD can also click "Sync Now" on the payments page.

**To adjust column mappings**, edit the `field_map` dict in `webapp/sheets_sync.py`.

---

## 10. AI Service Usage

The AI tutor uses Google Gemini Flash (free tier, ~1500 requests/day).

```python
from webapp.ai_service import get_tutoring_response, get_problem_solution

# Tutoring chat
answer = get_tutoring_response("What is the Pythagorean theorem?", subject="Mathematics")

# Problem solver
solution = get_problem_solution("Solve: 2x + 5 = 13", subject="Mathematics")
```

**To swap AI providers** (e.g., to OpenAI or Claude API in the future):
- Only modify `webapp/ai_service.py`
- Keep the same function signatures: `get_tutoring_response(question, subject)` and `get_problem_solution(problem, subject)`
- All views call these functions — no other files need changing

**Rate limit note:** Free Gemini Flash allows ~1,500 requests/day. If the school grows, upgrade to paid tier or implement daily query limits per user via `StudentProgress.ai_queries_used`.

---

## 11. Running Locally

```bash
# 1. Clone and enter project
git clone <repo-url>
cd chandramonians-web

# 2. Create virtual environment
python -m venv env
env\Scripts\activate          # Windows
# source env/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac
# Edit .env — set SECRET_KEY at minimum

# 5. Run migrations
python manage.py migrate

# 6. Create superuser (HOD)
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

# Open: http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

## 12. Deployment (Railway.app)

1. Push code to a GitHub private repository
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Railway detects `Procfile` and runs `gunicorn webapp.wsgi:application`
4. Click **+ New** → **Database** → **Add PostgreSQL** → copy the `DATABASE_URL`
5. Set environment variables in Railway dashboard (all from `.env.example`)
6. Railway auto-deploys on every `git push` to `main`

**Pre-deploy checklist:**
```bash
python manage.py check --deploy   # Must pass with 0 warnings
python manage.py collectstatic    # Collect static files
```

---

## 13. Known Issues & Tech Debt

- [ ] `AlumniFeedback.updated_at` uses `auto_now_add` instead of `auto_now` — fix in next migration
- [ ] `Hod_Views.replyFeedback` has a bug: `AlumniFeedback.objects.get(feedback_id)` should be `.get(id=feedback_id)` — fix before enabling feedback reply feature
- [ ] `Student` model has `USERNAME_FIELD` and `REQUIRED_FIELDS` — these are AbstractUser attributes and don't belong on Student; remove them
- [ ] No email verification on registration — add for production
- [ ] No rate limiting on AI tutor endpoint — add `ai_queries_used` check (e.g., max 20/day for free tier)
- [x] Templates upgraded to Bootstrap 5.3 + HTMX + Alpine.js
- [ ] `static/assets/` contains jQuery loaded twice in some templates — deduplicate
- [ ] No test suite yet — add `app/tests.py` before production launch

---

## 14. Feature Development Status

| Feature | Status |
|---------|--------|
| Custom auth (email-based) | ✅ Done |
| HOD alumni/staff CRUD | ✅ Done |
| Membership applications | ✅ Done |
| Alumni feedback system | ✅ Done (has bug in reply — see §13) |
| Staff notifications | ✅ Done |
| Security hardening (env vars, HSTS) | ✅ Done (this session) |
| django-jazzmin admin theme | ✅ Configured (install dep + migrate) |
| New models (8 models) | ✅ Written (run migrations) |
| Google Sheets sync service | ✅ Written (needs API credentials) |
| AI tutor service | ✅ Written (needs GEMINI_API_KEY) |
| Public views (home, news, events) | ✅ Written (needs templates) |
| Student educational hub views | ✅ Written (needs templates) |
| Member/payment views | ✅ Written (needs templates) |
| Templates: public/ | ✅ Done |
| Templates: education/ | ✅ Done |
| Templates: members/ | ✅ Done |
| Bootstrap 5.3 base template | ✅ Done |
| Django i18n EN/BN (bilingual) | ✅ Done — 159 strings, language switcher in nav + sidebar |
| Deployment to Railway | ⏳ Pending (Phase 8) |
