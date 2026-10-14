from datetime import date
from flask import Blueprint, abort, flash, g, redirect, request, url_for
from markupsafe import Markup
from auth import login_required, manager_required
from components.leave_balance_card import LeaveBalanceCard
from components.leave_calendar import LeaveCalendar
from components.leave_request_card import LeaveRequestCard
from components.leave_request_form import LeaveRequestForm
from entities.entity_leave_request import LEAVE_TYPES
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from services import alert_service, leave_service

bp = Blueprint("leave", __name__, url_prefix="/leave")
E = client.entities


@bp.route("/")
@login_required
def index():
    names = {e["id"]: e["full_name"] for e in E.Employee.list()}
    try:
        y, m = (int(x) for x in request.args.get("month", date.today().strftime("%Y-%m")).split("-"))
        date(y, m, 1)
    except ValueError:
        y, m = date.today().year, date.today().month
    me = g.employee["id"] if g.employee else 0
    reqs = E.LeaveRequest.list(limit=100) if g.is_manager else E.LeaveRequest.filter(employee_id=me, limit=100)
    cal_leaves = E.LeaveRequest.query("status IN ('approved','pending')") if g.is_manager else \
        E.LeaveRequest.query("status IN ('approved','pending') AND employee_id=?", (me,))
    parts = []
    if g.employee:
        parts.append(LeaveBalanceCard(leave_service.balances(me, g.settings)))
    form_emps = E.Employee.filter(status="active", order_by="full_name") if g.is_manager else None
    parts.append(Markup('<div class="cols"><div>') + LeaveCalendar(y, m, cal_leaves, names)
                 + Markup('</div><div><section class="panel"><header class="panel-head"><h2>Request leave</h2></header>')
                 + LeaveRequestForm(LEAVE_TYPES, form_emps) + Markup("</section></div></div>"))
    cards = [LeaveRequestCard(r, names.get(r["employee_id"], "Unknown"), g.is_manager,
                              r["employee_id"] == me or g.is_manager) for r in reqs]
    parts.append(Markup("<h2 class='sub'>Requests</h2><div class='grid cards'>") + Markup("").join(cards) + Markup("</div>"))
    if not cards:
        parts.append(Markup('<p class="empty">No leave requests yet.</p>'))
    return render_page("Leave", Markup("").join(parts), "leave")


@bp.post("/create")
@login_required
def create():
    emp_id = g.employee["id"] if g.employee else None
    if g.is_manager and request.form.get("employee_id"):
        emp_id = int(request.form["employee_id"])
    kind = request.form.get("leave_type")
    start, end = request.form.get("start_date", ""), request.form.get("end_date", "")
    try:
        days = leave_service.working_days(start, end)
    except ValueError:
        days = 0
    if not emp_id or kind not in LEAVE_TYPES:
        flash("Pick a leave type and make sure your profile is set up.", "error")
    elif days <= 0:
        flash("Choose valid dates that include at least one weekday (end date on or after start date).", "error")
    elif leave_service.overlaps(emp_id, start, end):
        flash("You already have leave that overlaps these dates.", "error")
    else:
        bal = leave_service.balances(emp_id, g.settings).get(kind)
        if bal and days > bal["remaining"]:
            flash(f"Only {bal['remaining']:g} day(s) of {kind} leave remaining; you asked for {days:g}.", "error")
        else:
            E.LeaveRequest.create(employee_id=emp_id, leave_type=kind, start_date=start, end_date=end,
                                  days=days, reason=request.form.get("reason", "").strip()[:500])
            who = E.Employee.get(emp_id)["full_name"]
            alert_service.create_alert(f"Leave request from {who}", f"{days:g} day(s) {kind}, {start} to {end}.",
                                       "info", "leave_request", None)
            flash("Leave request submitted.", "ok")
    return redirect(url_for("leave.index"))


@bp.post("/<int:leave_id>/<decision>")
@manager_required
def review(leave_id, decision):
    req = E.LeaveRequest.get(leave_id) or abort(404)
    if decision not in ("approved", "rejected") or req["status"] != "pending":
        abort(400)
    E.LeaveRequest.update(leave_id, status=decision, reviewed_by=g.user["id"],
                          review_note=request.form.get("review_note", "").strip()[:300])
    alert_service.create_alert(f"Leave {decision}", f"Your {req['leave_type']} leave ({req['start_date']} to {req['end_date']}) was {decision}.",
                               "info" if decision == "approved" else "warning", "leave_decision",
                               req["employee_id"], whatsapp=False)
    flash(f"Request {decision}.", "ok")
    return redirect(url_for("leave.index"))


@bp.post("/<int:leave_id>/cancel")
@login_required
def cancel(leave_id):
    req = E.LeaveRequest.get(leave_id) or abort(404)
    if not g.is_manager and (not g.employee or req["employee_id"] != g.employee["id"]):
        abort(403)
    E.LeaveRequest.update(leave_id, status="cancelled")
    flash("Request cancelled.", "ok")
    return redirect(url_for("leave.index"))
