from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.services.policy_profile import PolicyProfileService
from domains.core.schemas.policy_profile import PolicyProfile
from database import get_db

router = APIRouter(prefix="/api", tags=["PolicyProfiles"])

@router.post("/policy_profiles", response_model=PolicyProfile)
async def create_policy_profile(profile: PolicyProfile, db: Session = Depends(get_db)):
    service = PolicyProfileService(db)
    return service.create_policy_profile(profile)

@router.get("/policy_profiles/{profile_id}", response_model=PolicyProfile)
async def get_policy_profile(profile_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = PolicyProfileService(db)
    try:
        return service.get_policy_profile(profile_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))