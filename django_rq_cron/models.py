from django.db import models
import uuid


class CronJob(models.Model):
    """A cron job configuration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    name = models.TextField(max_length=50, unique=True)
    description = models.TextField(max_length=5000, blank=True)

    class Cadence(models.TextChoices):
        EVERY_MINUTE = "every_minute"
        EVERY_TEN_MINUTES = "every_ten_minutes"
        HOURLY = "hourly"
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"

    cadence = models.TextField(
        max_length=50, choices=Cadence.choices, default=Cadence.HOURLY
    )

    class Status(models.TextChoices):
        NEW = "new"
        SUCCEEDING = "succeeding"
        FAILING = "failing"
        DEPRECATED = "deprecated"

    status = models.TextField(max_length=50, choices=Status.choices, default=Status.NEW)
    latest_status_change = models.DateTimeField(null=True)
    latest_run_date = models.DateTimeField(null=True)

    @property
    def human_readable_time_since_status_change(self) -> str:
        """Return a human readable string representing the time since the status changed."""
        if not self.latest_run_date or not self.latest_status_change:
            return ""
        return self._convert_timedelta_to_human_readable(
            self.latest_run_date - self.latest_status_change
        )

    @staticmethod
    def _convert_timedelta_to_human_readable(timedelta) -> str:
        """Convert a timedelta to a human readable string."""
        total_seconds = int(timedelta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

        return ", ".join(parts) if parts else "0 seconds"

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class CronJobRun(models.Model):
    """A record of a cron job running."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    completion_date = models.DateTimeField(blank=True, null=True)

    cron_job = models.ForeignKey(
        "CronJob",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    status = models.TextField(
        max_length=50, choices=Status.choices, default=Status.SUCCEEDED
    )
    error = models.TextField(max_length=1000, blank=True)
    data = models.JSONField(null=True)

    class Meta:
        ordering = ("-creation_date",)


class CronJobStatusTransition(models.Model):
    """Track changes to a cron job's status."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "CronJob",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="status_transitions",
    )
    old_value = models.TextField(
        max_length=50, choices=CronJob.Status.choices, null=True
    )
    new_value = models.TextField(
        max_length=50, choices=CronJob.Status.choices, null=True
    )

    class Meta:
        ordering = ("-creation_date",)
