import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from db.session import get_db, SessionLocal
from domains.core.models.business import Business
from domains.core.models.user import User

@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()

def test_db_connection():
    db = SessionLocal()

def test_create_business(db_session: Session):
    business = Business(business_id="biz_123", name="Test Agency", qbo_id="test123")
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    assert business.name == "Test Agency"

def test_create_user(db_session: Session):
    business = Business(business_id="biz_456", name="Another Agency", qbo_id="test456")
    db_session.add(business)
    db_session.commit()

    user = User(
        user_id="user_123",
        business_id=business.business_id,
        email="test@oodaloo.com",
        hashed_password="abc"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.email == "test@oodaloo.com"
    assert user.business.name == "Another Agency"
