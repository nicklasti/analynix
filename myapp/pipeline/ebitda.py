"""EBITDA growth over the last twelve months, from finviz's quarterly income statements.

The finviz screener has no EBITDA growth column, so this takes one request per
stock: the last eight quarters of EBITDA, comparing the latest four with the
four before them. (Nobody publishes analysts' EBITDA forecasts for free, so there
is no forward EBITDA growth; forward EPS growth comes with the fundamentals.)
"""

import logging
import time
from datetime import date

from django.conf import settings
from django.db.models import F

from myapp.grading import NO_GRADE
from myapp.models import StockInfo

from .formatting import clean_text, parse_number, percent
from .fundamentals import with_block_retries

log = logging.getLogger(__name__)


def ttm_growth(quarters):
    """Growth of the latest four quarters' total over the four before.

    `quarters` is most recent first. None when there aren't eight quarters, or
    when the earlier total isn't positive (a growth rate off a loss means nothing).
    """
    if len(quarters) < 8 or any(value is None for value in quarters[:8]):
        return None
    current, previous = sum(quarters[:4]), sum(quarters[4:8])
    if previous <= 0:
        return None
    return current / previous - 1


def is_quarter(length):
    """'3 Months' or '13 Weeks' (retailers) is a quarter; '6 Months' is not."""
    parts = clean_text(length).split()
    if len(parts) != 2 or not parts[0].isdigit():
        return True  # unknown format: don't throw the data away
    count, unit = int(parts[0]), parts[1].lower()
    if unit.startswith("month"):
        return count <= 4
    if unit.startswith("week"):
        return count <= 17
    return True


def fetch_ebitda_growth(ticker):
    """TTM EBITDA growth for one stock (None when finviz doesn't have enough data)."""
    from finvizfinance.quote import Statements  # slow import; only needed here

    frame = Statements().get_statements(ticker, statement="I", timeframe="Q")
    if frame is None or "EBITDA" not in frame.index:
        return None
    if "Period Length" in frame.index:
        if not all(is_quarter(length) for length in frame.loc["Period Length"].tolist()[:8]):
            return None  # e.g. a company that reports every six months
    return ttm_growth([parse_number(value) for value in frame.loc["EBITDA"].tolist()])


def update_ebitda(tickers=None, limit=None, delay=None):
    """Fetch TTM EBITDA growth for each graded stock, longest-unchecked first.

    That order means a run that gets interrupted carries on next time where it
    stopped. About 2.5 seconds per stock.
    """
    from finvizfinance.exceptions import FinvizBlockedError

    delay = settings.SCRAPE_DELAY_SECONDS if delay is None else delay
    if tickers:
        names = list(tickers)
    else:
        names = list(
            StockInfo.objects.exclude(overall_grade=NO_GRADE)
            .order_by(F("ebitda_as_of").asc(nulls_first=True), "name")
            .values_list("name", flat=True)
        )
    if limit:
        names = names[:limit]

    updated = missing = failed = 0
    for number, ticker in enumerate(names, start=1):
        try:
            growth = with_block_retries(lambda: fetch_ebitda_growth(ticker), FinvizBlockedError, f"EBITDA for {ticker}")
        except FinvizBlockedError:
            log.error("finviz kept blocking us; stopping after %d stocks", number - 1)
            break
        except Exception as error:
            log.warning("EBITDA failed for %s: %s", ticker, error)
            failed += 1
        else:
            StockInfo.objects.filter(name=ticker).update(
                ebitda_growth_float=growth,
                ebitda_growth=percent(growth),
                ebitda_as_of=date.today(),
            )
            updated += growth is not None
            missing += growth is None
        if number % 250 == 0:
            log.info("EBITDA: %d/%d stocks done", number, len(names))
        time.sleep(delay)
    return {"updated": updated, "missing": missing, "failed": failed}
