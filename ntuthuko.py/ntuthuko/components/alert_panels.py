"""AlertPanels - one panel per severity with the latest unread alerts."""
from ui import fmt_datetime, tpl

_T = """<div class="alert-panels">
{% for p in panels %}
  <section class="panel sev-{{ p.severity }}">
    <header class="panel-head"><h2>{{ p.label }}</h2><span class="count">{{ p.total }}</span></header>
    {% for a in p.lines %}
      <a class="alert-line" href="{{ url_for('alerts.index') }}">
        <strong>{{ a.title }}</strong><small>{{ a.when }}</small>
      </a>
    {% else %}<p class="empty">All clear.</p>{% endfor %}
  </section>
{% endfor %}
</div>"""

LABELS = {"critical": "Needs action", "warning": "Warnings", "info": "Updates"}


def AlertPanels(alerts):
    panels = []
    for sev in ("critical", "warning", "info"):
        subset = [a for a in alerts if a["severity"] == sev and not a["is_read"]]
        panels.append({"severity": sev, "label": LABELS[sev], "total": len(subset),
                       "lines": [{**a, "when": fmt_datetime(a["created_at"].replace(" ", "T"))}
                                 for a in subset[:3]]})
    return tpl(_T, panels=panels)
