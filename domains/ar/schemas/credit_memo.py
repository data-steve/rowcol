from pydantic import BaseModel
from typing import Optional

class CreditMemoBase(BaseModel):
    business_id: Optional[int] = None
    qbo_id: Optional[str] = None
    invoice_id: int
    amount: float
    reason: Optional[str] = None
    status: Optional[str] = "review"

class CreditMemoCreate(BaseModel):
    invoice_id: int
    amount: float
    reason: Optional[str] = None

class CreditMemo(CreditMemoBase):
    memo_id: Optional[int] = None
    business_id: int  # Required in response

    class Config:
        from_attributes = True