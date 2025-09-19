from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class BillBase(BaseModel):
    business_id: str
    vendor_id: Optional[int] = None
    qbo_bill_id: str
    amount: float
    due_date: Optional[datetime] = None
    status: str = "pending"
    extracted_fields: Optional[Dict[str, Any]] = None
    gl_account: Optional[str] = None
    confidence: float = 0.0

class BillCreate(BillBase):
    pass

class Bill(BillBase):
    bill_id: Optional[int] = None

    class Config:
        from_attributes = True

# API Response schemas
class BillResponse(Bill):
    """Response schema for Bill API endpoints"""
    pass

class BillApprovalRequest(BaseModel):
    """Request schema for bill approval"""
    bill_id: int
    approved: bool
    notes: Optional[str] = None