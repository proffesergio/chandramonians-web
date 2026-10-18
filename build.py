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

    # Recheck before migrations as well: deploy hooks and dashboard rebuilds must
    # never publish an untested Git commit even if an ignore step is bypassed.
    if os.environ.get('VERCEL_GIT_COMMIT_SHA'):
        from scripts.vercel_build_gate import main as regression_gate
        if regression_gate() != 1:
            print('ERROR: this Git commit has not passed production CI. Refusing migrations/deployment.', file=sys.stderr)
            sys.exit(1)

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

    # One deployment only, explicitly enabled with --build-env. No runtime endpoint.
    if os.environ.get('RESTORE_COMMUNITY_FROM_SQLITE') == '1':
        call_command('restore_community', source=str(settings.BASE_DIR / 'db.sqlite3'))


if __name__ == '__main__':
    main()
