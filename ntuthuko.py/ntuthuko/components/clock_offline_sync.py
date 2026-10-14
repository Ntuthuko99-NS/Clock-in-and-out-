"""ClockOfflineSync - server side of offline time capture plus the small
browser script that queues clock events while offline and replays them later."""
from datetime import timedelta
from markupsafe import Markup
from services import alert_service, time_service
from ui import now, parse_dt

MAX_AGE_DAYS = 7


def sync_events(employee_id, events):
    """Idempotently apply queued events. Returns the uuids that need no retry."""
    done = []
    parsed = []
    for ev in events or []:
        ts, uid, action = parse_dt(str(ev.get("ts", ""))), str(ev.get("uuid", ""))[:64], ev.get("action")
        if not ts or not uid or action not in ("in", "out"):
            if uid:
                done.append(uid)  # malformed: drop so it never blocks the queue
            continue
        ts = min(ts, now())  # never accept the future
        if now() - ts > timedelta(days=MAX_AGE_DAYS):
            done.append(uid)
            continue
        parsed.append((ts, uid, action))
    for ts, uid, action in sorted(parsed):
        if action == "in":
            if not time_service.TimeEntry.first(client_uuid=uid):
                time_service.clock_in(employee_id, ts, uid)
        else:
            if not time_service.TimeEntry.first(client_out_uuid=uid):
                time_service.clock_out(employee_id, ts, uid)
        done.append(uid)
    return done


SCRIPT = Markup("""<script>
(function(){
  var KEY='ntu_clock_queue', form=document.getElementById('clock-form');
  if(!form) return;
  var csrf=document.querySelector('meta[name=csrf-token]').content;
  var badge=document.getElementById('offline-badge');
  function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch(e){return []}}
  function save(q){try{localStorage.setItem(KEY,JSON.stringify(q))}catch(e){}}
  function uuid(){return (window.crypto&&crypto.randomUUID)?crypto.randomUUID():'x'+Date.now()+Math.random().toString(16).slice(2)}
  function localIso(d){var p=function(n){return String(n).padStart(2,'0')};
    return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+'T'+p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds())}
  function show(){var n=load().length; if(badge){badge.hidden=!n; badge.textContent=n+' clock event'+(n>1?'s':'')+' waiting to sync'}}
  function flush(){
    var q=load(); if(!q.length||!navigator.onLine) return Promise.resolve(false);
    return fetch(form.dataset.sync,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},
      credentials:'same-origin',body:JSON.stringify({events:q})})
      .then(function(r){if(!r.ok) throw 0; return r.json()})
      .then(function(j){var d=j.processed||[]; save(load().filter(function(e){return d.indexOf(e.uuid)<0})); show(); return true})
      .catch(function(){return false});
  }
  form.addEventListener('submit',function(ev){
    ev.preventDefault();
    var q=load(); q.push({uuid:uuid(),action:form.dataset.next,ts:localIso(new Date())}); save(q); show();
    flush().then(function(ok){ if(ok) location.reload(); else if(badge) badge.hidden=false; });
  });
  window.addEventListener('online',function(){flush().then(function(ok){if(ok) location.reload()})});
  show(); flush();
})();
</script>""")
