import logging
from collections.abc import Iterable

import django_rq
from django.utils import timezone

from django_rq_cron.models import CronJob, CronJobRun, CronJobStatusTransition
from django_rq_cron.registry import REGISTERED_CRON_JOBS, RegisteredCronJob
from django_rq_cron.utils import get_next_scheduled_time

logger = logging.getLogger("django_rq_cron")


def crons_for_cadence(cadence: CronJob.Cadence) -> Iterable[RegisteredCronJob]:
    """Get all cron jobs for a given cadence."""
    for cron in REGISTERED_CRON_JOBS.values():
        if cron.cadence == cadence:
            yield cron


def run_cron(cron_name: str):
    """Run a cron job by name."""
    logger.info(f"Cron job started: {cron_name}")
    cron_job, _ = CronJob.objects.get_or_create(name=cron_name)
    start = timezone.now()
    run = CronJobRun.objects.create(
        cron_job=cron_job, status=CronJobRun.Status.IN_PROGRESS
    )
    try:
        cron = REGISTERED_CRON_JOBS[cron_name]
        cron.function()
    except Exception as e:
        logger.error(f"Cron job error: {cron_name} - {e}")
        try:
            # Try to log to Sentry if it's available
            import sentry_sdk

            sentry_sdk.capture_exception(e)
        except ImportError:
            pass

        run.status = CronJobRun.Status.FAILED
        run.error = str(e)
        run.save()
        if cron_job.status != CronJob.Status.FAILING:
            cron_job.latest_status_change = timezone.now()
            cron_job.status = CronJob.Status.FAILING
            cron_job.save()
            CronJobStatusTransition.objects.create(
                parent=cron_job,
                old_value=CronJob.Status.NEW,
                new_value=CronJob.Status.FAILING,
            )
        return

    end = timezone.now()
    run.status = CronJobRun.Status.SUCCEEDED
    run.completion_date = end
    run.save()
    logger.info(
        f"Cron job finished: {cron_job.name} - Processing time: {(end - start).total_seconds()}s"
    )
    cron_job.latest_run_date = end
    if cron_job.status != CronJob.Status.SUCCEEDING:
        original_status = cron_job.status
        cron_job.latest_status_change = timezone.now()
        cron_job.status = CronJob.Status.SUCCEEDING
        CronJobStatusTransition.objects.create(
            parent=cron_job,
            old_value=original_status,
            new_value=CronJob.Status.SUCCEEDING,
        )
    cron_job.cadence = cron.cadence
    cron_job.description = cron.description
    cron_job.save()

    # If there are any previous instances of this cron job that are still in progress,
    # we need to clean them up.
    CronJobRun.objects.filter(
        cron_job=cron_job, status=CronJobRun.Status.IN_PROGRESS
    ).exclude(id=run.id).delete()


def enqueue_next_run(cadence: CronJob.Cadence, queue_name: str = "default"):
    """Schedule the next run of all cron jobs with the given cadence."""
    crontab_string = next(
        (
            crontab_string
            for crontab_string, c in CRON_TAB_STRING_TO_CADENCE.items()
            if c == cadence
        ),
        None,
    )
    if crontab_string is None:
        raise ValueError(f"No crontab string found for cadence: {cadence}")

    # Only enqueue a run if there isn't already a run scheduled for this cadence at the exact time.
    scheduled_time = get_next_scheduled_time(crontab_string)
    job_id = f"cron-{cadence}-{scheduled_time}"
    logger.info(
        f"Scheduling next cron run: cadence={cadence}, scheduled_time={scheduled_time}, job_id={job_id}"
    )
    return django_rq.get_queue(queue_name).enqueue_at(
        scheduled_time,
        run_crons,
        job_id=job_id,
        args=(cadence, queue_name),
    )


def run_crons(cadence: CronJob.Cadence, default_queue: str = "default"):
    """Run all cron jobs with the given cadence."""
    relevant_crons = crons_for_cadence(cadence)
    for cron in relevant_crons:
        # Note that we enqueue the name and not the cron itself to cut down on
        # the amount of data we need to serialize.
        queue = django_rq.get_queue(cron.queue)
        queue.enqueue(run_cron, cron.name)
    enqueue_next_run(cadence, default_queue)


HOURLY_CRON_TAB = "0 * * * *"
TEN_MINUTES_CRON_TAB = "*/10 * * * *"
DAILY_CRON_TAB = "0 20 * * *"
EVERY_MINUTE_CRON_TAB = "* * * * *"
WEEKLY_CRON_TAB = "0 0 * * 1"
MONTHLY_CRON_TAB = "0 0 1 * *"

CRON_TAB_STRING_TO_CADENCE = {
    HOURLY_CRON_TAB: CronJob.Cadence.HOURLY,
    TEN_MINUTES_CRON_TAB: CronJob.Cadence.EVERY_TEN_MINUTES,
    DAILY_CRON_TAB: CronJob.Cadence.DAILY,
    EVERY_MINUTE_CRON_TAB: CronJob.Cadence.EVERY_MINUTE,
    WEEKLY_CRON_TAB: CronJob.Cadence.WEEKLY,
    MONTHLY_CRON_TAB: CronJob.Cadence.MONTHLY,
}


def bootstrap(default_queue: str = "default"):
    """Bootstrap all cron jobs by scheduling the first run of each cadence."""
    return [
        enqueue_next_run(cadence, default_queue)
        for cadence in CRON_TAB_STRING_TO_CADENCE.values()
    ]
