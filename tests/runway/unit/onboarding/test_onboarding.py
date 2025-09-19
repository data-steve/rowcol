from sqlalchemy.orm import Session
from runway.onboarding.services.onboarding import OnboardingService
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog

def test_qualify_dropoff(db: Session):
    service = OnboardingService(db)
    business_data = {"business_name": "Test Business", "email": "test@example.com"}
    user_data = {"email": "test@example.com", "weekly_review": False}
    
    business = service.qualify_onboarding(business_data, user_data)
    assert business is not None

def test_qualify_success(db: Session):
    service = OnboardingService(db)
    business_data = {"business_name": "Test Business", "email": "owner@test.com"}
    user_data = {"email": "owner@test.com", "weekly_review": True}
    
    business = service.qualify_onboarding(business_data, user_data)
    assert business is not None
    assert business.business_name == "Test Business"
