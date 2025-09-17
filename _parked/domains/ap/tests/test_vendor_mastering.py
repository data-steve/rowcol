import pytest
from unittest.mock import patch, MagicMock
from domains.ap.services.vendor_mastering import VendorMasteringService
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel
from domains.ap.models.vendor import Vendor as VendorModel

@pytest.fixture
def mock_db_session():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db

def test_get_or_create_vendor_new(mock_db_session):
    service = VendorMasteringService(mock_db_session)
    
    # Mock the canonical vendor that would be passed in
    mock_canonical_vendor = VendorCanonicalModel(id=1, name="Canonical Vendor")
    
    # Call the service
    vendor, created = service.get_or_create_vendor(mock_canonical_vendor, "test_business_id")
    
    # Assertions for a new vendor
    assert created is True
    assert vendor.canonical_vendor_id == 1
    assert vendor.business_id == "test_business_id"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_or_create_vendor_existing(mock_db_session):
    # Setup mock to return an existing vendor
    existing_vendor = VendorModel(id=10, canonical_vendor_id=1, business_id="test_business_id")
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_vendor

    service = VendorMasteringService(mock_db_session)
    
    # Mock the canonical vendor
    mock_canonical_vendor = VendorCanonicalModel(id=1, name="Canonical Vendor")
    
    # Call the service
    vendor, created = service.get_or_create_vendor(mock_canonical_vendor, "test_business_id")
    
    # Assertions for an existing vendor
    assert created is False
    assert vendor.id == 10
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()