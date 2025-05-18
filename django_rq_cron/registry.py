import importlib
import typing
from dataclasses import dataclass
from functools import partial

from django.apps import apps

from django_rq_cron.models import CronJob


@dataclass
class RegisteredCronJob:
    """A registered cron job."""

    name: str
    description: str
    cadence: CronJob.Cadence
    function: typing.Callable
    queue: str = "default"


REGISTERED_CRON_JOBS = {}


def extract_name(runner_function: typing.Callable) -> str:
    """Extract the name of a function to use as the cron job name."""
    if runner_function.__name__ == "do":
        return runner_function.__module__.split(".")[-1]
    return runner_function.__name__


def register_cron(
    runner_function: typing.Callable = None,
    *,
    description: str = "",
    tries: int = 1,
    cadence: CronJob.Cadence = CronJob.Cadence.HOURLY,
    queue: str = "default",
) -> typing.Callable:
    """
    Register a function as a cron job.

    Usage:
        @register_cron
        def my_cron_job():
            pass

        @register_cron(
            description="My cron job",
            cadence=CronJob.Cadence.DAILY,
            queue="high"
        )
        def my_other_cron_job():
            pass
    """
    if runner_function is None:
        return partial(
            register_cron,
            description=description,
            tries=tries,
            cadence=cadence,
            queue=queue,
        )

    name = extract_name(runner_function)
    registration = RegisteredCronJob(name, description, cadence, runner_function, queue)
    REGISTERED_CRON_JOBS[registration.name] = registration
    return runner_function


def import_crons():
    """
    Import all cron job modules from installed apps.

    This function searches for a 'crons' module in each installed app
    and imports it to register cron jobs.
    """
    # Get all installed apps
    installed_apps = [app_config.name for app_config in apps.get_app_configs()]

    # Import crons from each app
    for app_name in installed_apps:
        try:
            importlib.import_module(f"{app_name}.crons")
        except ModuleNotFoundError:
            pass
