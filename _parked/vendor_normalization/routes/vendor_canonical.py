from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infra.database.session import get_db
from domains.vendor_normalization.services import VendorNormalizationService

router = APIRouter()

@router.get("/{vendor_id}")
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    service = VendorNormalizationService(db)
    return service.get_vendor(vendor_id)