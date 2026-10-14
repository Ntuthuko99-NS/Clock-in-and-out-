from ui import tpl

_T = """<form method="post" action="{{ url_for('leave.create') }}" class="form grid2">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  {% if employees %}
  <label class="span2">On behalf of
    <select name="employee_id">{% for e in employees %}<option value="{{ e.id }}">{{ e.full_name }}</option>{% endfor %}</select></label>
  {% endif %}
  <label>Leave type
    <select name="leave_type">{% for t in types %}<option value="{{ t }}">{{ t|capitalize }}</option>{% endfor %}</select></label>
  <span></span>
  <label>From<input type="date" name="start_date" required></label>
  <label>To<input type="date" name="end_date" required></label>
  <label class="span2">Reason<textarea name="reason" rows="2"></textarea></label>
  <div class="span2 actions"><button class="btn primary">Submit request</button>
  <small>Weekends are not counted.</small></div>
</form>"""


def LeaveRequestForm(types, employees=None):
    return tpl(_T, types=types, employees=employees)
