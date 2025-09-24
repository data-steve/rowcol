import pytest
from unittest.mock import MagicMock
from domains.vendor_normalization.services.normalization import VendorNormalizationService
from domains.vendor_normalization.models import VendorCanonical as VendorCanonicalModel

@pytest.fixture
def mock_db_session():
    """Provides a mock SQLAlchemy session."""
    db = MagicMock()
    # Default mock for a vendor that doesn't exist
    db.query.return_value.filter.return_value.first.return_value = None
    return db

def test_normalize_vendor_new(mock_db_session):
    """Test creating a new canonical vendor when none exists."""
    service = VendorNormalizationService(mock_db_session)
    
    vendor = service.normalize_vendor("New Vendor Name 123", "test_business_id")
    
    assert vendor.canonical_name == "New Vendor Name 123"
    assert vendor.business_id == "test_business_id"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_normalize_vendor_existing(mock_db_session):
    """Test retrieving and updating an existing canonical vendor."""
    # Setup the mock to return an existing vendor
    existing_vendor = VendorCanonicalModel(
        id=1, 
        raw_name="Existing Vendor", 
        canonical_name="Existing Vendor", 
        business_id="test_business_id"
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_vendor
    
    service = VendorNormalizationService(mock_db_session)
    
    vendor = service.normalize_vendor("Existing Vendor", "test_business_id")
    
    assert vendor.id == 1
    assert vendor.canonical_name == "Existing Vendor"
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_called_once() # Commit happens on update
