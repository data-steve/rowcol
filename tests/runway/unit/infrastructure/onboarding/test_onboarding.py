import pytest
from sqlalchemy.orm import Session
from runway.services.2_experiences.onboarding import OnboardingService
from domains.core.models.business import Business
from domains.core.models.audit_log import AuditLog

@pytest.mark.asyncio
async def test_qualify_dropoff(db: Session):
    service = OnboardingService(db)
    business_data = {"name": "Test Business", "industry": "Software"}
    user_data = {"email": "test@example.com", "full_name": "Test User", "password_hash": "hashed_password"}
    
    business = await service.qualify_onboarding(business_data, user_data)
    assert business is not None

@pytest.mark.asyncio
async def test_qualify_success(db: Session):
    service = OnboardingService(db)
    business_data = {"name": "Test Business", "industry": "Software"}
    user_data = {"email": "owner@test.com", "full_name": "Owner User", "password_hash": "hashed_password"}
    
    business = await service.qualify_onboarding(business_data, user_data)
    assert business is not None
    assert business.name == "Test Business"
