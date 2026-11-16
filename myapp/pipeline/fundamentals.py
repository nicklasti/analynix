"""Fundamentals for every stock, from the finviz screener.

One screener page returns 20 stocks with every column we need, so the whole
market takes a few hundred requests instead of one request per stock.
"""

import logging
import time
import warnings

from django.conf import settings
from django.db import transaction

from myapp.models import StockInfo

from .formatting import (
    MISSING,
    clean_text,
    display_timestamp,
    human_format,
    parse_number,
    percent,
    positive,
    ratio,
)

log = logging.getLogger(__name__)

# finviz custom-screener column numbers and the column names the returned table
# uses for them. (finvizfinance.constants.CUSTOM_SCREENER_COLUMNS lists most of
# them; 133 "Sales YoY TTM" is newer than that list.)
COLUMNS = {
    1: "Ticker",
    2: "Company",
    3: "Sector",
    4: "Industry",
    6: "Market Cap",
    7: "P/E",
    8: "Fwd P/E",
    10: "P/S",
    11: "P/B",
    16: "EPS",
    18: "EPS Next Y",  # analysts' EPS growth estimate for next year
    133: "Sales YoY TTM",  # revenue growth, last 12 months vs the 12 before
    24: "Outstanding",
    25: "Float",
    30: "Short Float",
    31: "Short Ratio",
    41: "Profit M",
    48: "Beta",
    63: "Avg Volume",
    65: "Price",
    73: "Book/sh",
    78: "Income",
    82: "Sales",
}

# Funds and shells, not operating companies, so the metrics don't mean much.
EXCLUDED_INDUSTRIES = {
    "Exchange Traded Fund",
    "Closed-End Fund - Debt",
    "Closed-End Fund - Equity",
    "Closed-End Fund - Foreign",
    "Shell Companies",
}

# A full refresh deletes stocks finviz no longer lists (delisted, merged). As a
# safety net that only happens when the refresh returned at least this many stocks.
MIN_STOCKS_TO_PRUNE = 500


# finviz only shows the first 1,000 results of a screen to visitors without a
# subscription (page 51 is refused), so the market is fetched one industry at a time.
MAX_PAGES_PER_SCREEN = 50


def all_industries():
    """Every finviz industry except funds and shell companies."""
    from finvizfinance.constants import filter_dict

    not_industries = {"Any", "Stocks only (ex-Funds)"}
    return [
        name
        for name in filter_dict["Industry"]["option"]
        if name not in not_industries and name not in EXCLUDED_INDUSTRIES
    ]


def fetch_screener_pages(industry=None, min_market_cap=None, delay=None):
    """Yield the rows (dicts keyed by COLUMNS names) of each 20-stock screener page,
    for one industry or (by default) every industry.

    When finviz rate-limits us (Cloudflare 403), waits and retries the same page,
    so a long run survives a temporary block.
    """
    from finvizfinance.exceptions import FinvizBlockedError
    from finvizfinance.screener.custom import Custom  # slow import; only needed here

    delay = settings.SCRAPE_DELAY_SECONDS if delay is None else delay
    industries = [industry] if industry else all_industries()
    checked_columns = False
    for number, name in enumerate(industries, start=1):
        filters = {"Industry": name}
        if min_market_cap:
            filters["Market Cap."] = min_market_cap
        for page in range(1, MAX_PAGES_PER_SCREEN + 1):
            screener = Custom()
            screener.set_filter(filters_dict=filters)
            frame = with_block_retries(
                lambda: screener.screener_view(columns=list(COLUMNS), verbose=0, select_page=page),
                FinvizBlockedError,
                f"{name}, page {page}",
            )
            time.sleep(delay)
            if frame is None or frame.empty:
                break
            if not checked_columns:
                missing = set(COLUMNS.values()) - set(frame.columns)
                if missing:
                    raise RuntimeError(f"finviz screener is missing columns {sorted(missing)}; finviz may have changed")
                checked_columns = True
            rows = frame.to_dict("records")
            for row in rows:
                # The table sometimes leaves Industry blank; we know which one we asked for.
                if not clean_text(row.get("Industry")):
                    row["Industry"] = name
            yield rows
            if len(frame) < Custom.size:
                break  # last page
        else:
            log.warning("%s has more than %d stocks; only the first %d were fetched", name, 20 * MAX_PAGES_PER_SCREEN, 20 * MAX_PAGES_PER_SCREEN)
        if number % 25 == 0:
            log.info("Fundamentals: %d of %d industries fetched", number, len(industries))


# How long to wait after each consecutive block before giving up (about 45 minutes in
# all, so an unattended weekly run rides out a block).
BLOCK_WAITS = (30, 60, 120, 300, 600, 900, 900)


def with_block_retries(fetch, blocked_error, what):
    """Call fetch(); while finviz blocks us, wait (BLOCK_WAITS) and try again."""
    for wait in (*BLOCK_WAITS, None):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # finvizfinance warns on every select_page call
                return fetch()
        except blocked_error:
            if wait is None:
                raise
            log.warning("finviz is rate-limiting us (%s); waiting %d s", what, wait)
            time.sleep(wait)


def stock_fields(row):
    """StockInfo field values for one screener row."""
    number = {name: parse_number(row.get(name)) for name in COLUMNS.values() if name not in ("Ticker", "Company", "Sector", "Industry")}
    pe, fwdpe = positive(number["P/E"]), positive(number["Fwd P/E"])
    ps, pb = positive(number["P/S"]), positive(number["P/B"])
    bvps, shares_out = number["Book/sh"], number["Outstanding"]
    book_value = bvps * shares_out if bvps is not None and shares_out else None
    return {
        "company_name": clean_text(row.get("Company")),
        "sector": clean_text(row.get("Sector")),
        "industry": clean_text(row.get("Industry")),
        "stock_price": number["Price"] or 0,
        "beta": number["Beta"],
        "mkt_cap": number["Market Cap"],
        "mkt_cap_short": human_format(number["Market Cap"]),
        "revenue": number["Sales"],
        "revenue_short": human_format(number["Sales"]),
        "rev_growth_float": number["Sales YoY TTM"],
        "rev_growth": percent(number["Sales YoY TTM"]),
        "eps_growth_fwd_float": number["EPS Next Y"],
        "eps_growth_fwd": percent(number["EPS Next Y"]),
        "profit": number["Income"],
        "profit_short": human_format(number["Income"]),
        "profit_margin_float": number["Profit M"],
        "profit_margin": percent(number["Profit M"]),
        "pe_float": pe,
        "pe": ratio(pe),
        "fwdpe_float": fwdpe,
        "fwdpe": ratio(fwdpe),
        "eps_float": number["EPS"],
        "eps": ratio(number["EPS"]),
        "ps_float": ps,
        "ps": ratio(ps),
        "pb_float": pb,
        "pb": ratio(pb),
        "bvps": bvps,
        "book_value": human_format(book_value) if book_value is not None else MISSING,
        "avg_volume_float": number["Avg Volume"] or 0,
        "avg_volume": human_format(number["Avg Volume"]),
        "shares_float_float": number["Float"] or 0,
        "shares_float": human_format(number["Float"]),
        "short_float_float": number["Short Float"] or 0,
        "short_float": percent(number["Short Float"]),
        "dtc": number["Short Ratio"],
        "last_update": display_timestamp(),
    }


def update_fundamentals(industry=None, min_market_cap=None, prune=True, delay=None):
    """Fetch the screener and save every stock. Returns a summary dict.

    Each page is saved as soon as it arrives, so if finviz blocks us for good
    halfway through, the stocks fetched so far are still updated.
    """
    existing = set(StockInfo.objects.values_list("name", flat=True))
    created = updated = 0
    seen = set()
    for rows in fetch_screener_pages(industry=industry, min_market_cap=min_market_cap, delay=delay):
        with transaction.atomic():
            for row in rows:
                ticker = clean_text(row.get("Ticker")).upper()
                if not ticker or clean_text(row.get("Industry")) in EXCLUDED_INDUSTRIES:
                    continue
                seen.add(ticker)
                _, was_created = StockInfo.objects.update_or_create(name=ticker, defaults=stock_fields(row))
                created += was_created
                updated += not was_created
    log.info("finviz returned %d stocks", len(seen))

    # Only a complete refresh of the whole market can tell which stocks were delisted.
    stale = sorted(existing - seen) if prune and industry is None and len(seen) >= MIN_STOCKS_TO_PRUNE else []
    for start in range(0, len(stale), 500):
        StockInfo.objects.filter(name__in=stale[start : start + 500]).delete()
    return {"fetched": len(seen), "created": created, "updated": updated, "removed": len(stale)}
