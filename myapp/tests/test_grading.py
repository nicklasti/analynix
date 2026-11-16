import random
from collections import Counter
from types import SimpleNamespace

from django.test import SimpleTestCase

from myapp.grading import (
    GRADE_CUTOFFS,
    GRADE_MIDPOINTS,
    GRADES,
    LOW_GRADES,
    METRICS,
    NO_GRADE,
    TOP_GRADES,
    StockData,
    current_ai_grade,
    grade_stocks,
    letter_grade,
    metric_values,
    percentile_ranks,
)


def make_stock(name, industry="Banks", sector="Financial", ai_grade=None, **values):
    all_values = {metric.key: None for metric in METRICS}
    all_values.update(values)
    return StockData(name, industry, sector, all_values, ai_grade)


def full_stock(name, rank, industry="Banks", sector="Financial", **overrides):
    """A stock whose every metric is `rank` (higher rank = better on every metric)."""
    values = {
        "revenue": rank * 1e9,
        "rev_growth": rank / 100,
        "ebitda_growth": rank / 50,
        "eps_growth_fwd": rank / 40,
        "profit": rank * 1e8,
        "profit_margin": rank / 100,
        "pe": 100 - rank,
        "fwdpe": 100 - rank,
        "eps": float(rank),
        "ps": 100 - rank,
        "pb": 100 - rank,
    }
    values.update(overrides)
    return make_stock(name, industry, sector, **values)


class LetterGradeTests(SimpleTestCase):
    def test_cutoffs(self):
        self.assertEqual(letter_grade(100), "A+")
        self.assertEqual(letter_grade(97), "A+")
        self.assertEqual(letter_grade(96.99), "A")
        self.assertEqual(letter_grade(50), "C")
        self.assertEqual(letter_grade(43), "C")
        self.assertEqual(letter_grade(42.99), "C-")
        self.assertEqual(letter_grade(3), "F")
        self.assertEqual(letter_grade(2.99), "F-")
        self.assertEqual(letter_grade(0), "F-")
        self.assertEqual(letter_grade(None), NO_GRADE)

    def test_bands_form_a_symmetric_bell_curve_centred_on_c(self):
        bounds = [100.0] + [lower for lower, _ in GRADE_CUTOFFS]
        widths = [upper - lower for upper, lower in zip(bounds, bounds[1:])]
        self.assertEqual(widths, widths[::-1])
        self.assertEqual(GRADE_MIDPOINTS["C"], 50)
        self.assertEqual([grade for _, grade in GRADE_CUTOFFS], list(GRADES))

    def test_top_and_low_lists_are_mirror_images(self):
        self.assertEqual(TOP_GRADES, ("A+", "A", "A-", "B+", "B"))
        self.assertEqual(LOW_GRADES, ("D", "D-", "F+", "F", "F-"))


class PercentileTests(SimpleTestCase):
    def test_single_stock_is_in_the_middle(self):
        self.assertEqual(percentile_ranks({"a": 5}), {"a": 50.0})

    def test_ties_count_half(self):
        self.assertEqual(percentile_ranks({"a": 1, "b": 1}), {"a": 50.0, "b": 50.0})

    def test_lower_is_better(self):
        ranks = percentile_ranks({"cheap": 5, "pricey": 50}, higher_is_better=False)
        self.assertEqual(ranks, {"cheap": 75.0, "pricey": 25.0})


class GradeStocksTests(SimpleTestCase):
    def test_best_and_worst_in_an_industry(self):
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 21)]
        results = grade_stocks(stocks)
        best, worst = results["S20"], results["S1"]
        self.assertEqual(set(best.grades.values()), {"A+"})  # highest revenue AND lowest P/E
        self.assertEqual(set(worst.grades.values()), {"F-"})
        self.assertEqual(best.overall_grade, "A+")
        self.assertEqual(worst.overall_grade, "F-")

    def test_missing_metric_is_left_out_not_counted_as_f(self):
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 21)]
        stocks[-1] = full_stock("S20", 20, fwdpe=None)  # the best stock has no forward P/E
        result = grade_stocks(stocks)["S20"]
        self.assertEqual(result.grades["fwdpe_grade"], NO_GRADE)
        self.assertNotIn("fwdpe", result.percentiles)
        self.assertAlmostEqual(result.composite, 97.5)  # same as its other metrics, no penalty
        self.assertEqual(result.overall_grade, "A+")

    def test_missing_ps_does_not_reuse_another_stocks_grade(self):
        # The old grader set pb_grade instead of ps_grade here, so the stock kept
        # the previous stock's P/S grade.
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 21)]
        stocks.append(full_stock("NOPS", 10, ps=None))
        self.assertEqual(grade_stocks(stocks)["NOPS"].grades["ps_grade"], NO_GRADE)

    def test_small_industry_is_compared_with_its_sector(self):
        stocks = [full_stock(f"BIG{rank}", rank, industry="Big") for rank in range(1, 13)]
        stocks += [full_stock(f"TINY{rank}", rank, industry="Tiny") for rank in range(1, 4)]
        stocks += [full_stock("ALONE", 5, industry="Alone", sector="Other")]
        results = grade_stocks(stocks)
        self.assertEqual(set(results["BIG1"].peer_groups.values()), {"industry"})
        self.assertEqual(set(results["TINY1"].peer_groups.values()), {"sector"})
        self.assertEqual(set(results["ALONE"].peer_groups.values()), {"market"})
        # The median shown next to a grade comes from the same group as the grade.
        self.assertEqual(results["BIG1"].peer_medians["eps"], 6.5)  # median of 1..12
        self.assertEqual(results["TINY1"].peer_medians["eps"], 5.0)  # median of 1..12 and 1..3
        # A stock missing a number still gets its peer group's median.
        stocks.append(full_stock("NOEPS", 4, industry="Big", eps=None))
        result = grade_stocks(stocks)["NOEPS"]
        self.assertEqual(result.grades["eps_grade"], NO_GRADE)
        self.assertEqual(result.peer_medians["eps"], 6.5)

    def test_loss_makers_get_no_pe_grade(self):
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 12)]
        stocks.append(full_stock("LOSS", 1, pe=None))
        result = grade_stocks(stocks)["LOSS"]
        self.assertEqual(result.grades["pe_grade"], NO_GRADE)
        self.assertEqual(result.peer_medians["pe"], 94.0)  # median P/E of the profitable peers (89..99)

    def test_expensive_stock_is_not_rescued_by_loss_makers(self):
        # The Tesla case: P/E 430 in an industry where most companies lose money
        # used to grade B because every loss-maker ranked below it.
        stocks = [full_stock(f"P{n}", 10, pe=15.0 + n) for n in range(10)]
        stocks += [full_stock(f"L{n}", 10, pe=None) for n in range(15)]
        stocks.append(full_stock("PRICEY", 10, pe=430.0))
        self.assertEqual(grade_stocks(stocks)["PRICEY"].grades["pe_grade"], "F")

    def test_needs_enough_metrics_for_an_overall_grade(self):
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 21)]
        stocks.append(make_stock("SPARSE", revenue=1e9, profit=1e8, eps=1.0))
        result = grade_stocks(stocks)["SPARSE"]
        self.assertNotEqual(result.grades["grade"], NO_GRADE)
        self.assertEqual(result.overall_grade, NO_GRADE)
        self.assertIsNone(result.overall_score)

    def test_large_market_follows_the_bell_curve(self):
        rng = random.Random(7)
        stocks = []
        for number in range(3000):
            values = {
                "revenue": rng.lognormvariate(20, 2),
                "rev_growth": rng.gauss(0.05, 0.3),
                "profit": rng.gauss(1e7, 1e9),
                "profit_margin": rng.gauss(0.05, 0.4),
                "pe": rng.choice([None, rng.lognormvariate(3, 1)]),
                "fwdpe": rng.choice([None, rng.lognormvariate(3, 1)]),
                "eps": rng.gauss(1, 5),
                "ps": rng.lognormvariate(1, 1.5),
                "pb": rng.lognormvariate(1, 1),
                "ebitda_growth": rng.choice([None, rng.gauss(0.08, 0.5)]),
                "eps_growth_fwd": rng.choice([None, rng.gauss(0.1, 0.3)]),
            }
            stocks.append(make_stock(f"S{number}", industry=f"I{number % 40}", sector=f"X{number % 8}", **values))
        results = grade_stocks(stocks).values()
        counts = Counter(result.overall_grade for result in results)
        self.assertAlmostEqual(counts["A+"] / 3000, 0.03, delta=0.005)
        self.assertAlmostEqual(counts["C"] / 3000, 0.14, delta=0.005)
        self.assertAlmostEqual(counts["F-"] / 3000, 0.03, delta=0.005)
        top = sum(counts[grade] for grade in TOP_GRADES)
        low = sum(counts[grade] for grade in LOW_GRADES)
        self.assertAlmostEqual(top / 3000, 0.24, delta=0.005)
        self.assertAlmostEqual(low / 3000, 0.24, delta=0.005)

    def test_current_ai_grade_counts_once(self):
        stocks = [full_stock(f"S{rank}", rank) for rank in range(1, 21)]
        stocks[0] = full_stock("S1", 1)
        stocks[0].ai_grade = "A+"
        result = grade_stocks(stocks)["S1"]
        self.assertTrue(result.ai_grade_used)
        # Every metric at percentile 2.5, plus one A+ (98.5) at the same weight as a metric.
        count = len(METRICS)
        self.assertAlmostEqual(result.composite, (count * 2.5 + 98.5) / (count + 1))


class InputTests(SimpleTestCase):
    def row(self, **fields):
        defaults = dict(
            revenue=1e9,
            rev_growth_float=0.1,
            ebitda_growth_float=0.2,
            eps_growth_fwd_float=0.15,
            profit=1e8,
            profit_margin_float=0.1,
            pe_float=20.0,
            fwdpe_float=18.0,
            eps_float=2.0,
            ps_float=3.0,
            pb_float=4.0,
            bvps=10.0,
        )
        defaults.update(fields)
        return SimpleNamespace(**defaults)

    def test_no_pe_when_losing_money_and_no_pb_with_negative_book_value(self):
        self.assertIsNone(metric_values(self.row(pe_float=None, eps_float=-1.5))["pe"])
        self.assertIsNone(metric_values(self.row(pb_float=None, bvps=-2.0))["pb"])
        self.assertEqual(metric_values(self.row(eps_float=-1.5))["eps"], -1.5)  # EPS itself still counts

    def test_non_positive_ratios_are_missing(self):
        values = metric_values(self.row(fwdpe_float=0.0, ps_float=-1.0))
        self.assertIsNone(values["fwdpe"])
        self.assertIsNone(values["ps"])

    def test_only_current_ai_grades_count(self):
        self.assertIsNone(current_ai_grade({}))
        self.assertIsNone(current_ai_grade({"grade": "B+"}))  # old pipeline: no as_of
        self.assertIsNone(current_ai_grade({"grade": "Excellent", "as_of": "2026-11-01"}))
        self.assertEqual(current_ai_grade({"grade": "B+", "as_of": "2026-11-01"}), "B+")
