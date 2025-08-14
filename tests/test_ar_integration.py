import pytest
from datetime import datetime, timedelta

def test_ar_workflow(mock_qbo, client, test_firm, test_client, test_customer, test_invoice):
    # Create invoice
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

    # Send reminder
    response = client.post(
        f"/api/ar/collections/remind?firm_id={test_firm.firm_id}&invoice_id={test_invoice.invoice_id}"
    )
    assert response.status_code == 200