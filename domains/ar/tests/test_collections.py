import pytest
from domains.ar.services.collections import CollectionsService
from domains.ar.models.invoice import Invoice as InvoiceModel
from datetime import datetime, timedelta

def test_send_reminder(db, test_firm, test_client, test_invoice):
    test_invoice.due_date = datetime.utcnow() - timedelta(days=1)  # Make overdue
    db.commit()
    service = CollectionsService(db)
    invoice = service.send_reminder(test_firm.firm_id, test_invoice.invoice_id)
    assert invoice.status == "review"
    assert invoice.firm_id == test_firm.firm_id

def test_send_reminder_endpoint(client, test_firm, test_client, test_invoice, db):
    test_invoice.due_date = datetime.utcnow() - timedelta(days=1)
    db.commit()
    response = client.post(
        f"/api/ar/collections/remind?firm_id={test_firm.firm_id}&invoice_id={test_invoice.invoice_id}"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "review"