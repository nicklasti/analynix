import json
import math
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, TestCase, override_settings

from myapp.management.commands.run_scheduler import SCHEDULE, next_run
from myapp.models import StockInfo
from myapp.pipeline.ai_analysis import parse_grade, run_ai_analysis
from myapp.pipeline.formatting import human_format, parse_number, percent
from myapp.pipeline.fundamentals import all_industries, fetch_screener_pages, stock_fields, with_block_retries
from myapp.pipeline.ebitda import is_quarter, ttm_growth
from myapp.pipeline.news import safe_link

# Two rows as the finviz screener returned them (Nov 2026).
HERSHEY = {
    "Ticker": "HSY",
    "Company": "Hershey Company",
    "Sector": "Consumer Defensive",
    "Industry": "Confectioners",
    "Market Cap": 3.546e10,
    "P/E": 22.76,
    "Fwd P/E": 18.67,
    "P/S": 2.89,
    "P/B": 7.27,
    "EPS": 7.75,
    "Sales YoY TTM": "6.69%",
    "EPS Next Y": "8.78%",
    "Outstanding": 1.4636e8,
    "Float": 1.4498e8,
    "Short Float": "6.60%",
    "Short Ratio": 6.36,
    "Profit M": 0.1463,
    "Beta": 0.06,
    "Avg Volume": 1510000.0,
    "Price": 176.43,
    "Book/sh": "24.26",
    "Income": "1.79B",
    "Sales": "12.26B",
}
SOW_GOOD = dict(
    HERSHEY,
    Ticker="SOWG",
    **{"P/E": math.nan, "Fwd P/E": math.nan, "P/B": math.nan, "EPS": -28.3, "Book/sh": "-0.27", "Income": "-21.86M"},
)


class FormattingTests(SimpleTestCase):
    def test_parse_number(self):
        self.assertEqual(parse_number("1.79B"), 1.79e9)
        self.assertEqual(parse_number("-6.02M"), -6.02e6)
        self.assertAlmostEqual(parse_number("6.60%"), 0.066)
        self.assertEqual(parse_number(22.76), 22.76)
        for missing in ("-", "", None, math.nan, "n/a"):
            self.assertIsNone(parse_number(missing))

    def test_human_format(self):
        self.assertEqual(human_format(1234567), "1.23M")
        self.assertEqual(human_format(-6.02e6), "-6.02M")
        self.assertEqual(human_format(3.546e10), "35.5B")
        self.assertEqual(human_format(0), "0")
        self.assertEqual(human_format(None), "N/A")
        self.assertEqual(percent(0.0296), "2.96%")


class FundamentalsTests(SimpleTestCase):
    def test_screener_row_to_fields(self):
        fields = stock_fields(HERSHEY)
        self.assertEqual(fields["company_name"], "Hershey Company")
        self.assertEqual((fields["pe_float"], fields["pe"]), (22.76, "22.76"))
        self.assertEqual(fields["rev_growth"], "6.69%")  # TTM, not the latest quarter
        self.assertAlmostEqual(fields["eps_growth_fwd_float"], 0.0878)
        self.assertEqual(fields["profit"], 1.79e9)
        self.assertEqual(fields["revenue_short"], "12.3B")
        self.assertEqual(fields["book_value"], "3.55B")  # 24.26 per share x 146M shares
        self.assertAlmostEqual(fields["short_float_float"], 0.066)
        self.assertEqual(fields["dtc"], 6.36)

    def test_missing_values_are_none_not_zero(self):
        fields = stock_fields(SOW_GOOD)
        self.assertIsNone(fields["pe_float"])
        self.assertEqual(fields["pe"], "N/A")
        self.assertIsNone(fields["pb_float"])
        self.assertEqual(fields["bvps"], -0.27)  # negative book value, so no P/B grade
        self.assertEqual(fields["eps_float"], -28.3)


class FetchPagesTests(SimpleTestCase):
    def test_fetches_every_industry_page_by_page(self):
        import pandas as pd

        page_sizes = {("Banks", 1): 20, ("Banks", 2): 3, ("Gold", 1): 7}
        requested = []

        class FakeScreener:
            size = 20

            def set_filter(self, filters_dict):
                self.industry = filters_dict["Industry"]

            def screener_view(self, columns, verbose, select_page):
                requested.append((self.industry, select_page))
                count = page_sizes.get((self.industry, select_page), 0)
                return pd.DataFrame([dict(HERSHEY, Industry="")] * count) if count else None

        with (
            mock.patch("finvizfinance.screener.custom.Custom", FakeScreener),
            mock.patch("myapp.pipeline.fundamentals.all_industries", return_value=["Banks", "Gold"]),
            mock.patch("myapp.pipeline.fundamentals.time.sleep"),
        ):
            pages = list(fetch_screener_pages())
        self.assertEqual([len(rows) for rows in pages], [20, 3, 7])
        self.assertEqual(requested, [("Banks", 1), ("Banks", 2), ("Gold", 1)])  # stops after a short page
        # A blank Industry cell is filled in with the industry that was asked for.
        self.assertEqual({row["Industry"] for rows in pages for row in rows}, {"Banks", "Gold"})

    def test_industry_list_skips_funds_and_shells(self):
        industries = all_industries()
        self.assertGreater(len(industries), 100)
        for skipped in ("Any", "Stocks only (ex-Funds)", "Exchange Traded Fund", "Shell Companies", "Closed-End Fund - Debt"):
            self.assertNotIn(skipped, industries)


class EbitdaTests(SimpleTestCase):
    def test_ttm_growth(self):
        # NVDA, Nov 2026 (millions): latest four quarters vs the four before.
        quarters = [64861, 54533, 45110, 36761, 29109, 22249, 24577, 22347, 19075]
        self.assertAlmostEqual(ttm_growth(quarters), 201265 / 98282 - 1)
        self.assertIsNone(ttm_growth(quarters[:7]))  # not enough history
        self.assertIsNone(ttm_growth([5, 5, 5, 5, -10, -10, -10, -10]))  # growth off a loss means nothing
        self.assertIsNone(ttm_growth([5, None, 5, 5, 5, 5, 5, 5]))

    def test_quarter_lengths(self):
        self.assertTrue(is_quarter("3 Months"))
        self.assertTrue(is_quarter("13 Weeks"))  # retailers
        self.assertFalse(is_quarter("6 Months"))  # half-year reporting
        self.assertTrue(is_quarter("-"))


class NewsLinkTests(SimpleTestCase):
    def test_safe_link(self):
        self.assertEqual(safe_link("https://finance.yahoo.com/news/x.html"), "https://finance.yahoo.com/news/x.html")
        self.assertEqual(safe_link("/news/123/story"), "https://finviz.com/news/123/story")
        self.assertEqual(safe_link("javascript:alert(1)"), "")
        self.assertEqual(safe_link(""), "")


class BlockRetryTests(SimpleTestCase):
    def test_waits_and_retries_while_blocked(self):
        class Blocked(Exception):
            pass

        calls = []

        def fetch():
            calls.append(1)
            if len(calls) < 3:
                raise Blocked
            return "page"

        with mock.patch("myapp.pipeline.fundamentals.time.sleep") as sleep:
            self.assertEqual(with_block_retries(fetch, Blocked, "test"), "page")
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [30, 60])

    def test_gives_up_eventually(self):
        class Blocked(Exception):
            pass

        def fetch():
            raise Blocked

        with mock.patch("myapp.pipeline.fundamentals.time.sleep"), self.assertRaises(Blocked):
            with_block_retries(fetch, Blocked, "test")


class AnalyzeStockTests(SimpleTestCase):
    def test_reply_is_saved_under_the_keys_the_page_uses(self):
        import json
        from types import SimpleNamespace

        from myapp.models import StockInfo
        from myapp.pipeline.ai_analysis import analyze_stock

        reply = {"metrics": "m", "news": "n", "strengths": "s", "weaknesses": "w", "thesis": "t", "grade": "b plus"}
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(reply)))],
            usage=SimpleNamespace(prompt_tokens=900, completion_tokens=300),
        )
        client = mock.Mock()
        client.chat.completions.create.return_value = response
        stock = StockInfo(name="HSY", company_name="Hershey Company", overall_grade="B-", pe="22.76", pe_grade="C+")

        analysis, tokens = analyze_stock(client, "test-model", stock)

        self.assertEqual(tokens, (900, 300))
        self.assertEqual(analysis["grade"], "B+")
        self.assertEqual((analysis["sando"], analysis["weakt"], analysis["assesment"]), ("s", "w", "t"))
        self.assertEqual(analysis["model"], "test-model")
        self.assertTrue(analysis["as_of"])  # marks it as current, so its grade counts
        sent = client.chat.completions.create.call_args.kwargs
        self.assertEqual(sent["response_format"], {"type": "json_object"})
        payload = sent["messages"][1]["content"]
        self.assertIn('"P/E (TTM)": {"value": "22.76"', payload)
        self.assertNotIn("overall", payload.lower())  # the model never sees the overall rating


@override_settings(OPENAI_API_KEY="test-key", OPENAI_MODEL="test-model")
class RunAiAnalysisTests(TestCase):
    def test_stalest_first_and_ungraded_skipped(self):
        today = date.today()

        def stock(name, grade, days_ago=None):
            analysis = {"grade": "B", "as_of": (today - timedelta(days=days_ago)).isoformat()} if days_ago else {}
            StockInfo.objects.create(name=name, overall_grade=grade, gpt_analysis=analysis)

        stock("AAA", "B", days_ago=10)
        stock("BBB", "C")  # never analysed: goes first
        stock("CCC", "A", days_ago=40)
        stock("DDD", "N/A")  # no overall grade: skipped
        stock("EEE", "B", days_ago=2)  # analysed this week: skipped

        reply = {"metrics": "m", "news": "n", "strengths": "s", "weaknesses": "w", "thesis": "t", "grade": "B"}
        client = mock.Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(reply)))],
            usage=SimpleNamespace(prompt_tokens=800, completion_tokens=500),
        )
        with mock.patch("openai.OpenAI", return_value=client):
            summary = run_ai_analysis()

        sent = [json.loads(c.kwargs["messages"][1]["content"])["ticker"] for c in client.chat.completions.create.call_args_list]
        self.assertEqual(sent, ["BBB", "CCC", "AAA"])
        self.assertEqual((summary["analysed"], summary["input_tokens"], summary["output_tokens"]), (3, 2400, 1500))
        self.assertEqual(StockInfo.objects.get(name="BBB").gpt_analysis["as_of"], today.isoformat())


class AiGradeParsingTests(SimpleTestCase):
    def test_parse_grade(self):
        # The old regex turned "A+" into "A" (it tried "A" before "A+").
        self.assertEqual(parse_grade("A+"), "A+")
        self.assertEqual(parse_grade("b plus"), "B+")
        self.assertEqual(parse_grade("Grade: A-."), "A-")
        self.assertEqual(parse_grade("F-"), "F-")
        self.assertEqual(parse_grade("Excellent"), "N/A")
        self.assertEqual(parse_grade("ABC"), "N/A")
        self.assertEqual(parse_grade(None), "N/A")


class SchedulerTests(SimpleTestCase):
    def test_next_runs(self):
        prices, weekly = SCHEDULE
        monday_night = datetime(2026, 11, 9, 23, 0, tzinfo=UTC)
        self.assertEqual(next_run(monday_night, *prices[:3]), datetime(2026, 11, 10, 22, 30, tzinfo=UTC))
        self.assertEqual(next_run(monday_night, *weekly[:3]), datetime(2026, 11, 14, 6, 0, tzinfo=UTC))


class UpdateAllTests(SimpleTestCase):
    def run_update_all(self, marker, **options):
        from io import StringIO

        from django.core.management import call_command

        with (
            mock.patch("myapp.management.commands.update_all.finished_marker", return_value=marker),
            mock.patch("myapp.management.commands.update_all.call_command") as step,
            override_settings(OPENAI_API_KEY="test-key"),
        ):
            call_command("update_all", stdout=StringIO(), **options)
        return [c.args[0] for c in step.call_args_list]

    def test_skips_if_a_full_update_finished_recently(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / "last_full_update.txt"
            marker.write_text(datetime.now(UTC).isoformat())
            self.assertEqual(self.run_update_all(marker, if_older_than=6), [])

    def test_runs_every_step_then_records_that_it_finished(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / "last_full_update.txt"
            steps = self.run_update_all(marker, if_older_than=6)  # no marker yet: e.g. cut short by a restart
            self.assertEqual(
                steps,
                ["update_fundamentals", "update_prices", "grade_stocks", "update_ebitda", "grade_stocks", "update_news", "ai_analysis"],
            )
            self.assertTrue(marker.exists())
