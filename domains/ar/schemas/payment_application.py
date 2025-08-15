"""
Payment Application schemas for AR domain.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentApplicationCreate(BaseModel):
    customer_id: int
    amount: float
    date: datetime
    method: str
