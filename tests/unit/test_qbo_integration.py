import pytest
from sqlalchemy.orm import Session
from domains.integrations.qbo_integration import QBOIntegration
from domains.core.models.business import Business

@pytest.fixture
def mock_business(db: Session):
    business = Business(client_id=1, name="Test Agency", qbo_id="test123")
    db.add(business)
    db.commit()
    return business

def test_fetch_balances(db: Session, mock_business):
    qbo = QBOIntegration(mock_business)
    qbo.fetch_balances(db)
    balances = db.query(Balance).filter_by(business_id=1).all()
    assert len(balances) == 2
    assert balances[0].qbo_account_id == "123"
    assert balances[0].current_balance == 6000.0
