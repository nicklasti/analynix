from django.core.management.base import BaseCommand

from myapp.pipeline.ai_analysis import run_ai_analysis
from myapp.pipeline.grading_job import regrade_all


class Command(BaseCommand):
    help = (
        "Write the AI analyst summary and grade for each stock (needs OPENAI_API_KEY), "
        "then regrade so the new AI grades count toward the overall grades."
    )

    def add_arguments(self, parser):
        parser.add_argument("tickers", nargs="*", help="Only these tickers (always re-analysed).")
        parser.add_argument("--limit", type=int, help="Stop after this many stocks.")
        parser.add_argument(
            "--max-age-days",
            type=int,
            default=7,
            help="Skip stocks analysed within this many days (default 7), so a stopped run can resume.",
        )

    def handle(self, *args, **options):
        tickers = [ticker.upper() for ticker in options["tickers"]] or None
        summary = run_ai_analysis(tickers=tickers, limit=options["limit"], max_age_days=options["max_age_days"])
        if summary.get("skipped"):
            self.stdout.write(self.style.WARNING(f"AI analysis skipped: {summary['skipped']}."))
        if "input_tokens" in summary:
            self.stdout.write(
                self.style.SUCCESS(
                    "AI analysis: {analysed} stocks analysed, {failed} failed "
                    "({input_tokens:,} input + {output_tokens:,} output tokens).".format(**summary)
                )
            )
        if summary.get("analysed"):
            # The AI grade is one of the inputs to the overall grade, so regrade now.
            regrade_all()
            self.stdout.write("Overall grades updated to include the new AI grades.")
