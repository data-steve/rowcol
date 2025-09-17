from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from runway.onboarding.services.onboarding import OnboardingService

router = APIRouter()

@router.post("/")
def qualify(business_data: dict, user_data: dict, db: Session = Depends(get_db)):
    service = OnboardingService(db)
    return service.qualify_onboarding(business_data, user_data)
