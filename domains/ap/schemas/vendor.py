from pydantic import BaseModel
from typing import Optional

class VendorBase(BaseModel):
    business_id: str
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

# API Request/Response schemas
class VendorUpdate(BaseModel):
    """Update schema for Vendor"""
    name: Optional[str] = None
    contact_email: Optional[str] = None
    payment_terms: Optional[str] = None

class VendorResponse(Vendor):
    """Response schema for Vendor API endpoints"""
    pass