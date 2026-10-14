"""Tiny helpers shared by components and pages."""
from datetime import datetime
from flask import render_template_string
from markupsafe import Markup


def tpl(src, **ctx):
    """Render a Jinja string (autoescaped) and mark it safe for embedding."""
    return Markup(render_template_string(src, **ctx))


def now():
    return datetime.now().replace(microsecond=0)


def parse_dt(value):
    try:
        return datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError):
        return None


def fmt_time(value):
    d = parse_dt(value)
    return d.strftime("%H:%M") if d else "-"


def fmt_datetime(value):
    d = parse_dt(value)
    return d.strftime("%d %b %Y, %H:%M") if d else "-"


def fmt_hours(h):
    h = h or 0
    return f"{int(h)}h {int(round((h - int(h)) * 60)):02d}m"


def initials(name):
    parts = (name or "?").split()
    return "".join(p[0] for p in parts[:2]).upper()
