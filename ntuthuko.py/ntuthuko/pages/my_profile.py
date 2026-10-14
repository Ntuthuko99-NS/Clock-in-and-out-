from flask import Blueprint, flash, g, redirect, request, url_for
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash
from auth import login_required
from components.leave_balance_card import LeaveBalanceCard
from database import get_db
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from services import leave_service
from ui import tpl

bp = Blueprint("my_profile", __name__, url_prefix="/me")

_T = """<div class="cols"><section class="panel"><header class="panel-head"><h2>Your details</h2></header>
<dl class="meta"><div><dt>Name</dt><dd>{{ u.full_name }}</dd></div><div><dt>Email</dt><dd>{{ u.email }}</dd></div>
<div><dt>Role</dt><dd>{{ u.role }}</dd></div>{% if e %}<div><dt>Position</dt><dd>{{ e.position or '-' }}</dd></div>
<div><dt>Department</dt><dd>{{ e.department or '-' }}</dd></div><div><dt>Hire date</dt><dd>{{ e.hire_date or '-' }}</dd></div>{% endif %}</dl>
{% if e %}<form method="post" action="{{ url_for('my_profile.update') }}" class="form">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<label>Phone<input name="phone" value="{{ e.phone or '' }}"></label>
<label>WhatsApp number (for alerts)<input name="whatsapp_number" value="{{ e.whatsapp_number or '' }}"></label>
<button class="btn primary">Save contact details</button></form>{% endif %}</section>
<section class="panel"><header class="panel-head"><h2>Change password</h2></header>
<form method="post" action="{{ url_for('my_profile.password') }}" class="form">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<label>Current password<input type="password" name="current" required autocomplete="current-password"></label>
<label>New password (min 8 characters)<input type="password" name="new" minlength="8" required autocomplete="new-password"></label>
<button class="btn primary">Update password</button></form></section></div>"""


@bp.route("/")
@login_required
def index():
    body = tpl(_T, u=g.user, e=g.employee)
    if g.employee:
        body += Markup("<h2 class='sub'>Your leave balances</h2>") + LeaveBalanceCard(
            leave_service.balances(g.employee["id"], g.settings))
    return render_page("My profile", body, "my_profile")


@bp.post("/update")
@login_required
def update():
    if g.employee:
        client.entities.Employee.update(g.employee["id"], phone=request.form.get("phone", "").strip(),
                                        whatsapp_number=request.form.get("whatsapp_number", "").strip())
        flash("Contact details saved.", "ok")
    return redirect(url_for("my_profile.index"))


@bp.post("/password")
@login_required
def password():
    new = request.form.get("new", "")
    if not check_password_hash(g.user["password_hash"], request.form.get("current", "")):
        flash("Your current password is incorrect.", "error")
    elif len(new) < 8:
        flash("Use a new password with at least 8 characters.", "error")
    else:
        db = get_db()
        db.execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), g.user["id"]))
        db.commit()
        flash("Password updated.", "ok")
    return redirect(url_for("my_profile.index"))
