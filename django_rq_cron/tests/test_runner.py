import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from django_rq_cron.models import CronJob
from django_rq_cron.registry import RegisteredCronJob
from django_rq_cron.runner import run_cron, enqueue_next_run


def immediately_fail():
    raise Exception("This is a test exception")


@pytest.mark.django_db
def test_handle_failure(setup_django_db):
    # Register a failing cron job
    registered_cron = RegisteredCronJob(
        name="test_failing",
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
    assert CronJob.objects.get(name="test_failing").status == CronJob.Status.FAILING


# Mock the entire CronTab functionality
@patch('django_rq_cron.runner.get_next_scheduled_time')
@patch('django_rq.get_queue')
def test_enqueue_next_run(mock_get_queue, mock_get_next_scheduled_time):
    # Mock the next scheduled time
    mock_datetime = datetime.now(tz=timezone.utc)
    mock_get_next_scheduled_time.return_value = mock_datetime
    
    # Mock the queue
    mock_queue = MagicMock()
    mock_get_queue.return_value = mock_queue
    
    # This just makes sure the function runs without error
    result = enqueue_next_run(CronJob.Cadence.HOURLY)
    
    # Verify that the queue's enqueue_at method was called
    mock_queue.enqueue_at.assert_called_once()


@pytest.mark.django_db
def test_should_create_cron_job_if_not_exists(setup_django_db):
    # Register a cron job
    registered_cron = RegisteredCronJob(
        name="test_create",
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
    assert CronJob.objects.get(name="test_create").cadence == CronJob.Cadence.DAILY