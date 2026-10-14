"""EntityCompanySettings - company configuration, including leave allowances
(the LeaveRequest rules) and WhatsApp credentials."""
SCHEMA = {
    "name": "CompanySettings",
    "table": "company_settings",
    "fields": {
        "company_name": "text",
        "timezone": "text",
        "work_hours_per_day": "real",
        "late_threshold_minutes": "int",
        "max_shift_hours": "real",
        "leave_annual_days": "real",
        "leave_sick_days": "real",
        "leave_family_days": "real",
        "whatsapp_enabled": "bool",
        "whatsapp_phone_id": "text",
        "whatsapp_token": "text",
    },
    "required": ["company_name"],
    "defaults": {
        "company_name": "Ntuthuko Workforce", "timezone": "Africa/Johannesburg",
        "work_hours_per_day": 8, "late_threshold_minutes": 15, "max_shift_hours": 12,
        "leave_annual_days": 15, "leave_sick_days": 30, "leave_family_days": 3,
        "whatsapp_enabled": 0,
    },
}
