from __future__ import annotations

from datetime import date

from credibil.domain.accreditation.entities import (
    Accreditation,
    AccreditationCategory,
    AccreditationStatus,
)


class TestAccreditationCategory:
    def test_all_categories(self):
        assert len(AccreditationCategory) == 7
        assert AccreditationCategory.TESTING_LAB.value == "testing_lab"
        assert AccreditationCategory.CALIBRATION_LAB.value == "calibration_lab"
        assert AccreditationCategory.MEDICAL_LAB.value == "medical_lab"
        assert AccreditationCategory.PRODUCT_CERT_BODY.value == "product_cert_body"
        assert AccreditationCategory.ORGANIC_CERT_BODY.value == "organic_cert_body"
        assert (
            AccreditationCategory.MANAGEMENT_SYSTEM_CERT_BODY.value == "management_system_cert_body"
        )
        assert AccreditationCategory.INSPECTION_BODY.value == "inspection_body"


class TestAccreditationStatus:
    def test_all_statuses(self):
        assert AccreditationStatus.ACTIVE.value == "active"
        assert AccreditationStatus.SUSPENDED.value == "suspended"
        assert AccreditationStatus.SUSPENDED_PARTIAL.value == "suspended_partial"
        assert AccreditationStatus.WITHDRAWN.value == "withdrawn"


class TestAccreditation:
    def test_create_minimal(self):
        acc = Accreditation(
            organization_name="Test Lab",
            certificate_number="LI-001",
            category=AccreditationCategory.TESTING_LAB,
            standard="SM EN ISO/IEC 17025:2018",
        )
        assert acc.organization_name == "Test Lab"
        assert acc.certificate_number == "LI-001"
        assert acc.category == AccreditationCategory.TESTING_LAB
        assert acc.status == AccreditationStatus.ACTIVE
        assert acc.country_code == "MD"
        assert acc.id is not None

    def test_create_full(self):
        acc = Accreditation(
            organization_name="Test Lab SRL",
            director_name="Ion Popescu",
            address="str. Test 1, Chisinau",
            phone="+37322123456",
            fax="+37322123457",
            email="test@test.md",
            certificate_number="LI-004",
            category=AccreditationCategory.TESTING_LAB,
            standard="SM EN ISO/IEC 17025:2018",
            status=AccreditationStatus.ACTIVE,
            issue_date=date(2020, 1, 15),
            expiry_date=date(2025, 1, 15),
            scope="Testing of construction materials",
            certificate_url="https://acreditare.md/cert.pdf",
            annex_urls=[{"name": "Annex 1", "url": "https://acreditare.md/annex1.pdf"}],
            remarks="Some remarks",
            source_url="https://acreditare.md/laboratoare-de-incercari/",
        )
        assert acc.director_name == "Ion Popescu"
        assert acc.issue_date == date(2020, 1, 15)
        assert acc.expiry_date == date(2025, 1, 15)
        assert len(acc.annex_urls) == 1
        assert acc.certificate_url == "https://acreditare.md/cert.pdf"

    def test_update(self):
        acc = Accreditation(
            organization_name="Test Lab",
            certificate_number="LI-001",
            category=AccreditationCategory.TESTING_LAB,
            standard="SM EN ISO/IEC 17025:2018",
        )
        old_updated = acc.updated_at
        acc.update(status=AccreditationStatus.WITHDRAWN, remarks="Retras din 28.07.2025")
        assert acc.status == AccreditationStatus.WITHDRAWN
        assert acc.remarks == "Retras din 28.07.2025"
        assert acc.updated_at >= old_updated

    def test_repr(self):
        acc = Accreditation(
            organization_name="Test Laboratory SRL",
            certificate_number="LI-004",
            category=AccreditationCategory.TESTING_LAB,
            standard="SM EN ISO/IEC 17025:2018",
        )
        assert "LI-004" in repr(acc)
        assert "Test Laboratory" in repr(acc)

    def test_default_values(self):
        acc = Accreditation(
            organization_name="Test",
            certificate_number="LI-001",
            category=AccreditationCategory.TESTING_LAB,
            standard="SM EN ISO/IEC 17025:2018",
        )
        assert acc.annex_urls == []
        assert acc.raw_data == {}
        assert acc.last_synced is not None
        assert acc.created_at is not None
        assert acc.updated_at is not None
