"""AlertService - creates, queries and auto-generates alert notifications.
(Uses ntuthukoClient; the old base44Client import was removed.)"""
from datetime import date, datetime, timedelta
from flask import g
from ntuthuko_client import ntuthukoClient as client
from services import leave_service, time_service, whatsapp_service
from ui import now, parse_dt

Alert = client.entities.Alert


def create_alert(title, message="", severity="info", type="system", employee_id=None, whatsapp=True):
    """Create an alert unless an identical unread one already exists (de-duplication)."""
    if Alert.query("title=? AND type=? AND is_read=0 AND IFNULL(employee_id,0)=?",
                   (title, type, employee_id or 0)):
        return None
    alert = Alert.create(title=title, message=message, severity=severity,
                         type=type, employee_id=employee_id)
    if whatsapp and severity == "critical" and employee_id:
        whatsapp_service.notify_employee(employee_id, f"{title}: {message}")
    return alert


def _scope():
    """SQL where-clause limiting alerts to what the current user may see."""
    if g.is_manager:
        return "(employee_id IS NULL OR employee_id=?)", [g.employee["id"] if g.employee else 0]
    return "employee_id=?", [g.employee["id"] if g.employee else 0]


def visible_alerts(unread_only=False, severity=None, limit=None):
    where, params = _scope()
    if unread_only:
        where += " AND is_read=0"
    if severity:
        where += " AND severity=?"
        params.append(severity)
    return Alert.query(where, params, order_by="-created_at", limit=limit)


def unread_count():
    where, params = _scope()
    return Alert.count(where + " AND is_read=0", params)


def _mine(alert_id):
    alert = Alert.get(alert_id)
    where, params = _scope()
    ok = Alert.query(where + " AND id=?", params + [alert_id]) if alert else []
    return alert if ok else None


def mark_read(alert_id):
    if _mine(alert_id):
        Alert.update(alert_id, is_read=1)


def mark_all_read():
    where, params = _scope()
    for a in Alert.query(where + " AND is_read=0", params):
        Alert.update(a["id"], is_read=1)


def delete(alert_id):
    if _mine(alert_id):
        Alert.delete(alert_id)


def run_checks():
    """Late clock-ins and forgotten clock-outs. Cheap; called on dashboard load."""
    settings = g.settings
    today = date.today().isoformat()
    late_after = timedelta(minutes=settings.get("late_threshold_minutes", 15))
    on_leave = leave_service.on_leave_today()
    nowdt = now()

    for shift in client.entities.Shift.filter(date=today, status="scheduled"):
        emp_id = shift["employee_id"]
        if emp_id in on_leave:
            continue
        start = datetime.fromisoformat(f"{today}T{shift['start_time']}:00")
        if nowdt <= start + late_after:
            continue
        worked = client.entities.TimeEntry.query(
            "employee_id=? AND date(clock_in)=?", (emp_id, today), limit=1)
        if not worked:
            emp = client.entities.Employee.get(emp_id) or {"full_name": "An employee"}
            msg = f"{emp['full_name']} has not clocked in for the {shift['start_time']} shift on {today}."
            create_alert(f"Late clock-in: {emp['full_name']} ({today})", msg, "warning",
                         "late_clock_in", None)
            create_alert("You have not clocked in", msg, "warning", "late_clock_in", emp_id)

    max_h = settings.get("max_shift_hours", 12)
    for entry in client.entities.TimeEntry.filter(status="active"):
        if time_service.entry_hours(entry) > max_h:
            emp = client.entities.Employee.get(entry["employee_id"]) or {"full_name": "An employee"}
            create_alert(f"Missing clock-out: {emp['full_name']}",
                         f"Clocked in at {entry['clock_in']} and still running after {max_h:g} hours.",
                         "critical", "missing_clock_out", None, whatsapp=False)
