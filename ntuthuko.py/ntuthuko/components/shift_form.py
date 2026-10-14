from ui import tpl

_T = """<form method="post" action="{{ url_for('shifts.create') }}" class="form grid2">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <label>Employee
    <select name="employee_id" required>{% for e in employees %}<option value="{{ e.id }}">{{ e.full_name }}</option>{% endfor %}</select></label>
  <label>Title<input name="title" value="Shift"></label>
  <label>Date<input type="date" name="date" required value="{{ today }}"></label>
  <label>Location<input name="location"></label>
  <label>Start<input type="time" name="start_time" required value="08:00"></label>
  <label>End<input type="time" name="end_time" required value="16:00"></label>
  <label class="span2">Notes<input name="notes"></label>
  <div class="span2 actions"><button class="btn primary">Create shift</button></div>
</form>"""


def ShiftForm(employees, today):
    return tpl(_T, employees=employees, today=today)
