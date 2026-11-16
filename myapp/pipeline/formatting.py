"""Parsing finviz values and formatting numbers the way the site displays them."""

import math
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from django.conf import settings

SUFFIXES = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
MISSING = "N/A"


def parse_number(value):
    """A finviz cell as a float: '1.79B' -> 1.79e9, '6.60%' -> 0.066, '-' / NaN -> None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return None if math.isnan(value) else float(value)
    text = str(value).strip().replace(",", "")
    if text in ("", "-"):
        return None
    scale = 1.0
    if text.endswith("%"):
        text, scale = text[:-1], 0.01
    elif text[-1].upper() in SUFFIXES:
        text, scale = text[:-1], SUFFIXES[text[-1].upper()]
    try:
        return float(text) * scale
    except ValueError:
        return None


def clean_text(value):
    """A text cell with runs of whitespace collapsed; '' for missing."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return " ".join(str(value).split())


def human_format(number):
    """1234567 -> '1.23M' (three significant digits); None -> 'N/A'."""
    if number is None:
        return MISSING
    number = float(f"{number:.3g}")
    magnitude = 0
    while abs(number) >= 1000 and magnitude < 4:
        magnitude += 1
        number /= 1000.0
    return f"{number:f}".rstrip("0").rstrip(".") + ["", "K", "M", "B", "T"][magnitude]


def percent(fraction):
    """0.0296 -> '2.96%'; None -> 'N/A'."""
    return MISSING if fraction is None else f"{fraction:.2%}"


def ratio(number):
    """22.756 -> '22.76'; None -> 'N/A'."""
    return MISSING if number is None else f"{number:.2f}"


def positive(number):
    """Valuation ratios only exist when positive."""
    return number if number is not None and number > 0 else None


def display_timestamp(moment=None):
    """'Wed, Nov 11, 2026 05:30 PM EST' in the site's display time zone."""
    moment = moment or datetime.now(UTC)
    local = moment.astimezone(ZoneInfo(settings.DISPLAY_TIME_ZONE))
    return local.strftime("%a, %b %d, %Y %I:%M %p %Z")
