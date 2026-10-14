"""Clock in/out endpoints (form fallback + offline sync API)."""
from flask import Blueprint, flash, g, jsonify, redirect, request, url_for
from auth import login_required
from components.clock_offline_sync import sync_events
from services import alert_service, time_service

bp = Blueprint("clock", __name__, url_prefix="/clock")


@bp.post("/toggle")
@login_required
def toggle():
    if not g.employee:
        flash("Your login is not linked to an employee profile.", "error")
    elif time_service.open_entry(g.employee["id"]):
        time_service.clock_out(g.employee["id"])
        flash("Clocked out. Have a good one.", "ok")
    else:
        time_service.clock_in(g.employee["id"])
        flash("Clocked in.", "ok")
    return redirect(url_for("dashboard.index"))


@bp.post("/sync")
@login_required
def sync():
    if not g.employee:
        return jsonify(ok=False, error="No employee profile"), 400
    events = (request.get_json(silent=True) or {}).get("events", [])
    if not isinstance(events, list) or len(events) > 200:
        return jsonify(ok=False, error="Invalid payload"), 400
    return jsonify(ok=True, processed=sync_events(g.employee["id"], events))
