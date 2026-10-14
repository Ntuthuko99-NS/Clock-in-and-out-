from ui import tpl

_T = """<article class="card leave {{ r.status }}">
  <div class="card-top">
    <div class="grow"><h3>{{ name }}</h3>
      <small>{{ r.leave_type|capitalize }} leave, {{ '%g' % r.days }} day(s)</small></div>
    <span class="badge {{ tone }}">{{ r.status }}</span>
  </div>
  <p class="mono">{{ r.start_date }} to {{ r.end_date }}</p>
  {% if r.reason %}<p>{{ r.reason }}</p>{% endif %}
  {% if r.review_note %}<p class="note">Manager note: {{ r.review_note }}</p>{% endif %}
  <form method="post" class="card-actions">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    {% if can_review and r.status == 'pending' %}
      <input name="review_note" placeholder="Note (optional)">
      <button class="btn sm primary" formaction="{{ url_for('leave.review', leave_id=r.id, decision='approved') }}">Approve</button>
      <button class="btn sm danger" formaction="{{ url_for('leave.review', leave_id=r.id, decision='rejected') }}">Reject</button>
    {% endif %}
    {% if can_cancel and r.status in ['pending','approved'] %}
      <button class="btn sm ghost" formaction="{{ url_for('leave.cancel', leave_id=r.id) }}">Cancel request</button>
    {% endif %}
  </form>
</article>"""

TONES = {"pending": "warn", "approved": "ok", "rejected": "bad", "cancelled": "muted"}


def LeaveRequestCard(req, employee_name, can_review=False, can_cancel=False):
    return tpl(_T, r=req, name=employee_name, can_review=can_review, can_cancel=can_cancel,
               tone=TONES.get(req["status"], "muted"))
