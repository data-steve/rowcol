from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    business_id: int
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

# API Response schemas
class CustomerResponse(Customer):
    """Response schema for Customer API endpoints"""
    pass