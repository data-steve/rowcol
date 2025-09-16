import pytest
from sqlalchemy.orm import Session
from domains.core.models.balance import Balance
from datetime import datetime

def test_create_balance(db: Session, test_business):
    balance = Balance(
        business_id=test_business.client_id,
        qbo_account_id="123",
        current_balance=6000.0,
        available_balance=5500.0,
        snapshot_date=datetime.utcnow(),
        account_type="checking"
    )
    db.add(balance)
    db.commit()
    result = db.query(Balance).filter_by(qbo_account_id="123").first()
    assert result.current_balance == 6000.0
    assert result.account_type == "checking"
