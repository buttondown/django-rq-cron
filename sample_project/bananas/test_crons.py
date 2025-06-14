from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from datetime import timedelta
from unittest.mock import patch

from .models import Banana
from .crons.banana_aging import update_banana_ripeness, cleanup_old_bananas


class BananaCronTestCase(TestCase):
    """Test cases for banana cron jobs."""

    def setUp(self):
        """Set up test data."""
        # Clear any existing bananas
        Banana.objects.all().delete()

    def test_update_banana_ripeness_unripe_to_ripe(self):
        """Test bananas transition from unripe to ripe after 3 days."""
        # Create a 4-day-old unripe banana
        four_days_ago = timezone.now() - timedelta(days=4)
        with freeze_time(four_days_ago):
            banana = Banana.objects.create(status=Banana.Status.UNRIPE)

        # Run the cron job
        result = update_banana_ripeness()

        # Check the banana is now ripe
        banana.refresh_from_db()
        self.assertEqual(banana.status, Banana.Status.RIPE)
        self.assertEqual(result["updated_count"], 1)

    def test_update_banana_ripeness_ripe_to_overripe(self):
        """Test bananas transition from ripe to overripe after 6 days."""
        # Create a 7-day-old ripe banana
        seven_days_ago = timezone.now() - timedelta(days=7)
        with freeze_time(seven_days_ago):
            banana = Banana.objects.create(status=Banana.Status.RIPE)

        # Run the cron job
        result = update_banana_ripeness()

        # Check the banana is now overripe
        banana.refresh_from_db()
        self.assertEqual(banana.status, Banana.Status.OVERRIPE)
        self.assertEqual(result["updated_count"], 1)

    def test_update_banana_ripeness_no_change_needed(self):
        """Test that bananas with correct status are not updated."""
        # Create bananas with correct status for their age
        now = timezone.now()

        # 1-day-old unripe banana (correct)
        with freeze_time(now - timedelta(days=1)):
            unripe_banana = Banana.objects.create(status=Banana.Status.UNRIPE)

        # 4-day-old ripe banana (correct)
        with freeze_time(now - timedelta(days=4)):
            ripe_banana = Banana.objects.create(status=Banana.Status.RIPE)

        # 8-day-old overripe banana (correct)
        with freeze_time(now - timedelta(days=8)):
            overripe_banana = Banana.objects.create(status=Banana.Status.OVERRIPE)

        # Run the cron job
        result = update_banana_ripeness()

        # Check no bananas were updated
        self.assertEqual(result["updated_count"], 0)

        # Verify statuses remain the same
        unripe_banana.refresh_from_db()
        ripe_banana.refresh_from_db()
        overripe_banana.refresh_from_db()

        self.assertEqual(unripe_banana.status, Banana.Status.UNRIPE)
        self.assertEqual(ripe_banana.status, Banana.Status.RIPE)
        self.assertEqual(overripe_banana.status, Banana.Status.OVERRIPE)

    def test_update_banana_ripeness_multiple_bananas(self):
        """Test updating multiple bananas with different statuses."""
        now = timezone.now()

        # Create bananas that need updates
        bananas_to_create = [
            {"days_ago": 0, "status": Banana.Status.UNRIPE},  # No change needed
            {"days_ago": 3, "status": Banana.Status.UNRIPE},  # Should become ripe
            {"days_ago": 5, "status": Banana.Status.UNRIPE},  # Should become ripe
            {"days_ago": 6, "status": Banana.Status.RIPE},  # Should become overripe
            {"days_ago": 8, "status": Banana.Status.UNRIPE},  # Should become overripe
        ]

        bananas = []
        for banana_data in bananas_to_create:
            creation_time = now - timedelta(days=banana_data["days_ago"])
            with freeze_time(creation_time):
                banana = Banana.objects.create(status=banana_data["status"])
                bananas.append(banana)

        # Run the cron job
        result = update_banana_ripeness()

        # Check that 4 bananas were updated (all except the fresh one)
        self.assertEqual(result["updated_count"], 4)

        # Verify specific statuses
        for banana in bananas:
            banana.refresh_from_db()

        self.assertEqual(bananas[0].status, Banana.Status.UNRIPE)  # 0 days - no change
        self.assertEqual(bananas[1].status, Banana.Status.RIPE)  # 3 days - now ripe
        self.assertEqual(bananas[2].status, Banana.Status.RIPE)  # 5 days - now ripe
        self.assertEqual(
            bananas[3].status, Banana.Status.OVERRIPE
        )  # 6 days - now overripe
        self.assertEqual(
            bananas[4].status, Banana.Status.OVERRIPE
        )  # 8 days - now overripe

    def test_cleanup_old_bananas(self):
        """Test that old overripe bananas are cleaned up."""
        now = timezone.now()

        # Create bananas of different ages and statuses
        bananas_to_create = [
            {"days_ago": 5, "status": Banana.Status.OVERRIPE},  # Too young to clean
            {"days_ago": 10, "status": Banana.Status.OVERRIPE},  # Should be cleaned
            {"days_ago": 12, "status": Banana.Status.OVERRIPE},  # Should be cleaned
            {"days_ago": 15, "status": Banana.Status.RIPE},  # Old but not overripe
        ]

        bananas = []
        for banana_data in bananas_to_create:
            creation_time = now - timedelta(days=banana_data["days_ago"])
            with freeze_time(creation_time):
                banana = Banana.objects.create(status=banana_data["status"])
                bananas.append(banana)

        # Run the cleanup cron job
        result = cleanup_old_bananas()

        # Check that 2 bananas were cleaned up
        self.assertEqual(result["cleaned_count"], 2)

        # Verify only the correct bananas remain
        remaining_bananas = Banana.objects.all()
        self.assertEqual(remaining_bananas.count(), 2)

        # Check that the 5-day-old overripe and 15-day-old ripe bananas remain
        remaining_ids = [banana.id for banana in remaining_bananas]
        self.assertIn(bananas[0].id, remaining_ids)  # 5-day-old overripe
        self.assertIn(bananas[3].id, remaining_ids)  # 15-day-old ripe

    def test_cleanup_old_bananas_no_cleanup_needed(self):
        """Test cleanup when no bananas need to be removed."""
        now = timezone.now()

        # Create bananas that shouldn't be cleaned up
        bananas_to_create = [
            {"days_ago": 1, "status": Banana.Status.UNRIPE},
            {"days_ago": 5, "status": Banana.Status.RIPE},
            {
                "days_ago": 8,
                "status": Banana.Status.OVERRIPE,
            },  # Overripe but not old enough
        ]

        for banana_data in bananas_to_create:
            creation_time = now - timedelta(days=banana_data["days_ago"])
            with freeze_time(creation_time):
                Banana.objects.create(status=banana_data["status"])

        # Run the cleanup cron job
        result = cleanup_old_bananas()

        # Check that no bananas were cleaned up
        self.assertEqual(result["cleaned_count"], 0)
        self.assertEqual(Banana.objects.count(), 3)

    @patch("builtins.print")
    def test_update_banana_ripeness_prints_message(self, mock_print):
        """Test that the cron job prints a status message."""
        # Create a banana that needs updating
        three_days_ago = timezone.now() - timedelta(days=3)
        with freeze_time(three_days_ago):
            Banana.objects.create(status=Banana.Status.UNRIPE)

        # Run the cron job
        update_banana_ripeness()

        # Check that print was called with the expected message
        mock_print.assert_called_with("Updated 1 banana(s) ripeness status")

    @patch("builtins.print")
    def test_cleanup_old_bananas_prints_message(self, mock_print):
        """Test that the cleanup cron job prints a status message."""
        # Create an old overripe banana
        twelve_days_ago = timezone.now() - timedelta(days=12)
        with freeze_time(twelve_days_ago):
            Banana.objects.create(status=Banana.Status.OVERRIPE)

        # Run the cleanup cron job
        cleanup_old_bananas()

        # Check that print was called with the expected message
        mock_print.assert_called_with("Cleaned up 1 old banana(s)")

    def test_banana_aging_edge_cases(self):
        """Test edge cases for banana aging transitions."""
        now = timezone.now()

        # Test exact boundary conditions
        boundary_cases = [
            {
                "days_ago": 2,
                "initial_status": Banana.Status.UNRIPE,
                "expected_status": Banana.Status.UNRIPE,
            },  # Still unripe
            {
                "days_ago": 3,
                "initial_status": Banana.Status.UNRIPE,
                "expected_status": Banana.Status.RIPE,
            },  # Just became ripe
            {
                "days_ago": 5,
                "initial_status": Banana.Status.UNRIPE,
                "expected_status": Banana.Status.RIPE,
            },  # Still ripe
            {
                "days_ago": 6,
                "initial_status": Banana.Status.RIPE,
                "expected_status": Banana.Status.OVERRIPE,
            },  # Just became overripe
        ]

        bananas = []
        for case in boundary_cases:
            creation_time = now - timedelta(days=case["days_ago"])
            with freeze_time(creation_time):
                banana = Banana.objects.create(status=case["initial_status"])
                bananas.append((banana, case["expected_status"]))

        # Run the cron job
        update_banana_ripeness()

        # Verify each banana has the expected status
        for banana, expected_status in bananas:
            banana.refresh_from_db()
            self.assertEqual(banana.status, expected_status)
