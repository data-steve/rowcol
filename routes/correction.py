from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.correction import Correction as CorrectionModel
from schemas.correction import Correction
from database import get_db

router = APIRouter(prefix="/api", tags=["Corrections"])

@router.post("/corrections", response_model=Correction)
async def create_correction(correction: Correction, db: Session = Depends(get_db)):
    db_correction = CorrectionModel(**correction.dict())
    db.add(db_correction)
    db.commit()
    db.refresh(db_correction)
    return db_correction

@router.get("/corrections/{correction_id}", response_model=Correction)
async def get_correction(correction_id: int, firm_id: str, db: Session = Depends(get_db)):
    correction = db.query(CorrectionModel).filter(CorrectionModel.correction_id == correction_id, CorrectionModel.firm_id == firm_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="Correction not found")
    return correction