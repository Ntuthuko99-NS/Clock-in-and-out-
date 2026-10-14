"""ActiveEmployees (refactored from StatsCard): who is clocked in right now."""
from services.time_service import entry_hours
from ui import fmt_hours, fmt_time, initials, tpl

_T = """<section class="panel">
  <header class="panel-head"><h2>Working now</h2><span class="count">{{ rows|length }}</span></header>
  {% for r in rows %}
  <div class="row">
    <span class="avatar sm">{{ r.initials }}</span>
    <div class="grow"><strong>{{ r.name }}</strong><small>{{ r.position or 'Employee' }}</small></div>
    <div class="right"><span class="mono">{{ r.since }}</span><small>{{ r.duration }} so far</small></div>
  </div>
  {% else %}
  <p class="empty">Nobody is clocked in right now.</p>
  {% endfor %}
</section>"""


def DashboardActiveEmployees(entries, employees_by_id):
    rows = []
    for e in entries:
        emp = employees_by_id.get(e["employee_id"], {})
        rows.append({"name": emp.get("full_name", "Unknown"), "position": emp.get("position"),
                     "initials": initials(emp.get("full_name")), "since": fmt_time(e["clock_in"]),
                     "duration": fmt_hours(entry_hours(e))})
    return tpl(_T, rows=rows)
