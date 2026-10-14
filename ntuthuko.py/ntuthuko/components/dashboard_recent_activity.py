from ui import fmt_datetime, tpl

_T = """<section class="panel">
  <header class="panel-head"><h2>Recent activity</h2></header>
  {% for a in items %}
  <div class="row">
    <span class="dot {{ a.kind }}"></span>
    <div class="grow">{{ a.text }}</div>
    <small class="mono">{{ a.when }}</small>
  </div>
  {% else %}<p class="empty">Activity will appear here as people clock in and request leave.</p>{% endfor %}
</section>"""


def DashboardRecentActivity(entries, leaves, employees_by_id, limit=8):
    items = []
    name = lambda i: employees_by_id.get(i, {}).get("full_name", "Someone")
    for e in entries:
        items.append({"kind": "clock", "ts": e["clock_in"], "text": f"{name(e['employee_id'])} clocked in"})
        if e.get("clock_out"):
            items.append({"kind": "clock", "ts": e["clock_out"], "text": f"{name(e['employee_id'])} clocked out"})
    for l in leaves:
        items.append({"kind": "leave", "ts": (l.get("created_at") or "").replace(" ", "T"),
                      "text": f"{name(l['employee_id'])} requested {l['days']:g} day(s) {l['leave_type']} leave ({l['status']})"})
    items.sort(key=lambda i: i["ts"] or "", reverse=True)
    for i in items:
        i["when"] = fmt_datetime(i["ts"])
    return tpl(_T, items=items[:limit])
