from . import (entity_alert, entity_company_settings, entity_employee,
               entity_leave_request, entity_shift, entity_time_entry)

ALL_SCHEMAS = {
    m.SCHEMA["name"]: m.SCHEMA
    for m in (entity_employee, entity_shift, entity_time_entry,
              entity_leave_request, entity_alert, entity_company_settings)
}
