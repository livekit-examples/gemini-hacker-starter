"""Tools for the ComuneAgent — public administration / municipal services.

Each function is a plain Python callable that the agent registers via
``self.register_tool(fn)``. They read from the seeded JSON data files and
return typed dicts so the frontend panel can render structured cards.
"""
from __future__ import annotations

import json
import random
import string
from datetime import date, timedelta
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_services() -> list[dict]:
    with open(_DATA_DIR / "comune_services.json", encoding="utf-8") as f:
        return json.load(f)


def _load_applications() -> list[dict]:
    with open(_DATA_DIR / "comune_applications.json", encoding="utf-8") as f:
        return json.load(f)


def lookup_service_requirements(service_name: str) -> dict:
    """Look up required documents and details for a municipal service.

    Matches *service_name* against the name, keywords, and service_id fields
    of the seeded services data. The search is case-insensitive.

    Returns::

        {
            "service": str,
            "service_id": str,
            "required_documents": list[str],
            "processing_days": int,
            "fee_eur": float,
            "office": str,
            "bookable_online": bool,
            "notes": str,
            "found": bool,
        }
    """
    needle = service_name.lower().strip()
    services = _load_services()

    for svc in services:
        # Check name, service_id, and all keywords
        candidates = [svc["name"].lower(), svc["service_id"].lower()] + [
            kw.lower() for kw in svc.get("keywords", [])
        ]
        if any(needle in candidate or candidate in needle for candidate in candidates):
            return {
                "service": svc["name"],
                "service_id": svc["service_id"],
                "required_documents": svc["required_documents"],
                "processing_days": svc["processing_days"],
                "fee_eur": svc["fee_eur"],
                "office": svc["office"],
                "bookable_online": svc["bookable_online"],
                "notes": svc["notes"],
                "found": True,
            }

    return {
        "service": service_name,
        "service_id": "",
        "required_documents": [],
        "processing_days": 0,
        "fee_eur": 0.0,
        "office": "",
        "bookable_online": False,
        "notes": "",
        "found": False,
    }


def check_application_status(application_id: str) -> dict:
    """Retrieve the current status of a municipal application by its ID.

    Returns::

        {
            "application_id": str,
            "service": str,
            "status": "pending" | "approved" | "rejected" | "requires_documents",
            "submitted_on": str,   # ISO date
            "expected_by": str,    # ISO date
            "notes": str,
            "found": bool,
        }
    """
    needle = application_id.strip().upper()
    applications = _load_applications()

    for app in applications:
        if app["application_id"].upper() == needle:
            return {
                "application_id": app["application_id"],
                "service": app["service"],
                "status": app["status"],
                "submitted_on": app["submitted_on"],
                "expected_by": app["expected_by"],
                "notes": app["notes"],
                "found": True,
            }

    return {
        "application_id": application_id,
        "service": "",
        "status": "pending",
        "submitted_on": "",
        "expected_by": "",
        "notes": "Nessuna pratica trovata con questo identificativo.",
        "found": False,
    }


def book_appointment(service: str, citizen_name: str, preferred_date: str) -> dict:
    """Book an appointment for a bookable municipal service.

    If the service is not bookable online, *found* is returned as ``False``
    with an explanation in *instructions*.

    Returns::

        {
            "confirmation_id": str,
            "service": str,
            "citizen_name": str,
            "date": str,           # ISO date
            "time": str,           # HH:MM
            "office": str,
            "instructions": str,
            "found": bool,
        }
    """
    svc_info = lookup_service_requirements(service)

    if not svc_info["found"]:
        return {
            "confirmation_id": "",
            "service": service,
            "citizen_name": citizen_name,
            "date": preferred_date,
            "time": "",
            "office": "",
            "instructions": (
                f"Il servizio '{service}' non è stato trovato nel catalogo comunale. "
                "Si prega di contattare direttamente lo sportello."
            ),
            "found": False,
        }

    if not svc_info["bookable_online"]:
        return {
            "confirmation_id": "",
            "service": svc_info["service"],
            "citizen_name": citizen_name,
            "date": preferred_date,
            "time": "",
            "office": svc_info["office"],
            "instructions": (
                f"Il servizio '{svc_info['service']}' non è prenotabile online. "
                f"Recarsi direttamente presso: {svc_info['office']}. "
                "Orari di apertura: lunedì-venerdì 8:30–12:30, martedì e giovedì anche 14:30–17:00."
            ),
            "found": False,
        }

    # Generate a deterministic-ish confirmation ID
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    confirmation_id = f"APT-{date.today().strftime('%Y%m%d')}-{suffix}"

    # Snap to a weekday if preferred_date falls on a weekend
    try:
        appt_date = date.fromisoformat(preferred_date)
    except ValueError:
        appt_date = date.today() + timedelta(days=7)

    while appt_date.weekday() >= 5:  # Saturday=5, Sunday=6
        appt_date += timedelta(days=1)

    # Assign a morning slot
    time_slot = "09:30"

    return {
        "confirmation_id": confirmation_id,
        "service": svc_info["service"],
        "citizen_name": citizen_name,
        "date": appt_date.isoformat(),
        "time": time_slot,
        "office": svc_info["office"],
        "instructions": (
            f"Appuntamento confermato per {citizen_name}. "
            f"Presentarsi presso {svc_info['office']} il {appt_date.strftime('%d/%m/%Y')} alle {time_slot}. "
            "Portare tutti i documenti richiesti per il servizio. "
            "In caso di impossibilità, cancellare l'appuntamento almeno 24 ore prima."
        ),
        "found": True,
    }
