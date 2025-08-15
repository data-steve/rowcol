from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
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