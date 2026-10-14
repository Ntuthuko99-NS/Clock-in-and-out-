import csv
import io
from datetime import date, timedelta
from flask import Blueprint, Response, g, request
from markupsafe import Markup
from auth import login_required
from components.timesheet_table import TimesheetTable
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from services.time_service import entries_between, entry_hours
from ui import tpl

bp = Blueprint("timesheet", __name__, url_prefix="/timesheet")

_FILTER = """<form class="toolbar" method="get">
 <label>From <input type="date" name="start" value="{{ start }}"></label>
 <label>To <input type="date" name="end" value="{{ end }}"></label>
 {% if mgr %}<label>Employee <select name="employee_id"><option value="">Everyone</option>
 {% for e in emps %}<option value="{{ e.id }}" {{ 'selected' if e.id == sel }}>{{ e.full_name }}</option>{% endfor %}</select></label>{% endif %}
 <button class="btn">Apply</button>
 <a class="btn ghost" href="{{ url_for('timesheet.export', start=start, end=end, employee_id=sel or '') }}">Export CSV</a></form>"""


def _params():
    today = date.today()
    start = request.args.get("start") or (today - timedelta(days=today.weekday())).isoformat()
    end = request.args.get("end") or today.isoformat()
    try:
        date.fromisoformat(start); date.fromisoformat(end)
    except ValueError:
        start, end = (today - timedelta(days=today.weekday())).isoformat(), today.isoformat()
    if g.is_manager:
        sel = request.args.get("employee_id", type=int)
    else:
        sel = g.employee["id"] if g.employee else -1
    return start, end, sel


@bp.route("/")
@login_required
def index():
    start, end, sel = _params()
    emps = client.entities.Employee.list(order_by="full_name")
    entries = entries_between(start, end, sel)
    body = tpl(_FILTER, start=start, end=end, sel=sel, emps=emps, mgr=g.is_manager) + \
        TimesheetTable(entries, {e["id"]: e for e in emps}, show_employee=g.is_manager)
    return render_page("Timesheet", body, "timesheet")


@bp.route("/export.csv")
@login_required
def export():
    start, end, sel = _params()
    names = {e["id"]: e["full_name"] for e in client.entities.Employee.list()}
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Employee", "Date", "Clock in", "Clock out", "Break (min)", "Hours"])
    for e in entries_between(start, end, sel):
        # Prefix risky cells so spreadsheet apps never treat text as a formula.
        name = names.get(e["employee_id"], "")
        name = "'" + name if name[:1] in "=+-@" else name
        w.writerow([name, e["clock_in"][:10], e["clock_in"], e.get("clock_out") or "",
                    e.get("break_minutes") or 0, f"{entry_hours(e):.2f}"])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=timesheet_{start}_{end}.csv"})
