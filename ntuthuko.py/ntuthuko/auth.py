"""Session auth, roles and CSRF protection."""
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import abort, g, redirect, request, session, url_for
from ntuthuko_client import ntuthukoClient as client
from database import get_db

MANAGER_ROLES = ("admin", "manager")


def load_user():
    g.user, g.employee, g.is_manager = None, None, False
    g.settings = client.entities.CompanySettings.first() or {}
    uid = session.get("user_id")
    if uid:
        row = get_db().execute("SELECT * FROM users WHERE id=? AND is_active=1", (uid,)).fetchone()
        if row:
            g.user = dict(row)
            g.employee = client.entities.Employee.first(user_id=uid)
            g.is_manager = g.user["role"] in MANAGER_ROLES
        else:
            session.clear()


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def check_csrf():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        if not sent or not secrets.compare_digest(sent, session.get("csrf", "")):
            abort(400, "Invalid or missing security token. Reload the page and try again.")


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if not g.user:
            return redirect(url_for("auth.login", next=request.path))
        return fn(*a, **kw)
    return wrapper


def manager_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*a, **kw):
        if not g.is_manager:
            abort(403)
        return fn(*a, **kw)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*a, **kw):
        if g.user["role"] != "admin":
            abort(403)
        return fn(*a, **kw)
    return wrapper


def is_locked(user):
    if user.get("locked_until"):
        return datetime.fromisoformat(user["locked_until"]) > datetime.now()
    return False


def register_failed_login(user_id):
    db = get_db()
    db.execute("UPDATE users SET failed_logins = failed_logins + 1 WHERE id=?", (user_id,))
    row = db.execute("SELECT failed_logins FROM users WHERE id=?", (user_id,)).fetchone()
    if row["failed_logins"] >= 5:
        until = (datetime.now() + timedelta(minutes=10)).isoformat(timespec="seconds")
        db.execute("UPDATE users SET locked_until=?, failed_logins=0 WHERE id=?", (until, user_id))
    db.commit()
