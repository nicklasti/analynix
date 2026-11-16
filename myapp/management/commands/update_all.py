import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


def finished_marker():
    """A file next to the database recording when a full update last finished."""
    return Path(settings.DATABASES["default"]["NAME"]).with_name("last_full_update.txt")


class Command(BaseCommand):
    help = (
        "Refresh everything in order: fundamentals, prices, grades, EBITDA growth, news, "
        "AI analysis (if OPENAI_API_KEY is set), regrading after each slow step."
    )

    def add_arguments(self, parser):
        parser.add_argument("--skip-prices", action="store_true")
        parser.add_argument("--skip-ebitda", action="store_true")
        parser.add_argument("--skip-news", action="store_true")
        parser.add_argument("--skip-ai", action="store_true")
        parser.add_argument("--min-market-cap", help='Passed to update_fundamentals, e.g. "+Small (over $300mln)".')
        parser.add_argument(
            "--if-older-than",
            type=float,
            metavar="DAYS",
            help="Only run if no full update has finished in this many days (used when the server starts, "
            "so a restart in the middle of an update picks it up again).",
        )

    def handle(self, *args, **options):
        marker = finished_marker()
        if options["if_older_than"] is not None and marker.exists():
            finished = datetime.fromisoformat(marker.read_text().strip())
            if datetime.now(UTC) - finished < timedelta(days=options["if_older_than"]):
                self.stdout.write(f"Skipping: the last full update finished {finished:%Y-%m-%d %H:%M} UTC.")
                return

        started = time.monotonic()
        steps = [("update_fundamentals", {"min_market_cap": options["min_market_cap"]})]
        if not options["skip_prices"]:
            steps.append(("update_prices", {}))
        # Grade early so the site has current grades while the slow steps run.
        steps.append(("grade_stocks", {}))
        if not options["skip_ebitda"]:
            steps += [("update_ebitda", {}), ("grade_stocks", {})]
        if not options["skip_news"]:
            steps.append(("update_news", {}))
        if not options["skip_ai"] and settings.OPENAI_API_KEY:
            steps.append(("ai_analysis", {}))  # regrades itself, so the AI grades count
        for name, kwargs in steps:
            self.stdout.write(f"--- {name}")
            call_command(name, **{k: v for k, v in kwargs.items() if v is not None})

        marker.write_text(datetime.now(UTC).isoformat())
        minutes = (time.monotonic() - started) / 60
        self.stdout.write(self.style.SUCCESS(f"Everything refreshed in {minutes:.0f} minutes."))
