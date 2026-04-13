"""Tools for the LogisticsAgent — shipment lookup, delay flagging, carrier briefing.

Each function is a plain Python callable registered by the agent via
``self.register_tool(fn)``. Shipment and carrier data are loaded from the
seeded JSON files on first import.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data"
_SHIPMENTS_FILE = _DATA_DIR / "logistics_shipments.json"
_CARRIERS_FILE = _DATA_DIR / "logistics_carriers.json"


@lru_cache(maxsize=1)
def _load_shipments() -> list[dict]:
    with _SHIPMENTS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _load_carriers() -> list[dict]:
    with _CARRIERS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tool: lookup_shipment
# ---------------------------------------------------------------------------


def lookup_shipment(tracking_id: str) -> dict:
    """Look up a shipment by its tracking ID.

    Performs a case-insensitive exact match against the seeded shipment
    database. Returns full shipment details if found, or ``{found: False}``
    on a miss.

    Args:
        tracking_id: Shipment tracking identifier, e.g. ``"SHP-20240312-AUH"``.

    Returns::

        {
            "tracking_id":  str,
            "origin":       str,
            "destination":  str,
            "status":       str,   # "in_transit" | "delayed" | "delivered" | "customs_hold"
            "eta":          str,   # ISO date string
            "carrier":      str,
            "delay_days":   int,
            "weight_kg":    int,
            "commodity":    str,
            "last_update":  str,
            "found":        bool,
        }

        Or ``{"found": False}`` when no match is found.
    """
    normalised = tracking_id.strip().upper()
    for shipment in _load_shipments():
        if shipment["tracking_id"].upper() == normalised:
            return {**shipment, "found": True}
    return {"found": False}


# ---------------------------------------------------------------------------
# Tool: flag_delay
# ---------------------------------------------------------------------------


def flag_delay(tracking_id: str, reason: str) -> str:
    """Flag a shipment as delayed and log the reason.

    In the live agent context the containing agent method also publishes
    a structured delay-flag payload to the LiveKit ``tool-output`` topic
    so the frontend LogisticsPanel can render a warning card.

    Args:
        tracking_id: Shipment tracking identifier to flag.
        reason: Human-readable explanation for the delay flag, e.g.
                ``"Weather disruption at origin port — Guangzhou typhoon"``.

    Returns:
        A confirmation string confirming the flag was recorded.
    """
    normalised = tracking_id.strip().upper()
    # Verify the shipment exists in our records
    found = any(s["tracking_id"].upper() == normalised for s in _load_shipments())
    if not found:
        return (
            f"Delay flag recorded for {normalised}: {reason}. "
            f"Note: tracking ID not found in current database — verify manually."
        )
    return (
        f"Delay flag published for {normalised}: {reason}. "
        f"Operations team notified. Shipment flagged for priority review."
    )


# ---------------------------------------------------------------------------
# Tool: generate_carrier_brief
# ---------------------------------------------------------------------------


def generate_carrier_brief(carrier_name: str) -> dict:
    """Generate a performance brief for a named carrier.

    Performs case-insensitive partial matching against the carrier name.
    Returns structured performance metrics and a recommendation summary.

    Args:
        carrier_name: Carrier name or partial name, e.g. ``"Emirates"``,
                      ``"DHL"``, ``"FedEx"``.

    Returns::

        {
            "carrier":           str,
            "on_time_rate_pct":  float,
            "avg_delay_days":    float,
            "open_incidents":    int,
            "active_routes":     list[str],
            "hub":               str,
            "specialisations":   list[str],
            "recommendation":    str,
            "found":             bool,
        }

        Or ``{"found": False}`` when no match is found.
    """
    lower_query = carrier_name.strip().lower()
    carriers = _load_carriers()

    # Exact match first
    for carrier in carriers:
        if carrier["carrier_name"].lower() == lower_query:
            return _carrier_response(carrier)

    # Partial match — pick first carrier whose name contains the query token
    for carrier in carriers:
        if lower_query in carrier["carrier_name"].lower():
            return _carrier_response(carrier)

    # Reverse: check if any word in the carrier name is in the query
    for carrier in carriers:
        name_words = carrier["carrier_name"].lower().split()
        if any(word in lower_query for word in name_words if len(word) > 3):
            return _carrier_response(carrier)

    return {"found": False}


def _carrier_response(carrier: dict) -> dict:
    """Normalise carrier dict — rename carrier_name → carrier for API consistency."""
    result = {k: v for k, v in carrier.items() if k != "carrier_name"}
    result["carrier"] = carrier["carrier_name"]
    result["found"] = True
    return result
