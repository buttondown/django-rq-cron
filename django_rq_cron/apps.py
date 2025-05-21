from django.apps import AppConfig


class DjangoRQCronConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_rq_cron"
    verbose_name = "Django RQ Cron"

    def ready(self):
        """Import crons when the app is ready."""
        from django_rq_cron.registry import import_crons

        import_crons()
