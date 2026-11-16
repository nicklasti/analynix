"""Store missing numbers as NULL, and price history as a real JSON list.

The old pipeline saved a missing finviz value ("-") as 0, and the old grader then
averaged those zeros in as if they were real numbers. The text field next to each
number still says "N/A" or "0" for those, which tells us which zeros were missing.
"""

import json
import math

from django.db import migrations

MISSING_TEXT = {"N/A", "-", "", "0", "default"}


def _is_missing(text, number):
    return str(text).strip() in MISSING_TEXT or number is None


def forwards(apps, schema_editor):
    StockInfo = apps.get_model("myapp", "StockInfo")
    for stock in StockInfo.objects.all().iterator(chunk_size=100):
        changes = {}

        # Ratios only exist when positive; finviz shows "-" otherwise.
        for text_field, number_field in (
            ("pe", "pe_float"),
            ("fwdpe", "fwdpe_float"),
            ("ps", "ps_float"),
            ("pb", "pb_float"),
        ):
            number = getattr(stock, number_field)
            if _is_missing(getattr(stock, text_field), number) or number <= 0:
                changes[number_field] = None
                changes[text_field] = "N/A"

        # A stored 0 meant "missing" for these.
        if not stock.eps_float:
            changes.update(eps_float=None, eps="N/A")
        if _is_missing(stock.profit_margin, stock.profit_margin_float):
            changes.update(profit_margin_float=None, profit_margin="N/A")
        if _is_missing(stock.rev_growth, stock.rev_growth_float):
            changes.update(rev_growth_float=None, rev_growth="N/A")
        if not stock.revenue:
            changes.update(revenue=None, revenue_short="N/A")
        if not stock.profit:
            changes.update(profit=None, profit_short="N/A")
        if not stock.mkt_cap:
            changes.update(mkt_cap=None, mkt_cap_short="N/A")
        for number_field in ("bvps", "beta", "dtc"):
            if not getattr(stock, number_field):
                changes[number_field] = None

        # Prices were saved as one JSON *string*; store a list and drop gaps (NaN).
        prices, dates = stock.prices, stock.dates
        if isinstance(prices, str):
            prices = json.loads(prices)
            if isinstance(prices, list) and isinstance(dates, list):
                pairs = [
                    (day, round(price, 2))
                    for day, price in zip(dates, prices)
                    if isinstance(price, (int, float)) and not math.isnan(price)
                ]
                changes["dates"] = [day for day, _ in pairs]
                changes["prices"] = [price for _, price in pairs]

        if changes:
            StockInfo.objects.filter(pk=stock.pk).update(**changes)


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0044_nullable_metrics_and_drop_list_tables"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        # Cache table from the old CACHES setting; nothing used it.
        migrations.RunSQL("DROP TABLE IF EXISTS my_table_name", migrations.RunSQL.noop),
    ]
