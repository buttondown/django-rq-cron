from django.db import models
from django.utils import timezone


class Banana(models.Model):
    """A banana in the banana stand."""

    class Status(models.TextChoices):
        UNRIPE = "unripe", "Unripe"
        RIPE = "ripe", "Ripe"
        OVERRIPE = "overripe", "Overripe"

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.UNRIPE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banana #{self.pk} ({self.get_status_display()})"

    @property
    def days_old(self):
        """Return the number of days since this banana was created."""
        return (timezone.now() - self.created_at).days

    class Meta:
        ordering = ["-created_at"]
