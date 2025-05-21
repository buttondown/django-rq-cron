from django.db import models


class BaseModel(models.Model):
    """Base model with creation and modification date."""

    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseTransition(models.Model):
    """
    Base model for tracking changes to a field over time.
    This is used to track status changes in models.
    """

    creation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    @classmethod
    def construct_parent(cls, parent_model):
        return models.ForeignKey(
            parent_model, null=False, blank=False, on_delete=models.CASCADE
        )

    @classmethod
    def construct_old_value(cls, choices):
        return models.CharField(max_length=50, choices=choices, null=True, blank=True)

    @classmethod
    def construct_new_value(cls, choices):
        return models.CharField(max_length=50, choices=choices, null=False, blank=False)

    class Meta:
        abstract = True


class CronJobRun(BaseModel):
    """A record of a cron job running."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    cron_job = models.ForeignKey(
        "CronJob",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    completion_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(
        max_length=50, choices=Status.choices, default=Status.SUCCEEDED
    )
    error = models.TextField(max_length=1000, blank=True)
    data = models.JSONField(null=True)

    class Meta:
        ordering = ("-creation_date",)


class CronJob(BaseModel):
    """A cron job configuration."""

    @classmethod
    def tracked_field_to_transition_class(cls) -> dict:
        return {
            "status": CronJobStatusTransition,
        }

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
            return None
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


class CronJobStatusTransition(BaseTransition):
    """Track changes to a cron job's status."""

    parent = BaseTransition.construct_parent(CronJob)
    old_value = BaseTransition.construct_old_value(CronJob.Status.choices)
    new_value = BaseTransition.construct_new_value(CronJob.Status.choices)
