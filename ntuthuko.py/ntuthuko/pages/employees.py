from flask import Blueprint, abort, flash, g, redirect, request, url_for
from markupsafe import Markup
from werkzeug.security import generate_password_hash
from auth import manager_required
from components.employee_card import EmployeeCard
from components.employee_form import EmployeeForm
from database import get_db
from layout import render_page
from ntuthuko_client import ntuthukoClient as client

bp = Blueprint("employees", __name__, url_prefix="/employees")
Employee = client.entities.Employee
FIELDS = ["full_name", "email", "phone", "whatsapp_number", "position", "department",
          "status", "hourly_rate", "hire_date"]


def _data():
    d = {k: request.form.get(k, "").strip() for k in FIELDS}
    d["email"] = d["email"].lower()
    try:
        d["hourly_rate"] = float(d["hourly_rate"] or 0)
    except ValueError:
        d["hourly_rate"] = 0
    if d["status"] not in ("active", "inactive"):
        d["status"] = "active"
    if g.user["role"] == "admin" and request.form.get("role") in ("employee", "manager", "admin"):
        d["role"] = request.form["role"]
    return d


@bp.route("/")
@manager_required
def index():
    q = request.args.get("q", "").strip()
    rows = Employee.query("full_name LIKE ? OR email LIKE ? OR department LIKE ?",
                          (f"%{q}%",) * 3, order_by="full_name") if q else Employee.list(order_by="full_name")
    body = Markup(f'<form class="toolbar" method="get"><input type="search" name="q" placeholder="Search name, email or department" value="{Markup.escape(q)}">'
                  '<button class="btn">Search</button></form><div class="grid cards">') \
        + Markup("").join(EmployeeCard(e, True) for e in rows) + Markup("</div>")
    if not rows:
        body += Markup('<p class="empty">No employees match. Add your first employee to get started.</p>')
    return render_page("Employees", body, "employees",
                       actions=Markup(f'<a class="btn primary" href="{url_for("employees.new")}">Add employee</a>'))


@bp.route("/new", methods=["GET", "POST"])
@manager_required
def new():
    if request.method == "POST":
        d = _data()
        pw = request.form.get("password", "")
        if Employee.first(email=d["email"]) or get_db().execute("SELECT 1 FROM users WHERE email=?", (d["email"],)).fetchone():
            flash("An employee or login with that email already exists.", "error")
        elif pw and len(pw) < 8:
            flash("Temporary password must be at least 8 characters.", "error")
        else:
            try:
                if pw:
                    db = get_db()
                    cur = db.execute("INSERT INTO users (email,password_hash,full_name,role) VALUES (?,?,?,?)",
                                     (d["email"], generate_password_hash(pw), d["full_name"], d.get("role", "employee")))
                    db.commit()
                    d["user_id"] = cur.lastrowid
                Employee.create(**d)
                flash("Employee added.", "ok")
                return redirect(url_for("employees.index"))
            except ValueError as e:
                flash(str(e), "error")
    return render_page("Add employee", EmployeeForm(None, g.user["role"] == "admin"), "employees")


@bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@manager_required
def edit(employee_id):
    emp = Employee.get(employee_id) or abort(404)
    if request.method == "POST":
        d = _data()
        try:
            Employee.update(employee_id, **d)
            if emp.get("user_id"):
                db = get_db()
                db.execute("UPDATE users SET full_name=?, role=COALESCE(?,role), is_active=? WHERE id=?",
                           (d["full_name"], d.get("role"), 1 if d["status"] == "active" else 0, emp["user_id"]))
                db.commit()
            flash("Changes saved.", "ok")
            return redirect(url_for("employees.index"))
        except ValueError as e:
            flash(str(e), "error")
    return render_page("Edit employee", EmployeeForm(emp, g.user["role"] == "admin"), "employees")


@bp.post("/<int:employee_id>/delete")
@manager_required
def remove(employee_id):
    emp = Employee.get(employee_id) or abort(404)
    if emp.get("user_id") == g.user["id"]:
        flash("You cannot delete your own profile.", "error")
    else:
        if emp.get("user_id"):
            db = get_db()
            db.execute("DELETE FROM users WHERE id=?", (emp["user_id"],))
            db.commit()
        Employee.delete(employee_id)
        flash("Employee deleted.", "ok")
    return redirect(url_for("employees.index"))
