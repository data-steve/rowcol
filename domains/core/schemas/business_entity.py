from pydantic import BaseModel
from typing import Optional

class BusinessEntityBase(BaseModel):
    business_id: str
    name: str
    ein: Optional[str] = None
    tax_classification: str
    state: Optional[str] = None

class BusinessEntityCreate(BusinessEntityBase):
    pass

class BusinessEntity(BusinessEntityBase):
    id: int

    class Config:
        from_attributes = True