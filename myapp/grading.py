"""
The Analynix grading scheme.

Every stock gets a letter grade (A+ down to F-) for the eleven METRICS below,
plus an overall grade. Grades are relative: a stock is compared with similar
companies, not judged against fixed thresholds.

Periods: TTM = the trailing twelve months, Fwd = analysts' consensus for the
next fiscal year, MRQ = the most recent quarter's balance sheet.

Metric grades
-------------
1. Peers: the other stocks in the same industry. When fewer than MIN_PEERS
   stocks in the industry have a number for the metric, the stock is compared
   with its whole sector instead (or with every stock, if the sector is also
   too small).
2. Percentile: the share of those peers the stock beats, with ties counted as
   half, so 50 means exactly in the middle. For P/E, forward P/E, P/S and P/B
   lower is better, so "beating" a peer means being cheaper than it.
3. Letter: the percentile becomes a letter through GRADE_CUTOFFS, a bell curve
   centred on C: about 3% of stocks get an A+, 14% a C and 3% an F-.

A missing number is left out (the grade shows "N/A"); it is not treated as zero
or as an F-. The valuation ratios are only graded when positive: a company that
is losing money has no meaningful P/E, so its P/E grade is N/A (the losses already
count through earnings, profit margin and EPS), and the same goes for P/B when
book value is negative (often just the result of large buybacks).

Overall grade
-------------
A stock's metric percentiles are averaged using WEIGHTS (with the AI analyst's
grade added when there is a current one). That average is ranked against every
other stock, which gives the overall score (0-100: the share of all stocks it
beats) and, through the same cutoffs, the overall letter grade. A stock needs at
least MIN_METRICS graded metrics to get an overall grade.

This module has no Django imports, so it can be tested on its own.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from statistics import median

GRADES = ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F+", "F", "F-")
NO_GRADE = "N/A"

# (lowest percentile that earns the grade, grade), best first. The bands form a
# symmetric bell curve around the middle (C = 43-57), so an average stock gets a C.
GRADE_CUTOFFS = (
    (97.0, "A+"),  # top 3%
    (94.0, "A"),
    (90.0, "A-"),
    (84.0, "B+"),
    (76.0, "B"),
    (67.0, "B-"),
    (57.0, "C+"),
    (43.0, "C"),  # middle 14%
    (33.0, "C-"),
    (24.0, "D+"),
    (16.0, "D"),
    (10.0, "D-"),
    (6.0, "F+"),
    (3.0, "F"),
    (0.0, "F-"),  # bottom 3%
)

# "Top Rated" page: B or better (top ~24%). "Low Rated" page: D or worse (bottom ~24%).
TOP_GRADES = GRADES[: GRADES.index("B") + 1]
LOW_GRADES = GRADES[GRADES.index("D") :]

# An industry needs this many stocks with a number for a metric to be the peer
# group for it; smaller industries are compared within their sector.
MIN_PEERS = 10

# A stock needs at least this many graded metrics (of 11) to get an overall grade,
# which leaves out preferred shares and companies with almost no data.
MIN_METRICS = 4


@dataclass(frozen=True)
class Metric:
    key: str  # key in StockData.values
    grade_field: str  # StockInfo field that stores the letter grade
    label: str
    higher_is_better: bool


METRICS = (
    Metric("revenue", "grade", "Revenue (TTM)", True),
    Metric("rev_growth", "rev_growth_grade", "Revenue growth (TTM)", True),
    Metric("ebitda_growth", "ebitda_growth_grade", "EBITDA growth (TTM)", True),
    Metric("eps_growth_fwd", "eps_growth_fwd_grade", "EPS growth (Fwd)", True),
    Metric("profit", "profit_grade", "Earnings (TTM)", True),
    Metric("profit_margin", "profit_margin_grade", "Profit margin (TTM)", True),
    Metric("pe", "pe_grade", "P/E (TTM)", False),
    Metric("fwdpe", "fwdpe_grade", "P/E (Fwd)", False),
    Metric("eps", "eps_grade", "EPS (TTM)", True),
    Metric("ps", "ps_grade", "P/S (TTM)", False),
    Metric("pb", "pb_grade", "P/B (MRQ)", False),
)

# How much each metric counts toward the overall grade.
WEIGHTS = {metric.key: 1.0 for metric in METRICS}

# The AI analyst's grade counts as much as one metric. (The old scheme counted
# it five times over, and a missing AI grade cost a stock 35 points.)
AI_WEIGHT = 1.0


def _band_midpoints():
    midpoints, upper = {}, 100.0
    for lower, grade in GRADE_CUTOFFS:
        midpoints[grade] = (lower + upper) / 2
        upper = lower
    return midpoints


# A letter grade from the AI analyst counts as the percentile in the middle of
# its band, e.g. B+ (84-90) counts as 87.
GRADE_MIDPOINTS = _band_midpoints()


def letter_grade(percentile):
    """Letter grade for a percentile (0-100); "N/A" when there is none."""
    if percentile is None:
        return NO_GRADE
    for lower, grade in GRADE_CUTOFFS:
        if percentile >= lower:
            return grade
    return GRADES[-1]


def percentile_ranks(values, higher_is_better=True):
    """Map each key to the share (0-100) of the group it beats; ties count half.

    A group of one scores 50.
    """
    scores = {key: value if higher_is_better else -value for key, value in values.items()}
    ordered = sorted(scores.values())
    count = len(ordered)
    ranks = {}
    for key, score in scores.items():
        below = bisect_left(ordered, score)
        ties = bisect_right(ordered, score) - below  # includes the stock itself
        ranks[key] = 100.0 * (below + 0.5 * ties) / count
    return ranks


@dataclass
class StockData:
    """What the grader needs to know about one stock."""

    name: str
    industry: str
    sector: str
    values: dict  # metric key -> number, or None when missing
    ai_grade: str | None = None


@dataclass
class StockResult:
    grades: dict  # StockInfo grade field -> letter grade
    percentiles: dict  # metric key -> percentile (only graded metrics)
    peer_groups: dict  # metric key -> "industry", "sector" or "market"
    peer_medians: dict  # metric key -> median of that peer group (None if it has none)
    composite: float | None  # weighted average of percentiles
    overall_score: float | None  # share of all stocks this one beats (0-100)
    overall_grade: str = NO_GRADE
    ai_grade_used: bool = field(default=False)


def grade_stocks(stocks):
    """Grade every stock. Returns {ticker: StockResult}."""
    percentiles = {stock.name: {} for stock in stocks}
    peer_groups = {stock.name: {} for stock in stocks}
    peer_medians = {stock.name: {} for stock in stocks}

    for metric in METRICS:
        graded = [s for s in stocks if s.values.get(metric.key) is not None]
        by_industry, by_sector = defaultdict(list), defaultdict(list)
        for stock in graded:
            by_industry[stock.industry].append(stock)
            by_sector[stock.sector].append(stock)

        ranks, medians = {}, {}
        for stock in stocks:
            # The peer group depends only on the stock's industry and sector, so
            # stocks without this number still get one (for the median shown).
            if len(by_industry[stock.industry]) >= MIN_PEERS:
                level, label, members = "industry", stock.industry, by_industry[stock.industry]
            elif len(by_sector[stock.sector]) >= MIN_PEERS:
                level, label, members = "sector", stock.sector, by_sector[stock.sector]
            else:
                level, label, members = "market", None, graded
            if (level, label) not in ranks:
                values = {m.name: m.values[metric.key] for m in members}
                ranks[level, label] = percentile_ranks(values, metric.higher_is_better)
                medians[level, label] = median(values.values()) if values else None
            peer_groups[stock.name][metric.key] = level
            peer_medians[stock.name][metric.key] = medians[level, label]
            if stock.name in ranks[level, label]:
                percentiles[stock.name][metric.key] = ranks[level, label][stock.name]

    composites, used_ai = {}, set()
    for stock in stocks:
        weighted = [(WEIGHTS.get(k, 0.0), p) for k, p in percentiles[stock.name].items()]
        weighted = [(w, p) for w, p in weighted if w > 0]
        if len(weighted) < MIN_METRICS:
            continue
        if AI_WEIGHT > 0 and stock.ai_grade in GRADE_MIDPOINTS:
            weighted.append((AI_WEIGHT, GRADE_MIDPOINTS[stock.ai_grade]))
            used_ai.add(stock.name)
        total_weight = sum(w for w, _ in weighted)
        composites[stock.name] = sum(w * p for w, p in weighted) / total_weight

    overall = percentile_ranks(composites) if composites else {}

    results = {}
    for stock in stocks:
        stock_percentiles = percentiles[stock.name]
        score = overall.get(stock.name)
        results[stock.name] = StockResult(
            grades={m.grade_field: letter_grade(stock_percentiles.get(m.key)) for m in METRICS},
            percentiles=stock_percentiles,
            peer_groups=peer_groups[stock.name],
            peer_medians=peer_medians[stock.name],
            composite=composites.get(stock.name),
            overall_score=score,
            overall_grade=letter_grade(score),
            ai_grade_used=stock.name in used_ai,
        )
    return results


# --- Reading the inputs from a StockInfo row --------------------------------


def _positive(value):
    return value if value is not None and value > 0 else None


def metric_values(stock):
    """The grading inputs for one StockInfo row (None means missing).

    Valuation ratios count only when positive (see the module docstring).
    """
    return {
        "revenue": stock.revenue,
        "rev_growth": stock.rev_growth_float,
        "ebitda_growth": stock.ebitda_growth_float,
        "eps_growth_fwd": stock.eps_growth_fwd_float,
        "profit": stock.profit,
        "profit_margin": stock.profit_margin_float,
        "pe": _positive(stock.pe_float),
        "fwdpe": _positive(stock.fwdpe_float),
        "eps": stock.eps_float,
        "ps": _positive(stock.ps_float),
        "pb": _positive(stock.pb_float),
    }


def current_ai_grade(analysis):
    """The AI analyst's grade, if it was produced by the current pipeline.

    Analyses from the old pipeline (no "as_of" date) are ignored: the old prompt
    fed the model the old, miscalculated metric grades, so its grade inherited
    those errors.
    """
    if not isinstance(analysis, dict) or not analysis.get("as_of"):
        return None
    grade = analysis.get("grade")
    return grade if grade in GRADES else None
