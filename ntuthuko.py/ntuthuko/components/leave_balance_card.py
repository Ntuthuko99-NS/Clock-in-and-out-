from ui import tpl

_T = """<div class="balances">
{% for kind, b in balances.items() %}
  <article class="card balance">
    <h3>{{ kind|capitalize }} leave</h3>
    <p class="big">{{ '%g' % b.remaining }}<small> of {{ '%g' % b.total }} days left</small></p>
    <div class="bar"><span style="width: {{ ((b.used / b.total * 100) if b.total else 0)|round|int }}%"></span>
      <span class="pend" style="width: {{ ((b.pending / b.total * 100) if b.total else 0)|round|int }}%"></span></div>
    <small>{{ '%g' % b.used }} used, {{ '%g' % b.pending }} pending</small>
  </article>
{% endfor %}
</div>"""


def LeaveBalanceCard(balances):
    return tpl(_T, balances=balances)
