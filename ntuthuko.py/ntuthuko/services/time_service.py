"""Time-entry maths and clock in/out actions."""
from datetime import datetime
from ntuthuko_client import ntuthukoClient as client
from ui import now, parse_dt

TimeEntry = client.entities.TimeEntry


def entry_hours(entry, at=None):
    start = parse_dt(entry["clock_in"])
    if not start:
        return 0.0
    end = parse_dt(entry.get("clock_out")) or (at or now())
    secs = (end - start).total_seconds() - (entry.get("break_minutes") or 0) * 60
    return max(secs, 0) / 3600


def open_entry(employee_id):
    return TimeEntry.first(employee_id=employee_id, status="active")


def clock_in(employee_id, ts=None, client_uuid=None):
    if open_entry(employee_id):
        return None
    return TimeEntry.create(employee_id=employee_id,
                            clock_in=(ts or now()).isoformat(timespec="seconds"),
                            client_uuid=client_uuid)


def clock_out(employee_id, ts=None, client_out_uuid=None):
    entry = open_entry(employee_id)
    if not entry:
        return None
    end = ts or now()
    start = parse_dt(entry["clock_in"])
    if start and end < start:
        end = start
    return TimeEntry.update(entry["id"], clock_out=end.isoformat(timespec="seconds"),
                            status="completed", client_out_uuid=client_out_uuid)


def entries_between(start_date, end_date, employee_id=None):
    where, params = "date(clock_in) BETWEEN ? AND ?", [start_date, end_date]
    if employee_id:
        where += " AND employee_id=?"
        params.append(employee_id)
    return TimeEntry.query(where, params, order_by="-clock_in")
