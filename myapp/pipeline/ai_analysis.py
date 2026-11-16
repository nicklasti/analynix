"""Optional AI analyst write-up and grade for each stock (OpenAI).

One request per stock returns a JSON object, replacing the old seven-message
conversation and the sentence filters that tried to clean up its replies.
"""

import json
import logging
import re
from datetime import date, timedelta

from django.conf import settings
from django.db.models.fields.json import KT

from myapp.grading import GRADES, METRICS, NO_GRADE
from myapp.models import StockInfo

from .formatting import display_timestamp

log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an equity research assistant writing short notes for retail investors on a "
    "stock-screening website. Write in a neutral third-person voice (never 'I' or 'you'). "
    "Use only the data provided and do not invent facts. Each metric comes with the "
    "industry median and a letter grade for how the stock ranks against its industry. "
    "Reply with a JSON object with these string keys: "
    '"metrics" (2-4 sentences on what the numbers say compared with the industry), '
    '"news" (2-4 sentences summarising the headlines, or saying there are none), '
    '"strengths" (2-3 sentences on strengths and opportunities), '
    '"weaknesses" (2-3 sentences on weaknesses and threats), '
    '"thesis" (3-5 sentences giving an overall investment view), '
    '"grade" (exactly one of: ' + ", ".join(GRADES) + ")."
)

# For each metric: the StockInfo field with the stock's value and the one with the industry median.
METRIC_DISPLAY_FIELDS = {
    "revenue": ("revenue_short", "avg_rev"),
    "rev_growth": ("rev_growth", "avg_rev_growth"),
    "ebitda_growth": ("ebitda_growth", "avg_ebitda_growth"),
    "eps_growth_fwd": ("eps_growth_fwd", "avg_eps_growth_fwd"),
    "profit": ("profit_short", "avg_profit"),
    "profit_margin": ("profit_margin", "avg_profit_margin"),
    "pe": ("pe", "avg_pe"),
    "fwdpe": ("fwdpe", "avg_fwdpe"),
    "eps": ("eps", "avg_eps"),
    "ps": ("ps", "avg_ps"),
    "pb": ("pb", "avg_pb"),
}


def parse_grade(value):
    """'B+', 'b plus', 'Grade: B+.' -> 'B+'; anything else -> 'N/A'."""
    text = str(value or "").strip().upper().rstrip(".")
    text = text.replace("PLUS", "+").replace("MINUS", "-").replace("−", "-").replace("–", "-")
    text = text.replace(" ", "")
    match = re.search(r"(?:^|[^A-Z])([A-DF][+-]?)$", text)
    return match.group(1) if match and match.group(1) in GRADES else NO_GRADE


def stock_payload(stock):
    """The facts the model is given about one stock (not its overall grade)."""
    metrics = {}
    for metric in METRICS:
        value_field, median_field = METRIC_DISPLAY_FIELDS[metric.key]
        median = getattr(stock, median_field)
        metrics[metric.label] = {
            "value": getattr(stock, value_field),
            "industry_median": "N/A" if median is None else median,
            "grade": getattr(stock, metric.grade_field),
        }
    news = stock.stock_news if isinstance(stock.stock_news, list) else []
    return {
        "ticker": stock.name,
        "company": stock.company_name,
        "sector": stock.sector,
        "industry": stock.industry,
        "price": stock.stock_price,
        "market_cap": stock.mkt_cap_short,
        "beta": stock.beta,
        "short_float": stock.short_float,
        "metrics": metrics,
        "headlines": [
            {"title": item.get("Article"), "source": item.get("Source"), "date": item.get("Date")}
            for item in news
        ],
    }


def analyze_stock(client, model, stock):
    """Ask the model about one stock.

    Returns (the dict saved in StockInfo.gpt_analysis, (input tokens, output tokens)).
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(stock_payload(stock))},
        ],
        response_format={"type": "json_object"},
    )
    reply = json.loads(response.choices[0].message.content or "{}")
    usage = getattr(response, "usage", None)
    tokens = (getattr(usage, "prompt_tokens", 0) or 0, getattr(usage, "completion_tokens", 0) or 0)
    # Keys match what the overview template already shows (including "assesment").
    analysis = {
        "metrics": str(reply.get("metrics", "")),
        "news": str(reply.get("news", "")),
        "sando": str(reply.get("strengths", "")),
        "weakt": str(reply.get("weaknesses", "")),
        "assesment": str(reply.get("thesis", "")),
        "grade": parse_grade(reply.get("grade")),
        "update_time": display_timestamp(),
        "as_of": date.today().isoformat(),
        "model": model,
    }
    return analysis, tokens


def run_ai_analysis(tickers=None, limit=None, max_age_days=7):
    """Analyse each graded stock whose AI analysis is missing or older than max_age_days.

    Stocks that have gone longest without an analysis go first, so when the
    credits run out partway, the next run carries on with the ones that were
    missed instead of starting from "A" again.
    """
    if not settings.OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY is not set; skipping the AI analysis")
        return {"analysed": 0, "failed": 0, "skipped": "no OPENAI_API_KEY"}
    from openai import OpenAI, RateLimitError  # only needed here

    client = OpenAI(api_key=settings.OPENAI_API_KEY, max_retries=3, timeout=120)
    model = settings.OPENAI_MODEL
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()

    stocks = StockInfo.objects.defer("prices", "dates")
    if tickers:
        stocks = stocks.filter(name__in=tickers).order_by("name")
    else:
        # Never analysed (no date) first, then the oldest analyses. Stocks without
        # an overall grade (preferred shares and the like) are skipped.
        stocks = stocks.exclude(overall_grade=NO_GRADE).order_by(
            KT("gpt_analysis__as_of").asc(nulls_first=True), "name"
        )
    analysed = failed = input_tokens = output_tokens = 0
    for stock in stocks.iterator(chunk_size=200):
        if limit and analysed >= limit:
            break
        as_of = (stock.gpt_analysis or {}).get("as_of", "") if isinstance(stock.gpt_analysis, dict) else ""
        if not tickers and as_of >= cutoff:
            continue  # analysed recently
        try:
            analysis, (used_in, used_out) = analyze_stock(client, model, stock)
        except RateLimitError as error:
            out_of_credits = {getattr(error, "type", None), getattr(error, "code", None)} & {
                "insufficient_quota",
                "credit_balance_exhausted",
            }
            if out_of_credits:
                # Every further request would fail the same way.
                log.error("OpenAI account has no credits left; stopping the AI analysis")
                return {
                    "analysed": analysed,
                    "failed": failed + 1,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "skipped": "the OpenAI account has no credits (add some at platform.openai.com)",
                }
            log.warning("AI analysis failed for %s: %s", stock.name, error)
            failed += 1
            continue
        except Exception as error:
            log.warning("AI analysis failed for %s: %s", stock.name, error)
            failed += 1
            continue
        StockInfo.objects.filter(name=stock.name).update(gpt_analysis=analysis)
        analysed += 1
        input_tokens += used_in
        output_tokens += used_out
        if analysed % 50 == 0:
            log.info("AI analysis: %d stocks done", analysed)
    return {"analysed": analysed, "failed": failed, "input_tokens": input_tokens, "output_tokens": output_tokens}
