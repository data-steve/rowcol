import pytest
from domains.ap.services.vendor_normalization import VendorNormalizationService
from domains.ap.schemas.vendor_canonical import VendorCanonical

def test_normalize_vendor(db):
    service = VendorNormalizationService(db)
    vendor = service.normalize_vendor("Starbucks1234", "550e8400-e29b-41d4-a716-446655440000")
    assert vendor.canonical_name == "Starbucks"
    assert vendor.confidence > 0
