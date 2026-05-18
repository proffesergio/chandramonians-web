Chandramonians Web — Full Production Roadmap

Dulalpur Chandramoni High School Alumni & Student Hub

---

Context

Existing Django 5.1 codebase for the Alumni Association of Dulalpur Chandramoni High School (DCMHS).
School abbreviation: DCMHS. Association name: Chandramonians.
Currently has: custom email auth, 4 user roles (HOD/Staff/Alumni/Student), membership workflow,
feedback system, basic CRUD for alumni/staff.

Goal: Transform into a world-class, production-ready portal that serves:

- Students — daily study hub, AI tutoring, exam prep, gamified learning
- Alumni — networking, job board, mentorship, membership management
- Staff/HOD — admin panel, content management, member payment records
- Association Committee — showcase, event management, financial transparency

Confirmed decisions:

- Stack: Keep Django + modernize (Bootstrap 5 + HTMX + Alpine.js)
- AI: Google Gemini Flash (free tier) for tutoring, problem solving, content generation
- Google Sheets: Auto-sync hourly → PostgreSQL → website payment display
- School name: Dulalpur Chandramoni High School (fix "DPCMHS" → "DCMHS" everywhere)

---

Architecture Overview

chandramonians-web/
├── webapp/ ← Django project (settings, main urls, role views)
│ ├── settings.py ← Env-driven config
│ ├── urls.py ← Master URL routing
│ ├── Hod_Views.py ← HOD admin views (extend existing)
│ ├── Staff_Views.py ← Staff views (extend existing)
│ ├── Alumni_Views.py ← Alumni portal views (extend existing)
│ ├── Public_Views.py ← NEW: public-facing pages
│ ├── Education_Views.py← NEW: student educational hub
│ ├── Member_Views.py ← NEW: member directory & payment records
│ ├── ai_service.py ← NEW: Gemini AI wrapper (isolated, swappable)
│ ├── sheets_sync.py ← NEW: Google Sheets sync service
│ └── forms.py ← Extend with new forms
├── app/
│ ├── models.py ← Extend with 8 new models
│ └── views.py ← Core auth views (clean up dead code)
├── templates/
│ ├── public/ ← NEW: public page templates
│ ├── education/ ← NEW: student hub templates
│ ├── members/ ← NEW: member portal templates
│ ├── hod/ (existing) ← Extend
│ ├── Alumni/ (existing)← Extend
│ ├── partials/ ← Modernize header/sidebar/footer
│ └── base.html ← Modernize to Bootstrap 5.3
├── static/assets/ ← Add HTMX, Alpine.js
├── .env ← SECRET_KEY, DB, API keys (never commit)
├── .env.example ← Template for .env (commit this)
├── .gitignore ← NEW: exclude .env, db.sqlite3, media/, etc.
├── Procfile ← NEW: for Railway/Render deployment
└── CLAUDE.md ← NEW: this session's output

---

Feature Map (Research-Backed)

🌐 PUBLIC PAGES (anyone can visit)

┌───────────────────────────┬──────────────────────────────────────────┬──────────┐
│ Feature │ Why │ Priority │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Hero landing page │ First impression, showcase school pride │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ About the Association │ Committee credibility, mission statement │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ News & Articles │ Fresh content = daily reason to visit │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Events Calendar │ Reunions, school events, online events │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Photo Gallery │ Nostalgia drives alumni engagement │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Contact Form │ Reachability for Committee │ P0 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Alumni Spotlight │ "Featured alumnus" rotates monthly │ P1 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ School Statistics Counter │ "X alumni, Y staff, Z events" animated │ P1 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Social Media Integration │ Facebook/YouTube feed embed │ P1 │
├───────────────────────────┼──────────────────────────────────────────┼──────────┤
│ Achievement Wall │ Notable alumni achievements showcase │ P2 │
└───────────────────────────┴──────────────────────────────────────────┴──────────┘

🎓 STUDENT HUB (login required for Students)

Research insight: Shikho users spend 45-50 min/day. Duolingo's streak drove 3x retention.

┌──────────────────────────┬─────────────────────────────────────────────────────────────┬──────────┐
│ Feature │ Why │ Priority │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ AI Tutoring Chat │ Ask any academic question, get step-by-step answers │ P0 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Daily Study Challenge │ 1 fresh MCQ per subject per day → streak system │ P0 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Exam Suggestions │ SSC/HSC chapter-wise important questions from Staff/Alumni │ P0 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Study Streak & Points │ Gamification: daily login streak, XP points like Duolingo │ P0 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Subject-wise Leaderboard │ Weekly top students (anonymized optional) │ P1 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Exam Countdown Timer │ Days left to SSC/HSC shown on dashboard │ P1 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Newspaper Corner │ Curated links to Prothom Alo, Daily Star, Samakal, Jugantor │ P1 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Educational News Feed │ Aggregated education news (board notices, scholarships) │ P1 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Board Notice Aggregator │ Pull notices from Dinajpur Education Board website │ P1 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Study Timer (Pomodoro) │ 25-min focus timer with session tracking │ P2 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Subject Notes Library │ Staff/alumni upload notes, students download │ P2 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Past Question Papers │ SSC/HSC previous years' question papers │ P2 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ AI Problem Solver │ Paste a math/science problem, get solution with steps │ P2 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Flash Card Maker │ Create/practice flashcards for any subject │ P3 │
├──────────────────────────┼─────────────────────────────────────────────────────────────┼──────────┤
│ Peer Discussion Forum │ Students ask questions, reply to each other │ P3 │
└──────────────────────────┴─────────────────────────────────────────────────────────────┴──────────┘

🏆 ALUMNI PORTAL (login required for Alumni)

Research insight: Best alumni sites combine networking + giving + events + storytelling.

┌────────────────────────┬────────────────────────────────────────────────────────┬──────────┐
│ Feature │ Why │ Priority │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Alumni Dashboard │ Stats, upcoming events, recent news │ P0 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Membership Application │ Apply for Life/General membership (existing + improve) │ P0 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Payment Status View │ See own payment record synced from Google Sheets │ P0 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Alumni Directory │ Search by batch year, profession, location │ P1 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Mentorship Program │ Alumni mentor current students (signup + match) │ P1 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Job Board │ Post jobs/internships for students & fellow alumni │ P1 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Alumni Feedback System │ Send feedback to HOD (existing + improve) │ P1 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Personal Profile │ Extended: profession, company, LinkedIn URL, photo │ P1 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Reunion RSVP │ Register for events, pay online (optional) │ P2 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Alumni Stories │ Submit your own achievement/story for spotlight │ P2 │
├────────────────────────┼────────────────────────────────────────────────────────┼──────────┤
│ Volunteer Signup │ Sign up to mentor, judge events, donate books │ P2 │
└────────────────────────┴────────────────────────────────────────────────────────┴──────────┘

👨‍💼 HOD / ADMIN PANEL (HOD + Staff roles)

Research insight: Self-service admin reduces 80% of manual data work.

┌────────────────────────────────┬──────────────────────────────────────────────────┬──────────┐
│ Feature │ Why │ Priority │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Enhanced Dashboard │ Stats: total members, payments, active students │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Member Payment Records │ Google Sheets-synced Life/General member table │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Manual Sync Trigger │ Button to force-refresh from Google Sheets │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Alumni CRUD (existing) │ Keep and improve existing add/edit/delete │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Staff CRUD (existing) │ Keep and improve existing │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Membership Approval │ Approve/reject applications (existing + improve) │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Content Management │ Publish news articles, events, gallery photos │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Exam Suggestion Upload │ Add/edit/delete exam suggestions by subject │ P0 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Notice Board Manager │ Post school/association notices │ P1 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Staff Notifications (existing) │ Keep and improve │ P1 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Committee Member Profiles │ Manage association committee member display │ P1 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Bulk Email/Notification │ Send announcement to all alumni / all students │ P2 │
├────────────────────────────────┼──────────────────────────────────────────────────┼──────────┤
│ Analytics Dashboard │ Page views, active users, popular features │ P2 │
└────────────────────────────────┴──────────────────────────────────────────────────┴──────────┘

💳 PAYMENT RECORDS MODULE (Members + HOD)

Google Sheets ID: 1X4T058McT6GTnmUyu1OsmLua9BwKPEz03Rr-rbcMRvs

┌───────────────────────┬─────────────────────────────────────────────┬──────────┐
│ Feature │ Why │ Priority │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ Life Members table │ Searchable, filterable by batch/year/status │ P0 │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ General Members table │ Separate tab/view with same filtering │ P0 │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ Own payment status │ Alumni see only their own record │ P0 │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ Hourly auto-sync │ Cron job pulls from Sheets via gspread │ P0 │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ Export to CSV │ HOD can download payment report │ P1 │
├───────────────────────┼─────────────────────────────────────────────┼──────────┤
│ Payment receipt view │ Clean printable receipt format per member │ P2 │
└───────────────────────┴─────────────────────────────────────────────┴──────────┘

---

Tech Stack (Final Confirmed)

Backend: Django 5.1.6 (keep)
Database: PostgreSQL (prod) / SQLite (dev)
ORM: Django ORM
Auth: Custom email-based (keep + harden)
Admin: django-jazzmin (beautiful themed admin)
API Layer: Django REST Framework (for HTMX AJAX endpoints)
Frontend: Bootstrap 5.3 + HTMX + Alpine.js
Charts: ApexCharts (already in codebase)
Tables: DataTables (already in codebase)
AI: Google Gemini Flash (google-generativeai SDK)
Sheets: gspread + google-auth (service account)
Scheduler: django-apscheduler (hourly sync cron)
Static Files: WhiteNoise (production)
Env Vars: django-environ (.env file)
WSGI: Gunicorn (production)
Deployment: Railway.app (recommended) or Render.com

---

New Dependencies (add to requirements.txt)

django-environ==0.11.2 # .env file support
psycopg2-binary==2.9.9 # PostgreSQL
whitenoise==6.7.0 # Static files in production
gunicorn==22.0.0 # Production WSGI
django-jazzmin==3.0.0 # Beautiful admin theme
djangorestframework==3.15.2 # REST APIs for HTMX
django-htmx==1.19.0 # HTMX helpers
gspread==6.1.2 # Google Sheets API
google-auth==2.29.0 # Google auth
google-generativeai==0.7.2 # Gemini AI
django-apscheduler==0.7.0 # Cron jobs (Sheets sync)

---

New Models (app/models.py additions)

# --- Payment Records (synced from Google Sheets) ---

class MembershipPayment(models.Model):
MEMBER_TYPE = [('LIFE', 'Life Member'), ('GENERAL', 'General Member')]
STATUS = [('PAID', 'Paid'), ('PENDING', 'Pending'), ('PARTIAL', 'Partial')]
member_name = models.CharField(max_length=200)
member_type = models.CharField(max_length=10, choices=MEMBER_TYPE)
payment_date = models.DateField(null=True, blank=True)
amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
receipt_number = models.CharField(max_length=100, blank=True)
batch_year = models.CharField(max_length=20, blank=True)
phone = models.CharField(max_length=20, blank=True)
status = models.CharField(max_length=10, choices=STATUS, default='PAID')
sheet_row_id = models.IntegerField(unique=True)
last_synced_at = models.DateTimeField(auto_now=True)

# --- Educational Content ---

class Subject(models.Model):
name = models.CharField(max_length=100)
grade = models.CharField(max_length=20) # 'SSC', 'HSC', 'Class 6-8'
icon_class = models.CharField(max_length=50, default='fa-book')

class ExamSuggestion(models.Model):
subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
year = models.IntegerField()
title = models.CharField(max_length=200)
content = models.TextField()
file = models.FileField(upload_to='suggestions/', null=True, blank=True)
uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
created_at = models.DateTimeField(auto_now_add=True)
is_published = models.BooleanField(default=False)

class DailyChallenge(models.Model):
subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
question = models.TextField()
option_a = models.CharField(max_length=300)
option_b = models.CharField(max_length=300)
option_c = models.CharField(max_length=300)
option_d = models.CharField(max_length=300)
correct_option = models.CharField(max_length=1) # 'a', 'b', 'c', or 'd'
explanation = models.TextField(blank=True)
date = models.DateField(unique=True) # one challenge per day
created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

class StudentProgress(models.Model): # Gamification tracker
user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
total_xp = models.IntegerField(default=0)
current_streak = models.IntegerField(default=0)
longest_streak = models.IntegerField(default=0)
last_active_date = models.DateField(null=True)
challenges_completed = models.IntegerField(default=0)
ai_queries_used = models.IntegerField(default=0)

# --- Public Content ---

class NewsArticle(models.Model):
CATEGORY = [('EDU', 'Education'), ('ASSOC', 'Association'), ('GENERAL', 'General'), ('NOTICE', 'Notice')]
title = models.CharField(max_length=300)
slug = models.SlugField(unique=True)
excerpt = models.TextField(max_length=500)
content = models.TextField()
category = models.CharField(max_length=10, choices=CATEGORY)
cover_image = models.ImageField(upload_to='news/', null=True, blank=True)
author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
published_at = models.DateTimeField(auto_now_add=True)
is_published = models.BooleanField(default=False)

class Event(models.Model):
title = models.CharField(max_length=200)
description = models.TextField()
event_date = models.DateTimeField()
location = models.CharField(max_length=200)
cover_image = models.ImageField(upload_to='events/', null=True, blank=True)
registration_link = models.URLField(blank=True)
is_published = models.BooleanField(default=True)
created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

class GalleryPhoto(models.Model):
title = models.CharField(max_length=200, blank=True)
photo = models.ImageField(upload_to='gallery/')
category = models.CharField(max_length=100, blank=True)
uploaded_at = models.DateTimeField(auto_now_add=True)
uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

# --- AI Chat Log ---

class AIChat(models.Model):
user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
session_id = models.CharField(max_length=100)
question = models.TextField()
answer = models.TextField()
subject = models.CharField(max_length=100, blank=True)
created_at = models.DateTimeField(auto_now_add=True)

# --- Extend Alumni model (add to existing) ---

# profession, company, linkedin_url, bio fields in a new AlumniProfile or extend Alumni model

---

URL Structure (complete routing map)

# --- PUBLIC (no login) ---

/ → Public home (hero, news, events, stats)
/about/ → About DCMHS + Chandramonians
/news/ → News & notices list
/news/<slug>/ → Article detail page
/events/ → Upcoming events list
/gallery/ → Photo gallery
/contact/ → Contact form
/members/directory/ → Public alumni directory (name/batch only)

# --- AUTH ---

/login → Login (existing)
/register/ → Register (existing)
/signup/ → POST handler (existing)
/doLogin → POST handler (existing)
/doLogout → Logout (existing)
/profile → User profile (existing)

# --- STUDENT HUB (login required, user_type=4) ---

/edu/ → Student hub home (dashboard + streak)
/edu/tutor/ → AI tutoring chat (HTMX-powered)
/edu/challenge/ → Daily challenge (MCQ of the day)
/edu/suggestions/ → Exam suggestions list by subject
/edu/suggestions/<id>/ → Suggestion detail / download
/edu/newspapers/ → Curated newspaper & news links
/edu/leaderboard/ → Weekly XP leaderboard
/edu/timer/ → Pomodoro study timer

# --- ALUMNI PORTAL (login required, user_type=3) ---

/Alumni/Home → Alumni dashboard (existing, improve)
/Alumni/ApplyForMembership → Membership apply (existing)
/Alumni/SendApplication → POST handler (existing)
/Alumni/Feedback → Feedback (existing)
/Alumni/SendFeedback → POST handler (existing)
/Alumni/Payments/ → Own payment record (NEW)
/Alumni/Directory/ → Full alumni directory with filters (NEW)
/Alumni/Jobs/ → Job board (NEW)
/Alumni/Mentorship/ → Mentor signup form (NEW)

# --- HOD PANEL (login required, user_type=1) ---

/hod/home → HOD dashboard (existing, enhance)
/hod/alumni/... → Alumni CRUD (existing)
/hod/staff/... → Staff CRUD (existing)
/hod/alumni/membership\* → Membership approval (existing)
/hod/alumni/feedback → Feedback (existing)
/hod/payments/ → Payment records table (NEW)
/hod/payments/sync/ → Trigger manual Sheets sync (NEW)
/hod/content/news/ → Manage news articles (NEW)
/hod/content/events/ → Manage events (NEW)
/hod/content/gallery/ → Manage gallery (NEW)
/hod/content/suggestions/ → Manage exam suggestions (NEW)
/hod/content/challenges/ → Manage daily challenges (NEW)
/hod/committee/ → Manage committee member profiles (NEW)

# --- STAFF PANEL (login required, user_type=2) ---

/Staff/home → Staff dashboard (existing)
/Staff/Notification → Notifications (existing)
/Staff/mark_as_done/<status> → Mark done (existing)
/Staff/upload-suggestion/ → Upload exam suggestion (NEW)

---

Implementation Phases

Phase 0: Security & Hygiene (Session 1 — do first, ~2 hours)

1.  Add .gitignore (exclude .env, db.sqlite3, media/, staticfiles/, pycache)
2.  Create .env.example with all variable names documented
3.  Rewrite webapp/settings.py to use django-environ

- SECRET_KEY = env('SECRET_KEY')
- DEBUG = env.bool('DEBUG', default=False)
- DATABASES = {'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')}
- ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

4.  Add HSTS, X-Frame-Options, Secure Cookies settings
5.  Add whitenoise.middleware.WhiteNoiseMiddleware to MIDDLEWARE
6.  Create Procfile: web: gunicorn webapp.wsgi:application
7.  Run python manage.py check --deploy → fix all warnings
8.  Clean app/views.py: remove ~130 lines of commented-out dead code

Critical files: webapp/settings.py, requirements.txt, .gitignore (new), .env.example (new), Procfile (new)

---

Phase 1: Admin Panel Upgrade (Session 2, ~1 hour)

1.  Install django-jazzmin, configure in INSTALLED_APPS
2.  Add JAZZMIN_SETTINGS in settings.py:

- Site title: "Chandramonians Admin"
- Logo, brand color (school colors)
- Custom sidebar icons for each model
- Show stats cards on dashboard

3.  Register all existing models with custom admin classes (filters, search, list_display)
4.  HOD dashboard already works — jazzmin makes it beautiful automatically

Critical files: webapp/settings.py (jazzmin config), app/admin.py

---

Phase 2: New Models & Migrations (Session 3, ~1.5 hours)

1.  Add all 8 new models to app/models.py
2.  Run python manage.py makemigrations && python manage.py migrate
3.  Register new models in app/admin.py with appropriate admin classes
4.  Extend existing Alumni model with profession/company/linkedin_url/bio fields

Critical files: app/models.py, app/admin.py

---

Phase 3: Google Sheets Sync (Session 4, ~2 hours)

Create webapp/sheets_sync.py:

# Uses gspread with service account credentials from env var GOOGLE_CREDS_JSON

# Reads Life Members sheet (gid=0) and General Members sheet (gid=1966697716)

# Maps columns by header row to MembershipPayment fields

# Upsert by sheet_row_id

# Returns sync summary (added, updated, errors)

Create webapp/scheduler.py using django-apscheduler:

- Register job: sync_sheets() every 60 minutes
- Start scheduler in AppConfig.ready() in app/apps.py

ENV VARS NEEDED:

- GOOGLE_CREDS_JSON — service account JSON (base64 encoded)
- GOOGLE_SHEET_ID = 1X4T058McT6GTnmUyu1OsmLua9BwKPEz03Rr-rbcMRvs

Setup instruction for user:

1.  Go to Google Cloud Console → Service Accounts → Create
2.  Download JSON credentials → encode to base64 → paste in .env
3.  Share the Google Sheet with the service account email (Editor read access)

Critical files: webapp/sheets_sync.py (new), webapp/scheduler.py (new), app/apps.py

---

Phase 4: Public Pages (Session 5, ~3 hours)

Create webapp/Public_Views.py with views:

- home_view(request) — landing page with stats, news, events, gallery preview
- about_view(request) — about page
- news_list_view(request) — news list with category filter
- news_detail_view(request, slug) — article detail
- events_view(request) — events list with countdown
- gallery_view(request) — masonry photo grid
- contact_view(request) — contact form (sends email via Django email)

Templates: templates/public/ directory
Base: Bootstrap 5.3 hero with school photo, school colors

---

Phase 5: Student Educational Hub (Session 6-7, ~4 hours)

Create webapp/Education_Views.py:

- edu_home_view(request) — student dashboard (streak, XP, upcoming challenges)
- ai_tutor_view(request) — chat interface
- ai_tutor_ask(request) — HTMX POST endpoint → calls Gemini → returns HTML fragment
- daily_challenge_view(request) — show today's MCQ
- submit_challenge(request) — POST: check answer, award XP, update streak
- suggestions_view(request) — exam suggestions by subject
- leaderboard_view(request) — weekly XP leaderboard
- newspapers_view(request) — curated newspaper links

Create webapp/ai_service.py:
import google.generativeai as genai

# System prompt: You are an academic tutor for DCMHS students in Bangladesh.

# Answer in simple English. For math/science show step-by-step workings.

# Be encouraging and age-appropriate for high school students.

def get_tutoring_response(question: str, subject: str = "") -> str:
...

Gamification logic in submit_challenge:

- Correct answer → +10 XP
- Daily login (any page) → +2 XP
- Streak bonus: 7-day streak → +20 XP
- Update StudentProgress model

ENV VARS NEEDED:

- GEMINI_API_KEY — from Google AI Studio (aistudio.google.com, free)

---

Phase 6: Member Portal & Payment Display (Session 8, ~2 hours)

Create webapp/Member_Views.py:

- payment_records_view(request) — HOD: full table (Life + General, filterable, exportable)
- alumni_payment_view(request) — Alumni: own payment status only
- alumni_directory_view(request) — alumni directory with batch/profession filters
- job_board_view(request) — job listings
- mentorship_view(request) — mentorship signup

Payment display design:

- Two tabs: "Life Members" | "General Members"
- DataTable with: Name, Batch Year, Payment Date, Amount, Status badge (green/yellow/red)
- Search box, filter by year, export CSV button (HOD only)
- Alumni see only their own row highlighted

---

Phase 7: Modernize UI (Session 9-10, ~4 hours)

- Upgrade templates/base.html to Bootstrap 5.3 + HTMX CDN + Alpine.js CDN
- Rebuild templates/partials/header.html — sticky navbar, role-aware links, mobile hamburger
- Rebuild templates/partials/sidebar.html — role-aware sidebar with icons
- New templates/public/home.html — hero, stats counter, news grid, events, gallery preview
- Modernize all HOD, Alumni, Staff templates to match new base
- Add templates/education/ directory with student hub templates
- AI chat template: WhatsApp-style chat bubbles, HTMX auto-scroll
- Responsive mobile-first throughout

---

Phase 8: Deployment (Session 11, ~1 hour)

Railway.app deployment steps:

1.  Push code to GitHub (private repo)
2.  Connect Railway → New Project → Deploy from GitHub
3.  Add PostgreSQL plugin in Railway
4.  Set all environment variables in Railway dashboard
5.  Railway auto-runs Procfile: gunicorn webapp.wsgi:application
6.  Add custom domain (optional)

---

CLAUDE.md Content Outline

(This will be the actual CLAUDE.md written to the project root)

Sections:

1.  Project Identity — school name, association name, mission, user roles
2.  Tech Stack — every technology used and why
3.  Architecture — file structure map with explanation of each directory
4.  User Roles & Permissions — HOD > Staff > Alumni > Student, what each can access
5.  Naming Conventions — models (PascalCase), views (snake_case + \_view suffix), URLs (kebab-case), templates (snake_case.html), CSS classes (BEM-like)
6.  How to Add a New Feature — checklist: model → migration → view → URL → template
7.  Environment Variables — full reference table
8.  Google Sheets Setup — step-by-step service account setup
9.  AI Service — how to use ai_service.py, how to swap providers
10. Running Locally — setup + run commands
11. Deployment Checklist — pre-deploy checks
12. Known Issues / Tech Debt — things to fix in future sessions

---

Files to Create/Modify (complete list)

┌─────────────────────────────────┬──────────────────────────────┬───────┐
│ File │ Action │ Phase │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ CLAUDE.md │ Create │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ .gitignore │ Create │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ .env.example │ Create │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ Procfile │ Create │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ requirements.txt │ Modify (add deps) │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/settings.py │ Rewrite (env-driven) │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ app/views.py │ Clean dead code │ P0 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ app/admin.py │ Modify (register all models) │ P1 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ app/models.py │ Modify (add 8 models) │ P2 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/sheets*sync.py │ Create │ P3 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/scheduler.py │ Create │ P3 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ app/apps.py │ Modify (start scheduler) │ P3 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/Public_Views.py │ Create │ P4 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/urls.py │ Modify (add all new routes) │ P4 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/Education_Views.py │ Create │ P5 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/ai_service.py │ Create │ P5 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ webapp/Member_Views.py │ Create │ P6 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/base.html │ Rewrite (Bootstrap 5.3) │ P7 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/partials/header.html │ Rewrite │ P7 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/partials/sidebar.html │ Rewrite │ P7 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/public/*.html │ Create (6 files) │ P4+P7 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/education/\_.html │ Create (6 files) │ P5+P7 │
├─────────────────────────────────┼──────────────────────────────┼───────┤
│ templates/members/\*.html │ Create (3 files) │ P6+P7 │
└─────────────────────────────────┴──────────────────────────────┴───────┘

---

Management Instructions for You (the owner)

Daily Operations

- Add news article: Login as HOD → Admin Panel → Content → News → Add Article → fill form → Publish
- Add event: Login as HOD → Admin Panel → Content → Events → Add Event
- Upload exam suggestion: Login as HOD or Staff → Admin → Suggestions → Add Suggestion
- Check payment records: Login as HOD → Payments → records auto-sync hourly. Click "Sync Now" to force refresh.
- Approve membership: Login as HOD → Membership Applications → Approve/Deny

Google Sheets Sync Setup (one-time)

1.  Go to Google Cloud Console (https://console.cloud.google.com)
2.  Create new project → Enable Google Sheets API + Google Drive API
3.  Create Service Account → Download JSON credentials
4.  Base64 encode the JSON: base64 credentials.json
5.  Paste the result as GOOGLE_CREDS_JSON in your .env file
6.  Share your Google Sheet with the service account email (looks like xxx@project.iam.gserviceaccount.com) — give it Viewer access
7.  The website will now sync automatically every hour

AI Tutoring Setup (one-time)

1.  Go to Google AI Studio (https://aistudio.google.com)
2.  Sign in with Google → Get API Key (free)
3.  Paste the key as GEMINI_API_KEY in your .env file
4.  Students can now use the AI tutor

Adding a New Committee Member

Login as HOD → Admin Panel → Committee → Add Member → Fill details → Save

Deploying Updates

1.  Go to Google Cloud Console (https://console.cloud.google.com)
2.  Create new project → Enable Google Sheets API + Google Drive API
3.  Create Service Account → Download JSON credentials
4.  Base64 encode the JSON: base64 credentials.json
5.  Paste the result as GOOGLE_CREDS_JSON in your .env file
6.  Share your Google Sheet with the service account email (looks like xxx@project.iam.gserviceaccount.com) — give it Viewer access
7.  The website will now sync automatically every hour

AI Tutoring Setup (one-time)

1.  Go to Google AI Studio (https://aistudio.google.com)
2.  Sign in with Google → Get API Key (free)
3.  Paste the key as GEMINI_API_KEY in your .env file
4.  Students can now use the AI tutor

Adding a New Committee Member

Login as HOD → Admin Panel → Committee → Add Member → Fill details → Save

Deploying Updates

After making changes:

1.  git add . → git commit -m "description" → git push
2.  Railway.app auto-deploys on push to main branch (zero downtime)

---

Verification Plan

1.  python manage.py check --deploy → 0 warnings
2.  Manual: Register as each user type (HOD, Staff, Alumni, Student) → verify correct dashboard redirect
3.  Manual: HOD triggers Sheets sync → MembershipPayment records appear in admin
4.  Manual: Student asks AI tutor a question → Gemini response appears
5.  Manual: Payment table shows Life/General tabs with search/filter working
6.  Manual: Daily challenge shows today's MCQ → submit answer → XP awarded → streak updated
7.  Manual: Unauth user visits / → public landing page with news/events visible
8.  Mobile: All pages responsive on 375px viewport
9.  Run python manage.py test → all tests pass

Railway Deployment

Once local testing passes, here's the complete Railway deployment guide:

1. Push to GitHub

git add .
git commit -m "Production-ready release — Phase 7 complete"
git remote add origin https://github.com/YOUR_USERNAME/chandramonians-web.git
git push -u origin main

If you already have a GitHub remote, just git push.

2. Create Railway project

1. Go to https://railway.app → New Project → Deploy from GitHub repo
1. Select your chandramonians-web repository → Railway detects the Procfile automatically

1. Add PostgreSQL

In your Railway project → click + New → Database → PostgreSQL
Railway creates the DB and gives you a DATABASE_URL automatically in the linked service.

4. Set environment variables

In Railway → your web service → Variables tab, add these (copy from your .env but change the values for production):

┌───────────────────┬────────────────────────────────────────────────────────────────────────────┐
│ Variable │ Value │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ SECRET_KEY │ Generate a new one (don't reuse dev key) │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ DEBUG │ False │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ ALLOWED_HOSTS │ yourapp.up.railway.app (Railway gives you this URL) │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ DATABASE_URL │ Auto-injected by Railway PostgreSQL plugin — leave empty, Railway links it │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ GEMINI_API_KEY │ Same as your .env │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ GOOGLE_CREDS_JSON │ Your base64-encoded Google service account JSON │
├───────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ GOOGLE_SHEET_ID │ 1X4T058McT6GTnmUyu1OsmLua9BwKPEz03Rr-rbcMRvs │
└───────────────────┴────────────────────────────────────────────────────────────────────────────┘

Generate a new production SECRET_KEY — run this locally:
! env\Scripts\python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

5. Add a start command

Railway reads your Procfile: web: gunicorn webapp.wsgi:application
Nothing else to configure — it just works.

6. Run migrations on Railway

After first deploy, open Railway → your service → Shell tab:
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

Or add a release command in Railway settings:
python manage.py migrate && python manage.py collectstatic --noinput

7. Get your live URL

Railway assigns yourapp.up.railway.app — you can add a custom domain in Settings → Domains.

---

Once you've run the install and can confirm runserver works without errors, paste any error output here and I'll fix it immediately.
