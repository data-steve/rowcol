from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class InvoiceBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    customer_id: int
    qbo_id: Optional[str] = None
    issue_date: datetime
    due_date: datetime
    total: float
    lines: Optional[List[Dict]] = None
    status: str = "draft"
    confidence: Optional[float] = 0.0
    attachment_refs: Optional[List[str]] = None

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    invoice_id: Optional[int] = None

    class Config:
        from_attributes = True