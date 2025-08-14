from sqlalchemy.orm import Session
from models.engagement import Engagement as EngagementModel
from schemas.engagement import Engagement
from typing import List, Optional
from datetime import datetime

class EngagementService:
    def __init__(self, db: Session):
        self.db = db

    def create_engagement(self, engagement: Engagement) -> EngagementModel:
        """Create a new engagement."""
        db_engagement = EngagementModel(**engagement.model_dump())
        self.db.add(db_engagement)
        self.db.commit()
        self.db.refresh(db_engagement)
        return db_engagement

    def get_engagement(self, engagement_id: int) -> EngagementModel:
        """Get an engagement by ID."""
        engagement = self.db.query(EngagementModel).filter(EngagementModel.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        return engagement

    def list_engagements(self) -> List[EngagementModel]:
        """List all engagements."""
        engagements = self.db.query(EngagementModel).all()
        return engagements

    def validate_engagement(self, engagement_id: int) -> EngagementModel:
        """Validate an engagement (mock implementation)."""
        engagement = self.db.query(EngagementModel).filter(EngagementModel.engagement_id == engagement_id).first()
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Mock validation logic
        engagement.status = "validated"
        self.db.commit()
        self.db.refresh(engagement)
        return engagement

    def sign_engagement(self, engagement_id: int, firm_id: str, signature_data: dict) -> EngagementModel:
        """Sign an engagement."""
        engagement = self.db.query(EngagementModel).filter(
            EngagementModel.engagement_id == engagement_id,
            EngagementModel.firm_id == firm_id
        ).first()
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Set signing data
        engagement.status = "signed"
        engagement.e_signature = signature_data
        engagement.agreed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(engagement)
        return engagement

    def sync_qbo(self, engagement_id: int, firm_id: str) -> EngagementModel:
        """Sync engagement with QBO (mock implementation)."""
        engagement = self.db.query(EngagementModel).filter(
            EngagementModel.engagement_id == engagement_id,
            EngagementModel.firm_id == firm_id
        ).first()
        if not engagement:
            raise ValueError("Engagement not found")
        
        # Mock QBO sync
        engagement.qbo_id = f"qbo_{engagement_id}"
        engagement.qbo_sync_status = "success"
        engagement.status = "synced"
        self.db.commit()
        self.db.refresh(engagement)
        return engagement