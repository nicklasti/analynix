"""Live prices, shared by every visitor.

When someone looks at a stock, its price is refreshed from Yahoo Finance if the
stored one is more than QUOTE_MAX_AGE old; everyone else in that window gets the
stored price. So a stock is looked up at most once a minute however many people
are viewing it. Ratios and grades are not touched; they have their own schedule.
"""

import logging
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from myapp.models import StockInfo

log = logging.getLogger(__name__)

QUOTE_MAX_AGE = timedelta(seconds=60)


def fetch_quote(ticker):
    """The latest trade price from Yahoo Finance, or None."""
    import yfinance as yf  # slow import; only needed here

    try:
        price = yf.Ticker(ticker).fast_info["last_price"]
    except Exception as error:
        log.warning("Live quote failed for %s: %s", ticker, error)
        return None
    return round(float(price), 2) if price else None


def current_price(stock):
    """(price, as of) for a StockInfo row, refreshing it first if it's stale."""
    now = timezone.now()
    if stock.price_updated_at and now - stock.price_updated_at < QUOTE_MAX_AGE:
        return stock.stock_price, stock.price_updated_at

    # Claim the refresh, so visitors arriving at the same moment don't all ask Yahoo.
    stale = Q(price_updated_at__isnull=True) | Q(price_updated_at__lt=now - QUOTE_MAX_AGE)
    claimed = StockInfo.objects.filter(pk=stock.pk).filter(stale).update(price_updated_at=now)
    if not claimed:
        stock.refresh_from_db(fields=["stock_price", "price_updated_at"])
        return stock.stock_price, stock.price_updated_at

    price = fetch_quote(stock.name)
    if price is None:
        return stock.stock_price, stock.price_updated_at or now
    StockInfo.objects.filter(pk=stock.pk).update(stock_price=price, price_updated_at=now)
    return price, now
