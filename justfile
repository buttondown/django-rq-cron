test:
    DJANGO_SETTINGS_MODULE=tests.settings uv run pytest

make-migrations:
    DJANGO_SETTINGS_MODULE=tests.settings uv run django-admin makemigrations

format:
    DJANGO_SETTINGS_MODULE=tests.settings uv run ruff format .
    DJANGO_SETTINGS_MODULE=tests.settings uv run ruff check .