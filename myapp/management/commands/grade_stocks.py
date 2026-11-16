from django.core.management.base import BaseCommand

from myapp.pipeline.grading_job import regrade_all


class Command(BaseCommand):
    help = "Recompute every stock's metric grades, overall grade and industry medians."

    def handle(self, *args, **options):
        counts = regrade_all()
        graded = sum(count for grade, count in counts.items() if grade != "N/A")
        self.stdout.write(self.style.SUCCESS(f"Graded {graded} stocks ({counts['N/A']} without enough data)."))
        self.stdout.write("Overall grades: " + ", ".join(f"{grade} {count}" for grade, count in counts.items()))
