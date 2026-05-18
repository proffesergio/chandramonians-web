from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        import sys
        # Don't start scheduler during migrations or management commands
        skip_cmds = {'migrate', 'makemigrations', 'check', 'collectstatic', 'test'}
        if not any(cmd in sys.argv for cmd in skip_cmds):
            from webapp import scheduler
            scheduler.start()
