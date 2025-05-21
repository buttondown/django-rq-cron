import logging

from django_rq_cron.registry import register_cron

logger = logging.getLogger("django_rq_cron")


@register_cron(
    description="Simple ping cron job to verify the cron system is working",
    cadence="hourly",
)
def do():
    """Simple ping job that logs a message."""
    logger.info("Cron ping job executed successfully")
