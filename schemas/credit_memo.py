from pydantic import BaseModel
from typing import Optional

class CreditMemoBase(BaseModel):
    firm_id: Optional[str] = None
    client_id: Optional[int] = None
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
    firm_id: str  # Required in response

    class Config:
        from_attributes = True