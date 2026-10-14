from ui import tpl

_T = """<form method="post" class="form grid2">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <label>Full name<input name="full_name" required value="{{ e.full_name or '' }}"></label>
  <label>Email<input type="email" name="email" required value="{{ e.email or '' }}"></label>
  <label>Phone<input name="phone" value="{{ e.phone or '' }}"></label>
  <label>WhatsApp number<input name="whatsapp_number" placeholder="0821234567" value="{{ e.whatsapp_number or '' }}"></label>
  <label>Position<input name="position" value="{{ e.position or '' }}"></label>
  <label>Department<input name="department" value="{{ e.department or '' }}"></label>
  <label>Role
    <select name="role" {{ '' if can_set_role else 'disabled' }}>
      {% for r in ['employee','manager','admin'] %}<option {{ 'selected' if (e.role or 'employee')==r }}>{{ r }}</option>{% endfor %}
    </select></label>
  <label>Status
    <select name="status">{% for s in ['active','inactive'] %}<option {{ 'selected' if (e.status or 'active')==s }}>{{ s }}</option>{% endfor %}</select></label>
  <label>Hourly rate (ZAR)<input type="number" step="0.01" min="0" name="hourly_rate" value="{{ e.hourly_rate or 0 }}"></label>
  <label>Hire date<input type="date" name="hire_date" value="{{ e.hire_date or '' }}"></label>
  {% if not e.id %}
  <label class="span2">Temporary password (creates a login; min 8 characters, leave blank for no login)
    <input type="password" name="password" minlength="8" autocomplete="new-password"></label>
  {% endif %}
  <div class="span2 actions">
    <button class="btn primary">{{ 'Save changes' if e.id else 'Add employee' }}</button>
    <a class="btn ghost" href="{{ url_for('employees.index') }}">Cancel</a>
  </div>
</form>"""


def EmployeeForm(emp=None, can_set_role=False):
    return tpl(_T, e=emp or {}, can_set_role=can_set_role)
