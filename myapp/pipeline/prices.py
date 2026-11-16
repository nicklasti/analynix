"""Daily price history for every stock, from Yahoo Finance (yfinance)."""

import logging
import time

from django.conf import settings
from django.utils import timezone

from myapp.models import StockInfo

from .formatting import display_timestamp

log = logging.getLogger(__name__)


def _closes(frame, ticker):
    """(dates, closes) for one ticker in a multi-ticker yfinance download."""
    if frame is None or ticker not in frame.columns.get_level_values(0):
        return [], []
    closes = frame[ticker]["Close"].dropna()
    dates = [day.strftime("%Y-%m-%d") for day in closes.index]
    return dates, [round(float(price), 2) for price in closes]


def update_prices(tickers=None, batch_size=100, delay=None):
    """Download the full price history for each stock and save it.

    Stocks Yahoo has no data for are left as they are (the old script deleted
    them, which made the list of stocks shrink every week).
    """
    import yfinance as yf  # slow import; only needed here

    delay = settings.SCRAPE_DELAY_SECONDS if delay is None else delay
    names = tickers or list(StockInfo.objects.order_by("name").values_list("name", flat=True))
    updated, failed = 0, []
    for start in range(0, len(names), batch_size):
        batch = names[start : start + batch_size]
        try:
            frame = yf.download(
                batch,
                period="max",
                auto_adjust=True,  # adjusted for splits and dividends
                group_by="ticker",
                threads=True,
                progress=False,
                multi_level_index=True,
            )
        except Exception:
            log.exception("Price download failed for %s..%s", batch[0], batch[-1])
            failed.extend(batch)
            continue
        for ticker in batch:
            dates, closes = _closes(frame, ticker)
            if not closes:
                failed.append(ticker)
                continue
            StockInfo.objects.filter(name=ticker).update(
                prices=closes,
                dates=dates,
                stock_price=closes[-1],
                price_updated_at=timezone.now(),
                last_update=display_timestamp(),
            )
            updated += 1
        log.info("Prices: %d/%d stocks done", min(start + batch_size, len(names)), len(names))
        time.sleep(delay)
    if failed:
        log.warning("No price data for %d stocks: %s", len(failed), ", ".join(failed[:50]))
    return {"updated": updated, "failed": len(failed)}
