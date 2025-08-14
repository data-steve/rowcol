from sqlalchemy.orm import Session
from models.policy_profile import PolicyProfile as PolicyProfileModel
from schemas.policy_profile import PolicyProfile
from typing import List

class PolicyProfileService:
    def __init__(self, db: Session):
        self.db = db

    def create_policy_profile(self, profile: PolicyProfile) -> PolicyProfile:
        """Create a new policy profile."""
        db_profile = PolicyProfileModel(**profile.dict())
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_policy_profile(self, profile_id: int, firm_id: str) -> PolicyProfile:
        """Get a policy profile by ID with firm_id filtering."""
        profile = self.db.query(PolicyProfileModel).filter(
            PolicyProfileModel.profile_id == profile_id,
            PolicyProfileModel.firm_id == firm_id
        ).first()
        if not profile:
            raise ValueError("Policy profile not found")
        return profile

    def list_policy_profiles(self, firm_id: str) -> List[PolicyProfile]:
        """List all policy profiles for a firm."""
        profiles = self.db.query(PolicyProfileModel).filter(
            PolicyProfileModel.firm_id == firm_id
        ).all()
        return profiles
