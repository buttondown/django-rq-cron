from django.core.management.base import BaseCommand
from django.utils import timezone
from bananas.models import Banana


class Command(BaseCommand):
    help = "Create sample bananas with different ages for testing"

    def handle(self, *args, **options):
        now = timezone.now()

        # Create bananas of different ages
        sample_bananas = [
            {"days_ago": 0, "status": Banana.Status.UNRIPE},  # Fresh banana
            {"days_ago": 1, "status": Banana.Status.UNRIPE},  # 1 day old
            {"days_ago": 3, "status": Banana.Status.UNRIPE},  # Should be ripe
            {"days_ago": 5, "status": Banana.Status.UNRIPE},  # Should be ripe
            {"days_ago": 7, "status": Banana.Status.RIPE},  # Should be overripe
            {
                "days_ago": 10,
                "status": Banana.Status.RIPE,
            },  # Should be overripe and cleaned up
        ]

        created_count = 0
        for banana_data in sample_bananas:
            creation_date = now - timezone.timedelta(days=banana_data["days_ago"])

            banana = Banana.objects.create(status=banana_data["status"])

            # Manually set the creation date to simulate aged bananas
            banana.created_at = creation_date
            banana.save()

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created banana #{banana.pk} ({banana_data['days_ago']} days old)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} sample bananas")
        )
