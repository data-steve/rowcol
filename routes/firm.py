from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.firm import Firm as FirmModel
from schemas.firm import Firm
from database import get_db

router = APIRouter(prefix="/api", tags=["Firms"])

@router.post("/firms", response_model=Firm)
async def create_firm(firm: Firm, db: Session = Depends(get_db)):
    db_firm = FirmModel(**firm.dict())
    db.add(db_firm)
    db.commit()
    db.refresh(db_firm)
    return db_firm

@router.get("/firms/{firm_id}", response_model=Firm)
async def get_firm(firm_id: str, db: Session = Depends(get_db)):
    firm = db.query(FirmModel).filter(FirmModel.firm_id == firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    return firm