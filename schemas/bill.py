from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class BillBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
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