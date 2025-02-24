* Activate virtualenv on server.

# source env/bin/activate  (linux)
# env\Scripts\activate (windows)

* Install requirements.txt with pip

# pip install -r requirements.txt

* Django Migrations

# python manage.py migrate

* Start django with runserver (to test) or connect webserver (nginx, uwsgi, gunicorn, ...)

# python manage.py runserver