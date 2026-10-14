"""EntityLeaveRequest - schema for leave requests."""
LEAVE_TYPES = ["annual", "sick", "family", "unpaid"]

SCHEMA = {
    "name": "LeaveRequest",
    "table": "leave_requests",
    "fields": {
        "employee_id": "int",
        "leave_type": "text",
        "start_date": "text",
        "end_date": "text",
        "days": "real",
        "reason": "text",
        "status": "text",          # pending | approved | rejected | cancelled
        "reviewed_by": "int",
        "review_note": "text",
    },
    "required": ["employee_id", "leave_type", "start_date", "end_date"],
    "defaults": {"status": "pending", "days": 1},
}
