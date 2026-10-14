"""Login, registration and logout."""
from datetime import datetime
from flask import Blueprint, flash, g, redirect, request, session, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash
from auth import is_locked, register_failed_login
from database import get_db
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from ui import tpl

bp = Blueprint("auth", __name__)

_FORM = """<div class="auth">
  <section class="auth-card">
    <h1>{{ company }}</h1>
    <p class="lead">{{ lead }}</p>
    {% for cat, msg in flashes %}<div class="flash {{ cat }}" role="alert">{{ msg }}</div>{% endfor %}
    <form method="post" class="form">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <input type="hidden" name="next" value="{{ next }}">
      {% if register %}<label>Full name<input name="full_name" required autocomplete="name"></label>{% endif %}
      <label>Email<input type="email" name="email" required autocomplete="username" autofocus></label>
      <label>Password<input type="password" name="password" required minlength="{{ 8 if register else 1 }}"
        autocomplete="{{ 'new-password' if register else 'current-password' }}"></label>
      <button class="btn primary big">{{ 'Create account' if register else 'Sign in' }}</button>
    </form>
    <p class="switch">{% if register %}Already have an account? <a href="{{ url_for('auth.login') }}">Sign in</a>
    {% else %}New here? <a href="{{ url_for('auth.register') }}">Create an account</a>{% endif %}</p>
  </section>
</div>"""


def _safe_next(value):
    return value if value and value.startswith("/") and not value.startswith("//") else ""


def _page(register=False):
    from flask import get_flashed_messages
    body = tpl(_FORM, company=g.settings.get("company_name", "Ntuthuko Workforce"), register=register,
               lead="Create your employee account." if register else "Sign in to track time, shifts and leave.",
               next=_safe_next(request.values.get("next")), flashes=get_flashed_messages(with_categories=True))
    return render_page("Create account" if register else "Sign in", body)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        row = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        user = dict(row) if row else None
        if user and is_locked(user):
            flash("Too many failed attempts. Try again in 10 minutes.", "error")
        elif user and user["is_active"] and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True
            db = get_db()
            db.execute("UPDATE users SET failed_logins=0, locked_until=NULL, last_login=? WHERE id=?",
                       (datetime.now().isoformat(timespec="seconds"), user["id"]))
            db.commit()
            return redirect(_safe_next(request.form.get("next")) or url_for("dashboard.index"))
        else:
            if user:
                register_failed_login(user["id"])
            flash("Email or password is incorrect.", "error")
    return _page()


@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        db = get_db()
        if not name or "@" not in email:
            flash("Enter your name and a valid email address.", "error")
        elif len(pw) < 8:
            flash("Use a password with at least 8 characters.", "error")
        elif db.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            flash("An account with this email already exists. Sign in instead.", "error")
        else:
            cur = db.execute("INSERT INTO users (email,password_hash,full_name,role) VALUES (?,?,?,'employee')",
                             (email, generate_password_hash(pw), name))
            db.commit()
            existing = client.entities.Employee.first(email=email)
            if existing and not existing.get("user_id"):
                client.entities.Employee.update(existing["id"], user_id=cur.lastrowid)
            elif not existing:
                client.entities.Employee.create(user_id=cur.lastrowid, full_name=name, email=email)
            flash("Account created. You can sign in now.", "ok")
            return redirect(url_for("auth.login"))
    return _page(register=True)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
