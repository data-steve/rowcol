import pytest
from sqlalchemy.orm import Session
from domains.integrations.qbo_integration import QBOIntegration
from domains.core.models.business import Business

def test_fetch_balances(db: Session, test_business):
    qbo = QBOIntegration(test_business)
    qbo.fetch_balances(db)
    balances = db.query(Balance).filter_by(business_id=test_business.client_id).all()
    assert len(balances) == 2
    assert balances[0].qbo_account_id == "123"
    assert balances[0].current_balance == 6000.0
