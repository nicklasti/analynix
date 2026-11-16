from django.core.management.base import BaseCommand

from myapp.pipeline.fundamentals import update_fundamentals


class Command(BaseCommand):
    help = "Fetch fundamentals for every stock from the finviz screener (about 20 minutes for the whole market)."

    def add_arguments(self, parser):
        parser.add_argument("--industry", help='Only this finviz industry, e.g. "Confectioners".')
        parser.add_argument(
            "--min-market-cap",
            help='finviz market-cap filter, e.g. "+Small (over $300mln)". Default: every stock.',
        )
        parser.add_argument(
            "--no-prune",
            action="store_true",
            help="Keep stocks finviz no longer lists (by default a full refresh removes them).",
        )

    def handle(self, *args, **options):
        summary = update_fundamentals(
            industry=options["industry"],
            min_market_cap=options["min_market_cap"],
            prune=not options["no_prune"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Fundamentals: {fetched} stocks fetched, {created} new, {updated} updated, "
                "{removed} no longer listed and removed.".format(**summary)
            )
        )
