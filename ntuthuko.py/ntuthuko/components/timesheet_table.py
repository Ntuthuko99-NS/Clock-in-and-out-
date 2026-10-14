from services.time_service import entry_hours
from ui import fmt_hours, fmt_time, tpl

_T = """<div class="panel flush table-wrap"><table class="table">
  <thead><tr>{% if show_employee %}<th>Employee</th>{% endif %}<th>Date</th><th>In</th><th>Out</th><th>Break</th><th class="num">Hours</th><th>Status</th></tr></thead>
  <tbody>
  {% for r in rows %}
    <tr>{% if show_employee %}<td>{{ r.name }}</td>{% endif %}
      <td>{{ r.date }}</td><td class="mono">{{ r.cin }}</td><td class="mono">{{ r.cout }}</td>
      <td>{{ r.brk }} min</td><td class="num mono">{{ r.hours }}</td>
      <td><span class="badge {{ 'ok' if r.status=='active' else 'muted' }}">{{ 'Working' if r.status=='active' else 'Done' }}</span></td></tr>
  {% else %}<tr><td colspan="7" class="empty">No time entries in this range.</td></tr>{% endfor %}
  </tbody>
  {% if rows %}<tfoot><tr><td colspan="{{ 5 if show_employee else 4 }}">Total</td><td class="num mono">{{ total }}</td><td></td></tr></tfoot>{% endif %}
</table></div>"""


def TimesheetTable(entries, employees_by_id, show_employee=True):
    rows, total = [], 0.0
    for e in entries:
        h = entry_hours(e)
        total += h
        rows.append({"name": employees_by_id.get(e["employee_id"], {}).get("full_name", "Unknown"),
                     "date": (e["clock_in"] or "")[:10], "cin": fmt_time(e["clock_in"]),
                     "cout": fmt_time(e.get("clock_out")), "brk": e.get("break_minutes") or 0,
                     "hours": fmt_hours(h), "status": e["status"]})
    return tpl(_T, rows=rows, show_employee=show_employee, total=fmt_hours(total))
