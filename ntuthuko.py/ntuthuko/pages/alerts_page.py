from flask import Blueprint, request, redirect, url_for
from auth import login_required
from components.alerts import Alerts
from layout import render_page
from services import alert_service

bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@bp.route("/")
@login_required
def index():
    f = request.args.get("filter", "all")
    sev = f if f in ("critical", "warning", "info") else None
    items = alert_service.visible_alerts(unread_only=(f == "unread"), severity=sev)
    return render_page("Alerts", Alerts(items, f), "alerts")


@bp.post("/read-all")
@login_required
def read_all():
    alert_service.mark_all_read()
    return redirect(url_for("alerts.index"))


@bp.post("/<int:alert_id>/read")
@login_required
def read(alert_id):
    alert_service.mark_read(alert_id)
    return redirect(url_for("alerts.index"))


@bp.post("/<int:alert_id>/delete")
@login_required
def remove(alert_id):
    alert_service.delete(alert_id)
    return redirect(url_for("alerts.index"))
