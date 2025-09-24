from domains.ar.services.invoice import InvoiceService
from datetime import datetime, timedelta

def test_create_invoice(mock_qbo, db, test_business, test_customer):
    service = InvoiceService(db, test_business.business_id)
    invoice = service.create_invoice(
        test_business.business_id, test_customer.customer_id, datetime.utcnow(),
        datetime.utcnow() + timedelta(days=30), 500.0, [{"item": "Service", "amount": 500.0}]
    )
    assert invoice.business_id == test_business.business_id
    assert invoice.total == 500.0
    assert invoice.status in ["draft", "review"]
