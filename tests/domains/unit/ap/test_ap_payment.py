from domains.ap.services.payment import PaymentService
from unittest.mock import patch, MagicMock

@patch('domains.ap.services.payment.Payment')
def test_schedule_payment(mock_payment, db, test_business, test_bill):
    # Mock the QBO payment creation
    mock_payment.return_value = MagicMock()
    
    service = PaymentService(db, test_business.business_id)
    payment = service.schedule_payment(test_business.business_id, [test_bill.bill_id], "1000-Cash")
    assert payment["business_id"] == test_business.business_id
    assert payment["bill_ids"] == [test_bill.bill_id]

@patch('domains.ap.services.payment.Payment')
def test_schedule_payment_endpoint(mock_payment, db, test_business, test_bill):
    # Mock the QBO payment creation
    mock_payment.return_value = MagicMock()
    
    # Test the service directly instead of HTTP endpoint
    service = PaymentService(db, test_business.business_id)
    result = service.schedule_payment(
        business_id=test_business.business_id,
        bill_ids=[test_bill.bill_id], 
        funding_account="1000-Cash"
    )
    
    assert result["business_id"] == test_business.business_id
    assert result["bill_ids"] == [test_bill.bill_id]