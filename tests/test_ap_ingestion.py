import pytest
from services.ap_ingestion import APIngestionService
from models.bill import Bill as BillModel
from unittest.mock import patch, MagicMock

def test_sync_bills(db, test_firm, test_client):
    service = APIngestionService(db)
    # Test with no QBO client configured (should return error)
    result = service.sync_bills(test_firm.firm_id, test_client.client_id)
    assert result["status"] == "error"
    assert "QBO client not configured" in result["message"]

def test_ingest_document(db, test_firm, test_client):
    service = APIngestionService(db)
    bill = service.ingest_document("mock_invoice.pdf", test_firm.firm_id, test_client.client_id)
    assert bill.firm_id == test_firm.firm_id
    assert bill.client_id == test_client.client_id
    assert bill.status == "pending"
    assert bill.extracted_fields is not None

def test_sync_bills_endpoint(client, test_firm, test_client):
    response = client.post(
        f"/api/ingest/ap/bills?firm_id={test_firm.firm_id}&client_id={test_client.client_id}"
    )
    # The endpoint should work but return an error status since QBO is not configured
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "error"
    assert "QBO client not configured" in response_data["message"]