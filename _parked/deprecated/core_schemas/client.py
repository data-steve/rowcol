from pydantic import BaseModel
from typing import Optional

class BusinessBase(BaseModel):
    firm_id: str
    name: str
    qbo_id: Optional[str] = None
    industry: Optional[str] = None
    policy_profile_id: Optional[int] = None

class BusinessCreate(BusinessBase):
    pass

class Business(BusinessBase):
    client_id: int

    class Config:
        from_attributes = True