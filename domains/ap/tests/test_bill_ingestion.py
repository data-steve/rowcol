import pytest
from fastapi.testclient import TestClient
from main import app
from domains.ap.services.bill_ingestion import BillIngestionService
from domains.ap.models.bill import Bill as BillModel

client = TestClient(app)

def test_ingest_bill(db, test_firm, test_client):
    service = BillIngestionService(db)
    bill = service.ingest_bill("mock_invoice.pdf", test_firm.firm_id, test_client.client_id)
    assert bill.firm_id == test_firm.firm_id
    assert bill.status in ["pending", "review"]
    assert bill.extracted_fields is not None

def test_upload_bill_endpoint(test_firm, test_client):
    response = client.post(
        f"/api/ingest/ap/bills/upload?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={"file_path": "mock_invoice.pdf"}
    )
    assert response.status_code == 200
    assert response.json()["extracted_fields"] is not None