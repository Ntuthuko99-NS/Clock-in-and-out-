"""EntityAlert - schema for alert notifications."""
SEVERITIES = ["info", "warning", "critical"]

SCHEMA = {
    "name": "Alert",
    "table": "alerts",
    "fields": {
        "employee_id": "int",      # NULL = visible to managers/admins
        "type": "text",            # late_clock_in | missing_clock_out | leave_request | system ...
        "title": "text",
        "message": "text",
        "severity": "text",
        "is_read": "bool",
    },
    "required": ["title"],
    "defaults": {"severity": "info", "is_read": 0, "type": "system"},
}
