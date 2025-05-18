# django-rq-cron

A Django app for running cron jobs with django-rq.

## Installation

```bash
pip install django-rq-cron
```

Add to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'django_rq',
    'django_rq_cron',
]
```

Configure `RQ_QUEUES` in your settings:

```python
RQ_QUEUES = {
    'default': {
        'URL': 'redis://localhost:6379/0',
        'DEFAULT_TIMEOUT': 360,
    },
}
```

Run migrations:

```bash
python manage.py migrate
```

## Usage

Create a cron job by defining a function with the `@register_cron` decorator:

```python
from django_rq_cron.registry import register_cron
from django_rq_cron.models import CronJob

@register_cron(
    description="My daily task",
    cadence=CronJob.Cadence.DAILY,
    queue="default"  # Optional, defaults to "default"
)
def my_daily_task():
    # Task implementation
    pass
```

The package will automatically discover cron jobs in a 'crons' module in each installed app.

Bootstrap cron jobs with the management command:

```bash
python manage.py bootstrap_cron_jobs
```

## Features

- Schedule jobs to run at different cadences (every minute, every 10 minutes, hourly, daily, weekly, monthly)
- Track job execution status in the database
- View job history and results in the Django admin
- Built-in jobs for cleanup and system health checks

## License

MIT
