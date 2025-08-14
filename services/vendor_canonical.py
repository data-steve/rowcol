from sqlalchemy.orm import Session
from models.vendor_canonical import VendorCanonical as VendorCanonicalModel
from schemas.vendor_canonical import VendorCanonical
from typing import List

class VendorCanonicalService:
    def __init__(self, db: Session):
        self.db = db

    def create_vendor_canonical(self, vendor: VendorCanonical) -> VendorCanonical:
        """Create a new vendor canonical."""
        db_vendor = VendorCanonicalModel(**vendor.dict())
        self.db.add(db_vendor)
        self.db.commit()
        self.db.refresh(db_vendor)
        return db_vendor

    def get_vendor_canonical(self, vendor_id: int, firm_id: str) -> VendorCanonical:
        """Get a vendor canonical by ID with firm_id filtering."""
        vendor = self.db.query(VendorCanonicalModel).filter(
            VendorCanonicalModel.vendor_id == vendor_id,
            VendorCanonicalModel.firm_id == firm_id
        ).first()
        if not vendor:
            raise ValueError("Vendor canonical not found")
        return vendor

    def list_vendor_canonicals(self, firm_id: str) -> List[VendorCanonical]:
        """List all vendor canonicals for a firm."""
        vendors = self.db.query(VendorCanonicalModel).filter(
            VendorCanonicalModel.firm_id == firm_id
        ).all()
        return vendors
