from sqlalchemy.orm import Session
from domains.policy.models.policy_profile import PolicyProfile as PolicyProfileModel
from domains.policy.schemas.policy_profile import PolicyProfile

class COASyncService:
    def __init__(self, db: Session):
        self.db = db

    def sync_coa(self, business_id: str) -> PolicyProfile:
        """Sync Chart of Accounts with QBO and update policy profile."""
        profile = self.db.query(PolicyProfileModel).filter(
            PolicyProfileModel.business_id == business_id
        ).first()
        if not profile:
            raise ValueError("PolicyProfile not found")
        
        # TODO: Phase 4+ - Evaluate if COA sync is needed for Oodaloo
        # - Do business owners need custom GL account mapping?
        # - Should this be automatic based on QBO setup?
        # - tickmark_map was a RowCol Close workbook feature - likely not needed
        # For now, use simple default mapping
        profile.tickmark_map = self._fetch_qbo_coa_mapping(business_id)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def _fetch_qbo_coa_mapping(self, business_id: str) -> dict:
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
