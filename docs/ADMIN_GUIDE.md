# Chandramonians live administration

For the current production checks, local fixes awaiting deployment, and remaining
development phases, see the [18 October 2026 audit](PRODUCTION_AUDIT_2026-10-18.md).

## Association inbox and additional administrator

The official administration/contact address is **thechandramonians@gmail.com**.
The additional production super admin uses that email with username
`chandramonians_official_admin`. Its generated website password is stored locally
in `.vercel/association-admin-credentials.json`, excluded from Git and deployment.
Sign in with the **email** at `/admin/` or `/login`. This website password does
not grant access to the Gmail mailbox. The earlier administrator account remains.

`ADMIN_EMAIL` controls the public contact email link, contact-form recipient, and
Django's `ADMINS`/`MANAGERS` notification recipients. The authenticated SMTP sender
is configured independently, so the association receives messages even when an
approved sending service uses another address. Contact messages set the visitor's
validated address as Reply-To. Volunteers and membership applications continue
to be stored for review; this change does not add automatic notifications to
those workflows.

To send using the association's Gmail account, set these **Production** variables
in the Vercel project that owns `www.chandramonians.com`, then redeploy:

```dotenv
ADMIN_EMAIL=thechandramonians@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=thechandramonians@gmail.com
EMAIL_HOST_PASSWORD=YOUR_GMAIL_APP_PASSWORD
DEFAULT_FROM_EMAIL=thechandramonians@gmail.com
SERVER_EMAIL=thechandramonians@gmail.com
EMAIL_TIMEOUT=15
```

Store the app password as a secret. Gmail requires 2-Step Verification to create
an App Password; generate it from the Google account's security settings. Use it
for SMTP, rather than the normal Gmail or website password.
[Google's App Password instructions](https://support.google.com/mail/answer/185833?hl=en)

No SMTP credential was present in either local environment file at the time of
this update. Vercel access has since been restored and encrypted GitHub deployment
secrets are configured; see [push-to-production deployment](DEPLOYMENT.md).
The email code/settings changes still need deployment and a real delivery check
after SMTP is configured. The regression tests use an in-memory mail backend
and send no real messages.

## Google and other social sign-in

Public registration already exists at `/register/` and `/signup/` for Student
and Alumni accounts. Creating a super admin above fulfills the account request;
Google/Facebook/GitHub sign-in has **not** been activated by this update.

Adding social login requires a provider application and its OAuth Client ID and
Client Secret. A suitable Django integration is `django-allauth`, with a dedicated
provider, a verified-email/account-linking policy, and role-preserving adapters.
Google's production callback would be
`https://www.chandramonians.com/accounts/google/login/callback/` once that
integration is implemented. Register the exact callback in the provider's console;
do not expect the callback URL to work before implementation.
[Provider configuration](https://docs.allauth.org/en/latest/socialaccount/provider_configuration.html),
[Google provider](https://docs.allauth.org/en/latest/socialaccount/providers/google.html)

New social signups should receive an ordinary Student/Alumni role. Administrator
access is granted by an existing administrator, rather than from an email string
or a role selected on a public registration form. To add another administrator
online today, use **Custom users → Add**, save the new account, then edit it to
set **User type: HOD**, **Staff status**, **Superuser status**, and **Active**.

## Can I register at /admin/?

`/admin/` is a sign-in page, not a public account-registration page. Create the
first administrator using the command below against production PostgreSQL. Once
signed in, an existing superuser can create further accounts under **Custom users → Add**.
Public signup intentionally cannot grant admin or HOD access.

This guide is separate from the public, feature-focused README. The application
runs on Vercel; live records are in PostgreSQL. Creating an account in local
SQLite does **not** create it on the live site.

## Create a community super admin

Use a trusted local computer connected to production PostgreSQL. Vercel does
not provide a conventional SSH shell. Production Secret/Sensitive variables are
write-only; `vercel env pull` can return empty values for them. Obtain the DB
connection string from its provider dashboard instead.

This deployment uses Neon PostgreSQL. In the Neon console, click **Connect**,
select the production branch, database, compute, and role, then copy the
connection string into the local file below. Keep it private and preserve SSL
parameters. [Neon's connection guide](https://neon.com/docs/connect/connect-from-any-app)

1. Install the project requirements in a Python virtual environment.
2. Create `.env.production.local` in the repository root using your editor.
   It is ignored by Git. Add the actual production connection string:

   ```dotenv
   DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
   ```

   The helper also accepts `.env.local.production`, the filename already in this
   checkout. Both filenames are excluded from Git. If both exist,
   `.env.production.local` takes precedence.

3. Activate the environment and run:

   ```powershell
   python scripts/manage_production.py check --database default
   python scripts/manage_production.py createcommunityadmin --email YOUR_EMAIL --username YOUR_UNIQUE_USERNAME
   ```

   Enter a strong password at the hidden prompts. The command sets
   `is_staff=True`, `is_superuser=True`, and `user_type='1'` (HOD), enabling
   both administrative interfaces. It refuses existing accounts and weak
   passwords. No password is written into source or deployment logs.

4. Sign in with the email address at
   [Django administration](https://www.chandramonians.com/admin/).
   Use [community login](https://www.chandramonians.com/login) for the
   [HOD dashboard](https://www.chandramonians.com/hod/home).

On this Windows checkout, `.venv\Scripts\python.exe` can replace `python`.
The wrapper refuses SQLite and a missing production database URL.
For secret-manager automation, `--noinput` reads `DJANGO_SUPERUSER_PASSWORD`;
remove that temporary variable afterward. Do not add an admin-creation web
endpoint or create a superuser on every deployment.

## Existing accounts and permissions

Reset an existing account's password with a hidden prompt:

```powershell
python scripts/manage_production.py changepassword EXISTING_EMAIL
```

Email is this project's authentication identifier. A superuser created using
standard Django `createsuperuser` can still have the default Student community
role. In `/admin/`, open **Custom users** and set that account's **User type**
to **HOD** to enable the association dashboard. The new custom command sets
this automatically.

| Panel | What it manages |
| --- | --- |
| `/admin/` | Users, permissions, alumni, payments, news, events, gallery, committee, and study content |
| `/hod/home` | Community overview and association management pages |
| `/hod/payments/` | Sheets sync, Life/General records, Excel/CSV imports, and CSV export |

**Custom users → Add** now includes email and community role. Django admin
access additionally requires **Staff status** and relevant model permissions.
The community Staff role and Django Staff status are separate controls.
Reserve Superuser for the owner and a trusted recovery administrator.

Suggested groups: Membership team, Treasurer, News editor, Education team,
and Event coordinator. Groups constrain `/admin/` model permissions. Existing
HOD pages still grant broad access by HOD role; use Django admin groups for
people who should only manage one type of content.

Public signup accepts Student/Alumni only. Administrators create Staff/HOD
accounts. New Alumni signups now create a linked profile. Payment imports
alone do not create alumni profiles or logins.

Both directory views now supply the `alumni_list` expected by their templates.
Previously this mismatch displayed an empty state even when profile records existed.

## Restore the confirmed records

The owner confirmed the local backup's 134 memberships and 7 alumni profiles:

```powershell
python scripts/manage_production.py restore_community --source db.sqlite3 --dry-run
python scripts/manage_production.py restore_community --source db.sqlite3
```

The command adds missing rows, keeps existing live records, uses one transaction,
and rolls back on a conflicting username. Membership keys are
`(member_type, sheet_row_id)`; alumni are linked by email. Repeating a restoration
does not duplicate records. Dry-run rolls back its transaction.

Restored profile accounts have unusable passwords and no staff/superuser
privileges. Verify the alumnus's identity before setting a new password in admin.
Old passwords and privileges are never imported.

When the production secret is only available inside Vercel, run one explicit
restoration build:

```powershell
vercel deploy --prod --skip-domain --build-env RESTORE_COMMUNITY_FROM_SQLITE=1 --yes
```

Review aggregate counts in the build log, verify the pages, and promote that
deployment. Do not save the restoration flag as a permanent project variable.
Normal deployments run migrations only. Archive the historical SQLite backup
securely before removing it from future source distributions.

## Reconnect Google Sheets

During review, `GOOGLE_CREDS_JSON` was absent from Vercel. The hourly background
scheduler is deliberately disabled on Vercel. Restoration repairs today's data;
the connection and an external scheduler are needed for future automatic updates.

1. Create a Google service account and enable Google Sheets API. Share the
   spreadsheet with its `client_email` as **Viewer**. Keep the sheet private.
2. Base64-encode the service-account JSON key. Store the result as the Vercel
   Secret `GOOGLE_CREDS_JSON` for Production and, if intended, Preview. Use the
   dashboard or a secure local file; never paste credentials into chat or Git.
3. Set `GOOGLE_SHEET_ID` to the spreadsheet ID, rather than its full URL.
4. Set `GOOGLE_SHEET_LIFE_TAB` and `GOOGLE_SHEET_GENERAL_TAB` to exact tab names.
   Blank values use tabs 0 and 1. Names are safer if someone reorders tabs.
5. Redeploy, sign in as HOD, and click **Sync from Google Sheets** at
   `/hod/payments/`. Review counts and the public member directory.

Recognised headers include `Member's Name`, `Batch`, `Mobile Number`,
`Total Paid Amount` / `One Time Payment`, `Due date`, and `Payment Status`.
A title above the header is supported within the first ten rows. Unrecognised
headers and partial failures are reported. Unpaid becomes Pending, and
Partially paid becomes Partial.

Current imports identify members by row number. Avoid sorting, inserting, or
deleting rows until stable Member IDs replace that key. The existing My Payment
page uses approximate name matching; do not treat it as verified account
reconciliation. An explicit payment-to-alumni relationship is a priority upgrade.

Without Google credentials, download the sheet as Excel and use **Upload Excel**.
Tab names must include `Life` or `General`. CSV imports cover one selected
category. Neither import creates alumni accounts.

## Schedule updates with n8n

Host n8n separately or use n8n Cloud. No service is provisioned by this change.

1. Generate a long random token. Save it as Vercel Secret `CRON_SECRET` and in
   an n8n Header Auth credential, then redeploy.
2. Publish this workflow with timezone **Asia/Dhaka**:

   ```text
   Schedule Trigger
     → HTTP Request: POST https://www.chandramonians.com/tasks/sync-members/
     → IF success
       → save aggregate result
       → otherwise alert the designated maintainer
   ```

3. Send `Authorization: Bearer YOUR_CRON_SECRET`. Use one run at a time,
   bounded retries with backoff, and a request timeout above the site's 60-second
   function limit. Store the token in credentials, rather than workflow text.
4. The endpoint returns 403 for an invalid token, 503 when no token is configured,
   and 502 on sync failure. Successful responses contain aggregate counts only.

GET is also accepted for Vercel Cron's bearer authentication. No cron schedule
is activated by default; check your Vercel plan's current scheduling limits.

## Manage community content

### Seminars, guest teaching, and school projects

1. Open **Events** in `/admin/` (direct link: `/admin/app/event/`). Click **Add**.
2. Choose **Guest teaching**, **Seminar & career talk**, **School improvement**,
   **Community gathering**, or **Alumni reunion**. Add a clear title, description,
   and audience such as Classes 9–10.
3. Enter the date/time, optional end time, location, confirmed guest faculty or
   speaker, and a coordinating user. Add an external registration URL if needed.
4. Leave the activity as a draft while planning. Set **Scheduled** and tick
   **Is published** only when the details are confirmed. Published scheduled
   activities appear on the home page and in the activity calendar. Cancelled
   activities are removed from the public activity lists.
5. After the activity, set **Completed**, record actual student attendance if
   available, and enter a verified outcome. Published completed outcomes appear
   in the home-page impact section. Attendance is a session count, not a count
   of unique students across the year.

The public form at `/volunteer/` saves guest-teaching offers, seminar offers,
school-project support, and general volunteering applications. It does not
create teaching appointments automatically or send emails. Applications are
private and available only to users with the model's admin permissions.

Open **Volunteer applications** (`/admin/app/volunteerapplication/`) to review
contact details, subject experience, and availability. Move a new application
through **Contacted**, **Approved**, **Declined**, or **Completed** as appropriate.
Assign a team member, link the application to an Event, and keep follow-up notes.
Applicants' original details and consent are read-only in this workspace.

Give coordinators the relevant Event and Volunteer application view/change
permissions through a Django group. Public users and staff without these
permissions cannot see applications. The first version has no automatic
notification or volunteer login tracking; use the application's saved contact
information to coordinate through your established process.

### Other content

- **News:** review a title, category, excerpt, body, and slug before publishing.
  Publish/Unpublish actions are available. Current external RSS headlines still
  bypass editorial review; the roadmap proposes a moderated inbox.
- **Events:** set date, location, registration URL, and publication state.
- **Gallery:** add photos/categories. Configure durable object storage before
  relying on Vercel uploads; its function filesystem is not a media store.
- **Committee:** maintain roles, professions, batches, and display order.
- **Education:** maintain subjects, exam suggestions, and daily challenges.

## References

- [Django management commands](https://docs.djangoproject.com/en/5.1/ref/django-admin/)
- [Vercel Secret variables](https://vercel.com/docs/environment-variables/sensitive-environment-variables)
- [gspread service accounts](https://docs.gspread.org/en/latest/oauth2.html)
- [n8n Schedule Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/)
- [Vercel cron security](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
