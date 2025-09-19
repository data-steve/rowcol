from pydantic import BaseModel
from typing import Optional

class BusinessBase(BaseModel):
    name: str
    qbo_id: Optional[str] = None
    industry: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass

class Business(BusinessBase):
    business_id: str

    class Config:
        from_attributes = True

# API Request/Response schemas
class BusinessUpdate(BaseModel):
    """Update schema for Business"""
    name: Optional[str] = None
    industry: Optional[str] = None
    qbo_id: Optional[str] = None
