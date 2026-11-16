"""Database models for Analynix."""

from django.db import models
from django.utils.html import format_html

from .grading import GRADES, METRICS, NO_GRADE, current_ai_grade

# Bootstrap button class per grade letter (D and F share the red style).
GRADE_BUTTON_CLASSES = {
    "A": "btn-success",
    "B": "btn-warning",
    "C": "btn-orange",
    "D": "btn-danger",
    "F": "btn-danger",
}


def grade_button(grade):
    """The coloured button the templates show for a letter grade."""
    if grade not in GRADES:
        return format_html('<button class="btn btn-secondary">{}</button>', NO_GRADE)
    return format_html('<button class="btn {}">{}</button>', GRADE_BUTTON_CLASSES[grade[0]], grade)


class StockInfo(models.Model):
    """One stock: fundamentals from finviz, price history, grades, news and AI analysis.

    Missing numbers are stored as NULL. The text fields next to the numbers hold
    the formatted values the site displays. The avg_* fields hold the *median* of
    the stock's peer group for that metric (see peer_groups); the names date from
    when they held industry averages.
    """

    # Identity
    name = models.TextField(default="default", primary_key=True)  # ticker
    company_name = models.TextField(default="default")
    sector = models.TextField(default="default")
    industry = models.TextField(default="default")

    # Price
    stock_price = models.FloatField(default=0)
    # When stock_price was last refreshed from a live quote (see pipeline/quotes.py).
    price_updated_at = models.DateTimeField(null=True, blank=True)
    prices = models.JSONField(default=dict)  # daily closes, same order as `dates`
    dates = models.JSONField(default=dict)
    last_update = models.TextField(default="default")

    # Fundamentals: display text and numeric value
    beta = models.FloatField(null=True, blank=True)
    mkt_cap = models.FloatField(null=True, blank=True)
    mkt_cap_short = models.TextField(default="default")
    revenue = models.FloatField(null=True, blank=True)  # TTM
    revenue_short = models.TextField(default="default")
    rev_growth = models.TextField(default="default")
    rev_growth_float = models.FloatField(null=True, blank=True)  # TTM vs the previous 12 months
    ebitda_growth = models.TextField(default="N/A")
    ebitda_growth_float = models.FloatField(null=True, blank=True)  # TTM vs the previous 12 months
    ebitda_as_of = models.DateField(null=True, blank=True)  # when ebitda_growth was last fetched
    eps_growth_fwd = models.TextField(default="N/A")
    eps_growth_fwd_float = models.FloatField(null=True, blank=True)  # analysts' estimate, next year
    profit = models.FloatField(null=True, blank=True)
    profit_short = models.TextField(default="default")
    profit_margin = models.TextField(default="default")
    profit_margin_float = models.FloatField(null=True, blank=True)
    pe = models.TextField(default="default")
    pe_float = models.FloatField(null=True, blank=True)
    fwdpe = models.TextField(default="default")
    fwdpe_float = models.FloatField(null=True, blank=True)
    eps = models.TextField(default="default")
    eps_float = models.FloatField(null=True, blank=True)
    ps = models.TextField(default="default")
    ps_float = models.FloatField(null=True, blank=True)
    pb = models.TextField(default="default")
    pb_float = models.FloatField(null=True, blank=True)
    book_value = models.TextField(default=0)
    bvps = models.FloatField(null=True, blank=True)
    avg_volume = models.TextField(default="default")
    avg_volume_float = models.FloatField(default=0)
    shares_float = models.TextField(default="default")
    shares_float_float = models.FloatField(default=0)
    short_float = models.TextField(default="default")
    short_float_float = models.FloatField(default=0)
    dtc = models.FloatField(null=True, blank=True)  # days to cover (short ratio)

    # Industry comparisons (medians; see the class docstring)
    avg_rev = models.TextField(default="default")
    avg_rev_growth = models.TextField(default="default")
    avg_ebitda_growth = models.TextField(default="N/A")
    avg_eps_growth_fwd = models.TextField(default="N/A")
    avg_profit = models.TextField(default="default")
    avg_profit_margin = models.TextField(default="default")
    avg_pe = models.FloatField(null=True, blank=True)
    avg_fwdpe = models.FloatField(null=True, blank=True)
    avg_eps = models.FloatField(null=True, blank=True)
    avg_ps = models.FloatField(null=True, blank=True)
    avg_pb = models.FloatField(null=True, blank=True)
    avg_mkt_cap = models.TextField(default="default")
    ind_size = models.TextField(default="default")
    mkt_share = models.TextField(default="default")
    mkt_share_float = models.FloatField(null=True, blank=True)

    # Grades (see myapp/grading.py). `grade` is the revenue grade.
    grade = models.TextField(default="default")
    rev_growth_grade = models.TextField(default="default")
    ebitda_growth_grade = models.TextField(default="N/A")
    eps_growth_fwd_grade = models.TextField(default="N/A")
    profit_grade = models.TextField(default="default")
    profit_margin_grade = models.TextField(default="default")
    pe_grade = models.TextField(default="default")
    fwdpe_grade = models.TextField(default="default")
    eps_grade = models.TextField(default="default")
    ps_grade = models.TextField(default="default")
    pb_grade = models.TextField(default="default")
    overall_grade = models.TextField(default="default")
    overall_grade_num = models.FloatField(default=0)  # overall score: % of stocks it beats
    # Metric key -> "industry", "sector" or "market": the group each grade (and the
    # median shown next to it) compares against. Small industries use their sector.
    peer_groups = models.JSONField(default=dict, blank=True)

    # News headlines and the AI analyst's write-up
    stock_news = models.JSONField(default=dict)
    gpt_analysis = models.JSONField(default=dict)

    class Meta:
        indexes = [models.Index(fields=["overall_grade", "overall_grade_num"])]

    def __str__(self):
        return f"{self.name} ({self.company_name})"

    @property
    def ai_grade(self):
        """The AI analyst's grade as displayed (old analyses included)."""
        analysis = self.gpt_analysis if isinstance(self.gpt_analysis, dict) else {}
        grade = analysis.get("grade")
        return grade if grade in GRADES else NO_GRADE

    @property
    def ai_grade_counts(self):
        """Whether the AI grade is current enough to count toward the overall grade."""
        return current_ai_grade(self.gpt_analysis) is not None

    def colorized_grades(self):
        """Grade buttons for every grade, keyed like the templates expect."""
        grades = {m.grade_field: grade_button(getattr(self, m.grade_field)) for m in METRICS}
        grades["overall_grade"] = grade_button(self.overall_grade)
        grades["gpt_grade"] = grade_button(self.ai_grade)
        return grades
