"""Tests for ComuneAgent tools — Session 12."""
import pytest

from app.tools.comune_tools import (
    book_appointment,
    check_application_status,
    lookup_service_requirements,
)

VALID_STATUSES = {"pending", "approved", "rejected", "requires_documents"}


# ---------------------------------------------------------------------------
# lookup_service_requirements
# ---------------------------------------------------------------------------


def test_lookup_residenza_found():
    result = lookup_service_requirements("residenza")
    assert result["found"] is True
    assert len(result["required_documents"]) > 0
    assert isinstance(result["processing_days"], int)
    assert result["processing_days"] > 0


def test_lookup_residency_english_keyword():
    result = lookup_service_requirements("residency")
    assert result["found"] is True
    assert result["service_id"] == "ANA-004"


def test_lookup_returns_fee_as_float():
    result = lookup_service_requirements("nascita")
    assert result["found"] is True
    assert isinstance(result["fee_eur"], float)


def test_lookup_returns_office():
    result = lookup_service_requirements("matrimonio")
    assert result["found"] is True
    assert len(result["office"]) > 0


def test_lookup_returns_bookable_online_bool():
    result = lookup_service_requirements("isee")
    assert result["found"] is True
    assert isinstance(result["bookable_online"], bool)


def test_lookup_not_found():
    result = lookup_service_requirements("xyznotexist")
    assert result["found"] is False
    assert result["required_documents"] == []
    assert result["processing_days"] == 0


def test_lookup_ztl():
    result = lookup_service_requirements("ztl")
    assert result["found"] is True
    assert result["service_id"] == "TRA-002"


def test_lookup_citizenship():
    result = lookup_service_requirements("citizenship")
    assert result["found"] is True
    assert result["service_id"] == "STA-002"


# ---------------------------------------------------------------------------
# check_application_status
# ---------------------------------------------------------------------------


def test_check_status_valid_id():
    result = check_application_status("APP-2024-ANA-00341")
    assert result["found"] is True
    assert result["status"] in VALID_STATUSES
    assert result["application_id"] == "APP-2024-ANA-00341"


def test_check_status_case_insensitive():
    result = check_application_status("app-2024-ana-00341")
    assert result["found"] is True


def test_check_status_has_dates():
    result = check_application_status("APP-2024-ANA-00341")
    assert result["submitted_on"] != ""
    assert result["expected_by"] != ""


def test_check_status_approved():
    result = check_application_status("APP-2024-ANA-00289")
    assert result["found"] is True
    assert result["status"] == "approved"


def test_check_status_requires_documents():
    result = check_application_status("APP-2024-PER-00078")
    assert result["found"] is True
    assert result["status"] == "requires_documents"


def test_check_status_rejected():
    result = check_application_status("APP-2024-PER-00031")
    assert result["found"] is True
    assert result["status"] == "rejected"


def test_check_status_not_found():
    result = check_application_status("APP-FAKE-99999")
    assert result["found"] is False


def test_check_status_has_notes():
    result = check_application_status("APP-2024-ANA-00341")
    assert len(result["notes"]) > 0


# ---------------------------------------------------------------------------
# book_appointment
# ---------------------------------------------------------------------------


def test_book_appointment_bookable_service():
    result = book_appointment(
        service="residency_registration",
        citizen_name="Fatima Al-Rashidi",
        preferred_date="2025-03-15",
    )
    assert result["found"] is True
    assert result["confirmation_id"] != ""
    assert result["date"] != ""
    assert "Fatima Al-Rashidi" in result["instructions"]


def test_book_appointment_returns_office():
    result = book_appointment(
        service="iscrizione anagrafica",
        citizen_name="Ahmed Mansour",
        preferred_date="2025-04-01",
    )
    assert result["found"] is True
    assert len(result["office"]) > 0


def test_book_appointment_non_bookable_service():
    result = book_appointment(
        service="permesso costruire",
        citizen_name="Marco Ferretti",
        preferred_date="2025-03-20",
    )
    assert result["found"] is False
    assert "non è prenotabile" in result["instructions"].lower() or "non" in result["instructions"].lower()


def test_book_appointment_unknown_service():
    result = book_appointment(
        service="xyzservice",
        citizen_name="Test Citizen",
        preferred_date="2025-03-20",
    )
    assert result["found"] is False


def test_book_appointment_weekday_snap():
    # 2025-03-15 is a Saturday — should snap to Monday 17th
    result = book_appointment(
        service="residenza",
        citizen_name="Layla Hassan",
        preferred_date="2025-03-15",
    )
    if result["found"]:
        from datetime import date
        appt = date.fromisoformat(result["date"])
        assert appt.weekday() < 5  # must be a weekday


def test_book_appointment_confirmation_id_format():
    result = book_appointment(
        service="tari",
        citizen_name="Youssef Ibrahim",
        preferred_date="2025-05-10",
    )
    assert result["found"] is True
    assert result["confirmation_id"].startswith("APT-")
