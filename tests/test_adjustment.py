import pytest
from services.adjustment import AdjustmentService
from models.credit_memo import CreditMemo as CreditMemoModel

def test_create_credit_memo(mock_qbo, db, test_firm, test_client, test_invoice):
    service = AdjustmentService(db)
    credit_memo = service.create_credit_memo(test_firm.firm_id, test_invoice.invoice_id, 100.0, "Discount")
    assert credit_memo.firm_id == test_firm.firm_id
    assert credit_memo.amount == 100.0
    assert credit_memo.status == "applied"  # Amount < 1000 gets "applied" status

def test_create_credit_memo_review_status(mock_qbo, db, test_firm, test_client, test_invoice):
    service = AdjustmentService(db)
    credit_memo = service.create_credit_memo(test_firm.firm_id, test_invoice.invoice_id, 1500.0, "Major Discount")
    assert credit_memo.firm_id == test_firm.firm_id
    assert credit_memo.amount == 1500.0
    assert credit_memo.status == "review"  # Amount > 1000 gets "review" status

def test_create_credit_memo_endpoint(mock_qbo, client, test_firm, test_client, test_invoice):
    response = client.post(
        f"/api/ar/credits?firm_id={test_firm.firm_id}&client_id={test_client.client_id}",
        json={"invoice_id": test_invoice.invoice_id, "amount": 100.0, "reason": "Discount"}
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 100.0