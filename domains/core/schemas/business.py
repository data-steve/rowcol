from pydantic import BaseModel
from typing import Optional

class BusinessBase(BaseModel):
    name: str
    qbo_id: Optional[str] = None
    industry: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BusinessBase):
    pass

class Business(BusinessBase):
    business_id: str

    class Config:
        from_attributes = True
