from flask import Blueprint, flash, g, redirect, request, url_for
from auth import admin_required
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from ui import tpl

bp = Blueprint("settings", __name__, url_prefix="/settings")

_T = """<form method="post" class="form grid2 panel">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<label>Company name<input name="company_name" required value="{{ s.company_name }}"></label>
<label>Timezone<input name="timezone" value="{{ s.timezone }}"></label>
<label>Work hours per day<input type="number" step="0.5" min="1" max="24" name="work_hours_per_day" value="{{ s.work_hours_per_day }}"></label>
<label>Late after (minutes)<input type="number" min="0" name="late_threshold_minutes" value="{{ s.late_threshold_minutes }}"></label>
<label>Flag missing clock-out after (hours)<input type="number" step="0.5" min="1" name="max_shift_hours" value="{{ s.max_shift_hours }}"></label>
<span></span>
<label>Annual leave (days/year)<input type="number" step="0.5" min="0" name="leave_annual_days" value="{{ s.leave_annual_days }}"></label>
<label>Sick leave (days/year)<input type="number" step="0.5" min="0" name="leave_sick_days" value="{{ s.leave_sick_days }}"></label>
<label>Family responsibility (days/year)<input type="number" step="0.5" min="0" name="leave_family_days" value="{{ s.leave_family_days }}"></label>
<div class="span2 actions"><button class="btn primary">Save settings</button></div></form>"""

NUM = ["work_hours_per_day", "late_threshold_minutes", "max_shift_hours",
       "leave_annual_days", "leave_sick_days", "leave_family_days"]


@bp.route("/", methods=["GET", "POST"])
@admin_required
def index():
    if request.method == "POST":
        data = {"company_name": request.form.get("company_name", "").strip(),
                "timezone": request.form.get("timezone", "").strip() or "Africa/Johannesburg"}
        try:
            for k in NUM:
                v = float(request.form.get(k, 0))
                if v < 0:
                    raise ValueError
                data[k] = int(v) if k == "late_threshold_minutes" else v
            if not data["company_name"]:
                raise ValueError
            client.entities.CompanySettings.update(g.settings["id"], **data)
            flash("Settings saved.", "ok")
            return redirect(url_for("settings.index"))
        except ValueError:
            flash("Enter a company name and non-negative numbers for every setting.", "error")
    return render_page("Settings", tpl(_T, s=client.entities.CompanySettings.first()), "settings")
