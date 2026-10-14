from ui import tpl

_T = """<a class="stat {{ tone }}" {% if href %}href="{{ href }}"{% endif %}>
  <span class="stat-value">{{ value }}</span>
  <span class="stat-label">{{ label }}</span>
  {% if hint %}<span class="stat-hint">{{ hint }}</span>{% endif %}
</a>"""


def DashboardStatCard(label, value, hint="", tone="", href=None):
    return tpl(_T, label=label, value=value, hint=hint, tone=tone, href=href)
