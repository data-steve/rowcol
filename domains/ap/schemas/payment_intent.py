from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentIntentBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    bill_ids: Optional[List[int]] = None
    provider: str = "qbo"
    total_amount: float
    funding_account: Optional[str] = None
    status: str = "pending"
    issued_at: Optional[datetime] = None
    cleared_at: Optional[datetime] = None
    fees: float = 0.0

class PaymentIntentCreate(PaymentIntentBase):
    pass

class PaymentIntent(PaymentIntentBase):
    intent_id: Optional[int] = None

    class Config:
        from_attributes = True