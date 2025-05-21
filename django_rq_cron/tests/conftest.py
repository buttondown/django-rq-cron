import os
import pytest
import django
from django.conf import settings
from django.core.management import call_command

# Ensure Django is initialized before tests run
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()

@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Ensure that the database is correctly configured and migrations are applied for tests."""
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    
    with django_db_blocker.unblock():
        # Create the test database and apply migrations
        call_command("migrate")

@pytest.fixture
def setup_django_db(db):
    """Fixture to ensure the database is set up and migrations are applied."""
    pass