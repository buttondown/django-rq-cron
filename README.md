# django-rq-cron

A Django app for running cron jobs with django-rq - simple, reliable scheduled task execution for Django projects.

## Installation

```bash
pip install django-rq-cron
```

Add to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.admin',  # Optional but recommended for the admin interface
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
    # You can define multiple queues with different priorities
    'high': {
        'URL': 'redis://localhost:6379/0',
        'DEFAULT_TIMEOUT': 500,
    },
}
```

Run migrations:

```bash
python manage.py migrate
```

Add the URLs to your main `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('django-rq/', include('django_rq.urls')),
]
```

## Usage

### Creating Cron Jobs

Create a cron job by defining a function with the `@register_cron` decorator:

```python
from django_rq_cron.registry import register_cron
from django_rq_cron.models import CronJob

@register_cron(
    description="My daily task that processes data",
    cadence=CronJob.Cadence.DAILY,
    queue="high"  # Optional, defaults to "default"
)
def my_daily_task():
    # Task implementation
    print("Running my daily task...")
    
    # You can use any Python code here
    data = fetch_some_data()
    process_data(data)
```

Available cadence options:
- `CronJob.Cadence.EVERY_MINUTE`
- `CronJob.Cadence.EVERY_TEN_MINUTES`
- `CronJob.Cadence.HOURLY`
- `CronJob.Cadence.DAILY`
- `CronJob.Cadence.WEEKLY`
- `CronJob.Cadence.MONTHLY`

### Cron Discovery

The package will automatically discover cron jobs in a 'crons' module in each installed app. For example:

```
myapp/
  __init__.py
  models.py
  views.py
  crons/  <-- Create this directory
    __init__.py
    daily_tasks.py  <-- Put your cron jobs here
```

Inside `daily_tasks.py`:

```python
from django_rq_cron.registry import register_cron
from django_rq_cron.models import CronJob

@register_cron(
    description="Send daily report emails",
    cadence=CronJob.Cadence.DAILY
)
def send_daily_reports():
    # Your daily report sending logic
    pass
```

### Bootstrapping Cron Jobs

After creating your cron job functions, bootstrap them to start execution:

```bash
python manage.py bootstrap_cron_jobs
```

This command will:
1. Discover all registered cron jobs
2. Create database entries for them
3. Schedule their first execution

### Monitoring and Admin Interface

django-rq-cron provides Django admin integration to monitor your cron jobs:

```python
# admin.py in your app
from django.contrib import admin
from django_rq_cron.models import CronJob, CronJobRun

admin.site.register(CronJob)
admin.site.register(CronJobRun)
```

The admin interface allows you to:
- View all registered cron jobs
- See their status (new, succeeding, failing, deprecated)
- Examine execution history
- View error details for failed runs

### Advanced Usage

#### Running a Cron Job Manually

You can trigger a cron job manually:

```python
from django_rq_cron.runner import run_cron

# Run by name
run_cron("my_daily_task")
```

#### Creating Custom Cadences

If you need a custom schedule beyond the predefined cadences, you can extend the system:

```python
# In your settings.py
DJANGO_RQ_CRON_CUSTOM_CADENCES = {
    'EVERY_FIVE_MINUTES': '*/5 * * * *',
}

# Then in your app
from django_rq_cron.registry import register_cron
from django_rq_cron.models import CronJob

@register_cron(
    description="Run every five minutes",
    cadence='EVERY_FIVE_MINUTES'  # Use your custom cadence
)
def frequent_task():
    # Your logic
    pass
```

## Features

- Schedule jobs to run at different cadences (every minute, every 10 minutes, hourly, daily, weekly, monthly)
- Track job execution status and history in the database
- View job history and results in the Django admin
- Built-in jobs for cleanup and system health checks
- Support for multiple queues with different priorities
- Easy integration with existing Django projects

## Testing

To run tests:

```bash
# Install dev dependencies
pip install pytest pytest-django

# Run tests
DJANGO_SETTINGS_MODULE=tests.settings pytest
```

## License

MIT