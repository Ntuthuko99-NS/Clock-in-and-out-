"""SQLite database: users (login) + one table per entity schema."""
import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash
from entities import ALL_SCHEMAS

SQL_TYPES = {"text": "TEXT", "int": "INTEGER", "real": "REAL", "bool": "INTEGER DEFAULT 0"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _entity_ddl(schema):
    cols = ",\n  ".join(f"{n} {SQL_TYPES[t]}" for n, t in schema["fields"].items())
    return (f"CREATE TABLE IF NOT EXISTS {schema['table']} (\n"
            f"  id INTEGER PRIMARY KEY AUTOINCREMENT,\n  {cols},\n"
            f"  created_at TEXT DEFAULT (datetime('now')),\n"
            f"  updated_at TEXT DEFAULT (datetime('now'))\n);")


EXTRA_DDL = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'employee',
  is_active INTEGER NOT NULL DEFAULT 1,
  failed_logins INTEGER NOT NULL DEFAULT 0,
  locked_until TEXT,
  last_login TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS whatsapp_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  to_number TEXT NOT NULL,
  body TEXT NOT NULL,
  status TEXT NOT NULL,
  detail TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_time_in ON time_entries(client_uuid) WHERE client_uuid IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_time_emp ON time_entries(employee_id, clock_in);
CREATE INDEX IF NOT EXISTS ix_leave_emp ON leave_requests(employee_id, start_date);
CREATE INDEX IF NOT EXISTS ix_shift_date ON shifts(date);
CREATE INDEX IF NOT EXISTS ix_alert_read ON alerts(is_read, created_at);
"""


def init_db(app):
    import sqlite3 as s
    db = s.connect(app.config["DATABASE"])
    db.row_factory = s.Row
    for schema in ALL_SCHEMAS.values():
        db.execute(_entity_ddl(schema))
    db.executescript(EXTRA_DDL)

    if not db.execute("SELECT 1 FROM company_settings").fetchone():
        d = ALL_SCHEMAS["CompanySettings"]["defaults"]
        db.execute(f"INSERT INTO company_settings ({','.join(d)}) VALUES ({','.join('?' * len(d))})",
                   list(d.values()))

    email = app.config["SEED_ADMIN_EMAIL"]
    if not db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        cur = db.execute(
            "INSERT INTO users (email,password_hash,full_name,role) VALUES (?,?,?,'admin')",
            (email, generate_password_hash(app.config["SEED_ADMIN_PASSWORD"]), "System Admin"))
        db.execute(
            "INSERT INTO employees (user_id,full_name,email,role,position,department,status) "
            "VALUES (?,?,?,'admin','Administrator','Management','active')",
            (cur.lastrowid, "System Admin", email))
    db.commit()
    db.close()
