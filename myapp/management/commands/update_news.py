from django.core.management.base import BaseCommand

from myapp.pipeline.news import update_news


class Command(BaseCommand):
    help = "Fetch the latest headlines for each stock from finviz (one request per stock)."

    def add_arguments(self, parser):
        parser.add_argument("tickers", nargs="*", help="Only these tickers (default: every stock).")
        parser.add_argument("--limit", type=int, help="Stop after this many stocks (best-rated first).")

    def handle(self, *args, **options):
        tickers = [ticker.upper() for ticker in options["tickers"]] or None
        summary = update_news(tickers=tickers, limit=options["limit"])
        self.stdout.write(self.style.SUCCESS("News: {updated} stocks updated, {failed} failed.".format(**summary)))
