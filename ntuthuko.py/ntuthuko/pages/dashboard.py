from datetime import date
from flask import Blueprint, g
from auth import login_required
from components.alert_panels import AlertPanels
from components.clock_widget import ClockWidget
from components.dashboard_active_employees import DashboardActiveEmployees
from components.dashboard_recent_activity import DashboardRecentActivity
from components.dashboard_stat_card import DashboardStatCard
from components.team_availability import TeamAvailability
from layout import render_page
from markupsafe import Markup
from ntuthuko_client import ntuthukoClient as client
from services import alert_service, leave_service, time_service

bp = Blueprint("dashboard", __name__)
E = client.entities


@bp.route("/")
@login_required
def index():
    alert_service.run_checks()
    today = date.today().isoformat()
    emps = E.Employee.filter(status="active", order_by="full_name")
    by_id = {e["id"]: e for e in E.Employee.list()}
    active = E.TimeEntry.filter(status="active")
    on_leave = leave_service.on_leave_today()
    shifts_today = {s["employee_id"]: s for s in E.Shift.filter(date=today)}
    mine = time_service.open_entry(g.employee["id"]) if g.employee else None

    parts = [ClockWidget(g.employee, mine)]
    if g.is_manager:
        stats = [
            DashboardStatCard("Active employees", len(emps), href="/employees"),
            DashboardStatCard("Working now", len(active), tone="ok"),
            DashboardStatCard("On leave today", len(on_leave & {e['id'] for e in emps})),
            DashboardStatCard("Pending leave", E.LeaveRequest.count("status='pending'"),
                              tone="warn", href="/leave"),
        ]
        parts.append(Markup('<div class="stats">') + Markup("").join(stats) + Markup("</div>"))
    parts.append(AlertPanels(alert_service.visible_alerts(unread_only=True, limit=60)))
    left = DashboardActiveEmployees(active, by_id) + DashboardRecentActivity(
        E.TimeEntry.list(order_by="-clock_in", limit=6) if g.is_manager else E.TimeEntry.filter(
            employee_id=g.employee["id"] if g.employee else 0, order_by="-clock_in", limit=6),
        E.LeaveRequest.list(limit=5) if g.is_manager else E.LeaveRequest.filter(
            employee_id=g.employee["id"] if g.employee else 0, limit=5), by_id)
    right = TeamAvailability(emps, {e["employee_id"] for e in active}, on_leave, shifts_today)
    parts.append(Markup('<div class="cols">') + Markup("<div>") + left + Markup("</div><div>") + right + Markup("</div></div>"))
    return render_page("Dashboard", Markup("").join(parts), "dashboard")
