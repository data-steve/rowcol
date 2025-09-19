from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentBase(BaseModel):
    business_id: str
    qbo_id: Optional[str] = None
    customer_id: Optional[int] = None
    invoice_ids: Optional[List[int]] = None
    amount: float
    date: datetime
    method: Optional[str] = None

class PaymentCreate(BaseModel):
    customer_id: int
    amount: float
    date: datetime
    method: Optional[str] = None

class Payment(PaymentBase):
    payment_id: Optional[int] = None

    class Config:
        from_attributes = True

# API Response schemas
class PaymentResponse(Payment):
    """Response schema for Payment API endpoints"""
    pass

class PaymentExecutionRequest(BaseModel):
    """Request schema for payment execution"""
    payment_id: int
    execute_date: Optional[datetime] = None

class PaymentScheduleRequest(BaseModel):
    """Request schema for payment scheduling"""
    bill_id: int
    scheduled_date: datetime
    amount: Optional[float] = None