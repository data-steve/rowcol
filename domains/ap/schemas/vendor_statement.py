from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class VendorStatementBase(BaseModel):
    business_id: str
    vendor_id: int
    period: date
    file_ref: Optional[str] = None
    parsed_invoices: Optional[List] = None
    mismatches: Optional[List] = None

class VendorStatementCreate(VendorStatementBase):
    pass

class VendorStatement(VendorStatementBase):
    statement_id: Optional[int] = None

    class Config:
        from_attributes = True