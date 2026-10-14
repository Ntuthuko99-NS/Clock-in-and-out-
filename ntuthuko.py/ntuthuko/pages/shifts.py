from datetime import date, timedelta
from flask import Blueprint, abort, flash, g, redirect, request, url_for
from markupsafe import Markup
from auth import login_required, manager_required
from components.shift_form import ShiftForm
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from ui import tpl

bp = Blueprint("shifts", __name__, url_prefix="/shifts")
E = client.entities

_LIST = """<div class="panel flush table-wrap"><table class="table">
<thead><tr><th>Date</th><th>Time</th><th>Employee</th><th>Title</th><th>Location</th><th>Status</th>{% if mgr %}<th></th>{% endif %}</tr></thead>
<tbody>{% for s in shifts %}<tr><td>{{ s.date }}</td><td class="mono">{{ s.start_time }} - {{ s.end_time }}</td>
<td>{{ names.get(s.employee_id, 'Unknown') }}</td><td>{{ s.title }}</td><td>{{ s.location or '-' }}</td>
<td><span class="badge {{ 'ok' if s.status=='completed' else 'muted' if s.status=='cancelled' else 'info' }}">{{ s.status }}</span></td>
{% if mgr %}<td><form method="post" action="{{ url_for('shifts.remove', shift_id=s.id) }}"><input type="hidden" name="csrf_token" value="{{ csrf_token() }}"><button class="btn sm danger">Delete</button></form></td>{% endif %}</tr>
{% else %}<tr><td colspan="7" class="empty">No shifts scheduled from this week onwards.</td></tr>{% endfor %}</tbody></table></div>"""


@bp.route("/")
@login_required
def index():
    start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    names = {e["id"]: e["full_name"] for e in E.Employee.list()}
    if g.is_manager:
        rows = E.Shift.query("date>=?", (start,), order_by="date")
    else:
        rows = E.Shift.query("date>=? AND employee_id=?", (start, g.employee["id"] if g.employee else 0), order_by="date")
    rows.sort(key=lambda s: (s["date"], s["start_time"]))
    body = tpl(_LIST, shifts=rows, names=names, mgr=g.is_manager)
    if g.is_manager:
        form = ShiftForm(E.Employee.filter(status="active", order_by="full_name"), date.today().isoformat())
        body = Markup('<section class="panel"><header class="panel-head"><h2>New shift</h2></header>') + form + Markup("</section>") + body
    return render_page("Shifts", body, "shifts")


@bp.post("/create")
@manager_required
def create():
    f = request.form
    try:
        if f["end_time"] <= f["start_time"]:
            raise ValueError("End time must be after start time.")
        E.Shift.create(employee_id=int(f["employee_id"]), title=f.get("title", "").strip() or "Shift",
                       date=f["date"], start_time=f["start_time"], end_time=f["end_time"],
                       location=f.get("location", "").strip(), notes=f.get("notes", "").strip())
        flash("Shift created.", "ok")
    except (ValueError, KeyError) as e:
        flash(str(e) if isinstance(e, ValueError) and "time" in str(e) else "Check the shift details and try again.", "error")
    return redirect(url_for("shifts.index"))


@bp.post("/<int:shift_id>/delete")
@manager_required
def remove(shift_id):
    E.Shift.get(shift_id) or abort(404)
    E.Shift.delete(shift_id)
    flash("Shift deleted.", "ok")
    return redirect(url_for("shifts.index"))
