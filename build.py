"""Vercel build script — apply Django migrations against the production database."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

    # This script only ever runs as a deploy build step, so it must never fall back
    # to the local SQLite default — doing so silently migrates a throwaway file in
    # the build sandbox and leaves the real database empty.
    if not os.environ.get('DATABASE_URL'):
        print(
            'ERROR: DATABASE_URL is not set for the build. In Vercel -> Settings -> '
            'Environment Variables, the variable must have the Build scope ticked, '
            'not just Production runtime.',
            file=sys.stderr,
        )
        sys.exit(1)

    import django
    django.setup()

    from django.conf import settings
    db = settings.DATABASES['default']
    engine = db['ENGINE']

    # Log which database is actually being migrated so the build log can be compared
    # against the database the running site connects to.
    print(f'Build migrate target: {engine} db={db.get("NAME")} host={db.get("HOST")}')

    if 'postgresql' not in engine:
        print(
            f'ERROR: build expected a PostgreSQL target but resolved {engine!r}. '
            'Refusing to migrate - the deployed site would still see an empty database.',
            file=sys.stderr,
        )
        sys.exit(1)

    from django.core.management import call_command

    print('Running migrations...')
    call_command('migrate', '--noinput', verbosity=2)
    call_command('showmigrations', '--list', verbosity=1)
    print('Migrations complete.')


if __name__ == '__main__':
    main()
