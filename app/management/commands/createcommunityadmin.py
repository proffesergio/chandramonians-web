import getpass
import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from app.models import CustomUser


class Command(BaseCommand):
    help = 'Create a superuser with access to both Django admin and the HOD dashboard.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--username', required=True)
        parser.add_argument('--noinput', action='store_true')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        username = options['username'].strip()
        if CustomUser.objects.filter(email__iexact=email).exists() or CustomUser.objects.filter(username=username).exists():
            raise CommandError('That email or username already exists. Use the existing account recovery procedure.')
        user = CustomUser(email=email, username=username, user_type='1', is_staff=True, is_superuser=True)
        try:
            user.full_clean(exclude=['password'])
            if options['noinput']:
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
                if not password:
                    raise CommandError('Set DJANGO_SUPERUSER_PASSWORD for --noinput; no password was created.')
            else:
                password = getpass.getpass('Password: ')
                if password != getpass.getpass('Password (again): '):
                    raise CommandError('Passwords do not match.')
            validate_password(password, user=user)
        except ValidationError as exc:
            raise CommandError('; '.join(exc.messages)) from exc
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS('Community super admin created. Sign in with the email at /admin/ or /login.'))
