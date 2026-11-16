from django.core.management.base import BaseCommand

from myapp.pipeline.prices import update_prices


class Command(BaseCommand):
    help = "Download each stock's full daily price history from Yahoo Finance."

    def add_arguments(self, parser):
        parser.add_argument("tickers", nargs="*", help="Only these tickers (default: every stock).")
        parser.add_argument("--batch-size", type=int, default=100, help="Tickers per Yahoo request.")

    def handle(self, *args, **options):
        tickers = [ticker.upper() for ticker in options["tickers"]] or None
        summary = update_prices(tickers=tickers, batch_size=options["batch_size"])
        self.stdout.write(
            self.style.SUCCESS("Prices: {updated} stocks updated, {failed} without data.".format(**summary))
        )
