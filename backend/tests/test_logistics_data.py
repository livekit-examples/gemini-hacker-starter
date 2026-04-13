"""Tests for logistics data files — Session 18.

Verifies:
- 15 shipments, 5 carriers with required fields
- No "Acme Corp" placeholder names
- Status values are valid
- Carrier metrics are in sensible ranges
"""
import json
from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).parent.parent / "app" / "data"
_SHIPMENTS_FILE = _DATA_DIR / "logistics_shipments.json"
_CARRIERS_FILE = _DATA_DIR / "logistics_carriers.json"

VALID_STATUSES = {"in_transit", "delayed", "delivered", "customs_hold"}


@pytest.fixture(scope="module")
def shipments() -> list[dict]:
    with _SHIPMENTS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def carriers() -> list[dict]:
    with _CARRIERS_FILE.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Shipments
# ---------------------------------------------------------------------------


def test_shipments_file_exists():
    assert _SHIPMENTS_FILE.exists()


def test_shipments_has_exactly_15_entries(shipments):
    assert len(shipments) == 15, f"Expected 15 shipments, got {len(shipments)}"


def test_all_shipments_have_tracking_id(shipments):
    for s in shipments:
        assert "tracking_id" in s
        assert isinstance(s["tracking_id"], str)
        assert s["tracking_id"].startswith("SHP-")


def test_all_shipments_have_origin(shipments):
    for s in shipments:
        assert "origin" in s
        assert len(s["origin"]) > 0


def test_all_shipments_have_destination(shipments):
    for s in shipments:
        assert "destination" in s
        assert len(s["destination"]) > 0


def test_all_shipments_have_valid_status(shipments):
    for s in shipments:
        assert s["status"] in VALID_STATUSES, f"Invalid status: {s['status']}"


def test_all_shipments_have_eta(shipments):
    for s in shipments:
        assert "eta" in s
        assert isinstance(s["eta"], str)
        assert len(s["eta"]) > 0


def test_all_shipments_have_carrier(shipments):
    for s in shipments:
        assert "carrier" in s
        assert len(s["carrier"]) > 0


def test_all_shipments_have_delay_days(shipments):
    for s in shipments:
        assert "delay_days" in s
        assert isinstance(s["delay_days"], int)
        assert s["delay_days"] >= 0


def test_tracking_ids_are_unique(shipments):
    ids = [s["tracking_id"] for s in shipments]
    assert len(ids) == len(set(ids)), "Duplicate tracking IDs found"


def test_no_acme_corp_in_shipments(shipments):
    all_text = json.dumps(shipments).lower()
    assert "acme" not in all_text, "Placeholder 'Acme' name found in shipments data"


def test_delayed_shipments_have_positive_delay(shipments):
    for s in shipments:
        if s["status"] == "delayed":
            assert s["delay_days"] > 0, f"Delayed shipment has 0 delay_days: {s['tracking_id']}"


def test_delivered_shipments_have_zero_delay(shipments):
    for s in shipments:
        if s["status"] == "delivered":
            assert s["delay_days"] == 0, f"Delivered shipment has non-zero delay: {s['tracking_id']}"


def test_mix_of_statuses_present(shipments):
    statuses = {s["status"] for s in shipments}
    assert len(statuses) >= 3, "Data should cover at least 3 different status types"


# ---------------------------------------------------------------------------
# Carriers
# ---------------------------------------------------------------------------


def test_carriers_file_exists():
    assert _CARRIERS_FILE.exists()


def test_carriers_has_exactly_5_entries(carriers):
    assert len(carriers) == 5, f"Expected 5 carriers, got {len(carriers)}"


def test_all_carriers_have_name(carriers):
    for c in carriers:
        assert "carrier_name" in c
        assert len(c["carrier_name"]) > 0


def test_all_carriers_have_on_time_rate(carriers):
    for c in carriers:
        assert "on_time_rate_pct" in c
        assert isinstance(c["on_time_rate_pct"], (int, float))
        assert 0 <= c["on_time_rate_pct"] <= 100


def test_all_carriers_have_avg_delay(carriers):
    for c in carriers:
        assert "avg_delay_days" in c
        assert isinstance(c["avg_delay_days"], (int, float))
        assert c["avg_delay_days"] >= 0


def test_all_carriers_have_open_incidents(carriers):
    for c in carriers:
        assert "open_incidents" in c
        assert isinstance(c["open_incidents"], int)
        assert c["open_incidents"] >= 0


def test_all_carriers_have_recommendation(carriers):
    for c in carriers:
        assert "recommendation" in c
        assert isinstance(c["recommendation"], str)
        assert len(c["recommendation"]) >= 20


def test_carrier_names_are_unique(carriers):
    names = [c["carrier_name"] for c in carriers]
    assert len(names) == len(set(names)), "Duplicate carrier names found"


def test_no_acme_corp_in_carriers(carriers):
    all_text = json.dumps(carriers).lower()
    assert "acme" not in all_text, "Placeholder 'Acme' name found in carriers data"
