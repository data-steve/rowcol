from pydantic import BaseModel
from typing import Optional, Dict

class FirmBase(BaseModel):
    name: str
    qbo_id: Optional[str] = None
    pricing_tier: str
    doc_volume: int
    settings: Dict

class FirmCreate(FirmBase):
    pass

class Firm(FirmBase):
    firm_id: str

    class Config:
        from_attributes = True