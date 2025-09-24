"""
Payment Application schemas for AR domain.
"""
from pydantic import BaseModel
from datetime import datetime

class PaymentApplicationCreate(BaseModel):
    customer_id: int
    amount: float
    date: datetime
    method: str
