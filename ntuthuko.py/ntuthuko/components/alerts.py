"""Alerts - notification list with read/delete management."""
from ui import fmt_datetime, tpl

_T = """<div class="toolbar">
  <nav class="tabs">
    <a href="?filter=all" class="{{ 'on' if filter=='all' }}">All</a>
    <a href="?filter=unread" class="{{ 'on' if filter=='unread' }}">Unread</a>
    {% for s in ['critical','warning','info'] %}<a href="?filter={{ s }}" class="{{ 'on' if filter==s }}">{{ s|capitalize }}</a>{% endfor %}
  </nav>
  <form method="post" action="{{ url_for('alerts.read_all') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="btn ghost">Mark all as read</button>
  </form>
</div>
<div class="panel flush">
{% for a in alerts %}
  <article class="alert-item sev-{{ a.severity }} {{ '' if a.is_read else 'unread' }}">
    <span class="sev-bar"></span>
    <div class="grow">
      <strong>{{ a.title }}</strong>
      <p>{{ a.message }}</p>
      <small>{{ a.when }}</small>
    </div>
    <form method="post" class="inline">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      {% if not a.is_read %}<button class="btn sm" formaction="{{ url_for('alerts.read', alert_id=a.id) }}">Mark read</button>{% endif %}
      <button class="btn sm danger" formaction="{{ url_for('alerts.remove', alert_id=a.id) }}">Delete</button>
    </form>
  </article>
{% else %}<p class="empty">No alerts to show for this filter.</p>{% endfor %}
</div>"""


def Alerts(alerts, filter="all"):
    items = [{**a, "when": fmt_datetime(a["created_at"].replace(" ", "T"))} for a in alerts]
    return tpl(_T, alerts=items, filter=filter)
