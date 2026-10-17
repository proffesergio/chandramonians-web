# Activate virtualenv on server.

* source env/bin/activate  (linux)
* env\Scripts\activate (windows)

# Install requirements.txt with pip

* pip install -r requirements.txt

# Django Migrations

* python manage.py migrate

# Start django with runserver (to test) or connect webserver (nginx, uwsgi, gunicorn, ...)

* python manage.py runserver

# Vercel deployment

Use the Django framework preset with the repository root as the Root Directory.
`vercel.json` runs `python build.py` to apply migrations to `DATABASE_URL`;
Vercel collects static files automatically. Configure `DATABASE_URL`, `SECRET_KEY`,
`DEBUG=False`, and `SITE_URL` for each deployment environment.

Public page templates live in `templates/pages/`. Do not name a template directory
`public`: Vercel's Python builder excludes `**/public/**` from the function bundle,
which causes `TemplateDoesNotExist` even when the files are committed.

Run `python manage.py test app` before deploying, then check `/`, `/about/`,
`/members/`, `/health/`, and `/static/assets/css/chandramonians.css` on the deployment.
