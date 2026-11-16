from django import template
from django.utils.html import format_html

register = template.Library()

PEER_NOTES = {
    "sector": (
        "sector",
        "Fewer than 10 stocks in this industry report this number, so the grade "
        "and median compare against the whole sector.",
    ),
    "market": (
        "all stocks",
        "Too few stocks in this industry and sector report this number, so the grade "
        "and median compare against every stock.",
    ),
}


@register.filter
def peer_note(peer_groups, metric):
    """' (sector)' after a median when the grade wasn't against the stock's own industry."""
    level = peer_groups.get(metric) if isinstance(peer_groups, dict) else None
    if level not in PEER_NOTES:
        return ""
    label, explanation = PEER_NOTES[level]
    return format_html(' <span title="{}" style="font-size: 80%; cursor: help;">({})</span>', explanation, label)


@register.filter
def dollars(value):
    """'1.79B' -> '$1.79B'; missing values -> 'N/A' (instead of '$N/A')."""
    if value in (None, "", "N/A", "default"):
        return "N/A"
    text = str(value)
    return "-$" + text[1:] if text.startswith("-") else "$" + text


@register.filter
def or_na(value):
    """None / empty / the old 'default' placeholder -> 'N/A'."""
    return "N/A" if value in (None, "", "default") else value
