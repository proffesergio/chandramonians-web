"""Run an explicit management command against production PostgreSQL."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    import environ
    env_file = ROOT / '.env.production.local'
    if not env_file.exists():
        env_file = ROOT / '.env.local.production'
    environ.Env.read_env(env_file, overwrite=True)
    if not os.environ.get('DATABASE_URL', '').startswith(('postgres://', 'postgresql://')):
        raise SystemExit('Set DATABASE_URL to the production PostgreSQL URL in .env.production.local. SQLite is refused.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
