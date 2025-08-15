from pydantic import BaseModel
from typing import Optional

class VendorBase(BaseModel):
    firm_id: str
    client_id: Optional[int] = None
    canonical_id: Optional[int] = None
    qbo_id: Optional[str] = None
    w9_status: str = "pending"
    default_gl_account: Optional[str] = None
    terms: Optional[str] = None
    fingerprint_hash: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    vendor_id: Optional[int] = None

    class Config:
        from_attributes = True