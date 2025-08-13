from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.policy_profile import PolicyProfile as PolicyProfileModel
from schemas.policy_profile import PolicyProfile
from database import get_db

router = APIRouter(prefix="/api", tags=["PolicyProfiles"])

@router.post("/policy_profiles", response_model=PolicyProfile)
async def create_policy_profile(profile: PolicyProfile, db: Session = Depends(get_db)):
    db_profile = PolicyProfileModel(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/policy_profiles/{profile_id}", response_model=PolicyProfile)
async def get_policy_profile(profile_id: int, firm_id: str, db: Session = Depends(get_db)):
    profile = db.query(PolicyProfileModel).filter(PolicyProfileModel.profile_id == profile_id, PolicyProfileModel.firm_id == firm_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Policy profile not found")
    return profile