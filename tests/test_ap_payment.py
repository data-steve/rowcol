import pytest
from services.ap_payment import APPaymentService
from models.bill import Bill as BillModel
from unittest.mock import patch, MagicMock

@patch('services.ap_payment.Payment')
def test_schedule_payment(mock_payment, db, test_firm, test_client, test_bill):
    # Mock the QBO payment creation
    mock_payment_instance = MagicMock()
    mock_payment.return_value = mock_payment_instance
    
    service = APPaymentService(db)
    payment = service.schedule_payment(test_firm.firm_id, [test_bill.bill_id], "1000-Cash", test_client.client_id)
    assert payment.firm_id == test_firm.firm_id
    assert payment.bill_ids == [test_bill.bill_id]

@patch('services.ap_payment.Payment')
def test_schedule_payment_endpoint(mock_payment, client, test_firm, test_client, test_bill):
    # Mock the QBO payment creation
    mock_payment_instance = MagicMock()
    mock_payment.return_value = mock_payment_instance
    
    response = client.post(
        f"/api/ingest/ap/payments?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={"bill_ids": [test_bill.bill_id], "funding_account": "1000-Cash"}
    )
    assert response.status_code == 200
    assert response.json()["bill_ids"] == [test_bill.bill_id]