import pytest
from sqlalchemy.orm import Session
from runway.services.onboarding import qualify_onboarding
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog

def test_qualify_dropoff(db: Session):
    result = qualify_onboarding("test@example.com", weekly_review=False, db=db)
    assert result["dropoff"] is True

def test_qualify_success(db: Session):
    result = qualify_onboarding("owner@test.com", weekly_review=True, db=db)
    assert result["success"] is True
    assert "business_id" in result
    business = db.query(Business).first()
    assert business.name == "owner Agency"
    audit = db.query(AuditLog).first()
    assert audit.action_type == "onboard_qualify"
