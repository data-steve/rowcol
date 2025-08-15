from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.core.schemas.rule import Rule
from domains.core.schemas.suggestion import Suggestion
from domains.core.schemas.correction import Correction, CorrectionCreate
from domains.ap.schemas.vendor_canonical import VendorCanonical
from domains.core.schemas.automation import VendorNormalizeInput, TransactionInput
from domains.core.services.policy_engine import PolicyEngineService
from domains.ap.services.vendor_normalization import VendorNormalizationService
from database import get_db
from typing import List

router = APIRouter(prefix="/api/automation", tags=["Automation"])

@router.get("/rules", response_model=List[Rule])
async def list_rules(firm_id: str, client_id: int = None, db: Session = Depends(get_db)):
    from domains.core.services.rule import RuleService
    service = RuleService(db)
    return service.list_rules(firm_id, client_id)

@router.post("/rules", response_model=Rule)
async def create_rule(rule: Rule, db: Session = Depends(get_db)):
    """Create a new rule."""
    from domains.core.services.rule import RuleService
    service = RuleService(db)
    return service.create_rule(rule)

@router.post("/vendors/normalize", response_model=VendorCanonical)
async def normalize_vendor(input: VendorNormalizeInput, db: Session = Depends(get_db)):
    service = VendorNormalizationService(db)
    vendor = service.normalize_vendor(input.raw_name, input.firm_id, input.client_id)
    return vendor

@router.post("/categorize", response_model=Suggestion)
async def categorize_transaction(input: TransactionInput, db: Session = Depends(get_db)):
    service = PolicyEngineService(db)
    suggestion = service.categorize_transaction(input.dict(), input.firm_id, input.client_id)
    return suggestion

@router.post("/corrections", response_model=Correction)
async def apply_correction(correction: CorrectionCreate, db: Session = Depends(get_db)):
    service = PolicyEngineService(db)
    correction = service.apply_correction(Correction(**correction.dict()), correction.firm_id)
    return correction