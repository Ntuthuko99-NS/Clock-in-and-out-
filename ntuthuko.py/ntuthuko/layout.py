"""Layout - shared page shell (sidebar nav, flash messages, alert badge)."""
from flask import g, get_flashed_messages, render_template_string, url_for
from markupsafe import Markup
from services import alert_service

NAV = [  # (endpoint, label, manager_only)
    ("dashboard.index", "Dashboard", False),
    ("timesheet.index", "Timesheet", False),
    ("shifts.index", "Shifts", False),
    ("leave.index", "Leave", False),
    ("alerts.index", "Alerts", False),
    ("employees.index", "Employees", True),
    ("reports.index", "Reports", True),
    ("whatsapp.index", "WhatsApp", True),
    ("settings.index", "Settings", True),
    ("my_profile.index", "My profile", False),
]

_BASE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="csrf-token" content="{{ csrf_token() }}">
<title>{{ title }} | {{ company }}</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head><body>
{% if g.user %}
<div class="shell">
  <aside class="side">
    <a class="brand" href="{{ url_for('dashboard.index') }}">{{ company }}</a>
    <nav>
      {% for ep, label, mgr in nav %}{% if not mgr or g.is_manager %}
        <a href="{{ url_for(ep) }}" class="{{ 'on' if active == ep.split('.')[0] }}">{{ label }}
          {% if ep == 'alerts.index' and unread %}<span class="pill">{{ unread }}</span>{% endif %}</a>
      {% endif %}{% endfor %}
    </nav>
    <div class="who">
      <strong>{{ g.user.full_name }}</strong><small>{{ g.user.role }}</small>
      <form method="post" action="{{ url_for('auth.logout') }}"><input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <button class="btn ghost sm">Sign out</button></form>
    </div>
  </aside>
  <main class="main">
    <header class="page-head"><h1>{{ title }}</h1><div>{{ actions }}</div></header>
    {% for cat, msg in flashes %}<div class="flash {{ cat }}" role="status">{{ msg }}</div>{% endfor %}
    {{ body }}
  </main>
</div>
{% else %}{{ body }}{% endif %}
</body></html>"""


def render_page(title, body, active="", actions=""):
    return render_template_string(
        _BASE, title=title, body=body, active=active, actions=actions, nav=NAV,
        company=g.settings.get("company_name", "Ntuthuko Workforce"),
        unread=alert_service.unread_count() if g.get("user") else 0,
        flashes=get_flashed_messages(with_categories=True))
