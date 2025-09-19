from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from pydantic import BaseModel

router = APIRouter()

class VendorNormalizeRequest(BaseModel):
    raw_name: str
    firm_id: str  # TODO: Update to business_id in Phase 1

class TransactionCategorizeRequest(BaseModel):
    txn_id: str
    description: str
    amount: float
    firm_id: str  # TODO: Update to business_id in Phase 1

@router.post("/vendors/normalize")
def normalize_vendor(request: VendorNormalizeRequest, db: Session = Depends(get_db)):
    """Normalize vendor names for automation."""
    # Simple normalization logic for testing
    canonical_name = request.raw_name.rstrip('0123456789')
    return {"canonical_name": canonical_name, "raw_name": request.raw_name}

@router.post("/categorize")
def categorize_transaction(request: TransactionCategorizeRequest, db: Session = Depends(get_db)):
    """Categorize transactions for automation."""
    # Simple categorization logic for testing
    return {
        "txn_id": request.txn_id,
        "description": request.description,
        "category": "Office Expenses",  # Default category
        "confidence": 0.8
    }
