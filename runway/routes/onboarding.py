from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.database.session import get_db
from runway.experiences.onboarding import OnboardingService
from typing import Dict, Any

router = APIRouter()

@router.post("/")
def qualify(business_data: dict, user_data: dict, db: Session = Depends(get_db)):
    service = OnboardingService(db)
    return service.qualify_onboarding(business_data, user_data)

@router.get("/{business_id}/status")
def get_onboarding_status(business_id: str, db: Session = Depends(get_db)):
    """Get comprehensive onboarding status including runway replay if available."""
    service = OnboardingService(db)
    return service.get_onboarding_status(business_id)

# Test drive functionality moved to dedicated test_drive routes
# Use /api/v1/test-drive/{business_id}/test-drive instead


# QBO connection routes moved to runway/infrastructure/qbo_setup/routes/qbo_setup.py
# Use /api/v1/infrastructure/qbo-setup/{business_id}/connect instead
