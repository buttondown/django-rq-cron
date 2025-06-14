from django_rq_cron.registry import register_cron
from django_rq_cron.models import CronJob
from django.utils import timezone
from bananas.models import Banana


@register_cron(
    description="Update banana ripeness based on age",
    cadence=CronJob.Cadence.HOURLY,
)
def update_banana_ripeness():
    """
    Update banana status based on their age:
    - 0-2 days: unripe
    - 3-5 days: ripe
    - 6+ days: overripe
    """
    now = timezone.now()
    updated_count = 0

    # Get all bananas that might need status updates
    bananas = Banana.objects.all()

    for banana in bananas:
        days_old = (now - banana.created_at).days
        new_status = None

        if days_old <= 2 and banana.status != Banana.Status.UNRIPE:
            new_status = Banana.Status.UNRIPE
        elif 3 <= days_old <= 5 and banana.status != Banana.Status.RIPE:
            new_status = Banana.Status.RIPE
        elif days_old >= 6 and banana.status != Banana.Status.OVERRIPE:
            new_status = Banana.Status.OVERRIPE

        if new_status:
            banana.status = new_status
            banana.save()
            updated_count += 1

    print(f"Updated {updated_count} banana(s) ripeness status")
    return {"updated_count": updated_count}


@register_cron(
    description="Clean up overripe bananas older than 10 days",
    cadence=CronJob.Cadence.DAILY,
)
def cleanup_old_bananas():
    """
    Remove bananas that have been overripe for more than 10 days total.
    """
    now = timezone.now()
    cutoff_date = now - timezone.timedelta(days=10)

    old_bananas = Banana.objects.filter(
        created_at__lt=cutoff_date, status=Banana.Status.OVERRIPE
    )

    count = old_bananas.count()
    old_bananas.delete()

    print(f"Cleaned up {count} old banana(s)")
    return {"cleaned_count": count}
