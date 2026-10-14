"""Reports - attendance and analytics."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from flask import Blueprint, request
from auth import manager_required
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from services.time_service import entries_between, entry_hours
from ui import fmt_hours, parse_dt, tpl

bp = Blueprint("reports", __name__, url_prefix="/reports")
E = client.entities

_T = """<form class="toolbar" method="get"><label>From <input type="date" name="start" value="{{ start }}"></label>
<label>To <input type="date" name="end" value="{{ end }}"></label><button class="btn">Run report</button></form>
<div class="stats">
 <div class="stat"><span class="stat-value">{{ total }}</span><span class="stat-label">Hours worked</span></div>
 <div class="stat"><span class="stat-value">{{ days_worked }}</span><span class="stat-label">Attendance days</span></div>
 <div class="stat warn"><span class="stat-value">{{ late_total }}</span><span class="stat-label">Late arrivals</span></div>
 <div class="stat"><span class="stat-value">{{ '%g' % leave_total }}</span><span class="stat-label">Leave days approved</span></div>
</div>
<div class="cols"><section class="panel"><header class="panel-head"><h2>Hours by employee</h2></header>
{% for r in rows %}<div class="hbar"><span>{{ r.name }}</span><div class="bar"><span style="width: {{ r.pct }}%"></span></div><b class="mono">{{ r.hours }}</b></div>
{% else %}<p class="empty">No time entries in this range.</p>{% endfor %}</section>
<section class="panel"><header class="panel-head"><h2>Per employee</h2></header>
<div class="table-wrap"><table class="table"><thead><tr><th>Employee</th><th class="num">Days</th><th class="num">Late</th><th class="num">Leave</th><th class="num">Pay (ZAR)</th></tr></thead><tbody>
{% for r in rows %}<tr><td>{{ r.name }}</td><td class="num">{{ r.days }}</td><td class="num">{{ r.late }}</td><td class="num">{{ '%g' % r.leave }}</td><td class="num mono">{{ '%.2f' % r.pay }}</td></tr>{% endfor %}
</tbody></table></div></section></div>
<section class="panel"><header class="panel-head"><h2>Leave days by type</h2></header>
{% for k, v in leave_types.items() %}<div class="hbar"><span>{{ k|capitalize }}</span><div class="bar"><span style="width: {{ (v / leave_max * 100)|round|int }}%"></span></div><b class="mono">{{ '%g' % v }}</b></div>
{% else %}<p class="empty">No approved leave in this range.</p>{% endfor %}</section>"""


@bp.route("/")
@manager_required
def index():
    today = date.today()
    start = request.args.get("start") or today.replace(day=1).isoformat()
    end = request.args.get("end") or today.isoformat()
    try:
        date.fromisoformat(start); date.fromisoformat(end)
    except ValueError:
        start, end = today.replace(day=1).isoformat(), today.isoformat()
    emps = {e["id"]: e for e in E.Employee.list()}
    entries = entries_between(start, end)
    grace = timedelta(minutes=client_setting("late_threshold_minutes", 15))
    shifts = {(s["employee_id"], s["date"]): s for s in E.Shift.query("date BETWEEN ? AND ?", (start, end))}
    stats = defaultdict(lambda: {"hours": 0.0, "days": set(), "late": 0, "leave": 0.0})
    for e in entries:
        s = stats[e["employee_id"]]
        s["hours"] += entry_hours(e)
        day = e["clock_in"][:10]
        s["days"].add(day)
        shift = shifts.get((e["employee_id"], day))
        if shift:
            planned = datetime.fromisoformat(f"{day}T{shift['start_time']}:00")
            if parse_dt(e["clock_in"]) > planned + grace:
                s["late"] += 1
    leave_types = defaultdict(float)
    for l in E.LeaveRequest.query("status='approved' AND start_date<=? AND end_date>=?", (end, start)):
        stats[l["employee_id"]]["leave"] += l["days"]
        leave_types[l["leave_type"]] += l["days"]
    top = max((s["hours"] for s in stats.values()), default=0) or 1
    rows = sorted(({"name": emps.get(i, {}).get("full_name", "Unknown"), "hours": fmt_hours(s["hours"]),
                    "pct": round(s["hours"] / top * 100), "days": len(s["days"]), "late": s["late"],
                    "leave": s["leave"], "pay": s["hours"] * (emps.get(i, {}).get("hourly_rate") or 0),
                    "_h": s["hours"]} for i, s in stats.items()), key=lambda r: -r["_h"])
    body = tpl(_T, start=start, end=end, rows=rows, total=fmt_hours(sum(r["_h"] for r in rows)),
               days_worked=sum(r["days"] for r in rows), late_total=sum(r["late"] for r in rows),
               leave_total=sum(leave_types.values()), leave_types=dict(leave_types),
               leave_max=max(leave_types.values(), default=1) or 1)
    return render_page("Reports", body, "reports")


def client_setting(key, default):
    from flask import g
    return g.settings.get(key, default)
