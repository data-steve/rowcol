from sqlalchemy.orm import Session
from domains.policy.models.policy_profile import PolicyProfile as PolicyProfileModel
from domains.policy.schemas.policy_profile import PolicyProfile

class COASyncService:
    def __init__(self, db: Session):
        self.db = db

    def sync_coa(self, firm_id: str, client_id: int, tickmark_map: dict = None) -> PolicyProfile:
        """Sync Chart of Accounts with QBO and update policy profile."""
        profile = self.db.query(PolicyProfileModel).filter(
            PolicyProfileModel.firm_id == firm_id, 
            PolicyProfileModel.client_id == client_id
        ).first()
        if not profile:
            raise ValueError("PolicyProfile not found")
        
        # Use provided tickmark map or fetch from QBO
        if tickmark_map:
            profile.tickmark_map = tickmark_map
        else:
            # TODO: Implement actual QBO COA sync
            profile.tickmark_map = self._fetch_qbo_coa_mapping(firm_id, client_id)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def _fetch_qbo_coa_mapping(self, firm_id: str, client_id: int) -> dict:
        """Fetch Chart of Accounts mapping from QBO."""
        # TODO: Implement actual QBO COA API integration
        # For now, return a reasonable default mapping
        return {
            "6000": "Operating Expenses",
            "7000": "Revenue",
            "1000": "Assets",
            "2000": "Liabilities",
            "3000": "Equity"
        }
