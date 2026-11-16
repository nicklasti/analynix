from django.core.management.base import BaseCommand

from myapp.pipeline.ebitda import update_ebitda


class Command(BaseCommand):
    help = "Fetch TTM EBITDA growth from finviz's quarterly income statements (one request per stock)."

    def add_arguments(self, parser):
        parser.add_argument("tickers", nargs="*", help="Only these tickers (default: every graded stock).")
        parser.add_argument("--limit", type=int, help="Stop after this many stocks (longest-unchecked first).")

    def handle(self, *args, **options):
        tickers = [ticker.upper() for ticker in options["tickers"]] or None
        summary = update_ebitda(tickers=tickers, limit=options["limit"])
        self.stdout.write(
            self.style.SUCCESS(
                "EBITDA growth: {updated} stocks updated, {missing} without enough data, {failed} failed.".format(
                    **summary
                )
            )
        )
