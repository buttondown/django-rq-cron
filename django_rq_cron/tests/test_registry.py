import pytest

from django_rq_cron.models import CronJob
from django_rq_cron.registry import register_cron, extract_name, REGISTERED_CRON_JOBS


def test_extract_name():
    def my_function():
        pass
    
    assert extract_name(my_function) == "my_function"
    
    def do():
        pass
    
    do.__module__ = "django_rq_cron.crons.ping"
    assert extract_name(do) == "ping"


def test_register_cron_with_decorator():
    # Clear the registry
    REGISTERED_CRON_JOBS.clear()
    
    @register_cron
    def test_cron():
        pass
    
    assert "test_cron" in REGISTERED_CRON_JOBS
    assert REGISTERED_CRON_JOBS["test_cron"].function == test_cron
    assert REGISTERED_CRON_JOBS["test_cron"].cadence == CronJob.Cadence.HOURLY
    assert REGISTERED_CRON_JOBS["test_cron"].description == ""
    assert REGISTERED_CRON_JOBS["test_cron"].queue == "default"


def test_register_cron_with_parameters():
    # Clear the registry
    REGISTERED_CRON_JOBS.clear()
    
    @register_cron(
        description="Test cron with parameters",
        cadence=CronJob.Cadence.DAILY,
        queue="high"
    )
    def test_cron_with_params():
        pass
    
    assert "test_cron_with_params" in REGISTERED_CRON_JOBS
    assert REGISTERED_CRON_JOBS["test_cron_with_params"].function == test_cron_with_params
    assert REGISTERED_CRON_JOBS["test_cron_with_params"].cadence == CronJob.Cadence.DAILY
    assert REGISTERED_CRON_JOBS["test_cron_with_params"].description == "Test cron with parameters"
    assert REGISTERED_CRON_JOBS["test_cron_with_params"].queue == "high"