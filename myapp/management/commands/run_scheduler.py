"""Run the data-update jobs on a schedule.

The Docker container runs this next to the web server, in place of the old
django-crontab + cron setup (cron also drops the environment variables that now
hold the secrets).
"""

import logging
import time
from datetime import UTC, datetime, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)

# (weekdays with Monday = 0, hour, minute in UTC, commands run one after another)
SCHEDULE = [
    # Weeknights after the US market closes (5:30 pm New York time in winter):
    # closing prices for the charts, then fresh headlines.
    ((0, 1, 2, 3, 4), 22, 30, ("update_prices", "update_news")),
    # Saturday 1 am New York time: fundamentals, prices, grades, EBITDA, headlines, AI.
    ((5,), 6, 0, ("update_all",)),
]


def next_run(now, weekdays, hour, minute):
    """The first time after `now` that falls on one of `weekdays` at hour:minute."""
    for days_ahead in range(8):
        candidate = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate.weekday() in weekdays and candidate > now:
            return candidate
    raise ValueError("weekdays must not be empty")


class Command(BaseCommand):
    help = "Prices and headlines on weeknights, everything on Saturdays, forever."

    def handle(self, *args, **options):
        while True:
            now = datetime.now(UTC)
            when, commands = min((next_run(now, *job[:3]), job[3]) for job in SCHEDULE)
            self.stdout.write(f"Next job: {', '.join(commands)} at {when:%Y-%m-%d %H:%M} UTC")
            time.sleep(max(0.0, (when - datetime.now(UTC)).total_seconds()))
            for command in commands:
                try:
                    call_command(command)
                except Exception:
                    log.exception("Scheduled job %s failed", command)
