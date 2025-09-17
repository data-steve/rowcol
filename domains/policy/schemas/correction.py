from pydantic import BaseModel
from typing import Optional, Dict

class CorrectionBase(BaseModel):
    business_id: str
    txn_id: str
    raw_descriptor: str
    final: Dict
    created_by: int
    scope: str
    suggested: Optional[Dict] = None
    rationale: Optional[str] = None

class CorrectionCreate(CorrectionBase):
    pass

class Correction(CorrectionBase):
    correction_id: Optional[int] = None
    business_id: str
    txn_id: str
    raw_descriptor: str
    suggested: Optional[Dict[str, str | float]] = None
    final: Dict[str, str]
    rationale: Optional[str] = None
    created_by: int
    scope: str

    class Config:
        from_attributes = True