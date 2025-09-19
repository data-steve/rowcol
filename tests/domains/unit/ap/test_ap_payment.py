from domains.ap.services.payment import PaymentService
from unittest.mock import patch, MagicMock

@patch('domains.ap.services.payment.Payment')
def test_schedule_payment(mock_payment, db, test_business, test_bill):
    # Mock the QBO payment creation
    mock_payment_instance = MagicMock()
    mock_payment.return_value = mock_payment_instance
    
    service = PaymentService(db, test_business.business_id)
    payment = service.schedule_payment(test_business.business_id, [test_bill.bill_id], "1000-Cash")
    assert payment["business_id"] == test_business.business_id
    assert payment["bill_ids"] == [test_bill.bill_id]

@patch('domains.ap.services.payment.Payment')
def test_schedule_payment_endpoint(mock_payment, client, test_business, test_bill):
    # Mock the QBO payment creation
    mock_payment_instance = MagicMock()
    mock_payment.return_value = mock_payment_instance
    
    response = client.post(
        f"/api/ingest/ap/payments?business_id={test_business.business_id}",
        json={"bill_ids": [test_bill.bill_id], "funding_account": "1000-Cash"}
    )
    assert response.status_code == 200
    assert response.json()["bill_ids"] == [test_bill.bill_id]