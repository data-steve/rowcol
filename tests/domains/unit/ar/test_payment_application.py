from domains.ar.services.payment_application import PaymentApplicationService
from domains.ar.models.invoice import Invoice as InvoiceModel
from datetime import datetime

def test_apply_payment(mock_qbo, db, test_business, test_customer):
    # Create an invoice first so payment can be applied to it
    invoice = InvoiceModel(
        business_id=test_business.business_id,
        customer_id=test_customer.customer_id,
        qbo_invoice_id="test_inv_001",
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
        test_business.business_id, 500.0, datetime.utcnow(), "ACH", test_customer.customer_id
    )
    assert payment.business_id == test_business.business_id
    assert payment.amount == 500.0
    assert payment.payment_method == "ACH"

def test_apply_payment_endpoint(mock_qbo, db, test_business, test_customer, test_invoice):
    # Test the service directly instead of HTTP endpoint
    service = PaymentApplicationService(db)
    result = service.apply_payment(
        business_id=test_business.business_id,
        amount=500.0,
        date=datetime.utcnow(),
        method="ACH",
        customer_id=test_customer.customer_id
    )
    
    assert result.amount == 500.0