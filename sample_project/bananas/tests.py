from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from datetime import timedelta

from .models import Banana


class BananaModelTestCase(TestCase):
    """Test cases for the Banana model."""

    def test_banana_creation_defaults(self):
        """Test that a banana is created with correct defaults."""
        banana = Banana.objects.create()

        self.assertEqual(banana.status, Banana.Status.UNRIPE)
        self.assertIsNotNone(banana.created_at)
        self.assertIsNotNone(banana.updated_at)

    def test_banana_str_representation(self):
        """Test the string representation of a banana."""
        banana = Banana.objects.create(status=Banana.Status.RIPE)
        expected = f"Banana #{banana.pk} (Ripe)"
        self.assertEqual(str(banana), expected)

    def test_banana_status_choices(self):
        """Test all available status choices work correctly."""
        # Test unripe
        unripe_banana = Banana.objects.create(status=Banana.Status.UNRIPE)
        self.assertEqual(unripe_banana.status, "unripe")
        self.assertEqual(unripe_banana.get_status_display(), "Unripe")

        # Test ripe
        ripe_banana = Banana.objects.create(status=Banana.Status.RIPE)
        self.assertEqual(ripe_banana.status, "ripe")
        self.assertEqual(ripe_banana.get_status_display(), "Ripe")

        # Test overripe
        overripe_banana = Banana.objects.create(status=Banana.Status.OVERRIPE)
        self.assertEqual(overripe_banana.status, "overripe")
        self.assertEqual(overripe_banana.get_status_display(), "Overripe")

    def test_days_old_property(self):
        """Test the days_old property calculation."""
        with freeze_time("2024-01-01 12:00:00"):
            banana = Banana.objects.create()

        # Test same day
        with freeze_time("2024-01-01 18:00:00"):
            self.assertEqual(banana.days_old, 0)

        # Test 1 day later
        with freeze_time("2024-01-02 12:00:00"):
            self.assertEqual(banana.days_old, 1)

        # Test 5 days later
        with freeze_time("2024-01-06 12:00:00"):
            self.assertEqual(banana.days_old, 5)

    def test_banana_ordering(self):
        """Test that bananas are ordered by creation date (newest first)."""
        with freeze_time("2024-01-01"):
            first_banana = Banana.objects.create()

        with freeze_time("2024-01-02"):
            second_banana = Banana.objects.create()

        with freeze_time("2024-01-03"):
            third_banana = Banana.objects.create()

        bananas = list(Banana.objects.all())
        self.assertEqual(bananas[0], third_banana)  # Newest first
        self.assertEqual(bananas[1], second_banana)
        self.assertEqual(bananas[2], first_banana)  # Oldest last

    def test_banana_updated_at_changes(self):
        """Test that updated_at field changes when banana is modified."""
        with freeze_time("2024-01-01 12:00:00"):
            banana = Banana.objects.create()
            original_updated_at = banana.updated_at

        with freeze_time("2024-01-01 13:00:00"):
            banana.status = Banana.Status.RIPE
            banana.save()

        self.assertNotEqual(banana.updated_at, original_updated_at)

    def test_multiple_bananas_with_different_ages(self):
        """Test scenario with multiple bananas of different ages."""
        now = timezone.now()

        # Create bananas with different creation times
        bananas_data = [
            {"days_ago": 0, "expected_days_old": 0},
            {"days_ago": 1, "expected_days_old": 1},
            {"days_ago": 3, "expected_days_old": 3},
            {"days_ago": 7, "expected_days_old": 7},
            {"days_ago": 15, "expected_days_old": 15},
        ]

        bananas = []
        for data in bananas_data:
            creation_time = now - timedelta(days=data["days_ago"])
            with freeze_time(creation_time):
                banana = Banana.objects.create()
                bananas.append(banana)

        # Check each banana's age
        for i, banana in enumerate(bananas):
            expected_age = bananas_data[i]["expected_days_old"]
            self.assertEqual(banana.days_old, expected_age)
