import pytest
from sqlalchemy.orm import Session
from database import get_db, Firm, User

@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()

def test_create_firm(db_session: Session):
    firm = Firm(name="Test Agency", qbo_tenant_id="test123", current_balance=6000.0)
    db_session.add(firm)
    db_session.commit()
    db_session.refresh(firm)
    assert firm.id is not None
    assert firm.current_balance == 6000.0
