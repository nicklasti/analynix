"""Recent headlines for each stock, from finviz."""

import logging
import time

from django.conf import settings

from myapp.models import StockInfo

from .formatting import clean_text

log = logging.getLogger(__name__)

HEADLINES_PER_STOCK = 6


def fetch_headlines(ticker, count=HEADLINES_PER_STOCK):
    """The latest headlines as dicts with the keys the overview page uses."""
    from finvizfinance.quote import finvizfinance  # slow import; only needed here

    frame = finvizfinance(ticker).ticker_news()
    if frame is None:
        return []
    headlines = []
    for row in frame.head(count).to_dict("records"):
        title = clean_text(row.get("Title"))
        if not title:
            continue
        date = row.get("Date")
        headlines.append(
            {
                "Article": title,
                "Source": clean_text(row.get("Source")),
                "Link": safe_link(clean_text(row.get("Link"))),
                "Date": date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else clean_text(date),
            }
        )
    return headlines


def safe_link(link):
    """An absolute http(s) URL, or "" (the page then shows the headline without a link)."""
    if link.startswith("/"):
        link = "https://finviz.com" + link
    return link if link.startswith(("https://", "http://")) else ""


def update_news(tickers=None, limit=None, delay=None):
    """Save the latest headlines for each stock (one finviz request per stock)."""
    from finvizfinance.exceptions import FinvizBlockedError

    from .fundamentals import with_block_retries

    delay = settings.SCRAPE_DELAY_SECONDS if delay is None else delay
    names = tickers or list(StockInfo.objects.order_by("-overall_grade_num").values_list("name", flat=True))
    if limit:
        names = names[:limit]
    updated, failed = 0, 0
    for number, ticker in enumerate(names, start=1):
        try:
            headlines = with_block_retries(lambda: fetch_headlines(ticker), FinvizBlockedError, f"news for {ticker}")
        except FinvizBlockedError:
            log.error("finviz kept blocking us; stopping after %d stocks", number - 1)
            break
        except Exception as error:
            log.warning("News failed for %s: %s", ticker, error)
            failed += 1
        else:
            StockInfo.objects.filter(name=ticker).update(stock_news=headlines)
            updated += 1
        if number % 100 == 0:
            log.info("News: %d/%d stocks done", number, len(names))
        time.sleep(delay)
    return {"updated": updated, "failed": failed}
