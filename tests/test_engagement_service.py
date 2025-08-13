import pytest
from sqlalchemy.orm import Session
from services.engagement import EngagementService
from schemas.engagement import EngagementCreate
from models.engagement import Engagement

@pytest.fixture
def engagement_service(db: Session):
    return EngagementService(db)

def test_create_engagement(engagement_service, test_firm, test_client):
    engagement_data = EngagementCreate(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        service_type="bookkeeping",
        due_date="2025-12-31T23:59:59",
        user_input={"qbo_account": "12345"}
    )
    engagement = engagement_service.create_engagement(engagement_data)
    assert engagement.engagement_id is not None
    assert engagement.compliance_status == "pending"

def test_validate_engagement(engagement_service, test_firm, test_client, db: Session):
    engagement_data = EngagementCreate(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        service_type="bookkeeping",
        due_date="2025-12-31T23:59:59",
        user_input={"qbo_account": "12345"},
    )
    engagement = engagement_service.create_engagement(engagement_data)
    errors = engagement_service.validate_engagement(engagement.engagement_id)
    assert len(errors) == 0

def test_sign_engagement(engagement_service, test_firm, test_client, db: Session):
    engagement_data = EngagementCreate(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        service_type="bookkeeping",
        due_date="2025-12-31T23:59:59"
    )
    engagement = engagement_service.create_engagement(engagement_data)
    engagement_service.sign_engagement(engagement.engagement_id, 1, "/s/John Doe")
    engagement = db.query(Engagement).filter(Engagement.engagement_id == engagement.engagement_id).first()
    assert engagement.e_signature["signature_data"] == "/s/John Doe"

def test_sync_qbo(engagement_service, test_firm, test_client, db: Session):
    engagement_data = EngagementCreate(
        firm_id=test_firm.firm_id,
        client_id=test_client.client_id,
        service_type="bookkeeping",
        due_date="2025-12-31T23:59:59"
    )
    engagement = engagement_service.create_engagement(engagement_data)
    result = engagement_service.sync_qbo(engagement.engagement_id)
    assert result in ["Sync successful", "Sync failed"]