"""EntityShift - shift entity with properties and requirements."""
SCHEMA = {
    "name": "Shift",
    "table": "shifts",
    "fields": {
        "employee_id": "int",
        "title": "text",
        "date": "text",            # YYYY-MM-DD
        "start_time": "text",      # HH:MM
        "end_time": "text",        # HH:MM
        "location": "text",
        "notes": "text",
        "status": "text",          # scheduled | completed | cancelled
    },
    "required": ["employee_id", "date", "start_time", "end_time"],
    "defaults": {"status": "scheduled", "title": "Shift"},
}
