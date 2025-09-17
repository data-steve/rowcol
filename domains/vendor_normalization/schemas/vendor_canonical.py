from pydantic import BaseModel
from typing import Optional

class VendorCanonicalBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    raw_name: str
    canonical_name: str
    mcc: Optional[str] = None
    naics: Optional[str] = None
    default_gl_account: Optional[str] = None
    confidence: float

class VendorCanonicalCreate(VendorCanonicalBase):
    pass

class VendorCanonical(VendorCanonicalBase):
    vendor_id: Optional[int] = None

    class Config:
        from_attributes = True