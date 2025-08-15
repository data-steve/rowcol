from sqlalchemy.orm import Session
from domains.core.models.correction import Correction as CorrectionModel
from domains.core.schemas.correction import Correction
from domains.core.services.policy_engine import PolicyEngineService
from typing import Optional, List

class CorrectionService:
    def __init__(self, db: Session):
        self.db = db
        self.policy_engine = PolicyEngineService(db)

    def apply_correction(self, firm_id: str, bill_id: int, corrected_gl_account: str, client_id: Optional[int] = None) -> CorrectionModel:
        """Apply a correction to a bill and update policy engine."""
        try:
            correction = CorrectionModel(
                firm_id=firm_id,
                client_id=client_id,
                txn_id=str(bill_id),  # Use txn_id instead of entity_id
                raw_descriptor="bill_correction",  # Use raw_descriptor instead of entity_type
                suggested={"account": corrected_gl_account, "confidence": 0.95},
                final={"account": corrected_gl_account, "class": "expense", "memo": "Corrected GL account"},
                rationale="Manual correction applied",
                created_by=1,  # Mock user ID
                scope="client"
            )
            self.db.add(correction)
            
            # Update policy engine with new rule
            self.policy_engine.add_rule(
                firm_id=firm_id,
                pattern="corrected_gl_account",
                output={"account": corrected_gl_account, "confidence": 0.95}
            )
            
            self.db.commit()
            self.db.refresh(correction)
            return correction
        
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Correction failed: {str(e)}")
        
    def create_correction(self, correction: Correction) -> CorrectionModel:
        """Create a new correction."""
        db_correction = CorrectionModel(**correction.dict())
        self.db.add(db_correction)
        self.db.commit()
        self.db.refresh(db_correction)
        return db_correction

    def get_correction(self, correction_id: int) -> CorrectionModel:
        """Get a correction by ID."""
        correction = self.db.query(CorrectionModel).filter(CorrectionModel.correction_id == correction_id).first()
        if not correction:
            raise ValueError("Correction not found")
        return correction

    def list_corrections(self, firm_id: str) -> List[CorrectionModel]:
        """List all corrections for a firm."""
        corrections = self.db.query(CorrectionModel).filter(CorrectionModel.firm_id == firm_id).all()
        return corrections

    def apply_correction_to_bill(self, correction_id: int, bill_id: int) -> CorrectionModel:
        """Apply a correction to a specific bill."""
        correction = self.db.query(CorrectionModel).filter(CorrectionModel.correction_id == correction_id).first()
        if not correction:
            raise ValueError("Correction not found")
        
        # Mock application logic
        correction.status = "applied"
        self.db.commit()
        self.db.refresh(correction)
        return correction
