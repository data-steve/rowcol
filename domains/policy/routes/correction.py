from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from domains.policy.services.correction import CorrectionService
from domains.policy.schemas.correction import Correction
from database import get_db

router = APIRouter(prefix="/api", tags=["Corrections"])

@router.post("/corrections", response_model=Correction)
async def create_correction(correction: Correction, db: Session = Depends(get_db)):
    service = CorrectionService(db)
    return service.create_correction(correction)

@router.get("/corrections/{correction_id}", response_model=Correction)
async def get_correction(correction_id: int, firm_id: str, db: Session = Depends(get_db)):
    service = CorrectionService(db)
    try:
        return service.get_correction(correction_id, firm_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))