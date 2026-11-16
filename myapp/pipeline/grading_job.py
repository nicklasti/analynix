"""Recompute every stock's grades and industry comparisons, and save them."""

import logging
from collections import Counter, defaultdict
from statistics import median  # for the industry's median market cap

from django.db import transaction

from myapp.grading import (
    GRADES,
    METRICS,
    NO_GRADE,
    StockData,
    current_ai_grade,
    grade_stocks,
    metric_values,
)
from myapp.models import StockInfo

from .formatting import MISSING, human_format, percent

log = logging.getLogger(__name__)

# Everything grading reads; skips the large price-history and news fields.
INPUT_FIELDS = (
    "name",
    "industry",
    "sector",
    "mkt_cap",
    "revenue",
    "rev_growth_float",
    "ebitda_growth_float",
    "eps_growth_fwd_float",
    "profit",
    "profit_margin_float",
    "pe_float",
    "fwdpe_float",
    "eps_float",
    "ps_float",
    "pb_float",
    "bvps",
    "gpt_analysis",
)

OUTPUT_FIELDS = [m.grade_field for m in METRICS] + [
    "overall_grade",
    "overall_grade_num",
    "peer_groups",
    "avg_rev",
    "avg_rev_growth",
    "avg_ebitda_growth",
    "avg_eps_growth_fwd",
    "avg_profit",
    "avg_profit_margin",
    "avg_pe",
    "avg_fwdpe",
    "avg_eps",
    "avg_ps",
    "avg_pb",
    "avg_mkt_cap",
    "ind_size",
    "mkt_share",
    "mkt_share_float",
]


def _rounded(number):
    return None if number is None else round(number, 2)


def regrade_all():
    """Grade every stock in the database. Returns {grade: count} for the overall grades."""
    stocks = list(StockInfo.objects.only(*INPUT_FIELDS))
    data = [
        StockData(
            name=stock.name,
            industry=stock.industry,
            sector=stock.sector,
            values=metric_values(stock),
            ai_grade=current_ai_grade(stock.gpt_analysis),
        )
        for stock in stocks
    ]
    results = grade_stocks(data)

    caps = defaultdict(list)
    for stock in stocks:
        if stock.mkt_cap:
            caps[stock.industry].append(stock.mkt_cap)

    for stock in stocks:
        result = results[stock.name]
        for field, letter in result.grades.items():
            setattr(stock, field, letter)
        stock.overall_grade = result.overall_grade
        stock.overall_grade_num = round(result.overall_score, 1) if result.overall_score is not None else 0
        stock.peer_groups = result.peer_groups
        # The median of the same peer group the grade compares against.
        peers = result.peer_medians
        stock.avg_rev = human_format(peers.get("revenue"))
        stock.avg_rev_growth = percent(peers.get("rev_growth"))
        stock.avg_ebitda_growth = percent(peers.get("ebitda_growth"))
        stock.avg_eps_growth_fwd = percent(peers.get("eps_growth_fwd"))
        stock.avg_profit = human_format(peers.get("profit"))
        stock.avg_profit_margin = percent(peers.get("profit_margin"))
        stock.avg_pe = _rounded(peers.get("pe"))
        stock.avg_fwdpe = _rounded(peers.get("fwdpe"))
        stock.avg_eps = _rounded(peers.get("eps"))
        stock.avg_ps = _rounded(peers.get("ps"))
        stock.avg_pb = _rounded(peers.get("pb"))
        industry_caps = caps.get(stock.industry, [])
        industry_size = sum(industry_caps)
        stock.avg_mkt_cap = human_format(median(industry_caps)) if industry_caps else MISSING
        stock.ind_size = human_format(industry_size) if industry_caps else MISSING
        share = stock.mkt_cap / industry_size if stock.mkt_cap and industry_size else None
        stock.mkt_share_float = share
        stock.mkt_share = percent(share)

    with transaction.atomic():
        StockInfo.objects.bulk_update(stocks, OUTPUT_FIELDS, batch_size=500)

    counts = Counter(result.overall_grade for result in results.values())
    used_ai = sum(result.ai_grade_used for result in results.values())
    log.info("Graded %d stocks (%d with an AI grade)", len(stocks), used_ai)
    return {grade: counts.get(grade, 0) for grade in (*GRADES, NO_GRADE)}
