import pytest
from domains.ap.services.vendor_mastering import VendorMasteringService
from domains.ap.models.vendor import Vendor as VendorModel
from unittest.mock import patch, MagicMock

@patch('domains.ap.services.vendor_mastering.QBOVendor')
def test_sync_vendors(mock_qbo_vendor, db, test_firm, test_client):
    # Mock QBO vendor to return empty list
    mock_qbo_vendor.filter.return_value = []
    
    service = VendorMasteringService(db)
    vendors = service.sync_vendors(test_firm.firm_id, test_client.client_id)
    assert len(vendors) == 0

def test_vendor_endpoint(client, test_firm, test_vendor):
    response = client.get(f"/api/ingest/ap/vendors/{test_vendor.vendor_id}?firm_id={test_firm.firm_id}")
    assert response.status_code == 200
    assert response.json()["vendor_id"] == test_vendor.vendor_id