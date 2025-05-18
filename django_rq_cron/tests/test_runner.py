import pytest

from django_rq_cron.models import CronJob
from django_rq_cron.registry import RegisteredCronJob
from django_rq_cron.runner import run_cron, enqueue_next_run


def immediately_fail():
    raise Exception("This is a test exception")


@pytest.mark.django_db
def test_handle_failure():
    # Register a failing cron job
    registered_cron = RegisteredCronJob(
        name="test",
        function=immediately_fail,
        cadence=CronJob.Cadence.HOURLY,
        description="This is a test cron",
    )
    
    # Store it in the registry for the runner to find
    from django_rq_cron.registry import REGISTERED_CRON_JOBS
    REGISTERED_CRON_JOBS[registered_cron.name] = registered_cron
    
    # Run the cron job
    run_cron(registered_cron.name)
    
    # Check that the cron job is marked as failing
    assert CronJob.objects.get(name="test").status == CronJob.Status.FAILING


def test_enqueue_next_run():
    # This just makes sure the function runs without error
    enqueue_next_run(CronJob.Cadence.HOURLY)


@pytest.mark.django_db
def test_should_create_cron_job_if_not_exists():
    # Register a cron job
    registered_cron = RegisteredCronJob(
        name="test",
        function=lambda: None,
        cadence=CronJob.Cadence.DAILY,
        description="This is a test cron",
    )
    
    # Store it in the registry for the runner to find
    from django_rq_cron.registry import REGISTERED_CRON_JOBS
    REGISTERED_CRON_JOBS[registered_cron.name] = registered_cron
    
    # Run the cron job
    run_cron(registered_cron.name)
    
    # Check that the cron job was created with the correct cadence
    assert CronJob.objects.get(name="test").cadence == CronJob.Cadence.DAILY