"""Views for the Analynix website."""

import json
import math
from urllib.parse import quote

import plotly.graph_objects as go
from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .grading import LOW_GRADES, TOP_GRADES
from .models import StockInfo, grade_button
from .pipeline.quotes import current_price

STOCKS_PER_PAGE = 100

# Columns the Top/Low Rated tables need (skips the big price-history fields).
LIST_FIELDS = (
    "name",
    "company_name",
    "industry",
    "mkt_cap_short",
    "overall_grade",
    "overall_grade_num",
    "pe_grade",
    "pb_grade",
    "ps_grade",
)


def index(request):
    """Home page. The search box starts out filled with the top-rated stock."""
    top_stock = (
        StockInfo.objects.filter(overall_grade__in=TOP_GRADES)
        .order_by("-overall_grade_num")
        .values_list("name", flat=True)
        .first()
    )
    return render(request, "index.html", {"stock": top_stock or ""})


def about(request):
    return render(request, "about.html")


def privacy(request):
    return render(request, "privacy.html")


def manifest(request):
    """Web app manifest: lets phones add the site to the home screen as an app."""
    return render(request, "pwa/manifest.webmanifest", content_type="application/manifest+json")


def service_worker(request):
    """Served from the site root so it covers every page."""
    response = render(request, "pwa/sw.js", content_type="text/javascript")
    response["Cache-Control"] = "no-cache"  # so changes to the worker reach phones quickly
    return response


def error_404_view(request, exception=None):
    return render(request, "404.html", status=404)


def ads_txt(request):
    """Google AdSense looks for /ads.txt at the root of the site."""
    path = settings.BASE_DIR / "static" / "ads.txt"
    if not path.exists():
        raise Http404
    return HttpResponse(path.read_text(), content_type="text/plain")


def overview(request):
    """The page for one stock: price chart, metrics, grades, AI analysis and news."""
    ticker = request.GET.get("text", "").strip().upper()
    if not ticker:
        return redirect("index")
    stock = get_object_or_404(StockInfo, name=ticker)
    # Only show AI analyses from the current pipeline (they have an "as_of" date).
    # The 2023 ones discuss the old, miscalculated grades, so they'd contradict the page.
    analysis = stock.gpt_analysis if stock.ai_grade_counts else {}
    # Headlines from the old pipeline have no date (and are from 2023), so skip them too.
    news = [item for item in stock.stock_news or [] if isinstance(item, dict) and item.get("Date")]
    edgar = "https://www.sec.gov/edgar/search/#/q={}&filter_forms={}"
    context = {
        "stock": stock,
        "grades": stock.colorized_grades(),
        "chart": price_chart(stock),
        "analysis": analysis,
        "ai_model": analysis.get("model", ""),
        "news": news,
        "edgar_link_8k": edgar.format(quote(ticker), "8-K"),
        "edgar_link_10q": edgar.format(quote(ticker), "10-Q"),
        "edgar_link_10k": edgar.format(quote(ticker), "10-K"),
    }
    return render(request, "overview.html", context)


def beststocks(request):
    """Stocks graded B or better, best first."""
    return _stock_list(request, "beststocks.html", TOP_GRADES, "-overall_grade_num", "best_stock_list")


def worststocks(request):
    """Stocks graded D or worse, worst first."""
    return _stock_list(request, "worststocks.html", LOW_GRADES, "overall_grade_num", "worst_stock_list")


def live_quote(request):
    """The current price of one stock as JSON; the stock page calls this to stay live."""
    ticker = request.GET.get("text", "").strip().upper()
    stock = get_object_or_404(StockInfo.objects.only("name", "stock_price", "price_updated_at"), name=ticker)
    price, as_of = current_price(stock)
    response = JsonResponse({"ticker": stock.name, "price": price, "as_of": as_of.isoformat() if as_of else None})
    response["Cache-Control"] = "no-store"
    return response


SQUEEZE_LIST_SIZE = 100


def shortsqueeze(request):
    """The stocks with the most days to cover (shares sold short / average daily volume)."""
    stocks = list(
        StockInfo.objects.filter(dtc__isnull=False)
        .order_by("-dtc", "name")
        .only("name", "company_name", "industry", "dtc", "short_float", "mkt_cap_short", "overall_grade")[
            :SQUEEZE_LIST_SIZE
        ]
    )
    for stock in stocks:
        stock.grade_buttons = {"overall_grade": grade_button(stock.overall_grade)}
    return render(request, "shortsqueeze.html", {"stocks": stocks})


def _stock_list(request, template, grades, order, list_name):
    stocks = StockInfo.objects.filter(overall_grade__in=grades).order_by(order, "name").only(*LIST_FIELDS)
    page_obj = Paginator(stocks, STOCKS_PER_PAGE).get_page(request.GET.get("page"))
    rows = list(page_obj.object_list)
    for stock in rows:
        stock.grade_buttons = {
            field: grade_button(getattr(stock, field))
            for field in ("overall_grade", "pe_grade", "pb_grade", "ps_grade")
        }
    return render(request, template, {"page_obj": page_obj, list_name: rows})


def _price_series(stock):
    """(dates, closing prices) with gaps removed. Old rows stored prices as a JSON string."""
    prices, dates = stock.prices, stock.dates
    if isinstance(prices, str):
        prices = json.loads(prices)
    if not isinstance(prices, list) or not isinstance(dates, list):
        return [], []
    pairs = [
        (day, round(price, 2))
        for day, price in zip(dates, prices)
        if isinstance(price, (int, float)) and not math.isnan(price)
    ]
    return [day for day, _ in pairs], [price for _, price in pairs]


def price_chart(stock):
    """The interactive price chart as an HTML snippet ("" when there's no price history)."""
    dates, prices = _price_series(stock)
    if not prices:
        return ""
    figure = go.Figure(data=[go.Scatter(x=dates, y=prices, mode="lines", line_color="#7c9cec")])
    figure.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all"),
            ],
            font_color="black",
        ),
        showline=True,
        linewidth=2,
        linecolor="#293b45",
        gridcolor="#293b45",
    )
    figure.update_yaxes(autorange=True, showline=True, linewidth=2, linecolor="#293b45", gridcolor="#293b45")
    figure.update_layout(
        plot_bgcolor="#1f2d35",
        paper_bgcolor="#1f2d35",
        font_color="white",
        title_font_color="white",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    # Load plotly.js from its CDN instead of inlining ~4 MB of JavaScript in every page,
    # and let the chart resize with the screen (phones, rotating).
    return figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False, "responsive": True},
    )
