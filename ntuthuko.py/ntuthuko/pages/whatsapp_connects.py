"""WhatsAppConnects - connect the WhatsApp Business Cloud API and send alerts."""
from flask import Blueprint, flash, g, redirect, request, url_for
from auth import manager_required, admin_required
from layout import render_page
from ntuthuko_client import ntuthukoClient as client
from services import whatsapp_service
from ui import tpl

bp = Blueprint("whatsapp", __name__, url_prefix="/whatsapp")

_T = """<div class="cols">
<section class="panel"><header class="panel-head"><h2>Connection</h2>
<span class="badge {{ 'ok' if connected else 'muted' }}">{{ 'Connected' if connected else 'Not connected' }}</span></header>
{% if admin %}<form method="post" action="{{ url_for('whatsapp.save') }}" class="form">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<label>Phone number ID (WhatsApp Business Cloud API)<input name="whatsapp_phone_id" value="{{ s.whatsapp_phone_id or '' }}"></label>
<label>Access token<input type="password" name="whatsapp_token" placeholder="{{ 'Saved - leave blank to keep' if s.whatsapp_token else 'Paste token' }}" autocomplete="off"></label>
<label class="check"><input type="checkbox" name="whatsapp_enabled" {{ 'checked' if s.whatsapp_enabled }}> Send critical alerts to employees on WhatsApp</label>
<button class="btn primary">Save connection</button></form>
{% else %}<p class="empty">Only an admin can change the WhatsApp connection.</p>{% endif %}</section>
<section class="panel"><header class="panel-head"><h2>Send a test message</h2></header>
<form method="post" action="{{ url_for('whatsapp.test') }}" class="form">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<label>To (e.g. 0821234567)<input name="to" required></label>
<label>Message<textarea name="body" rows="3" required maxlength="1000">Hello from {{ s.company_name }}.</textarea></label>
<button class="btn">Send test</button></form></section></div>
<section class="panel flush table-wrap"><table class="table"><thead><tr><th>When</th><th>To</th><th>Message</th><th>Status</th></tr></thead><tbody>
{% for m in log %}<tr><td class="mono">{{ m.created_at }}</td><td>{{ m.to_number }}</td><td>{{ m.body }}</td>
<td><span class="badge {{ 'ok' if m.status=='sent' else 'bad' if m.status=='failed' else 'muted' }}" title="{{ m.detail }}">{{ m.status|replace('_',' ') }}</span></td></tr>
{% else %}<tr><td colspan="4" class="empty">No messages yet.</td></tr>{% endfor %}</tbody></table></section>"""


@bp.route("/")
@manager_required
def index():
    s = client.entities.CompanySettings.first()
    connected = bool(s["whatsapp_enabled"] and s["whatsapp_phone_id"] and s["whatsapp_token"])
    return render_page("WhatsApp", tpl(_T, s=s, connected=connected, admin=g.user["role"] == "admin",
                                      log=whatsapp_service.recent_messages()), "whatsapp")


@bp.post("/save")
@admin_required
def save():
    data = {"whatsapp_phone_id": request.form.get("whatsapp_phone_id", "").strip(),
            "whatsapp_enabled": 1 if request.form.get("whatsapp_enabled") else 0}
    if request.form.get("whatsapp_token", "").strip():
        data["whatsapp_token"] = request.form["whatsapp_token"].strip()
    client.entities.CompanySettings.update(g.settings["id"], **data)
    flash("WhatsApp connection saved.", "ok")
    return redirect(url_for("whatsapp.index"))


@bp.post("/test")
@manager_required
def test():
    ok, msg = whatsapp_service.send_message(request.form.get("to", ""), request.form.get("body", "")[:1000])
    flash(msg, "ok" if ok else "error")
    return redirect(url_for("whatsapp.index"))
