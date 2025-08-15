from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    qbo_id: Optional[str] = None
    name: str
    email: Optional[str] = None
    terms: Optional[str] = None
    fingerprint_hash: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: Optional[int] = None

    class Config:
        from_attributes = True