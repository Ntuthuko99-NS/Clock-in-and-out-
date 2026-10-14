"""Leave balances and day counting."""
from datetime import date, timedelta
from ntuthuko_client import ntuthukoClient as client

LeaveRequest = client.entities.LeaveRequest


def working_days(start, end):
    """Mon-Fri days between two ISO dates, inclusive."""
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    if d1 < d0:
        return 0
    return sum(1 for i in range((d1 - d0).days + 1) if (d0 + timedelta(i)).weekday() < 5)


def allowance(settings):
    return {"annual": settings.get("leave_annual_days", 15),
            "sick": settings.get("leave_sick_days", 30),
            "family": settings.get("leave_family_days", 3)}


def balances(employee_id, settings, year=None):
    year = year or date.today().year
    rows = LeaveRequest.query(
        "employee_id=? AND status IN ('approved','pending') AND substr(start_date,1,4)=?",
        (employee_id, str(year)))
    out = {}
    for kind, total in allowance(settings).items():
        used = sum(r["days"] for r in rows if r["leave_type"] == kind and r["status"] == "approved")
        pending = sum(r["days"] for r in rows if r["leave_type"] == kind and r["status"] == "pending")
        out[kind] = {"total": total, "used": used, "pending": pending,
                     "remaining": total - used - pending}
    return out


def overlaps(employee_id, start, end, ignore_id=None):
    return LeaveRequest.query(
        "employee_id=? AND status IN ('approved','pending') AND start_date<=? AND end_date>=? AND id!=?",
        (employee_id, end, start, ignore_id or 0))


def on_leave_today(day=None):
    day = (day or date.today()).isoformat()
    return {r["employee_id"] for r in LeaveRequest.query(
        "status='approved' AND start_date<=? AND end_date>=?", (day, day))}
