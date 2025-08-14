from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.vendor_canonical import VendorCanonicalService
from schemas.vendor_canonical import VendorCanonical
from database import get_db

router = APIRouter(prefix="/api", tags=["VendorCanonical"])

@router.post("/vendor_canonical", response_model=VendorCanonical)
async def create_vendor(vendor: VendorCanonical, db: Session = Depends(get_db)):
    service = VendorCanonicalService(db)
    return service.create_vendor_canonical(vendor)

@router.get("/vendor_canonical/{vendor_id}", response_model=VendorCanonical)
async def get_vendor(vendor_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = VendorCanonicalService(db)
    try:
        return service.get_vendor_canonical(vendor_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))