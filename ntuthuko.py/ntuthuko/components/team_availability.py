from ui import initials, tpl

_T = """<section class="panel">
  <header class="panel-head"><h2>Team availability</h2></header>
  <div class="avail">
  {% for r in rows %}
    <div class="avail-item">
      <span class="avatar sm">{{ r.initials }}</span>
      <div class="grow"><strong>{{ r.name }}</strong><small>{{ r.detail }}</small></div>
      <span class="badge {{ r.tone }}">{{ r.status }}</span>
    </div>
  {% else %}<p class="empty">No active employees yet.</p>{% endfor %}
  </div>
</section>"""


def TeamAvailability(employees, clocked_in_ids, on_leave_ids, shifts_today):
    """shifts_today: {employee_id: shift dict}"""
    rows = []
    for e in employees:
        i = e["id"]
        shift = shifts_today.get(i)
        if i in on_leave_ids:
            status, tone, detail = "On leave", "warn", "Approved leave today"
        elif i in clocked_in_ids:
            status, tone, detail = "Working", "ok", "Clocked in"
        elif shift:
            status, tone, detail = "Scheduled", "info", f"Shift {shift['start_time']}-{shift['end_time']}"
        else:
            status, tone, detail = "Off", "muted", e.get("position") or "No shift today"
        rows.append({"name": e["full_name"], "initials": initials(e["full_name"]),
                     "status": status, "tone": tone, "detail": detail})
    order = {"Working": 0, "Scheduled": 1, "On leave": 2, "Off": 3}
    rows.sort(key=lambda r: order[r["status"]])
    return tpl(_T, rows=rows)
