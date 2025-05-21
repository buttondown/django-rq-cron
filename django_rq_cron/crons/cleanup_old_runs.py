import logging
from datetime import timedelta

from django.utils import timezone

from django_rq_cron.models import CronJobRun
from django_rq_cron.registry import register_cron

logger = logging.getLogger("django_rq_cron")


@register_cron(
    description="Clean up old cron job runs to prevent database bloat", cadence="daily"
)
def do():
    """Remove cron job runs older than 30 days."""
    cutoff_date = timezone.now() - timedelta(days=30)

    # Get the count of runs to be deleted
    count = CronJobRun.objects.filter(creation_date__lt=cutoff_date).count()

    # Delete the runs
    CronJobRun.objects.filter(creation_date__lt=cutoff_date).delete()

    logger.info(f"Cleaned up {count} cron job runs older than 30 days")
