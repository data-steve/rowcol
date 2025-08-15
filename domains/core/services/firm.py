from sqlalchemy.orm import Session
from domains.core.models.firm import Firm as FirmModel
from domains.core.schemas.firm import Firm
from typing import List

class FirmService:
    def __init__(self, db: Session):
        self.db = db

    def create_firm(self, firm: Firm) -> FirmModel:
        """Create a new firm."""
        db_firm = FirmModel(**firm.dict())
        self.db.add(db_firm)
        self.db.commit()
        self.db.refresh(db_firm)
        return db_firm

    def get_firm(self, firm_id: str) -> FirmModel:
        """Get a firm by ID."""
        firm = self.db.query(FirmModel).filter(FirmModel.firm_id == firm_id).first()
        if not firm:
            raise ValueError("Firm not found")
        return firm

    def list_firms(self) -> List[FirmModel]:
        """List all firms."""
        firms = self.db.query(FirmModel).all()
        return firms
