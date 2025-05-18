from django.core.management.base import BaseCommand

from django_rq_cron.registry import import_crons
from django_rq_cron.runner import bootstrap


class Command(BaseCommand):
    help = "Bootstrap cron jobs by scheduling the first run of each cadence."

    def add_arguments(self, parser):
        parser.add_argument(
            "--queue",
            type=str,
            default="default",
            help="The name of the RQ queue to use for scheduling cron jobs.",
        )

    def handle(self, *args, **options):
        queue = options["queue"]

        # Import cron jobs from all installed apps
        import_crons()

        # Bootstrap cron jobs
        jobs = bootstrap(queue)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully bootstrapped {len(jobs)} cron job cadences."
            )
        )
