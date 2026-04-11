"""Tests for seeded comune data files — Session 12."""
import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.parent / "app" / "data"

REQUIRED_SERVICE_FIELDS = {
    "service_id",
    "name",
    "keywords",
    "required_documents",
    "processing_days",
    "fee_eur",
    "office",
    "bookable_online",
    "notes",
}

REQUIRED_APPLICATION_FIELDS = {
    "application_id",
    "service",
    "service_id",
    "status",
    "submitted_on",
    "expected_by",
    "notes",
}

VALID_STATUSES = {"pending", "approved", "rejected", "requires_documents"}


@pytest.fixture(scope="module")
def services():
    with open(DATA_DIR / "comune_services.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def applications():
    with open(DATA_DIR / "comune_applications.json", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Services data
# ---------------------------------------------------------------------------


def test_exactly_15_services(services):
    assert len(services) == 15


def test_services_have_required_fields(services):
    for svc in services:
        missing = REQUIRED_SERVICE_FIELDS - svc.keys()
        assert not missing, f"Service {svc.get('service_id')} missing: {missing}"


def test_service_ids_are_unique(services):
    ids = [svc["service_id"] for svc in services]
    assert len(ids) == len(set(ids))


def test_service_required_documents_non_empty(services):
    for svc in services:
        assert len(svc["required_documents"]) > 0, (
            f"Service {svc['service_id']} has no required_documents"
        )


def test_service_keywords_non_empty(services):
    for svc in services:
        assert len(svc["keywords"]) > 0, (
            f"Service {svc['service_id']} has no keywords"
        )


def test_service_bookable_online_is_bool(services):
    for svc in services:
        assert isinstance(svc["bookable_online"], bool), (
            f"Service {svc['service_id']} bookable_online is not bool"
        )


def test_service_processing_days_positive(services):
    for svc in services:
        assert isinstance(svc["processing_days"], int)
        assert svc["processing_days"] >= 0


def test_service_fee_eur_is_number(services):
    for svc in services:
        assert isinstance(svc["fee_eur"], (int, float))
        assert svc["fee_eur"] >= 0


def test_service_notes_non_empty(services):
    for svc in services:
        assert len(svc["notes"]) > 0, (
            f"Service {svc['service_id']} has empty notes"
        )


# ---------------------------------------------------------------------------
# Applications data
# ---------------------------------------------------------------------------


def test_exactly_12_applications(applications):
    assert len(applications) == 12


def test_applications_have_required_fields(applications):
    for app in applications:
        missing = REQUIRED_APPLICATION_FIELDS - app.keys()
        assert not missing, f"Application {app.get('application_id')} missing: {missing}"


def test_application_ids_are_unique(applications):
    ids = [app["application_id"] for app in applications]
    assert len(ids) == len(set(ids))


def test_application_statuses_valid(applications):
    for app in applications:
        assert app["status"] in VALID_STATUSES, (
            f"Application {app['application_id']} has invalid status: {app['status']}"
        )


def test_all_four_statuses_represented(applications):
    statuses = {app["status"] for app in applications}
    assert statuses == VALID_STATUSES, (
        f"Not all statuses represented. Found: {statuses}"
    )


def test_application_ids_follow_format(applications):
    for app in applications:
        app_id = app["application_id"]
        assert app_id.startswith("APP-"), f"ID {app_id!r} doesn't start with APP-"
        parts = app_id.split("-")
        assert len(parts) >= 4, f"ID {app_id!r} doesn't have enough segments"


def test_application_notes_non_empty(applications):
    for app in applications:
        assert len(app["notes"]) > 0, (
            f"Application {app['application_id']} has empty notes"
        )


def test_application_dates_non_empty(applications):
    for app in applications:
        assert app["submitted_on"] != "", (
            f"Application {app['application_id']} has empty submitted_on"
        )
        assert app["expected_by"] != "", (
            f"Application {app['application_id']} has empty expected_by"
        )
