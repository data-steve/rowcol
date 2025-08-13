from sqlalchemy.orm import Session
from models.policy_profile import PolicyProfile as PolicyProfileModel
from schemas.policy_profile import PolicyProfile

class PolicyProfileService:
    def __init__(self, db: Session):
        self.db = db

    def update_policy(self, firm_id: str, client_id: int, policy: PolicyProfile) -> PolicyProfile:
        profile = self.db.query(PolicyProfileModel).filter(PolicyProfileModel.firm_id == firm_id, PolicyProfileModel.client_id == client_id).first()
        if not profile:
            profile = PolicyProfileModel(**policy.dict())
            self.db.add(profile)
        else:
            for key, value in policy.dict().items():
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return PolicyProfile.from_orm(profile)
