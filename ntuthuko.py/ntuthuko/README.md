# Ntuthuko Workforce (Python / Flask / SQLite)

Time tracking, shifts, leave, alerts and WhatsApp notifications. Pure Python backend;
the only JavaScript is the small offline clock-queue script inside `components/clock_offline_sync.py`.

## Run
    pip install -r requirements.txt
    export SECRET_KEY="a-long-random-string"      # required for real deployments
    python run.py                                  # http://127.0.0.1:5000

First login (seeded on first run): `admin@ntuthuko.local` / `Admin@123`.
Change it under **My profile**, or set ADMIN_EMAIL / ADMIN_PASSWORD before the first run.
The SQLite file `ntuthuko.db` is created automatically.

## Layout
| Path | What it is |
|---|---|
| `ntuthuko_client.py` | `ntuthukoClient` (replaces `base44Client`): `entities.Employee.filter/create/update/delete` |
| `database.py` | SQLite schema built from the entity files + `users` login table |
| `entities/` | EntityEmployee, EntityShift, EntityTimeEntry, EntityLeaveRequest, EntityAlert, EntityCompanySettings |
| `services/alert_service.py` | AlertService (create, scope, auto late/missing clock-out checks) |
| `components/` | AlertPanels, Alerts, ClockOfflineSync, ClockWidget, Dashboard* cards, EmployeeCard/Form, Leave*, ShiftForm, TeamAvailability, TimesheetTable |
| `pages/` | Login/Register, Dashboard, Employees, Leave, MyProfile, Reports, Settings, Shifts, Timesheet, WhatsAppConnects, Alerts |
| `layout.py` | Layout (sidebar, flash messages, unread badge) |

## Roles
`admin` (everything, settings, WhatsApp keys) / `manager` (employees, reports, approvals) / `employee` (own time, leave, shifts).

## Security notes
Passwords hashed (scrypt via Werkzeug), CSRF token on every POST, lockout after 5 failed logins (10 min),
role checks on every route, parameterised SQL, autoescaped templates. For production, serve behind HTTPS,
set `SESSION_COOKIE_SECURE=True`, and run with gunicorn instead of `run.py`.
WhatsApp tokens are stored in the database in plain text; restrict file access to `ntuthuko.db`.
