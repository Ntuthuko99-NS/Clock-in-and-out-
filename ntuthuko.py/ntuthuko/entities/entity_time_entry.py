"""EntityTimeEntry - clock in/out records."""
SCHEMA = {
    "name": "TimeEntry",
    "table": "time_entries",
    "fields": {
        "employee_id": "int",
        "clock_in": "text",        # ISO datetime
        "clock_out": "text",
        "break_minutes": "int",
        "notes": "text",
        "status": "text",          # active | completed
        "client_uuid": "text",     # offline-sync idempotency key (clock in)
        "client_out_uuid": "text", # offline-sync idempotency key (clock out)
    },
    "required": ["employee_id", "clock_in"],
    "defaults": {"break_minutes": 0, "status": "active"},
}
