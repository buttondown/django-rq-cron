from datetime import datetime

import crontab


def get_next_scheduled_time(crontab_string: str) -> datetime:
    """Get the next time a cron job should run for a given crontab string."""
    return crontab.CronTab(crontab_string).next(return_datetime=True, default_utc=True)
