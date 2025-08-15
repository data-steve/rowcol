import pytest
from domains.ar.services.payment_application import PaymentApplicationService
from domains.ap.models.payment import Payment as PaymentModel
from domains.ar.models.invoice import Invoice as InvoiceModel
from datetime import datetime

def test_apply_payment(mock_qbo, db, test_firm, test_client, test_customer):
    # Create an invoice first so payment can be applied to it
    invoice = InvoiceModel(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        customer_id=test_customer.customer_id,
        qbo_id="test_inv_001",
        issue_date=datetime.utcnow(),
        due_date=datetime.utcnow(),
        total=500.0,
        lines=[{"item": "Service", "amount": 500.0}],
        status="sent"
    )
    db.add(invoice)
    db.commit()
    
    service = PaymentApplicationService(db)
    payment = service.apply_payment(
        test_firm.firm_id, 500.0, datetime.utcnow(), "ACH", test_customer.customer_id
    )
    assert payment.firm_id == test_firm.firm_id
    assert payment.amount == 500.0
    assert payment.method == "ACH"

def test_apply_payment_endpoint(mock_qbo, client, test_firm, test_client, test_customer, test_invoice):
    response = client.post(
        f"/api/ar/payments/apply?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={
            "customer_id": test_customer.customer_id,
            "amount": 500.0,
            "date": datetime.utcnow().isoformat(),
            "method": "ACH"
        }
    )
    assert response.status_code == 200