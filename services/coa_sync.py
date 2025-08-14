from sqlalchemy.orm import Session
from models.policy_profile import PolicyProfile as PolicyProfileModel
from schemas.policy_profile import PolicyProfile

class COASyncService:
    def __init__(self, db: Session):
        self.db = db

    def sync_coa(self, firm_id: str, client_id: int) -> PolicyProfile:
        profile = self.db.query(PolicyProfileModel).filter(PolicyProfileModel.firm_id == firm_id, PolicyProfileModel.client_id == client_id).first()
        if not profile:
            raise ValueError("PolicyProfile not found")
        profile.tickmark_map = {"6000": "Expenses", "7000": "Revenue"}
        self.db.commit()
        self.db.refresh(profile)
        return profile
