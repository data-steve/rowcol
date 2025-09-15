import pytest
from runway.services.onboarding import qualify_onboarding
from domains.core.models import Firm, AuditLog

def test_qualify_dropoff(db_session):
    result = qualify_onboarding("test@example.com", weekly_review=False, db=db_session)
    assert result["dropoff"] is True

def test_qualify_success(db_session):
    result = qualify_onboarding("owner@test.com", weekly_review=True, db=db_session)
    assert result["success"] is True
    assert "firm_id" in result
    firm = db_session.query(Firm).first()
    assert firm.name == "owner Agency"
    audit = db_session.query(AuditLog).first()
    assert audit.action_type == "onboard_qualify"
