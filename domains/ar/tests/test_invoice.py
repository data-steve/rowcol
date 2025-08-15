import pytest
from domains.ar.services.invoice import InvoiceService
from domains.ar.models.invoice import Invoice as InvoiceModel
from datetime import datetime, timedelta

def test_create_invoice(mock_qbo, db, test_firm, test_client, test_customer):
    service = InvoiceService(db)
    invoice = service.create_invoice(
        test_firm.firm_id, test_customer.customer_id, datetime.utcnow(),
        datetime.utcnow() + timedelta(days=30), 500.0, [{"item": "Service", "amount": 500.0}]
    )
    assert invoice.firm_id == test_firm.firm_id
    assert invoice.total == 500.0
    assert invoice.status in ["draft", "review"]

def test_create_invoice_endpoint(mock_qbo, client, test_firm, test_client, test_customer):
    response = client.post(
        f"/api/ar/invoices?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={
            "customer_id": test_customer.customer_id,
            "issue_date": datetime.utcnow().isoformat(),
            "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "total": 500.0,
            "lines": [{"item": "Service", "amount": 500.0}]
        }
    )
    assert response.status_code == 200
    assert response.json()["total"] == 500.0