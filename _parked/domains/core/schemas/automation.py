from pydantic import BaseModel
from typing import Optional

class VendorNormalizeInput(BaseModel):
    raw_name: str
    firm_id: str
    client_id: Optional[int] = None

class TransactionInput(BaseModel):
    txn_id: str
    description: str
    amount: float
    firm_id: str
    client_id: Optional[int] = None
    mcc: Optional[str] = None
    weekday: Optional[str] = None
