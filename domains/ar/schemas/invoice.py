from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class InvoiceBase(BaseModel):
    business_id: Optional[int] = None
    customer_id: int
    qbo_id: Optional[str] = None
    issue_date: datetime
    due_date: datetime
    total: float
    lines: Optional[List[Dict]] = None
    status: str = "draft"
    confidence: Optional[float] = 0.0
    attachment_refs: Optional[List[str]] = None

class InvoiceCreate(BaseModel):
    customer_id: int
    issue_date: datetime
    due_date: datetime
    total: float
    lines: Optional[List[Dict]] = None
    qbo_id: Optional[str] = None
    status: Optional[str] = "draft"
    confidence: Optional[float] = 0.0
    attachment_refs: Optional[List[str]] = None

class Invoice(InvoiceBase):
    invoice_id: Optional[int] = None

    class Config:
        from_attributes = True

# API Response schemas
class InvoiceResponse(Invoice):
    """Response schema for Invoice API endpoints"""
    pass