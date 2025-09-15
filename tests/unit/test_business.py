import pytest
from sqlalchemy.orm import Session
from domains.core.models.business import Business

def test_create_business(db: Session):
    business = Business(
        client_id=1,
        name="Test Agency",
        qbo_id="test123",
        industry="agency"
    )
    db.add(business)
    db.commit()
    result = db.query(Business).filter_by(client_id=1).first()
    assert result.name == "Test Agency"
    assert result.qbo_id == "test123"
    assert result.industry == "agency"
