"""Vercel build script — apply Django migrations against the production database."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

    if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
        print('ERROR: DATABASE_URL is not set. Add it in Vercel env vars for Production + Build.', file=sys.stderr)
        sys.exit(1)

    import django
    django.setup()

    from django.conf import settings
    engine = settings.DATABASES['default']['ENGINE']
    print(f'Build migrate target: {engine}')

    if os.environ.get('VERCEL') and 'sqlite' in engine:
        print(
            'ERROR: Vercel build is using SQLite. DATABASE_URL must be available during build '
            '(Vercel → Settings → Environment Variables → ensure Production scope includes Build).',
            file=sys.stderr,
        )
        sys.exit(1)

    from django.core.management import call_command

    print('Running migrations...')
    call_command('migrate', '--noinput', verbosity=2)
    print('Migrations complete.')


if __name__ == '__main__':
    main()
