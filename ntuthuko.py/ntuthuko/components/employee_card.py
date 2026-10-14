from ui import initials, tpl

_T = """<article class="card employee">
  <div class="card-top">
    <span class="avatar">{{ e.initials }}</span>
    <div class="grow"><h3>{{ e.full_name }}</h3><small>{{ e.position or 'No position set' }}{% if e.department %} - {{ e.department }}{% endif %}</small></div>
    <span class="badge {{ 'ok' if e.status=='active' else 'muted' }}">{{ e.status }}</span>
  </div>
  <dl class="meta">
    <div><dt>Email</dt><dd>{{ e.email }}</dd></div>
    <div><dt>Phone</dt><dd>{{ e.phone or '-' }}</dd></div>
    <div><dt>Role</dt><dd>{{ e.role }}</dd></div>
  </dl>
  {% if can_edit %}
  <div class="card-actions">
    <a class="btn sm" href="{{ url_for('employees.edit', employee_id=e.id) }}">Edit</a>
    <form method="post" action="{{ url_for('employees.remove', employee_id=e.id) }}" onsubmit="return confirm('Delete {{ e.full_name|e }}? Their time and leave records are kept but unlinked.')">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
      <button class="btn sm danger">Delete</button>
    </form>
  </div>{% endif %}
</article>"""


def EmployeeCard(emp, can_edit=False):
    return tpl(_T, e={**emp, "initials": initials(emp["full_name"])}, can_edit=can_edit)
