"""WhatsApp Cloud API sender (Meta Graph API). Falls back to logging when disabled."""
import json
import re
import urllib.request
import urllib.error
from database import get_db
from ntuthuko_client import ntuthukoClient as client

GRAPH_URL = "https://graph.facebook.com/v19.0/{phone_id}/messages"


def normalise_number(number):
    """South African friendly: 0821234567 -> 27821234567. Returns digits only."""
    digits = re.sub(r"\D", "", number or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "27" + digits[1:]
    return digits


def _log(to, body, status, detail=""):
    db = get_db()
    db.execute("INSERT INTO whatsapp_messages (to_number, body, status, detail) VALUES (?,?,?,?)",
               (to, body, status, detail[:500]))
    db.commit()


def send_message(number, body):
    """Returns (ok, status_text)."""
    s = client.entities.CompanySettings.first() or {}
    to = normalise_number(number)
    if not to:
        _log(number or "", body, "failed", "Invalid phone number")
        return False, "Invalid phone number"
    if not (s.get("whatsapp_enabled") and s.get("whatsapp_phone_id") and s.get("whatsapp_token")):
        _log(to, body, "not_sent", "WhatsApp is not connected")
        return False, "WhatsApp is not connected. Add your credentials and enable it first."
    payload = json.dumps({"messaging_product": "whatsapp", "to": to, "type": "text",
                          "text": {"body": body}}).encode()
    req = urllib.request.Request(
        GRAPH_URL.format(phone_id=s["whatsapp_phone_id"]), data=payload, method="POST",
        headers={"Authorization": f"Bearer {s['whatsapp_token']}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            _log(to, body, "sent", f"HTTP {resp.status}")
            return True, "Message sent"
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="ignore")
        _log(to, body, "failed", f"HTTP {e.code}: {detail}")
        return False, f"WhatsApp rejected the message (HTTP {e.code})."
    except Exception as e:  # network errors
        _log(to, body, "failed", str(e))
        return False, "Could not reach WhatsApp. Check your connection."


def notify_employee(employee_id, body):
    emp = client.entities.Employee.get(employee_id)
    if emp and emp.get("whatsapp_number"):
        return send_message(emp["whatsapp_number"], body)
    return False, "Employee has no WhatsApp number"


def recent_messages(limit=20):
    return client.raw("SELECT * FROM whatsapp_messages ORDER BY id DESC LIMIT ?", (limit,))
