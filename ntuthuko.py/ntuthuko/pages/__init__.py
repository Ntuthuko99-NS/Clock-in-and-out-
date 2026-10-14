from . import (alerts_page, auth_pages, clock, dashboard, employees, leave,
               my_profile, reports, settings, shifts, timesheet, whatsapp_connects)

BLUEPRINTS = [auth_pages.bp, dashboard.bp, clock.bp, employees.bp, leave.bp, shifts.bp,
              timesheet.bp, reports.bp, settings.bp, my_profile.bp, alerts_page.bp,
              whatsapp_connects.bp]
