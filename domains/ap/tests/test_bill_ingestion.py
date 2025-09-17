import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from domains.ap.services import ingest
from domains.ap.models.bill import Bill as BillModel

client = TestClient(app)

def test_ingest_bill(db, test_business):
    # Mocking the QBO bill object
    mock_qbo_bill = MagicMock()
    mock_qbo_bill.Id = "qbo123"
    mock_qbo_bill.VendorRef.name = "Test Vendor"
    mock_qbo_bill.TotalAmt = 150.00
    mock_qbo_bill.DueDate = "2025-01-01"
    mock_qbo_bill.to_json.return_value = {
        "Id": "qbo123",
        "VendorRef": {"name": "Test Vendor"},
        "TotalAmt": 150.00,
        "DueDate": "2025-01-01"
    }

    # Mocking the vendor normalization service
    with patch('domains.ap.services.ingest.VendorNormalizationService') as mock_vendor_service:
        mock_vendor_instance = mock_vendor_service.return_value
        mock_vendor_instance.get_or_create.return_value = MagicMock(id=1) # Mock canonical vendor

        ingest_service = ingest.IngestionService(db)
        bill = ingest_service.ingest_bill(mock_qbo_bill, test_business.business_id)
        
        assert bill is not None
        assert bill.qbo_bill_id == "qbo123"
        assert bill.amount == 150.00
        assert bill.vendor_id == 1
        
        # Verify it's in the DB
        retrieved_bill = db.query(BillModel).filter(BillModel.qbo_bill_id == "qbo123").first()
        assert retrieved_bill is not None
        assert retrieved_bill.amount == 150.00