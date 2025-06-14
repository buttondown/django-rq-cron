# Banana Stand Sample Application

This is a sample Django application demonstrating the use of django-rq-cron with a simple "banana stand" model.

## Features

- **Banana Model**: Tracks bananas with status (unripe, ripe, overripe) and creation date
- **Automated Aging**: Cron job that updates banana ripeness based on age
- **Cleanup**: Daily cleanup of old overripe bananas
- **Admin Interface**: Django admin for managing bananas and monitoring cron jobs

## Banana Lifecycle

Bananas automatically age based on their creation date:

- **Days 0-2**: Unripe 🟢
- **Days 3-5**: Ripe 🟡  
- **Days 6+**: Overripe 🟤
- **Days 10+**: Automatically removed 🗑️

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis server running on localhost:6379
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Install dependencies:**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install project dependencies
   uv sync
   
   # Install django-rq-cron from the parent directory
   uv pip install -e ../
   ```

2. **Run migrations:**
   ```bash
   uv run python manage.py migrate
   ```

3. **Create a superuser:**
   ```bash
   uv run python manage.py createsuperuser
   ```

4. **Bootstrap cron jobs:**
   ```bash
   uv run python manage.py bootstrap_cron_jobs
   ```

5. **Create sample bananas:**
   ```bash
   uv run python manage.py create_sample_bananas
   ```

### Running the Application

1. **Start Redis (if not already running):**
   ```bash
   redis-server
   ```

2. **Start the Django development server:**
   ```bash
   uv run python manage.py runserver
   ```

3. **Start the RQ worker (in another terminal):**
   ```bash
   uv run python manage.py rqworker
   ```

4. **Access the admin interface:**
   - Go to http://127.0.0.1:8000/admin/
   - Login with your superuser credentials
   - View and manage bananas and cron jobs

### Testing the Cron Jobs

You can manually trigger the cron jobs for testing:

```python
# In Django shell (uv run python manage.py shell)
from django_rq_cron.runner import run_cron

# Update banana ripeness
run_cron("update_banana_ripeness")

# Clean up old bananas
run_cron("cleanup_old_bananas")
```

### Testing

Run the test suite to verify everything works correctly:

```bash
# Run all tests
uv run pytest

# Run only model tests
uv run pytest bananas/tests.py

# Run only cron job tests
uv run pytest bananas/test_crons.py

# Run with verbose output
uv run pytest -v
```

The test suite includes:
- **Model Tests**: Banana creation, status transitions, aging calculations
- **Cron Job Tests**: Ripeness updates, cleanup functionality, edge cases
- **Integration Tests**: Multiple bananas with different ages and statuses

### Monitoring

- **Bananas**: http://127.0.0.1:8000/admin/bananas/banana/
- **Cron Jobs**: http://127.0.0.1:8000/admin/django_rq_cron/cronjob/
- **Cron Job Runs**: http://127.0.0.1:8000/admin/django_rq_cron/cronjobrun/
- **RQ Dashboard**: http://127.0.0.1:8000/django-rq/

## Cron Jobs

### Update Banana Ripeness (Hourly)
- **Function**: `update_banana_ripeness`
- **Schedule**: Every hour
- **Purpose**: Updates banana status based on age

### Cleanup Old Bananas (Daily)
- **Function**: `cleanup_old_bananas` 
- **Schedule**: Daily
- **Purpose**: Removes bananas older than 10 days

## Model Structure

### Banana
- `status`: Choice field (unripe, ripe, overripe)
- `created_at`: Auto-populated creation timestamp
- `updated_at`: Auto-updated modification timestamp
- `days_old`: Property calculating age in days
