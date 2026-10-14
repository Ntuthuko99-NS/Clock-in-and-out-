import calendar
from datetime import date
from ui import tpl

_T = """<section class="panel">
  <header class="panel-head">
    <h2>{{ title }}</h2>
    <span class="pager"><a class="btn sm" href="?month={{ prev }}">Previous</a><a class="btn sm" href="?month={{ nxt }}">Next</a></span>
  </header>
  <div class="cal">
    {% for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}<div class="cal-h">{{ d }}</div>{% endfor %}
    {% for c in cells %}
      <div class="cal-c {{ 'out' if not c.day }} {{ 'today' if c.today }} {{ 'wk' if c.weekend }}">
        {% if c.day %}<span class="n">{{ c.day }}</span>
          {% for l in c.leaves[:3] %}<span class="chip {{ l.status }}" title="{{ l.name }} - {{ l.type }} ({{ l.status }})">{{ l.name.split(' ')[0] }}</span>{% endfor %}
          {% if c.leaves|length > 3 %}<small>+{{ c.leaves|length - 3 }} more</small>{% endif %}
        {% endif %}
      </div>
    {% endfor %}
  </div>
  <p class="legend"><span class="chip approved">Approved</span> <span class="chip pending">Pending</span></p>
</section>"""


def LeaveCalendar(year, month, leaves, names):
    cells, today = [], date.today()
    for week in calendar.Calendar(0).monthdatescalendar(year, month):
        for d in week:
            if d.month != month:
                cells.append({"day": None, "leaves": []})
                continue
            iso = d.isoformat()
            cells.append({"day": d.day, "today": d == today, "weekend": d.weekday() >= 5,
                          "leaves": [{"name": names.get(l["employee_id"], "?"), "type": l["leave_type"],
                                      "status": l["status"]} for l in leaves
                                     if l["start_date"] <= iso <= l["end_date"]]})
    py, pm = (year - 1, 12) if month == 1 else (year, month - 1)
    ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
    return tpl(_T, cells=cells, title=f"{calendar.month_name[month]} {year}",
               prev=f"{py}-{pm:02d}", nxt=f"{ny}-{nm:02d}")
