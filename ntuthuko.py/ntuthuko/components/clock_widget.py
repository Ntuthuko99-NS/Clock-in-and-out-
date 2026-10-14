from services.time_service import entry_hours
from ui import fmt_hours, fmt_time, tpl
from components.clock_offline_sync import SCRIPT

_T = """<section class="panel clock {{ 'on' if working }}">
  {% if not emp %}
    <p class="empty">Your login is not linked to an employee profile, so time tracking is unavailable.</p>
  {% else %}
  <div class="clock-state">
    <span class="pulse"></span>
    <div>
      <h2>{{ 'You are clocked in' if working else 'You are clocked out' }}</h2>
      <p class="mono">{% if working %}Since {{ since }} - {{ duration }}{% else %}Ready when you are{% endif %}</p>
    </div>
  </div>
  <form id="clock-form" method="post" action="{{ url_for('clock.toggle') }}"
        data-next="{{ 'out' if working else 'in' }}" data-sync="{{ url_for('clock.sync') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="btn big {{ 'danger' if working else 'primary' }}">{{ 'Clock out' if working else 'Clock in' }}</button>
  </form>
  <p id="offline-badge" class="badge warn" hidden></p>
  {{ script }}
  {% endif %}
</section>"""


def ClockWidget(employee, entry):
    return tpl(_T, emp=employee, working=bool(entry), script=SCRIPT,
               since=fmt_time(entry["clock_in"]) if entry else "",
               duration=fmt_hours(entry_hours(entry)) if entry else "")
