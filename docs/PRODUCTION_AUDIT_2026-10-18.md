# Production and development audit — 18 October 2026

The production super admin was created and successfully signed in on the live
site. The security and workflow fixes described below are local changes awaiting
deployment. No application code was deployed during this audit.

Email follow-up: a second super admin for `thechandramonians@gmail.com` was
created and verified through live sign-in. Local email routing now uses that
association inbox, and the expanded suite passes **42 Django tests**. See the
[admin guide](ADMIN_GUIDE.md) for the private credential-file location, SMTP
setup, deployment-access limitation, and social-login prerequisites. These
email changes have not been deployed; the earlier results below describe the
initial audit.

## Production access and verification

- Used `.env.local.production`; `.env.production.local` does not exist in this
  checkout. The production management helper supports both names.
- Preserved the existing owner alumni account. Created a separate admin account
  using the owner's Gmail plus address, with HOD role and active staff/superuser
  flags. Its email, username, and generated password are in
  `.vercel/super-admin-credentials.json`, excluded from Git and Vercel uploads.
- Verified the password through Django authentication against production
  PostgreSQL and through a real HTTPS login on the production domain.
- Community login redirected to `/hod/home`. `/admin/`, `/hod/home`,
  `/hod/payments/`, user administration, Event administration, Volunteer
  administration, alumni/staff lists, and HOD feedback all returned HTTP 200.
- `/health/` returned HTTP 200. All production migrations were applied.
- Database inventory: 134 membership rows, 11 alumni profiles, 0 subjects,
  0 daily challenges, and 0 exam suggestions.
- Visiting the alumni feedback route as HOD returned HTTP 500 on the existing
  deployment. The local role guard now rejects that wrong-role request with 403.
- Did not trigger a payment sync, send email, create sample public content,
  or exercise destructive actions on production.

## Fixed locally

| Severity | Finding | Change |
| --- | --- | --- |
| Critical | Legacy HOD routes lacked authentication/role checks, allowing unauthorized account and membership operations | Every HOD view requires authenticated HOD role through `app/permissions.py`; regression checks cover anonymous users and all other roles |
| High | Deletes and approvals ran on GET, allowing changes through links and bypassing CSRF protection | Deletes, updates, approvals, denials, notification writes, and feedback replies require POST; action controls submit CSRF-protected forms |
| High | A staff notification could be marked read by anyone who knew its ID | Staff role is required and notification queries are limited to the current staff account |
| Medium | Wrong-role visits to legacy alumni/staff pages could crash or reveal unrelated dashboard data | Added explicit role guards; missing alumni profiles return 404 where looked up |
| Medium | Feedback replies used an invalid ORM lookup and the submitted ID referred to the account rather than the feedback | Correct feedback ID, lookup, return page, and Bootstrap 5 modal attributes |
| Medium | Approved memberships displayed as denied in alumni history, and vice versa | Corrected status labels and made history modal controls work with Bootstrap 5 |
| Low | Duplicate alumni username warning raised an exception | Corrected the message call |

Account update/deletion handlers also restrict targets to the intended Alumni or
Staff role, preventing those handlers from changing a HOD account.

## Remaining priorities

| Priority | Problem and impact | Where to fix |
| --- | --- | --- |
| P0 | Publish the local access-control fixes. The existing deployment continues running the vulnerable handlers until a release | `webapp/Hod_Views.py`, `webapp/Staff_Views.py`, `webapp/Alumni_Views.py`, associated templates, `app/permissions.py` |
| P1 | Own-payment pages guess identity from names/first words. Changing a profile name can select another person's record, including private payment details | Add a verified payment-to-alumni relationship in `app/models.py`; use it in `Member_Views.alumni_own_payment_view` and `Alumni_Views.homeView`; reconcile records manually, without guessing |
| P1 | Django is pinned to unsupported 5.1.6, outside its security support period | Test a dependency upgrade in `requirements.txt`; Django 5.2 LTS is a supported candidate. [Official support table](https://www.djangoproject.com/download/#supported-versions) |
| P1 | Tutor requests use `gemini-1.5-flash`, shut down on 29 September 2025. Adding a key alone will not repair the tutor | Update `webapp/ai_service.py`, its SDK dependency, and model configuration; verify a supported model with the real provider. [Google release notes](https://ai.google.dev/gemini-api/docs/changelog#september-29-2025) |
| P1 | AI usage is counted but never limited; requests also award XP for provider error text | Add bounded requests, daily server-side quota enforcement, success/error handling, and input limits in `Education_Views.ai_tutor_ask` |
| P1 | Challenge completion lives only in the browser session; fresh sessions can repeat XP awards. Progress writes can race | Persist attempts with a unique `(user, challenge)` constraint; award XP transactionally; use `timezone.localdate()` consistently in `Education_Views.py` |
| P1 | Uploads use local `MEDIA_ROOT`; production URLs are only wired in DEBUG mode and Vercel function storage is not durable media storage | Configure an object storage backend and production media URLs in `webapp/settings.py`; verify gallery/profile/suggestion upload and download |
| P1 | Membership identity is tied to spreadsheet row numbers, so sorting/inserting/deleting rows can overwrite the wrong record or leave stale members | Introduce stable Member IDs and reconciliation rules in `sheets_sync.py` and CSV/Excel imports |
| P2 | Mentorship POST displays success without saving an application; job board is a placeholder | Implement models/forms/admin/workflow in `Member_Views.py`, or clearly disable applications until available |
| P2 | Membership form payment-method and membership-type selects have no names or saved model fields | Define valid membership/payment-method fields, validate them in a Django form, migrate the model, and update `templates/Alumni/membership_apply.html` |
| P2 | Leaderboard is all-time overall XP, rather than weekly per subject as planned; streaks update only on hub visits | Record dated/subject-specific XP events and derive intended weekly rankings and daily activity |
| P2 | Registration has no email verification; custom profile updates bypass password validators/session-preserving password change handling | Add email verification and login/signup throttling; use validated password change forms and `update_session_auth_hash` in `app/views.py` |

## Original phase status

| Phase in `pro-plan.md` | Status and remaining work |
| --- | --- |
| 0 — Security and hygiene | Partial. Environment-based settings and headers exist. Legacy permission gaps are patched locally; supported framework, password flows, login abuse protection, and production settings verification still need work |
| 1 — Admin panel | Core implemented and verified live. Account recovery access now exists. Content editors should use Django admin model permissions/groups |
| 2 — Models and migrations | Core models exist and production migrations are current. Planned jobs, mentorship applications, verified payment identity, and durable challenge attempts still need models |
| 3 — Sheets synchronization | Import/manual/secured scheduled-sync code exists and payments are populated. Current live Google credentials, last successful sync, external hourly schedule, and alerting were not verified; APScheduler is disabled on Vercel |
| 4 — Public pages | Core pages implemented; existing tests exercise their templates. Contact delivery needs a real SMTP verification; production uploads need object storage |
| 5 — Student hub | Partial. Pages exist, but production study content is empty. Retired AI model, missing quotas, challenge replay, Dhaka date boundaries, and planned weekly ranking behavior need work |
| 6 — Member portal | Partial. Directory, membership applications, payment filters/import/export exist. Own-payment identity, real job listings, and saved mentorship applications are incomplete |
| 7 — Interface | Public redesign and five interaction tests exist. Legacy Bootstrap 4 controls remain elsewhere; the feedback and membership history controls touched here now use Bootstrap 5. A fresh full mobile/browser accessibility pass remains |
| 8 — Deployment | Site is already on Vercel/PostgreSQL; original Railway instructions are stale. This audit's code fixes need deployment. Durable media, backup/restore exercises, integration monitoring, and a usable local CLI project connection remain operational work |

The newer `docs/COMMUNITY_ROADMAP.md` also deliberately leaves alumni map
connections, mentorship matching, moderated opportunities/news, scholarship
campaigns, and n8n follow-up workflows for future releases. They are proposals,
not features already delivered.

## Where the owner should test and update content

1. Sign in with the **email** at `https://www.chandramonians.com/admin/`.
   Retrieve the generated password from the ignored credential file and change
   it through Django admin's password-change page after the first sign-in.
2. Use `/hod/home` for the association overview and `/hod/payments/` for payment
   administration. Do not rely on name-matched individual payment statements.
3. Use `/admin/app/subject/`, `/admin/app/examsuggestion/`, and
   `/admin/app/dailychallenge/` to add reviewed learning content.
4. Use `/admin/app/newsarticle/`, `/admin/app/event/`,
   `/admin/app/volunteerapplication/`, and `/admin/app/committeemember/` for
   community content and applications. Configure storage before relying on uploads.
5. Release the permission fixes first, then verify correct-role access, rejected
   wrong-role access, approval status, feedback reply, and staff notifications.

## Validation and limits

An isolated Python 3.11 environment was created at `.vercel/audit311` because the
existing `.venv` runs Python 3.15 while its PostgreSQL/Pillow binaries target
Python 3.12. Its PostgreSQL driver could not load. Use the isolated environment
for the commands below, or recreate the normal environment with matching Python
and freshly installed dependencies.

```powershell
.vercel/audit311/Scripts/python.exe -B manage.py test --noinput
.vercel/audit311/Scripts/python.exe -B manage.py makemigrations --check --dry-run
node --test tests/community-interactions.test.cjs
git diff --check
```

The test suite runs on an isolated local test database, not production. No model
changes or new migrations are needed by these fixes. Credentials are ignored by
Git and excluded from deployment; the pre-existing modified `db.sqlite3` was
preserved. Vercel CLI could not retrieve this checkout's linked project settings,
so production variable names and deployment configuration were not independently
verified. This is a targeted code/flow audit, not a complete penetration test or
a new mobile visual/accessibility certification.

Final results: **37 Django tests passed; 5 JavaScript interaction tests passed**.
Migration drift check reported no changes, and `git diff --check` passed.
