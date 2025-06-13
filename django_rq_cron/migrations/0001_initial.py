from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CronJob",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("modification_date", models.DateTimeField(auto_now=True)),
                ("name", models.TextField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True, max_length=5000)),
                (
                    "cadence",
                    models.TextField(
                        choices=[
                            ("every_minute", "Every Minute"),
                            ("every_ten_minutes", "Every Ten Minutes"),
                            ("hourly", "Hourly"),
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                        ],
                        default="hourly",
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.TextField(
                        choices=[
                            ("new", "New"),
                            ("succeeding", "Succeeding"),
                            ("failing", "Failing"),
                            ("deprecated", "Deprecated"),
                        ],
                        default="new",
                        max_length=50,
                    ),
                ),
                ("latest_status_change", models.DateTimeField(null=True)),
                ("latest_run_date", models.DateTimeField(null=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="CronJobRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("modification_date", models.DateTimeField(auto_now=True)),
                ("completion_date", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.TextField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                        ],
                        default="succeeded",
                        max_length=50,
                    ),
                ),
                ("error", models.TextField(blank=True, max_length=1000)),
                ("data", models.JSONField(null=True)),
                (
                    "cron_job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="runs",
                        to="django_rq_cron.cronjob",
                    ),
                ),
            ],
            options={
                "ordering": ("-creation_date",),
            },
        ),
        migrations.CreateModel(
            name="CronJobStatusTransition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                (
                    "old_value",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("new", "New"),
                            ("succeeding", "Succeeding"),
                            ("failing", "Failing"),
                            ("deprecated", "Deprecated"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "new_value",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("succeeding", "Succeeding"),
                            ("failing", "Failing"),
                            ("deprecated", "Deprecated"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_rq_cron.cronjob",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
