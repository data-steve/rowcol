from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.vendor_canonical import VendorCanonical as VendorCanonicalModel
from schemas.vendor_canonical import VendorCanonical
from database import get_db

router = APIRouter(prefix="/api", tags=["VendorCanonical"])

@router.post("/vendor_canonical", response_model=VendorCanonical)
async def create_vendor(vendor: VendorCanonical, db: Session = Depends(get_db)):
    db_vendor = VendorCanonicalModel(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

@router.get("/vendor_canonical/{vendor_id}", response_model=VendorCanonical)
async def get_vendor(vendor_id: int, firm_id: str, db: Session = Depends(get_db)):
    vendor = db.query(VendorCanonicalModel).filter(VendorCanonicalModel.vendor_id == vendor_id, VendorCanonicalModel.firm_id == firm_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor