"""EntityEmployee - schema definition."""
SCHEMA = {
    "name": "Employee",
    "table": "employees",
    "fields": {
        "user_id": "int",
        "full_name": "text",
        "email": "text",
        "phone": "text",
        "whatsapp_number": "text",
        "position": "text",
        "department": "text",
        "role": "text",            # admin | manager | employee
        "status": "text",          # active | inactive
        "hourly_rate": "real",
        "hire_date": "text",
    },
    "required": ["full_name", "email"],
    "defaults": {"role": "employee", "status": "active", "hourly_rate": 0},
}
